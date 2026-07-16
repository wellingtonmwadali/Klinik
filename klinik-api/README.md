# Klinik API

A comprehensive clinic booking system API built with Django REST Framework.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)

## ✨ Features

- **Patient Management** - CRUD operations for patient records
- **Doctor Management** - Manage doctor profiles and specializations
- **Appointment Scheduling** - Book, update, and manage appointments
- **RESTful API** - Clean and well-documented API endpoints
- **Automated Testing** - Comprehensive test coverage with pytest
- **CI/CD Pipeline** - Automated testing and deployment via GitHub Actions
- **Production-Ready** - Configured for deployment on Render

## 🛠️ Tech Stack

- **Backend Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (Supabase)
- **Testing**: pytest, pytest-django
- **Code Quality**: ruff (linting), black (formatting)
- **Deployment**: Render
- **CI/CD**: GitHub Actions

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (for production)
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Klinik
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/`

## 💻 Development Workflow

### Branch Naming Conventions

- `feature/[app-name]` - For app-specific features (e.g., `feature/appointments`)
- `feature/[description]` - For cross-cutting features (e.g., `feature/authentication`)
- `bugfix/[description]` - For bug fixes
- `hotfix/[description]` - For urgent production fixes

### Creating a Feature Branch

```bash
# Ensure you're on the feature branch
git checkout feature

# Pull latest changes
git pull origin feature

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Before Committing

1. **Format your code**
   ```bash
   black .
   ```

2. **Check linting**
   ```bash
   ruff check .
   ```

3. **Run tests**
   ```bash
   pytest
   ```

### Opening a Pull Request

1. Push your branch to GitHub
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request to merge into `feature` branch
3. Ensure all CI checks pass
4. Request review from team members
5. Once approved and CI passes, merge into `feature`

## 🌿 Branching Strategy

```
feature/appointments ──PR──> feature ──PR──> main ──auto──> Render
                              ↑                ↑
                         CI checks        CI checks
                       (block if fail)   (block if fail)
```

### Branch Flow

1. **Development**: Work on `feature/*` branches
2. **Integration**: Merge `feature/*` → `feature` via PR (CI must pass)
3. **Production**: Merge `feature` → `main` via PR (CI must pass)
4. **Deployment**: Render automatically deploys on `main` merge

### CI/CD Pipeline

GitHub Actions runs on every PR to `feature` and `main`:

- ✅ **Tests** - pytest with coverage reporting
- ✅ **Linting** - ruff code quality checks
- ✅ **Formatting** - black code style verification

**Merge is blocked if any check fails.**

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=apps --cov-report=term-missing
```

### Run specific test file
```bash
pytest apps/appointments/tests.py
```

### Run tests by marker
```bash
pytest -m integration
```

## 🚀 Deployment

### Render Configuration

The project is configured for automatic deployment to Render:

1. **Push to main branch** triggers automatic deployment
2. **Database migrations** run automatically during build
3. **Static files** are collected via WhiteNoise
4. **Health check** available at `/health/`

### Environment Variables (Render)

Required environment variables are configured in `render.yaml`:
- `SECRET_KEY` - Django secret key (auto-generated)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Your Render domain
- `DATABASE_URL` - Provided by Render PostgreSQL

### Manual Deployment Steps

If setting up Render manually:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set branch to `main`
4. Use Python 3.11 runtime
5. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
6. Start command: `gunicorn config.wsgi:application`
7. Add PostgreSQL database
8. Configure environment variables

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000/`
- **Production**: `https://your-app.onrender.com/`

### Endpoints

#### Health Check
```
GET /health/
```
Returns service health status.

#### Appointments
```
GET    /api/appointments/         - List all appointments
POST   /api/appointments/         - Create appointment
GET    /api/appointments/{id}/    - Retrieve appointment
PUT    /api/appointments/{id}/    - Update appointment
PATCH  /api/appointments/{id}/    - Partial update
DELETE /api/appointments/{id}/    - Delete appointment
```

#### Doctors
```
GET    /api/doctors/              - List all doctors
POST   /api/doctors/              - Create doctor
GET    /api/doctors/{id}/         - Retrieve doctor
PUT    /api/doctors/{id}/         - Update doctor
PATCH  /api/doctors/{id}/         - Partial update
DELETE /api/doctors/{id}/         - Delete doctor
```

#### Patients
```
GET    /api/patients/             - List all patients
POST   /api/patients/             - Create patient
GET    /api/patients/{id}/        - Retrieve patient
PUT    /api/patients/{id}/        - Update patient
PATCH  /api/patients/{id}/        - Partial update
DELETE /api/patients/{id}/        - Delete patient
```

### Authentication

Currently uses session authentication. Add token-based authentication for production use.

## 📁 Project Structure

```
klinik-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── config/
│   ├── settings/
│   │   ├── base.py            # Base settings
│   │   ├── development.py     # Development settings
│   │   └── production.py      # Production settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config
├── apps/
│   ├── appointments/          # Appointments app
│   ├── doctors/               # Doctors app
│   └── patients/              # Patients app
├── requirements/
│   ├── base.txt              # Core dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
├── tests/                     # Integration tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns
├── manage.py                 # Django management script
├── pytest.ini                # Pytest configuration
├── pyproject.toml            # Tool configuration (ruff, black, isort)
├── render.yaml               # Render deployment config
└── requirements.txt          # Main requirements file
```

## 🤝 Contributing

1. Follow the branching strategy outlined above
2. Ensure all tests pass before opening a PR
3. Use the PR template to provide context
4. Request code review from team members
5. Keep commits atomic and well-documented

## 📄 License

See [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.
