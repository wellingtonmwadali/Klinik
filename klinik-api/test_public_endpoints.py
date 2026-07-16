"""Test public endpoints without authentication."""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*70)
print("TESTING PUBLIC ENDPOINTS (No Authentication)")
print("="*70)

# Test 1: List all doctors
print("\n📍 TEST 1: GET /api/doctors/ (List all doctors)")
print("-" * 70)
response = requests.get(f"{BASE_URL}/api/doctors/")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    # Check if paginated response
    if isinstance(data, dict) and 'results' in data:
        doctors = data['results']
        print(f"✅ SUCCESS! Found {len(doctors)} doctors (Total: {data.get('count', len(doctors))}):")
    else:
        doctors = data
        print(f"✅ SUCCESS! Found {len(doctors)} doctors:")
    for doctor in doctors:
        print(f"  • Dr. {doctor['full_name']} - {doctor['specialization']}")
else:
    print(f"❌ FAILED: {response.text}")

# Test 2: Get specific doctor details
print("\n\n📍 TEST 2: GET /api/doctors/2/ (Doctor details)")
print("-" * 70)
response = requests.get(f"{BASE_URL}/api/doctors/2/")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    doctor = response.json()
    print(f"✅ SUCCESS!")
    print(f"  Name: Dr. {doctor['full_name']}")
    print(f"  Specialization: {doctor['specialization']}")
    print(f"  License: {doctor['license_number']}")
    print(f"  Email: {doctor['email']}")
    print(f"  Bio: {doctor['bio'][:80]}...")
else:
    print(f"❌ FAILED: {response.text}")

# Test 3: Get availability
print("\n\n📍 TEST 3: GET /api/doctors/2/availability/?date=2026-07-20")
print("-" * 70)
response = requests.get(f"{BASE_URL}/api/doctors/2/availability/", params={"date": "2026-07-20"})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ SUCCESS!")
    print(f"  Doctor: {data['doctor_name']}")
    print(f"  Date: {data['date']}")
    print(f"  Total Slots: {data['total_slots']}")
    print(f"  First 3 slots:")
    for slot in data['available_slots'][:3]:
        print(f"    • {slot['start_time']} - {slot['end_time']}")
else:
    print(f"❌ FAILED: {response.text}")

# Test 4: Try to create a doctor (should fail - admin only)
print("\n\n📍 TEST 4: POST /api/doctors/ (Create doctor - should fail)")
print("-" * 70)
response = requests.post(f"{BASE_URL}/api/doctors/", json={
    "first_name": "Test",
    "last_name": "Doctor",
    "specialization": "Testing"
})
print(f"Status Code: {response.status_code}")
if response.status_code == 403:
    print(f"✅ CORRECT! Unauthorized access blocked")
    print(f"  {response.json().get('detail', 'Access denied')}")
elif response.status_code == 401:
    print(f"✅ CORRECT! Authentication required")
    print(f"  {response.json().get('detail', 'Not authenticated')}")
else:
    print(f"⚠️  Unexpected status: {response.status_code}")
    print(f"  {response.text}")

print("\n" + "="*70)
print("✅ PUBLIC ENDPOINT TESTS COMPLETED")
print("="*70 + "\n")
