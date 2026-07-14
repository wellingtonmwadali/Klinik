from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.doctors.models import Doctor
from apps.doctors.services import WorkScheduleService
from apps.patients.models import Patient
from core.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with realistic data for 5 doctors and 5 patients"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database with realistic data...")

        # Create roles
        self.stdout.write("Creating roles...")
        roles = {}
        for role_name, description in [
            (Role.PATIENT, "Patient - can book and manage appointments"),
            (Role.DOCTOR, "Doctor - can manage their schedule and appointments"),
            (Role.ADMIN, "Admin - full system access"),
            (Role.RECEPTIONIST, "Receptionist - can manage appointments on behalf of patients"),
        ]:
            role, created = Role.objects.get_or_create(
                name=role_name, defaults={"description": description}
            )
            roles[role_name] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created role: {role_name}"))
            else:
                self.stdout.write(f"  - Role already exists: {role_name}")

        # Create admin user
        self.stdout.write("\nCreating admin user...")
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@klinik.com",
                "role": roles[Role.ADMIN],
                "is_staff": True,
                "is_superuser": True,
                "is_email_verified": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS("  ✓ Created admin user (username: admin, password: admin123)")
            )
        else:
            self.stdout.write("  - Admin user already exists")

        # Create 5 doctors with realistic data
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("CREATING 5 DOCTORS")
        self.stdout.write("=" * 60)

        doctors_data = [
            {
                "username": "dr.mwangi",
                "email": "james.mwangi@klinik.com",
                "first_name": "James",
                "last_name": "Mwangi",
                "phone": "+254722456789",
                "specialization": "General Practice",
                "license_number": "KMC-GP-2018-1234",
                "bio": "General practitioner with 8 years of experience in family medicine. Specializes in preventive care and chronic disease management.",
                "consultation_duration": 30,
                "max_advance_booking_days": 30,
                # Early shift, Mon-Fri: 6:00 AM-3:00 PM (9h span, 1h break = 8h net/day, 40h/week)
                "work_schedule": [
                    (0, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Monday
                    (1, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Tuesday
                    (2, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Wednesday
                    (3, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Thursday
                    (4, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Friday
                ],
            },
            {
                "username": "dr.njeri",
                "email": "grace.njeri@klinik.com",
                "first_name": "Grace",
                "last_name": "Njeri",
                "phone": "+254733567890",
                "specialization": "Pediatrics",
                "license_number": "KMC-PED-2015-5678",
                "bio": "Board-certified pediatrician with over 11 years of experience. Passionate about child health and development, specializing in newborn care and childhood vaccinations.",
                "consultation_duration": 30,
                "max_advance_booking_days": 45,
                # Standard shift, Mon-Fri: 9:00 AM-6:00 PM (9h span, 1h break = 8h net/day, 40h/week)
                "work_schedule": [
                    (0, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Monday
                    (1, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Tuesday
                    (2, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Wednesday
                    (3, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Thursday
                    (4, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Friday
                ],
            },
            {
                "username": "dr.omondi",
                "email": "peter.omondi@klinik.com",
                "first_name": "Peter",
                "last_name": "Omondi",
                "phone": "+254744678901",
                "specialization": "Cardiology",
                "license_number": "KMC-CAR-2012-9012",
                "bio": "Experienced cardiologist with 14 years of clinical practice. Specializes in heart disease prevention, hypertension management, and cardiac rehabilitation.",
                "consultation_duration": 30,
                "max_advance_booking_days": 60,
                # Late shift, Mon-Fri: 12:00 PM-9:00 PM (9h span, 1h break = 8h net/day, 40h/week)
                "work_schedule": [
                    (0, time(12, 0), time(21, 0), time(16, 0), time(17, 0)),  # Monday
                    (1, time(12, 0), time(21, 0), time(16, 0), time(17, 0)),  # Tuesday
                    (2, time(12, 0), time(21, 0), time(16, 0), time(17, 0)),  # Wednesday
                    (3, time(12, 0), time(21, 0), time(16, 0), time(17, 0)),  # Thursday
                    (4, time(12, 0), time(21, 0), time(16, 0), time(17, 0)),  # Friday
                ],
            },
            {
                "username": "dr.wanjiku",
                "email": "sarah.wanjiku@klinik.com",
                "first_name": "Sarah",
                "last_name": "Wanjiku",
                "phone": "+254755789012",
                "specialization": "Dermatology",
                "license_number": "KMC-DER-2016-3456",
                "bio": "Dermatologist with 10 years of experience in treating skin conditions. Expertise in acne treatment, skin cancer screening, and cosmetic dermatology.",
                "consultation_duration": 30,
                "max_advance_booking_days": 30,
                # Standard shift, Wed-Sun: 9:00 AM-6:00 PM (9h span, 1h break = 8h net/day, 40h/week)
                "work_schedule": [
                    (2, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Wednesday
                    (3, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Thursday
                    (4, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Friday
                    (5, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Saturday
                    (6, time(9, 0), time(18, 0), time(12, 0), time(13, 0)),  # Sunday
                ],
            },
            {
                "username": "dr.kamau",
                "email": "david.kamau@klinik.com",
                "first_name": "David",
                "last_name": "Kamau",
                "phone": "+254766890123",
                "specialization": "Orthopedics",
                "license_number": "KMC-ORT-2014-7890",
                "bio": "Orthopedic surgeon with 12 years of experience in musculoskeletal conditions. Specializes in sports injuries, joint replacement, and fracture care.",
                "consultation_duration": 30,
                "max_advance_booking_days": 45,
                # Early shift, Tue-Sat: 6:00 AM-3:00 PM (9h span, 1h break = 8h net/day, 40h/week)
                "work_schedule": [
                    (1, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Tuesday
                    (2, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Wednesday
                    (3, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Thursday
                    (4, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Friday
                    (5, time(6, 0), time(15, 0), time(10, 0), time(11, 0)),  # Saturday
                ],
            },
        ]

        for doctor_data in doctors_data:
            work_schedule = doctor_data.pop("work_schedule")

            # Create user account for doctor
            doctor_user, user_created = User.objects.get_or_create(
                username=doctor_data["username"],
                defaults={
                    "email": doctor_data["email"],
                    "first_name": doctor_data["first_name"],
                    "last_name": doctor_data["last_name"],
                    "role": roles[Role.DOCTOR],
                    "is_staff": True,
                    "is_email_verified": True,
                },
            )
            if user_created:
                doctor_user.set_password("doctor123")
                doctor_user.save()

            # Create doctor profile
            doctor, doctor_created = Doctor.objects.get_or_create(
                email=doctor_data["email"],
                defaults={
                    "user": doctor_user,
                    "first_name": doctor_data["first_name"],
                    "last_name": doctor_data["last_name"],
                    "phone": doctor_data["phone"],
                    "specialization": doctor_data["specialization"],
                    "license_number": doctor_data["license_number"],
                    "bio": doctor_data["bio"],
                    "consultation_duration": doctor_data["consultation_duration"],
                    "max_advance_booking_days": doctor_data[
                        "max_advance_booking_days"
                    ],
                    "is_accepting_appointments": True,
                    "status": Doctor.STATUS_ACTIVE,
                },
            )

            if doctor_created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Created: {doctor.full_name} - {doctor.specialization}"
                    )
                )
            else:
                self.stdout.write(f"- Doctor already exists: {doctor.full_name}")
            self.stdout.write(f"  Email: {doctor.email} | Phone: {doctor.phone}")
            self.stdout.write(
                f"  License: {doctor.license_number} | Duration: {doctor.consultation_duration} min"
            )

            # Sync work schedule (replaces any existing schedule for this effective period)
            days = [
                {
                    "weekday": weekday,
                    "start_time": start_time,
                    "end_time": end_time,
                    "break_start_time": break_start,
                    "break_end_time": break_end,
                }
                for weekday, start_time, end_time, break_start, break_end in work_schedule
            ]
            WorkScheduleService.set_weekly_schedule(
                doctor=doctor,
                days=days,
                effective_from=date.today(),
            )
            self.stdout.write(f"  Work schedule: {len(days)} days configured")

        # Create 5 patients with realistic data
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("CREATING 5 PATIENTS")
        self.stdout.write("=" * 60)

        patients_data = [
            {
                "username": "patient.achieng",
                "email": "mary.achieng@email.com",
                "first_name": "Mary",
                "last_name": "Achieng",
                "date_of_birth": date(1985, 3, 15),
                "gender": "F",
                "phone": "+254712345678",
                "address": "15 Kenyatta Avenue, Nairobi",
                "blood_group": "O+",
                "medical_history": "Hypertension diagnosed 2020. Currently on medication. No known drug allergies.",
                "allergies": "Penicillin",
                "current_medications": "Amlodipine 5mg daily",
                "emergency_contact_name": "John Achieng",
                "emergency_contact_phone": "+254723456789",
                "emergency_contact_relationship": "Husband",
                "insurance_provider": "AAR Insurance",
                "insurance_policy_number": "AAR-2023-45678",
                "insurance_expiry_date": date(2026, 12, 31),
            },
            {
                "username": "patient.mutua",
                "email": "patrick.mutua@email.com",
                "first_name": "Patrick",
                "last_name": "Mutua",
                "date_of_birth": date(1992, 7, 22),
                "gender": "M",
                "phone": "+254734567890",
                "address": "23 Moi Avenue, Mombasa",
                "blood_group": "A+",
                "medical_history": "Type 2 Diabetes mellitus diagnosed 2019. Well controlled with oral medication.",
                "allergies": "None",
                "current_medications": "Metformin 500mg twice daily, Atorvastatin 20mg at night",
                "emergency_contact_name": "Rose Mutua",
                "emergency_contact_phone": "+254745678901",
                "emergency_contact_relationship": "Wife",
                "insurance_provider": "Jubilee Insurance",
                "insurance_policy_number": "JUB-2024-78901",
                "insurance_expiry_date": date(2027, 6, 30),
            },
            {
                "username": "patient.wambui",
                "email": "ann.wambui@email.com",
                "first_name": "Ann",
                "last_name": "Wambui",
                "date_of_birth": date(2015, 11, 5),
                "gender": "F",
                "phone": "+254756789012",
                "address": "47 Ngong Road, Karen, Nairobi",
                "blood_group": "B+",
                "medical_history": "Childhood asthma, well controlled. All vaccinations up to date.",
                "allergies": "Dust mites, pollen",
                "current_medications": "Salbutamol inhaler as needed",
                "emergency_contact_name": "Lucy Wambui",
                "emergency_contact_phone": "+254767890123",
                "emergency_contact_relationship": "Mother",
                "insurance_provider": "CIC Insurance",
                "insurance_policy_number": "CIC-2025-12345",
                "insurance_expiry_date": date(2027, 11, 30),
            },
            {
                "username": "patient.otieno",
                "email": "robert.otieno@email.com",
                "first_name": "Robert",
                "last_name": "Otieno",
                "date_of_birth": date(1978, 5, 30),
                "gender": "M",
                "phone": "+254778901234",
                "address": "89 Tom Mboya Street, Kisumu",
                "blood_group": "AB+",
                "medical_history": "Coronary artery disease, myocardial infarction 2021. Regular cardiology follow-up.",
                "allergies": "Sulfa drugs",
                "current_medications": "Aspirin 75mg, Clopidogrel 75mg, Atenolol 50mg, Rosuvastatin 20mg",
                "emergency_contact_name": "Elizabeth Otieno",
                "emergency_contact_phone": "+254789012345",
                "emergency_contact_relationship": "Sister",
                "insurance_provider": "Madison Insurance",
                "insurance_policy_number": "MAD-2023-56789",
                "insurance_expiry_date": date(2026, 9, 30),
            },
            {
                "username": "patient.njoroge",
                "email": "susan.njoroge@email.com",
                "first_name": "Susan",
                "last_name": "Njoroge",
                "date_of_birth": date(2000, 2, 14),
                "gender": "F",
                "phone": "+254790123456",
                "address": "12 University Way, Nairobi",
                "blood_group": "O-",
                "medical_history": "Healthy young adult. No chronic conditions. Regular checkups.",
                "allergies": "None known",
                "current_medications": "Oral contraceptive pills",
                "emergency_contact_name": "Michael Njoroge",
                "emergency_contact_phone": "+254701234567",
                "emergency_contact_relationship": "Father",
                "insurance_provider": "Britam Insurance",
                "insurance_policy_number": "BRI-2024-98765",
                "insurance_expiry_date": date(2027, 2, 28),
            },
        ]

        for patient_data in patients_data:
            # Create user account for patient
            patient_user, user_created = User.objects.get_or_create(
                username=patient_data["username"],
                defaults={
                    "email": patient_data["email"],
                    "first_name": patient_data["first_name"],
                    "last_name": patient_data["last_name"],
                    "role": roles[Role.PATIENT],
                    "is_staff": True,  # Allow admin access for testing
                    "is_email_verified": True,
                },
            )
            if user_created:
                patient_user.set_password("patient123")
                patient_user.save()

            # Create patient profile
            patient, patient_created = Patient.objects.get_or_create(
                email=patient_data["email"],
                defaults={
                    "user": patient_user,
                    "first_name": patient_data["first_name"],
                    "last_name": patient_data["last_name"],
                    "date_of_birth": patient_data["date_of_birth"],
                    "gender": patient_data["gender"],
                    "phone": patient_data["phone"],
                    "address": patient_data["address"],
                    "blood_group": patient_data["blood_group"],
                    "medical_history": patient_data["medical_history"],
                    "allergies": patient_data["allergies"],
                    "current_medications": patient_data["current_medications"],
                    "emergency_contact_name": patient_data["emergency_contact_name"],
                    "emergency_contact_phone": patient_data["emergency_contact_phone"],
                    "emergency_contact_relationship": patient_data[
                        "emergency_contact_relationship"
                    ],
                    "insurance_provider": patient_data["insurance_provider"],
                    "insurance_policy_number": patient_data["insurance_policy_number"],
                    "insurance_expiry_date": patient_data["insurance_expiry_date"],
                    "status": Patient.STATUS_ACTIVE,
                },
            )

            if patient_created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Created: {patient.full_name} (Age: {patient.age})"
                    )
                )
                self.stdout.write(f"  Email: {patient.email} | Phone: {patient.phone}")
                self.stdout.write(
                    f"  Blood Group: {patient.blood_group} | Gender: {patient.get_gender_display()}"
                )
                self.stdout.write(
                    f"  Insurance: {patient.insurance_provider} ({patient.insurance_policy_number})"
                )
            else:
                self.stdout.write(f"- Patient already exists: {patient.full_name}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ DATABASE SEEDING COMPLETED!"))
        self.stdout.write("=" * 60)

        self.stdout.write("\n📋 SUMMARY:")
        self.stdout.write("  • Roles: 4 (Admin, Doctor, Patient, Receptionist)")
        self.stdout.write("  • Doctors: 5 specialists")
        self.stdout.write("  • Patients: 5 with complete medical records")
        self.stdout.write("  • Admin Users: 1")

        self.stdout.write("\n🔑 LOGIN CREDENTIALS:")
        self.stdout.write("  Admin:")
        self.stdout.write("    • username: admin, password: admin123")
        self.stdout.write("\n  Doctors (all use password: doctor123):")
        self.stdout.write("    • dr.mwangi - General Practice")
        self.stdout.write("    • dr.njeri - Pediatrics")
        self.stdout.write("    • dr.omondi - Cardiology")
        self.stdout.write("    • dr.wanjiku - Dermatology")
        self.stdout.write("    • dr.kamau - Orthopedics")
        self.stdout.write("\n  Patients (all use password: patient123):")
        self.stdout.write("    • patient.achieng - Mary Achieng")
        self.stdout.write("    • patient.mutua - Patrick Mutua")
        self.stdout.write("    • patient.wambui - Ann Wambui")
        self.stdout.write("    • patient.otieno - Robert Otieno")
        self.stdout.write("    • patient.njoroge - Susan Njoroge")
