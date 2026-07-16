# Klinik — Clinic Appointment Booking System

A small system where patients book, cancel, and reschedule 30-minute
appointments with one of 5 doctors, and staff manage doctor schedules.

- **klinik-api** — Django REST Framework backend. All the logic lives here.
- **klinik-admin** — Next.js app for patient login/booking and staff/doctor views. Talks to the API on the server side only.

**Live API:** https://klinik-xhmb.onrender.com
**Live URL:** https://klinik-zeta.vercel.app/


---

## 1. System Design

### Models

```
User (login account) — has a Role: PATIENT / DOCTOR / ADMIN
  ├─ Doctor profile (if role = DOCTOR)
  └─ Patient profile (if role = PATIENT)

Doctor
  ├─ WorkSchedule — recurring hours per weekday + break time
  └─ Unavailability — one-off blocks (leave, sick days, etc.)

Appointment
  ├─ doctor, patient, start_datetime, end_datetime, status
  ├─ idempotency_key — so a double-click/retry can't create two bookings
  └─ history — a log of every cancel/reschedule, with reason and who did it
```

One `User` table with a `role` field, rather than three separate login
systems, so patients/doctors/admins can all log in through the same door and
just get routed differently.

### Key decisions

- **Availability is calculated on the fly**, not stored as pre-made slot rows.
  It's computed as: doctor's working hours − existing bookings − unavailable
  periods. This means changing a doctor's schedule updates availability
  instantly, with no background job needed to regenerate anything.
- **Double-booking is blocked at the database level**, not just in application
  code. There's a database constraint that makes it impossible for two
  appointments to exist for the same doctor at the same time. This closes a
  race condition where two patients click "book" on the same slot at almost
  the same instant — a plain "check, then save" in application code alone
  can't fully prevent that.
- **Cancelling/rescheduling never deletes data** — appointments are marked
  cancelled (with a reason) or linked to their replacement, and every change
  is logged. This gives us a paper trail without extra work later.
- **A doctor's schedule has hard rules**, enforced by the database, not just
  convention: a 9-hour shift, a 1-hour break, all inside clinic hours
  (06:00–22:00). If someone tries to save a schedule that breaks these rules,
  it's rejected immediately rather than causing confusing bugs later.

### Trade-offs

- **Session-cookie login, not JWT.** Simpler for a single web app; would need
  revisiting if a mobile app is added later.
- **One database, no caching layer.** Fine at 5-doctor scale; would need
  attention if the clinic grows to hundreds of doctors.
- **No "receptionist" role yet** — front-desk staff currently use an admin
  account. Easy to add later if needed.

---

## 2. API

| Method | Path | What it does |
|---|---|---|
| `POST` | `/api/appointments/` | Book a slot. Checks it's within working hours, not in the past, and not already taken. |
| `GET` | `/api/doctors/{id}/availability/?date=YYYY-MM-DD` | List free 30-minute slots for a doctor on a date. |
| `POST` | `/api/appointments/{id}/cancel/` | Cancel with a reason. Fails if already cancelled. Frees the slot. |
| `POST` | `/api/appointments/{id}/reschedule/` | Move to a new slot (validated like a fresh booking). Fails if cancelled. Old slot freed, new slot claimed. |
| `GET` | `/api/patients/{id}/appointments/` | *(bonus)* Upcoming appointments, soonest first. |
| `POST` | `/api/patients/register/` | Patient self-signup. |
| `POST`/`GET` | `/api/auth/login`, `/logout`, `/me` | Session login. |
| `GET`/`PUT` | `/api/doctors/{id}/work-schedule/` | View/update a doctor's weekly hours. |
| `GET`/`POST` | `/api/doctors/{id}/unavailability/` | View/add blocked-off periods (leave, etc.). |

*Cancel and reschedule are described as `PATCH` in the brief; they're built as
DRF actions (`POST .../cancel/`, `POST .../reschedule/`) since they're
specific state changes rather than generic field updates.*

**Validation:** all booking rules (working hours, not-in-the-past,
not-already-taken) live in one place, so booking and rescheduling always
follow the same rules. Errors come back as `400` with a clear message
(e.g. `"This slot is outside the doctor's working hours."`), not a generic
server error.

**Code layout:**
```
klinik-api/
├── config/     settings, urls
├── core/       User/Role, login endpoints
├── apps/
│   ├── appointments/   models, business logic, views, tests
│   ├── doctors/        models, availability logic, views, tests
│   └── patients/        models, views, tests
└── tests/      shared test setup
```
Business rules live in a `services.py` per app, kept separate from the views —
so the rules can be tested directly without needing to make an HTTP request.

**Tests:** `pytest`, covering booking conflicts, working-hours edge cases,
double-cancel, rescheduling a cancelled appointment, and availability
calculation around breaks and blocked periods. Run with:
```bash
pytest --cov=apps --cov-report=term-missing
```

---

## 3. Deployment & CI/CD

- **Public URL:** https://klinik-xhmb.onrender.com — Django API on Render
  (free-tier web service + managed Postgres, defined in `klinik-api/render.yaml`).
- **Branches:** `feature/*` → `feature` → `main`. **Merging into `main`
  triggers an automatic deploy** on Render.
- **CI (GitHub Actions):**
  - `klinik-api`: on every push/PR to `main`/`feature` — runs tests
    (`pytest`), checks for missing migrations, lints (`ruff`), checks
    formatting (`black`), and scans for security issues (`bandit`).
  - `klinik-admin`: on push/PR to `main` — lints and builds the Next.js app.
- Not yet automated: deploying `klinik-admin` itself (no CD step wired up for
  it yet).

---

## 4. AI Reflection

**1. Where AI was used:** talking through design trade-offs (slot storage,
preventing double-booking), scaffolding DRF serializers/views and test
fixtures, drafting the Render config and GitHub Actions workflows, and
writing this README.

**2. A suggestion that helped:** asked how to stop two patients booking the
same slot at once. The first instinct was "check if it's free, then save" in
code — but that has a race condition (two requests can both pass the check
before either saves). The fix was a database-level uniqueness constraint on
(doctor, time), which closes the race completely regardless of application
code.

**3. Where AI got it wrong:** an early demo-data script (`seed_data.py`) was
generated for a richer `Patient` model (with fields like date of birth, blood
group, insurance info). The `Patient` model was later simplified to just
contact info, but the seed script was never updated to match — it still
references fields that no longer exist and would error if run today. Caught
by comparing the script against the current model, not by running it.

**4. Decisions made without AI:**
- Enforcing the doctor schedule rules (9-hour shift, 1-hour break, clinic
  hours) at the database level instead of just as a convention — from
  experience that "the app currently behaves" isn't the same as "it's
  guaranteed."
- Choosing session-based login over JWT for now — for a single web app with
  5 doctors, the added complexity of token refresh/revocation isn't worth it
  yet. That's a judgment call about this clinic's actual size, not something
  AI can weigh in on.

---

## 5. Demo Logins

Seeded with `python manage.py seed_data`.



**Doctors** (all use password `doctor@123`):

| Email  | Specialization | Hours |
|---|---|---|---|
| james.mwangi@klinik.com  | General Practice | Mon–Fri, 06:00–15:00 |
| grace.njeri@klinik.com  | Pediatrics | Mon–Fri, 09:00–18:00 |
| peter.omondi@klinik.com  | Cardiology | Mon–Fri, 12:00–21:00 |
| sarah.wanjiku@klinik.com | Dermatology | Wed–Sun, 09:00–18:00 |
| david.kamau@klinik.com | Orthopedics | Tue–Sat, 06:00–15:00 |

You can log in with either the email or the username shown above.

> Note: the patient demo accounts in the same seed script are currently
> broken (see reflection #3 above). Use `/api/patients/register/` to create a
> working patient account instead.

---

## 6. Local Setup

```bash
# Backend
cd klinik-api
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
cp .env.example .env      # fill in SECRET_KEY / DATABASE_URL
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# Frontend
cd klinik-admin
npm install
npm run dev   # expects DJANGO_API_URL in .env.local
```


> (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`) from
> `config/settings/base.py` into your own `.env`.
