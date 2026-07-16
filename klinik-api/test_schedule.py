"""Test script to verify work schedules."""
from apps.doctors.models import Doctor, DoctorWorkSchedule

# Check each doctor's schedule
doctors = Doctor.objects.all()
print(f"\n{'='*60}")
print("WORK SCHEDULE VERIFICATION")
print(f"{'='*60}\n")

for dr in doctors:
    print(f"Doctor: {dr.full_name} ({dr.specialization})")
    print(f"  Consultation duration: {dr.consultation_duration} min")
    
    schedules = dr.work_schedule.all()
    print(f"  Work days: {schedules.count()}")
    
    total_hours = 0
    for s in schedules:
        # Calculate hours
        start_minutes = s.start_time.hour * 60 + s.start_time.minute
        end_minutes = s.end_time.hour * 60 + s.end_time.minute
        work_minutes = end_minutes - start_minutes
        
        # Subtract break time
        if s.break_start_time and s.break_end_time:
            break_start_minutes = s.break_start_time.hour * 60 + s.break_start_time.minute
            break_end_minutes = s.break_end_time.hour * 60 + s.break_end_time.minute
            break_minutes = break_end_minutes - break_start_minutes
            work_minutes -= break_minutes
        
        work_hours = work_minutes / 60
        total_hours += work_hours
        
        print(f"    {s.get_weekday_display()}: {s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}", end="")
        if s.break_start_time and s.break_end_time:
            print(f" (Break: {s.break_start_time.strftime('%H:%M')} - {s.break_end_time.strftime('%H:%M')})", end="")
        print(f" = {work_hours}h")
    
    print(f"  Total hours per week: {total_hours}h\n")

print(f"{'='*60}")
print("✅ All doctors should have 40 hours/week")
print(f"{'='*60}\n")
