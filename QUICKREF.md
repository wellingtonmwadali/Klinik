# Quick Reference Card

## 🔧 Common Commands

### Local Development
```bash
# Start development server
python manage.py runserver

# Run tests
pytest

# Run tests with coverage
pytest --cov=apps

# Format code
black .

# Check linting
ruff check .

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Git Workflow
```bash
# Start new feature
git checkout feature
git pull origin feature
git checkout -b feature/your-feature-name

# Commit changes
git add .
git commit -m "feat: your description"

# Push to GitHub
git push origin feature/your-feature-name

# Update from feature branch
git pull origin feature

# Check current branch
git branch
```

## 📁 Project Structure Quick Reference

```
Klinik/
├── apps/                          # Django applications
│   ├── appointments/              # Appointment management
│   ├── doctors/                   # Doctor profiles
│   └── patients/                  # Patient records
├── config/                        # Project configuration
│   ├── settings/                  # Environment-specific settings
│   │   ├── base.py               # Shared settings
│   │   ├── development.py        # Dev settings
│   │   └── production.py         # Production settings
│   └── urls.py                   # URL routing
├── tests/                         # Integration tests
├── requirements/                  # Dependencies
│   ├── base.txt                  # Core dependencies
│   ├── dev.txt                   # Development tools
│   └── prod.txt                  # Production-specific
└── .github/workflows/ci.yml      # CI/CD pipeline
```

## 🌐 API Endpoints

### Health Check
- `GET /health/` - Service health status

### Appointments
- `GET /api/appointments/` - List appointments
- `POST /api/appointments/` - Create appointment
- `GET /api/appointments/{id}/` - Get appointment
- `PUT /api/appointments/{id}/` - Update appointment
- `DELETE /api/appointments/{id}/` - Delete appointment

### Doctors
- `GET /api/doctors/` - List doctors
- `POST /api/doctors/` - Create doctor
- `GET /api/doctors/{id}/` - Get doctor
- `PUT /api/doctors/{id}/` - Update doctor
- `DELETE /api/doctors/{id}/` - Delete doctor

### Patients
- `GET /api/patients/` - List patients
- `POST /api/patients/` - Create patient
- `GET /api/patients/{id}/` - Get patient
- `PUT /api/patients/{id}/` - Update patient
- `DELETE /api/patients/{id}/` - Delete patient

## 🔄 Workflow Diagram

```
┌─────────────────┐
│ Developer       │
└────────┬────────┘
         │ 1. Create feature/xxx branch
         ▼
┌─────────────────┐
│ feature/xxx     │
│ (Development)   │
└────────┬────────┘
         │ 2. Open PR
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ ✓ Tests         │
│ ✓ Linting       │
│ ✓ Formatting    │
└────────┬────────┘
         │ 3. CI passes
         ▼
┌─────────────────┐
│ feature         │
│ (Staging)       │
└────────┬────────┘
         │ 4. Open PR when ready
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ ✓ Tests         │
│ ✓ Linting       │
│ ✓ Formatting    │
└────────┬────────┘
         │ 5. CI passes
         ▼
┌─────────────────┐
│ main            │
│ (Production)    │
└────────┬────────┘
         │ 6. Auto-deploy
         ▼
┌─────────────────┐
│ Render          │
│ (Live)          │
└─────────────────┘
```

## 🚦 CI/CD Status Checks

All PRs require these checks to pass:

| Check | What it does | How to fix locally |
|-------|--------------|-------------------|
| **test** | Runs pytest test suite | `pytest` |
| **lint** | Checks code quality with ruff | `ruff check .` |
| **format** | Verifies black formatting | `black --check .` or `black .` to fix |

## 📝 Commit Message Convention

Use conventional commits format:

```
<type>: <description>

[optional body]
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `style:` Formatting changes
- `chore:` Maintenance tasks

Examples:
```bash
git commit -m "feat: add appointment cancellation endpoint"
git commit -m "fix: resolve doctor availability conflict"
git commit -m "docs: update API documentation"
git commit -m "test: add patient creation tests"
```

## 🔐 Environment Variables

### Development (.env)
```env
SECRET_KEY=your-dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:pass@localhost:5432/klinik_db
```

### Production (Render)
- Set in Render dashboard
- `DEBUG=False`
- `SECRET_KEY` generated automatically
- `DATABASE_URL` from Render PostgreSQL
- `ALLOWED_HOSTS` = your Render domain

## 🧪 Testing Quick Reference

```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/appointments/

# Run specific test file
pytest apps/appointments/tests.py

# Run specific test
pytest apps/appointments/tests.py::TestAppointmentModel::test_create_appointment

# Run with markers
pytest -m integration

# Run with coverage
pytest --cov=apps --cov-report=html

# Run verbose
pytest -v

# Run and stop at first failure
pytest -x
```

## 🐛 Common Issues & Solutions

### Import Error
```bash
# Problem: ModuleNotFoundError
# Solution: Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements/dev.txt
```

### Database Error
```bash
# Problem: Database doesn't exist
# Solution: Run migrations
python manage.py migrate
```

### CI Failing
```bash
# Problem: Black formatting fails
# Solution: Format code
black .
git add .
git commit --amend --no-edit
git push --force-with-lease
```

### Tests Failing
```bash
# Problem: Tests fail locally
# Solution: Check database and dependencies
python manage.py migrate
pytest -v  # See detailed error
```

## 📞 Important URLs

- **Local Dev**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/health/
- **GitHub Repo**: [Your repository URL]
- **Render Dashboard**: https://dashboard.render.com/

## 🎯 Before Opening PR

Checklist:
- [ ] Code formatted with `black .`
- [ ] Linting passes with `ruff check .`
- [ ] Tests pass with `pytest`
- [ ] Migrations created if models changed
- [ ] Documentation updated if needed
- [ ] PR description filled out
- [ ] Feature tested manually

## 💡 Pro Tips

1. **Pull before you push**: Always `git pull origin feature` before pushing
2. **Test locally first**: Run the full CI suite locally before pushing
3. **Keep PRs small**: Easier to review and merge
4. **Write good commit messages**: Follow conventional commits
5. **Use the PR template**: Fill it out completely
6. **Respond to reviews quickly**: Don't let PRs go stale
7. **Keep feature branch updated**: Regularly merge from feature to avoid conflicts

## 🆘 Need Help?

1. Check [README.md](README.md) for comprehensive documentation
2. Check [BRANCHING.md](BRANCHING.md) for workflow details
3. Check [SETUP.md](SETUP.md) for setup instructions
4. Open a GitHub issue if stuck
