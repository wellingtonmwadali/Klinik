"""Test the doctor availability endpoint."""
import django
import os
import json
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client

client = Client()

def print_response(response, test_name):
    """Pretty print the response."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    if response.status_code != 404:
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.content.decode())
    print(f"{'='*60}\n")

# Test 1: Valid request for Dr. Mwangi (30-min slots)
print("\n" + "="*60)
print("AVAILABILITY ENDPOINT TESTS")
print("="*60)

# Get tomorrow's date
tomorrow = (date.today() + timedelta(days=1)).isoformat()
next_monday = (date.today() + timedelta(days=(7 - date.today().weekday()))).isoformat()

print(f"\nToday: {date.today()}")
print(f"Tomorrow: {tomorrow}")
print(f"Next Monday: {next_monday}")

# Test 1: Valid request - Dr. Mwangi (ID=2, 30-min slots)
try:
    response = client.get(f"/api/doctors/2/availability/", {'date': next_monday})
    print_response(response, f"Valid Request - Dr. Mwangi on {next_monday}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {data['total_slots']} available slots")
        print(f"   Expected: ~16 slots (8 hours / 30 min)")
        if data['available_slots']:
            print(f"   First slot: {data['available_slots'][0]}")
            print(f"   Last slot: {data['available_slots'][-1]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Valid request - Dr. Njeri (ID=3, 20-min slots)
try:
    response = client.get(f"/api/doctors/3/availability/", {'date': next_monday})
    print_response(response, f"Valid Request - Dr. Njeri on {next_monday}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {data['total_slots']} available slots")
        print(f"   Expected: ~24 slots (8 hours / 20 min)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Valid request - Dr. Omondi (ID=4, 45-min slots)
try:
    response = client.get(f"/api/doctors/4/availability/", {'date': next_monday})
    print_response(response, f"Valid Request - Dr. Omondi on {next_monday}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {data['total_slots']} available slots")
        print(f"   Expected: ~10 slots (8 hours / 45 min)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Missing date parameter
try:
    response = client.get(f"/api/doctors/2/availability/")
    print_response(response, "Missing Date Parameter")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Invalid date format
try:
    response = client.get(f"/api/doctors/2/availability/", {'date': '15-07-2026'})
    print_response(response, "Invalid Date Format")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Past date
try:
    response = client.get(f"/api/doctors/2/availability/", {'date': '2026-07-01'})
    print_response(response, "Past Date")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Sunday (non-working day)
next_sunday = (date.today() + timedelta(days=(6 - date.today().weekday() + 7) % 7 or 7)).isoformat()
try:
    response = client.get(f"/api/doctors/2/availability/", {'date': next_sunday})
    print_response(response, f"Sunday (Non-working day) - {next_sunday}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {data['total_slots']} slots (should be 0)")
        if 'message' in data:
            print(f"   Message: {data['message']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Non-existent doctor
try:
    response = client.get(f"/api/doctors/999/availability/", {'date': next_monday})
    print_response(response, "Non-existent Doctor")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ ALL TESTS COMPLETED")
print("="*60 + "\n")
