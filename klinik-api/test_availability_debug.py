#!/usr/bin/env python
"""Debug script to test doctor availability endpoint."""
import os
import sys
import django
import json
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from apps.doctors.models import Doctor, DoctorWorkSchedule
from datetime import time

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f" {text}")
    print(f"{'='*70}\n")

def print_section(text):
    """Print a section header."""
    print(f"\n>>> {text}")
    print("=" * 70)

def check_doctors():
    """Check if any doctors exist in the database."""
    print_section("Checking doctors in database")
    
    doctors = Doctor.objects.all()
    print(f"Total doctors: {doctors.count()}")
    
    if not doctors.exists():
        print("❌ No doctors found in database!")
        print("   Please create doctors first via Django admin or migrations.")
        return False
    
    for doctor in doctors:
        print(f"\n✅ Doctor ID {doctor.id}: Dr. {doctor.full_name} ({doctor.specialization})")
        print(f"   Email: {doctor.email}")
        print(f"   Phone: {doctor.phone}")
        print(f"   Status: {doctor.status}")
        print(f"   Is Active: {doctor.is_active}")
        print(f"   Accepting Appointments: {doctor.is_accepting_appointments}")
        print(f"   Consultation Duration: {doctor.consultation_duration} minutes")
    
    return doctors.exists()

def check_work_schedules():
    """Check if doctors have work schedules."""
    print_section("Checking work schedules")
    
    schedules = DoctorWorkSchedule.objects.all()
    print(f"Total schedules: {schedules.count()}")
    
    if not schedules.exists():
        print("❌ No work schedules found!")
        print("   Please set up work schedules for doctors.")
        return False
    
    # Group by doctor
    by_doctor = {}
    for schedule in schedules:
        if schedule.doctor.id not in by_doctor:
            by_doctor[schedule.doctor.id] = []
        by_doctor[schedule.doctor.id].append(schedule)
    
    for doctor_id, docs_schedules in by_doctor.items():
        doctor = Doctor.objects.get(id=doctor_id)
        print(f"\n✅ Dr. {doctor.full_name} has {len(docs_schedules)} schedule entries:")
        
        for sched in sorted(docs_schedules, key=lambda s: s.weekday):
            weekday_name = sched.get_weekday_display()
            print(f"   • {weekday_name}: {sched.start_time} - {sched.end_time}")
            if sched.break_start_time and sched.break_end_time:
                print(f"     Break: {sched.break_start_time} - {sched.break_end_time}")
            print(f"     Effective: {sched.effective_from} to {sched.effective_until or 'indefinite'}")
    
    return schedules.exists()

def test_availability_endpoint(doctor_id, test_date):
    """Test the availability endpoint."""
    print_section(f"Testing availability endpoint for Doctor {doctor_id} on {test_date}")
    
    client = Client()
    url = f"/api/doctors/{doctor_id}/availability/"
    
    print(f"Endpoint: {url}?date={test_date}")
    print(f"Full URL: http://localhost:8000{url}?date={test_date}\n")
    
    try:
        response = client.get(url, {'date': test_date})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ Doctor not found (404)")
            return False
        
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Endpoint returned 200 OK\n")
            print(json.dumps(data, indent=2))
            
            # Analyze response
            print(f"\n📊 Summary:")
            print(f"   Doctor: {data.get('doctor_name')}")
            print(f"   Date: {data.get('date')}")
            print(f"   Total Available Slots: {data.get('total_slots')}")
            
            if data.get('message'):
                print(f"   Message: {data.get('message')}")
            
            if data.get('work_hours'):
                print(f"   Work Hours: {data['work_hours']['start']} - {data['work_hours']['end']}")
            
            if data.get('available_slots'):
                print(f"\n   First 3 slots:")
                for slot in data['available_slots'][:3]:
                    print(f"     • {slot['start_time']} - {slot['end_time']}")
            
            return True
        
        elif response.status_code == 400:
            print("⚠️  Endpoint returned 400 Bad Request\n")
            print(json.dumps(data, indent=2))
            print(f"\nError: {data.get('detail', data.get('error', 'Unknown error'))}")
            return False
        
        elif response.status_code == 500:
            print("❌ Endpoint returned 500 Internal Server Error\n")
            print(json.dumps(data, indent=2))
            print(f"\nError: {data.get('detail', data.get('error', 'Unknown error'))}")
            if data.get('technical_detail'):
                print(f"Technical Details: {data.get('technical_detail')}")
            return False
        
        else:
            print(f"❓ Unexpected status code: {response.status_code}\n")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug script."""
    print_header("Doctor Availability Endpoint Debug Script")
    
    # Check doctors
    if not check_doctors():
        print("\n" + "="*70)
        print("❌ Setup Issue: No doctors in database")
        print("="*70)
        return
    
    # Check schedules
    if not check_work_schedules():
        print("\n" + "="*70)
        print("⚠️  Setup Issue: No work schedules defined")
        print("   Doctors exist but have no schedules configured.")
        print("="*70)
        return
    
    # Test availability endpoint
    print_section("Testing Availability Endpoints")
    
    doctors = Doctor.objects.all()
    
    # Get next Monday as test date
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # If today is Monday, use next Monday
    next_monday = today + timedelta(days=days_until_monday)
    
    test_date = next_monday.isoformat()
    
    for doctor in doctors[:1]:  # Test only first doctor
        success = test_availability_endpoint(doctor.id, test_date)
        
        if success:
            print("\n✅ Endpoint test PASSED")
        else:
            print("\n❌ Endpoint test FAILED")
    
    print_header("Debug Script Complete")

if __name__ == '__main__':
    main()
