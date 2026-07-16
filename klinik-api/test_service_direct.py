"""Direct test of availability service."""
import django
import os
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.doctors.models import Doctor
from apps.doctors.services import AvailabilityService
import json

print("\n" + "="*60)
print("DIRECT SERVICE TEST - Doctor Availability")
print("="*60 + "\n")

# Get next Monday
today = date.today()
next_monday = today + timedelta(days=(7 - today.weekday()))

print(f"Today: {today} ({today.strftime('%A')})")
print(f"Next Monday: {next_monday}\n")

# Test each doctor
doctors = Doctor.objects.all()

for doctor in doctors:
    print(f"\n{'='*60}")
    print(f"DOCTOR: {doctor.full_name} ({doctor.specialization})")
    print(f"Consultation Duration: {doctor.consultation_duration} minutes")
    print(f"{'='*60}")
    
    try:
        result = AvailabilityService.calculate_available_slots(doctor, next_monday)
        
        print(f"\nDate: {result['date']}")
        print(f"Total Available Slots: {result['total_slots']}")
        
        if result['work_hours']:
            wh = result['work_hours']
            print(f"Work Hours: {wh['start']} - {wh['end']}")
            if wh['break_start'] and wh['break_end']:
                print(f"Break: {wh['break_start']} - {wh['break_end']}")
        
        if result.get('message'):
            print(f"Message: {result['message']}")
        
        # Show first and last few slots
        slots = result['available_slots']
        if slots:
            print(f"\nFirst 3 slots:")
            for slot in slots[:3]:
                print(f"  {slot['start_time']} - {slot['end_time']}")
            
            if len(slots) > 6:
                print(f"  ...")
                print(f"Last 3 slots:")
                for slot in slots[-3:]:
                    print(f"  {slot['start_time']} - {slot['end_time']}")
        
        # Calculate expected slots (with 10-minute buffer between slots)
        if doctor.consultation_duration > 0:
            # 8 working hours = 480 minutes
            # Each slot cycle = consultation_duration + 10 min buffer
            slot_cycle_duration = doctor.consultation_duration + 10
            expected_slots = 480 // slot_cycle_duration
            print(f"\nExpected slots: ~{expected_slots} (480 min / {slot_cycle_duration} min per slot cycle)")
            print(f"  (Consultation: {doctor.consultation_duration} min + Buffer: 10 min)")
            print(f"Actual slots: {result['total_slots']}")
            
            if abs(result['total_slots'] - expected_slots) <= 1:
                print("✅ PASS: Slot count matches expected")
            else:
                print(f"⚠️  WARNING: Slot count mismatch")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

# Test Sunday (non-working day)
next_sunday = today + timedelta(days=(6 - today.weekday() + 7) % 7 or 7)
doctor = doctors.first()

print(f"\n{'='*60}")
print(f"TEST: Non-working day (Sunday)")
print(f"{'='*60}")
print(f"Doctor: {doctor.full_name}")
print(f"Date: {next_sunday} ({next_sunday.strftime('%A')})")

try:
    result = AvailabilityService.calculate_available_slots(doctor, next_sunday)
    print(f"Total Slots: {result['total_slots']}")
    if result.get('message'):
        print(f"Message: {result['message']}")
    if result['total_slots'] == 0:
        print("✅ PASS: No slots on Sunday as expected")
    else:
        print("❌ FAIL: Should have no slots on Sunday")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*60)
print("✅ DIRECT SERVICE TESTS COMPLETED")
print("="*60 + "\n")
