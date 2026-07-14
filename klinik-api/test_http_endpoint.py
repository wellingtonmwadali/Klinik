"""Test the availability HTTP endpoint."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*70)
print("TESTING AVAILABILITY HTTP ENDPOINT")
print("="*70)

# Create session and login
print("\n🔐 Logging in...")
session = requests.Session()

# First get CSRF token
session.get(f"{BASE_URL}/admin/login/")
csrftoken = session.cookies.get('csrftoken')

# Login as admin
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'csrfmiddlewaretoken': csrftoken,
}
login_response = session.post(f"{BASE_URL}/admin/login/", data=login_data, headers={'Referer': f"{BASE_URL}/admin/login/"})

if login_response.status_code == 200:
    print("✅ Logged in successfully\n")
else:
    print(f"❌ Login failed: {login_response.status_code}")

# Test 1: Get availability for Dr. Mwangi on next Monday
print("\n📍 TEST 1: Get availability for next Monday")
print("-" * 70)
response = session.get(f"{BASE_URL}/api/doctors/2/availability/", params={"date": "2026-07-20"})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"Doctor: {data['doctor_name']} ({data['specialization']})")
    print(f"Date: {data['date']}")
    print(f"Consultation Duration: {data['consultation_duration']} minutes")
    print(f"Total Available Slots: {data['total_slots']}")
    print(f"\nWork Hours: {data['work_hours']['start']} - {data['work_hours']['end']}")
    print(f"Lunch Break: {data['work_hours']['break_start']} - {data['work_hours']['break_end']}")
    print(f"\nFirst 5 slots:")
    for slot in data['available_slots'][:5]:
        print(f"  • {slot['start_time']} - {slot['end_time']}")
    print(f"\nLast 3 slots:")
    for slot in data['available_slots'][-3:]:
        print(f"  • {slot['start_time']} - {slot['end_time']}")
else:
    print(f"❌ ERROR: {response.text}")

# Test 2: Error handling - Missing date parameter
print("\n\n📍 TEST 2: Missing date parameter (should fail)")
print("-" * 70)
response = session.get(f"{BASE_URL}/api/doctors/2/availability/")
print(f"Status Code: {response.status_code}")
if response.status_code == 400:
    error = response.json()
    print(f"✅ Correctly rejected: {error.get('error', error)}")
else:
    print(f"Response: {response.text}")

# Test 3: Error handling - Invalid date format
print("\n\n📍 TEST 3: Invalid date format (should fail)")
print("-" * 70)
response = session.get(f"{BASE_URL}/api/doctors/2/availability/", params={"date": "20-07-2026"})
print(f"Status Code: {response.status_code}")
if response.status_code == 400:
    error = response.json()
    print(f"✅ Correctly rejected: {error.get('error', error)}")
else:
    print(f"Response: {response.text}")

# Test 4: Error handling - Past date
print("\n\n📍 TEST 4: Past date (should fail)")
print("-" * 70)
response = session.get(f"{BASE_URL}/api/doctors/2/availability/", params={"date": "2026-07-01"})
print(f"Status Code: {response.status_code}")
if response.status_code == 400:
    error = response.json()
    print(f"✅ Correctly rejected: {error.get('error', error)}")
else:
    print(f"Response: {response.text}")

# Test 5: Sunday (non-working day)
print("\n\n📍 TEST 5: Sunday - non-working day")
print("-" * 70)
response = session.get(f"{BASE_URL}/api/doctors/2/availability/", params={"date": "2026-07-19"})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total Slots: {data['total_slots']}")
    if data.get('message'):
        print(f"Message: {data['message']}")
    if data['total_slots'] == 0:
        print(f"✅ Correct: No slots on Sunday")
else:
    print(f"Response: {response.text}")

# Test 6: Different doctors
print("\n\n📍 TEST 6: Check all 5 doctors")
print("-" * 70)
for doctor_id in range(1, 6):
    response = session.get(f"{BASE_URL}/api/doctors/{doctor_id}/availability/", params={"date": "2026-07-20"})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['doctor_name']}: {data['total_slots']} slots available")
    else:
        print(f"❌ Doctor {doctor_id}: Failed")

print("\n" + "="*70)
print("✅ HTTP ENDPOINT TESTS COMPLETED")
print("="*70 + "\n")
