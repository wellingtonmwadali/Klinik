# """Service layer for doctor-related business logic."""
# from datetime import date, datetime, time, timedelta
# from typing import List, Dict, Any, Optional

# from django.db import models, transaction
# from django.utils import timezone
# from django.core.exceptions import ValidationError

# from .models import Doctor, DoctorWorkSchedule, DoctorUnavailability
# from apps.appointments.models import Appointment


# class AvailabilityService:
#     """Service for calculating doctor availability slots."""
    
#     # Buffer time (in minutes) between consultations for doctor preparation and delays
#     BUFFER_MINUTES = 10

#     @staticmethod
#     def calculate_available_slots(doctor: Doctor, requested_date: date) -> Dict[str, Any]:
#         """
#         Calculate available time slots for a doctor on a given date.
        
#         Args:
#             doctor: Doctor instance
#             requested_date: Date to check availability for
            
#         Returns:
#             Dictionary with slots and metadata
            
#         Raises:
#             ValidationError: If doctor is unavailable or date is invalid
#         """
#         # Validate doctor status
#         AvailabilityService._validate_doctor(doctor)
        
#         # Validate requested date
#         AvailabilityService._validate_date(doctor, requested_date)
        
#         # Get work schedule for the requested weekday
#         weekday = requested_date.weekday()
#         work_schedule = AvailabilityService._get_work_schedule(doctor, requested_date, weekday)
        
#         if not work_schedule:
#             # Doctor doesn't work on this day
#             return {
#                 'doctor_id': doctor.id,
#                 'doctor_name': f"Dr. {doctor.full_name}",
#                 'specialization': doctor.specialization,
#                 'date': requested_date.isoformat(),
#                 'consultation_duration': doctor.consultation_duration,
#                 'available_slots': [],
#                 'total_slots': 0,
#                 'work_hours': None,
#                 'message': f"Doctor does not work on {requested_date.strftime('%A')}s"
#             }
        
#         # Generate all possible slots based on work hours
#         all_slots = AvailabilityService._generate_slots(
#             doctor,
#             requested_date,
#             work_schedule
#         )
        
#         # Filter out unavailable slots
#         available_slots = AvailabilityService._filter_unavailable_slots(
#             doctor,
#             requested_date,
#             all_slots
#         )
        
#         # Build response
#         return {
#             'doctor_id': doctor.id,
#             'doctor_name': f"Dr. {doctor.full_name}",
#             'specialization': doctor.specialization,
#             'date': requested_date.isoformat(),
#             'consultation_duration': doctor.consultation_duration,
#             'available_slots': available_slots,
#             'total_slots': len(available_slots),
#             'work_hours': {
#                 'start': work_schedule.start_time.strftime('%H:%M:%S'),
#                 'end': work_schedule.end_time.strftime('%H:%M:%S'),
#                 'break_start': work_schedule.break_start_time.strftime('%H:%M:%S') if work_schedule.break_start_time else None,
#                 'break_end': work_schedule.break_end_time.strftime('%H:%M:%S') if work_schedule.break_end_time else None,
#             }
#         }
    
#     @staticmethod
#     def _validate_doctor(doctor: Doctor) -> None:
#         """Validate doctor is available for appointments."""
#         if not doctor.is_active:
#             raise ValidationError(
#                 f"Doctor {doctor.full_name} is currently inactive and not accepting appointments. "
#                 f"Please contact the clinic for assistance."
#             )
        
#         if doctor.status == Doctor.STATUS_INACTIVE:
#             raise ValidationError(
#                 f"Doctor {doctor.full_name} is marked as inactive. "
#                 f"Please choose another doctor or contact the clinic."
#             )
        
#         if doctor.status == Doctor.STATUS_ON_LEAVE:
#             raise ValidationError(
#                 f"Doctor {doctor.full_name} is currently on leave. "
#                 f"Please choose another doctor or try again later."
#             )
        
#         if not doctor.is_accepting_appointments:
#             raise ValidationError(
#                 f"Doctor {doctor.full_name} is not currently accepting new appointments. "
#                 f"Please choose another doctor or contact the clinic."
#             )
    
#     @staticmethod
#     def _validate_date(doctor: Doctor, requested_date: date) -> None:
#         """Validate the requested date is bookable."""
#         today = timezone.now().date()
        
#         # Check if date is in the past
#         if requested_date < today:
#             raise ValidationError(
#                 f"Cannot book appointments in the past. "
#                 f"Date {requested_date} is before today ({today}). "
#                 f"Please select a date from today onwards."
#             )
        
#         # Check if date exceeds maximum advance booking days
#         max_date = today + timedelta(days=doctor.max_advance_booking_days)
#         if requested_date > max_date:
#             raise ValidationError(
#                 f"Date {requested_date} exceeds maximum advance booking limit. "
#                 f"Doctor {doctor.full_name} allows bookings up to {doctor.max_advance_booking_days} days in advance. "
#                 f"Latest bookable date is {max_date}. Please select an earlier date."
#             )
    
#     @staticmethod
#     def _get_work_schedule(
#         doctor: Doctor,
#         requested_date: date,
#         weekday: int,
#     ) -> Optional[DoctorWorkSchedule]:
#         """Get the applicable work schedule for a doctor on a specific date."""
#         try:
#             schedules = (
#                 DoctorWorkSchedule.objects.filter(
#                     doctor=doctor,
#                     weekday=weekday,
#                     effective_from__lte=requested_date,
#                 )
#                 .filter(
#                     models.Q(effective_until__isnull=True)
#                     | models.Q(effective_until__gte=requested_date)
#                 )
#                 .order_by('-effective_from', '-id')
#             )

#             return schedules.first()
#         except Exception as e:
#             raise ValidationError(f"Error fetching work schedule: {str(e)}")
    
#     @staticmethod
#     def _generate_slots(
#         doctor: Doctor,
#         requested_date: date,
#         work_schedule: DoctorWorkSchedule
#     ) -> List[Dict[str, Any]]:
#         """Generate all possible time slots for a work day."""
#         if not work_schedule:
#             return []
        
#         try:
#             slots = []
#             consultation_duration = doctor.consultation_duration
            
#             # Validate required fields exist
#             if not work_schedule.start_time or not work_schedule.end_time:
#                 return []
            
#             # Start with work start time (naive datetime)
#             current_time = datetime.combine(requested_date, work_schedule.start_time)
#             end_datetime = datetime.combine(requested_date, work_schedule.end_time)
            
#             # Handle break times
#             break_start = None
#             break_end = None
#             if work_schedule.break_start_time and work_schedule.break_end_time:
#                 break_start = datetime.combine(requested_date, work_schedule.break_start_time)
#                 break_end = datetime.combine(requested_date, work_schedule.break_end_time)
            
#             # Generate slots
#             while current_time < end_datetime:
#                 slot_end = current_time + timedelta(minutes=consultation_duration)
                
#                 # Check if slot would extend past work end time
#                 if slot_end > end_datetime:
#                     break
                
#                 # Check if slot overlaps with break time
#                 if break_start and break_end:
#                     # Skip if slot overlaps with break
#                     if not (slot_end <= break_start or current_time >= break_end):
#                         # Move to end of break
#                         if current_time < break_end:
#                             current_time = break_end
#                             continue
                
#                 # Add slot - make times aware as UTC
#                 try:
#                     slot_start_utc = timezone.make_aware(current_time, timezone.utc)
#                     slot_end_utc = timezone.make_aware(slot_end, timezone.utc)
                    
#                     slots.append({
#                         'start_time': current_time.time().isoformat(),
#                         'end_time': slot_end.time().isoformat(),
#                         'start_datetime': slot_start_utc.isoformat(),
#                         'end_datetime': slot_end_utc.isoformat(),
#                     })
#                 except (ValueError, TypeError) as e:
#                     # Log error and continue - skip this slot
#                     continue
                
#                 # Move to next slot (add buffer time for doctor preparation)
#                 current_time = slot_end + timedelta(minutes=AvailabilityService.BUFFER_MINUTES)
            
#             return slots
        
#         except Exception as e:
#             raise ValidationError(f"Error generating time slots: {str(e)}")
    
#     @staticmethod
#     def _filter_unavailable_slots(
#         doctor: Doctor,
#         requested_date: date,
#         all_slots: List[Dict[str, Any]]
#     ) -> List[Dict[str, Any]]:
#         """Filter out slots that are unavailable due to bookings or unavailability."""
#         if not all_slots:
#             return []
        
#         try:
#             # Get current time in UTC
#             now_utc = timezone.now()
            
#             # Get all active appointments for the doctor on this date
#             start_of_day = timezone.make_aware(
#                 datetime.combine(requested_date, time.min),
#                 timezone.utc
#             )
#             end_of_day = timezone.make_aware(
#                 datetime.combine(requested_date, time.max),
#                 timezone.utc
#             )
            
#             # Get active appointments as list to avoid multiple DB queries
#             active_appointments = list(Appointment.objects.filter(
#                 doctor=doctor,
#                 start_datetime__gte=start_of_day,
#                 start_datetime__lte=end_of_day,
#                 status__in=[
#                     Appointment.STATUS_SCHEDULED,
#                     Appointment.STATUS_CONFIRMED,
#                     Appointment.STATUS_IN_PROGRESS
#                 ]
#             ).values_list('start_datetime', 'end_datetime'))
            
#             # Get unavailability periods for this date
#             unavailability_periods = list(DoctorUnavailability.objects.filter(
#                 doctor=doctor,
#                 start_datetime__lte=end_of_day,
#                 end_datetime__gte=start_of_day
#             ).values_list('start_datetime', 'end_datetime'))
            
#             # Filter slots
#             available_slots = []
#             for slot in all_slots:
#                 try:
#                     # Safely parse ISO format strings
#                     start_datetime_str = slot.get('start_datetime', '')
#                     end_datetime_str = slot.get('end_datetime', '')
                    
#                     if not start_datetime_str or not end_datetime_str:
#                         continue
                    
#                     # Parse ISO format datetime strings
#                     slot_start = datetime.fromisoformat(
#                         start_datetime_str.replace('Z', '+00:00')
#                     )
#                     slot_end = datetime.fromisoformat(
#                         end_datetime_str.replace('Z', '+00:00')
#                     )
                    
#                     # Skip if slot is in the past
#                     if slot_start < now_utc:
#                         continue
                    
#                     # Check if slot overlaps with any appointment
#                     is_booked = any(
#                         AvailabilityService._time_ranges_overlap(
#                             slot_start, slot_end, appt_start, appt_end
#                         )
#                         for appt_start, appt_end in active_appointments
#                     )
                    
#                     if is_booked:
#                         continue
                    
#                     # Check if slot overlaps with unavailability
#                     is_unavailable = any(
#                         AvailabilityService._time_ranges_overlap(
#                             slot_start, slot_end, unavail_start, unavail_end
#                         )
#                         for unavail_start, unavail_end in unavailability_periods
#                     )
                    
#                     if is_unavailable:
#                         continue
                    
#                     # Slot is available
#                     available_slots.append(slot)
                
#                 except (ValueError, TypeError, KeyError) as e:
#                     # Skip slots that can't be parsed
#                     continue
            
#             return available_slots
        
#         except Exception as e:
#             raise ValidationError(f"Error filtering available slots: {str(e)}")
    
#     @staticmethod
#     def _time_ranges_overlap(
#         start1: datetime,
#         end1: datetime,
#         start2: datetime,
#         end2: datetime
#     ) -> bool:
#         """Check if two time ranges overlap."""
#         if not all([start1, end1, start2, end2]):
#             return False
#         try:
#             return start1 < end2 and end1 > start2
#         except (TypeError, ValueError):
#             return False


# class WorkScheduleService:
#     """Service for setting a doctor's weekly work schedule as one atomic unit."""

#     @staticmethod
#     def _net_hours(day: Dict[str, Any]) -> float:
#         gross = DoctorWorkSchedule._hours_between(day["start_time"], day["end_time"])
#         break_hours = DoctorWorkSchedule._hours_between(
#             day["break_start_time"], day["break_end_time"]
#         )
#         return gross - break_hours

#     @staticmethod
#     @transaction.atomic
#     def set_weekly_schedule(
#         doctor: Doctor,
#         days: List[Dict[str, Any]],
#         effective_from: date,
#         effective_until: Optional[date] = None,
#     ) -> List[DoctorWorkSchedule]:
#         """
#         Replace a doctor's work schedule for the given effective period.

#         Args:
#             doctor: Doctor instance
#             days: list of dicts, one per working day, each with keys
#                 weekday, start_time, end_time, break_start_time, break_end_time
#             effective_from: date the new schedule takes effect
#             effective_until: optional date the schedule ends (None = indefinite)

#         Returns:
#             The newly created DoctorWorkSchedule instances.

#         Raises:
#             ValidationError: if the submitted days don't satisfy the clinic's
#                 scheduling rules (5 distinct weekdays, 40 net hours/week, and
#                 each day's own rules enforced via DoctorWorkSchedule.clean()).
#         """
#         if len(days) != DoctorWorkSchedule.WORKING_DAYS_PER_WEEK:
#             raise ValidationError(
#                 f"Exactly {DoctorWorkSchedule.WORKING_DAYS_PER_WEEK} working days must be "
#                 f"provided; got {len(days)}."
#             )

#         weekdays = [day["weekday"] for day in days]
#         if len(set(weekdays)) != len(weekdays):
#             raise ValidationError("Duplicate weekdays are not allowed in a weekly schedule.")

#         # Clear out any existing schedule for this effective period first so that
#         # per-instance validation below (in particular the uniqueness check on
#         # doctor+weekday+start_time+effective_from) isn't tripped up by the rows
#         # we're about to replace. If anything below raises, @transaction.atomic
#         # rolls this delete back too.
#         DoctorWorkSchedule.objects.filter(
#             doctor=doctor,
#             effective_from=effective_from,
#             effective_until=effective_until,
#         ).delete()

#         instances = []
#         total_net_hours = 0.0
#         for day in days:
#             instance = DoctorWorkSchedule(
#                 doctor=doctor,
#                 effective_from=effective_from,
#                 effective_until=effective_until,
#                 **day,
#             )
#             instance.full_clean()
#             instances.append(instance)
#             total_net_hours += WorkScheduleService._net_hours(day)

#         if total_net_hours != DoctorWorkSchedule.WEEKLY_HOURS:
#             raise ValidationError(
#                 f"Total weekly hours must equal {DoctorWorkSchedule.WEEKLY_HOURS}; "
#                 f"got {total_net_hours}."
#             )

#         DoctorWorkSchedule.objects.bulk_create(instances)

#         return instances


"""Service layer for doctor-related business logic."""
import uuid
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Any, Optional

from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Doctor, DoctorWorkSchedule, DoctorUnavailability
from apps.appointments.models import Appointment


class AvailabilityService:
    """Service for calculating doctor availability slots."""
    
    # Buffer time (in minutes) between consultations for doctor preparation and delays
    BUFFER_MINUTES = 10

    @staticmethod
    def calculate_available_slots(
        doctor: Doctor,
        requested_date: date,
        exclude_appointment_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """
        Calculate available time slots for a doctor on a given date.
        
        Args:
            doctor: Doctor instance
            requested_date: Date to check availability for
            exclude_appointment_id: If given, this appointment's own current
                slot is not counted as "booked" when computing availability.
                Used when rescheduling, so an appointment doesn't conflict
                with itself.
            
        Returns:
            Dictionary with slots and metadata
            
        Raises:
            ValidationError: If doctor is unavailable or date is invalid
        """
        # Validate doctor status
        AvailabilityService._validate_doctor(doctor)
        
        # Validate requested date
        AvailabilityService._validate_date(doctor, requested_date)
        
        # Get work schedule for the requested weekday
        weekday = requested_date.weekday()
        work_schedule = AvailabilityService._get_work_schedule(doctor, requested_date, weekday)
        
        if not work_schedule:
            # Doctor doesn't work on this day
            return {
                'doctor_id': doctor.id,
                'doctor_name': f"Dr. {doctor.full_name}",
                'specialization': doctor.specialization,
                'date': requested_date.isoformat(),
                'consultation_duration': doctor.consultation_duration,
                'available_slots': [],
                'total_slots': 0,
                'work_hours': None,
                'message': f"Doctor does not work on {requested_date.strftime('%A')}s"
            }
        
        # Generate all possible slots based on work hours
        all_slots = AvailabilityService._generate_slots(
            doctor,
            requested_date,
            work_schedule
        )
        
        # Filter out unavailable slots
        available_slots = AvailabilityService._filter_unavailable_slots(
            doctor,
            requested_date,
            all_slots,
            exclude_appointment_id=exclude_appointment_id,
        )
        
        # Build response
        return {
            'doctor_id': doctor.id,
            'doctor_name': f"Dr. {doctor.full_name}",
            'specialization': doctor.specialization,
            'date': requested_date.isoformat(),
            'consultation_duration': doctor.consultation_duration,
            'available_slots': available_slots,
            'total_slots': len(available_slots),
            'work_hours': {
                'start': work_schedule.start_time.strftime('%H:%M:%S'),
                'end': work_schedule.end_time.strftime('%H:%M:%S'),
                'break_start': work_schedule.break_start_time.strftime('%H:%M:%S') if work_schedule.break_start_time else None,
                'break_end': work_schedule.break_end_time.strftime('%H:%M:%S') if work_schedule.break_end_time else None,
            }
        }
    
    @staticmethod
    def _validate_doctor(doctor: Doctor) -> None:
        """Validate doctor is available for appointments."""
        if not doctor.is_active:
            raise ValidationError(
                f"Doctor {doctor.full_name} is currently inactive and not accepting appointments. "
                f"Please contact the clinic for assistance."
            )
        
        if doctor.status == Doctor.STATUS_INACTIVE:
            raise ValidationError(
                f"Doctor {doctor.full_name} is marked as inactive. "
                f"Please choose another doctor or contact the clinic."
            )
        
        if doctor.status == Doctor.STATUS_ON_LEAVE:
            raise ValidationError(
                f"Doctor {doctor.full_name} is currently on leave. "
                f"Please choose another doctor or try again later."
            )
        
        if not doctor.is_accepting_appointments:
            raise ValidationError(
                f"Doctor {doctor.full_name} is not currently accepting new appointments. "
                f"Please choose another doctor or contact the clinic."
            )
    
    @staticmethod
    def _validate_date(doctor: Doctor, requested_date: date) -> None:
        """Validate the requested date is bookable."""
        today = timezone.now().date()
        
        # Check if date is in the past
        if requested_date < today:
            raise ValidationError(
                f"Cannot book appointments in the past. "
                f"Date {requested_date} is before today ({today}). "
                f"Please select a date from today onwards."
            )
        
        # Check if date exceeds maximum advance booking days
        max_date = today + timedelta(days=doctor.max_advance_booking_days)
        if requested_date > max_date:
            raise ValidationError(
                f"Date {requested_date} exceeds maximum advance booking limit. "
                f"Doctor {doctor.full_name} allows bookings up to {doctor.max_advance_booking_days} days in advance. "
                f"Latest bookable date is {max_date}. Please select an earlier date."
            )
    
    @staticmethod
    def _get_work_schedule(
        doctor: Doctor,
        requested_date: date,
        weekday: int,
    ) -> Optional[DoctorWorkSchedule]:
        """Get the applicable work schedule for a doctor on a specific date."""
        try:
            schedules = (
                DoctorWorkSchedule.objects.filter(
                    doctor=doctor,
                    weekday=weekday,
                    effective_from__lte=requested_date,
                )
                .filter(
                    models.Q(effective_until__isnull=True)
                    | models.Q(effective_until__gte=requested_date)
                )
                .order_by('-effective_from', '-id')
            )

            return schedules.first()
        except Exception as e:
            raise ValidationError(f"Error fetching work schedule: {str(e)}")
    
    @staticmethod
    def _generate_slots(
        doctor: Doctor,
        requested_date: date,
        work_schedule: DoctorWorkSchedule
    ) -> List[Dict[str, Any]]:
        """Generate all possible time slots for a work day."""
        if not work_schedule:
            return []
        
        try:
            slots = []
            consultation_duration = doctor.consultation_duration
            
            # Validate required fields exist
            if not work_schedule.start_time or not work_schedule.end_time:
                return []
            
            # Start with work start time (naive datetime)
            current_time = datetime.combine(requested_date, work_schedule.start_time)
            end_datetime = datetime.combine(requested_date, work_schedule.end_time)
            
            # Handle break times
            break_start = None
            break_end = None
            if work_schedule.break_start_time and work_schedule.break_end_time:
                break_start = datetime.combine(requested_date, work_schedule.break_start_time)
                break_end = datetime.combine(requested_date, work_schedule.break_end_time)
            
            # Generate slots
            while current_time < end_datetime:
                slot_end = current_time + timedelta(minutes=consultation_duration)
                
                # Check if slot would extend past work end time
                if slot_end > end_datetime:
                    break
                
                # Check if slot overlaps with break time
                if break_start and break_end:
                    # Skip if slot overlaps with break
                    if not (slot_end <= break_start or current_time >= break_end):
                        # Move to end of break
                        if current_time < break_end:
                            current_time = break_end
                            continue
                
                # Add slot - make times aware as UTC
                try:
                    slot_start_utc = timezone.make_aware(current_time, timezone.utc)
                    slot_end_utc = timezone.make_aware(slot_end, timezone.utc)
                    
                    slots.append({
                        'start_time': current_time.time().isoformat(),
                        'end_time': slot_end.time().isoformat(),
                        'start_datetime': slot_start_utc.isoformat(),
                        'end_datetime': slot_end_utc.isoformat(),
                    })
                except (ValueError, TypeError) as e:
                    # Log error and continue - skip this slot
                    continue
                
                # Move to next slot (add buffer time for doctor preparation)
                current_time = slot_end + timedelta(minutes=AvailabilityService.BUFFER_MINUTES)
            
            return slots
        
        except Exception as e:
            raise ValidationError(f"Error generating time slots: {str(e)}")
    
    @staticmethod
    def _filter_unavailable_slots(
        doctor: Doctor,
        requested_date: date,
        all_slots: List[Dict[str, Any]],
        exclude_appointment_id: Optional[uuid.UUID] = None,
    ) -> List[Dict[str, Any]]:
        """Filter out slots that are unavailable due to bookings or unavailability."""
        if not all_slots:
            return []
        
        try:
            # Get current time in UTC
            now_utc = timezone.now()
            
            # Get all active appointments for the doctor on this date
            start_of_day = timezone.make_aware(
                datetime.combine(requested_date, time.min),
                timezone.utc
            )
            end_of_day = timezone.make_aware(
                datetime.combine(requested_date, time.max),
                timezone.utc
            )
            
            # Get active appointments as list to avoid multiple DB queries.
            # exclude_appointment_id lets a reschedule-in-progress ignore its
            # own current slot instead of treating it as a conflict with itself.
            active_appointments_qs = Appointment.objects.filter(
                doctor=doctor,
                start_datetime__gte=start_of_day,
                start_datetime__lte=end_of_day,
                status__in=[
                    Appointment.STATUS_SCHEDULED,
                    Appointment.STATUS_CONFIRMED,
                    Appointment.STATUS_IN_PROGRESS
                ]
            )
            if exclude_appointment_id is not None:
                active_appointments_qs = active_appointments_qs.exclude(
                    id=exclude_appointment_id
                )
            active_appointments = list(
                active_appointments_qs.values_list('start_datetime', 'end_datetime')
            )
            
            # Get unavailability periods for this date
            unavailability_periods = list(DoctorUnavailability.objects.filter(
                doctor=doctor,
                start_datetime__lte=end_of_day,
                end_datetime__gte=start_of_day
            ).values_list('start_datetime', 'end_datetime'))
            
            # Filter slots
            available_slots = []
            for slot in all_slots:
                try:
                    # Safely parse ISO format strings
                    start_datetime_str = slot.get('start_datetime', '')
                    end_datetime_str = slot.get('end_datetime', '')
                    
                    if not start_datetime_str or not end_datetime_str:
                        continue
                    
                    # Parse ISO format datetime strings
                    slot_start = datetime.fromisoformat(
                        start_datetime_str.replace('Z', '+00:00')
                    )
                    slot_end = datetime.fromisoformat(
                        end_datetime_str.replace('Z', '+00:00')
                    )
                    
                    # Skip if slot is in the past
                    if slot_start < now_utc:
                        continue
                    
                    # Check if slot overlaps with any appointment
                    is_booked = any(
                        AvailabilityService._time_ranges_overlap(
                            slot_start, slot_end, appt_start, appt_end
                        )
                        for appt_start, appt_end in active_appointments
                    )
                    
                    if is_booked:
                        continue
                    
                    # Check if slot overlaps with unavailability
                    is_unavailable = any(
                        AvailabilityService._time_ranges_overlap(
                            slot_start, slot_end, unavail_start, unavail_end
                        )
                        for unavail_start, unavail_end in unavailability_periods
                    )
                    
                    if is_unavailable:
                        continue
                    
                    # Slot is available
                    available_slots.append(slot)
                
                except (ValueError, TypeError, KeyError) as e:
                    # Skip slots that can't be parsed
                    continue
            
            return available_slots
        
        except Exception as e:
            raise ValidationError(f"Error filtering available slots: {str(e)}")
    
    @staticmethod
    def _time_ranges_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap."""
        if not all([start1, end1, start2, end2]):
            return False
        try:
            return start1 < end2 and end1 > start2
        except (TypeError, ValueError):
            return False


class WorkScheduleService:
    """Service for setting a doctor's weekly work schedule as one atomic unit."""

    @staticmethod
    @transaction.atomic
    def set_weekly_schedule(
        doctor: Doctor,
        days: List[Dict[str, Any]],
        effective_from: date,
        effective_until: Optional[date] = None,
    ) -> List[DoctorWorkSchedule]:
        """
        Replace a doctor's work schedule for the given effective period.

        Args:
            doctor: Doctor instance
            days: list of dicts, one per working day, each with keys
                weekday, start_time, end_time, break_start_time, break_end_time
            effective_from: date the new schedule takes effect
            effective_until: optional date the schedule ends (None = indefinite)

        Returns:
            The newly created DoctorWorkSchedule instances.

        Raises:
            ValidationError: if the submitted days don't satisfy the clinic's
                scheduling rules (1-7 distinct weekdays, each day's own rules
                enforced via DoctorWorkSchedule.clean()).
        """
        if not (1 <= len(days) <= 7):
            raise ValidationError(
                f"Between 1 and 7 working days must be provided; got {len(days)}."
            )

        weekdays = [day["weekday"] for day in days]
        if len(set(weekdays)) != len(weekdays):
            raise ValidationError("Duplicate weekdays are not allowed in a weekly schedule.")

        # Clear out any existing schedule rows that could still be in effect from
        # effective_from onward, not just ones matching this exact effective
        # period — this endpoint replaces the doctor's schedule going forward, so
        # a prior version with a different effective_from/effective_until must
        # not be left dangling alongside the new one (that would leave duplicate/
        # overlapping weekday coverage for the "currently effective" schedule).
        # If anything below raises, @transaction.atomic rolls this delete back too.
        DoctorWorkSchedule.objects.filter(
            doctor=doctor,
        ).filter(
            models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=effective_from)
        ).delete()

        instances = []
        for day in days:
            instance = DoctorWorkSchedule(
                doctor=doctor,
                effective_from=effective_from,
                effective_until=effective_until,
                **day,
            )
            instance.full_clean()
            instances.append(instance)

        DoctorWorkSchedule.objects.bulk_create(instances)

        return instances

    @staticmethod
    def find_conflicting_appointments(
        doctor: Doctor,
        effective_from: date,
    ) -> List[Appointment]:
        """
        Find the doctor's future active appointments that no longer fit their
        current work schedule (weekday no longer worked, or time falls outside
        the day's hours or inside the break). Meant to be called right after
        set_weekly_schedule so callers can prompt rescheduling for these.
        """
        now = timezone.now()
        appointments = Appointment.objects.filter(
            doctor=doctor,
            start_datetime__gte=max(
                now, timezone.make_aware(datetime.combine(effective_from, time.min), timezone.utc)
            ),
            status__in=[
                Appointment.STATUS_SCHEDULED,
                Appointment.STATUS_CONFIRMED,
                Appointment.STATUS_IN_PROGRESS,
            ],
        )

        conflicting = []
        for appointment in appointments:
            appointment_date = appointment.start_datetime.date()
            weekday = appointment_date.weekday()
            schedule = AvailabilityService._get_work_schedule(doctor, appointment_date, weekday)

            if not schedule:
                conflicting.append(appointment)
                continue

            start_time = appointment.start_datetime.time()
            end_time = appointment.end_datetime.time()

            fits_hours = start_time >= schedule.start_time and end_time <= schedule.end_time
            overlaps_break = (
                schedule.break_start_time
                and schedule.break_end_time
                and start_time < schedule.break_end_time
                and end_time > schedule.break_start_time
            )

            if not fits_hours or overlaps_break:
                conflicting.append(appointment)

        return conflicting


class DoctorUnavailabilityService:
    """Service for blocking out a doctor's time (e.g. a day off)."""

    @staticmethod
    @transaction.atomic
    def create_unavailability(
        *,
        doctor: Doctor,
        start_datetime: datetime,
        end_datetime: datetime,
        reason: str,
        notes: str = "",
        created_by=None,
    ) -> tuple[DoctorUnavailability, List[Appointment]]:
        """
        Block out a period for the doctor and return the created record along
        with any active appointments that fall within it, so the caller can
        prompt rescheduling for them.
        """
        affected = list(
            Appointment.objects.filter(
                doctor=doctor,
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime,
                status__in=[
                    Appointment.STATUS_SCHEDULED,
                    Appointment.STATUS_CONFIRMED,
                    Appointment.STATUS_IN_PROGRESS,
                ],
            )
        )

        unavailability = DoctorUnavailability.objects.create(
            doctor=doctor,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=reason,
            notes=notes,
            affects_existing_appointments=bool(affected),
            created_by=created_by,
        )

        return unavailability, affected
