# Setup & Next Steps

## ✅ Completed

The following has been set up:

### 1. Project Structure
- ✅ Django project with modular app structure
- ✅ Three core apps: appointments, doctors, patients
- ✅ Configuration split (base, development, production)
- ✅ Static and media file configuration

### 2. CI/CD Pipeline
- ✅ GitHub Actions workflow (`.github/workflows/ci.yml`)
- ✅ Automated testing with pytest
- ✅ Code linting with ruff
- ✅ Code formatting checks with black

### 3. Deployment Configuration
- ✅ Render deployment config (`render.yaml`)
- ✅ Production settings optimized for Render
- ✅ Database configuration for PostgreSQL
- ✅ Health check endpoint

### 4. Development Tools
- ✅ pytest configuration with Django integration
- ✅ Code quality tools configured (ruff, black, isort)
- ✅ Development and production requirements
- ✅ Environment variable template (`.env.example`)

### 5. Documentation
- ✅ Comprehensive README with API documentation
- ✅ Branching strategy guide (`BRANCHING.md`)
- ✅ Pull request template

### 6. Git Branches
- ✅ `main` branch (production)
- ✅ `feature` branch (integration/staging)

---

## 🔧 Manual Setup Required

### 1. GitHub Repository Settings

#### Branch Protection for `main` Branch

1. Go to **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `main`
3. Configure the following:
   - ✅ Require pull request reviews before merging (1 approval)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Status checks to require:
     - `test` (Run Tests)
     - `lint` (Lint Code)
     - `format` (Check Code Formatting)
   - ✅ Do not allow bypassing the above settings
   - ✅ Restrict who can push to matching branches
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

#### Branch Protection for `feature` Branch

1. Go to **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `feature`
3. Configure the following:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Status checks to require:
     - `test` (Run Tests)
     - `lint` (Lint Code)
     - `format` (Check Code Formatting)
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

**Note**: Status checks will appear after the first PR is opened and CI runs.

### 2. Render Deployment Setup

#### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Select the repository and branch: `main`
5. Render will detect `render.yaml` and configure automatically
6. Review and confirm the settings
7. Click **Apply**

#### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `klinik-api`
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```
     gunicorn config.wsgi:application
     ```
5. Add PostgreSQL database:
   - Click **New** → **PostgreSQL**
   - Name it `klinik-db`
   - Select the free plan
6. Add environment variables:
   - `SECRET_KEY`: Generate using `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: Your Render domain (e.g., `klinik-api.onrender.com`)
   - `DATABASE_URL`: Will be auto-filled by Render when you connect the database
7. Enable auto-deploy from `main` branch

### 3. Local Development Setup

Each developer should:

```bash
# 1. Clone the repository
git clone <repository-url>
cd Klinik

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements/dev.txt

# 5. Copy environment file
cp .env.example .env

# 6. Edit .env with your local settings
# Update SECRET_KEY, DATABASE_URL, etc.

# 7. Run migrations
python manage.py migrate

# 8. Create superuser
python manage.py createsuperuser

# 9. Run tests to verify setup
pytest

# 10. Start development server
python manage.py runserver
```

---

## 🚀 Next Development Steps

### Phase 1: Verify Setup (Week 1)

1. **Test CI Pipeline**
   ```bash
   # Create a test feature branch
   git checkout feature
   git checkout -b feature/test-ci
   
   # Make a small change (e.g., add a comment)
   # Commit and push
   git add .
   git commit -m "test: verify CI pipeline"
   git push origin feature/test-ci
   
   # Open PR to feature branch
   # Verify all CI checks run and pass
   ```

2. **Test Deployment**
   - Merge a small change to `main`
   - Verify Render automatically deploys
   - Check health endpoint: `https://your-app.onrender.com/health/`
   - Verify API endpoints are accessible

3. **Set Up Branch Protection**
   - Follow instructions above
   - Test that direct pushes to `main` and `feature` are blocked
   - Test that PRs with failing CI cannot be merged

### Phase 2: Core Features (Week 2-3)

1. **Authentication & Authorization**
   - Implement token-based authentication (JWT)
   - Add user registration and login endpoints
   - Implement role-based permissions (Patient, Doctor, Admin)

2. **Enhanced Models**
   - Add custom user model if needed
   - Add medical records to appointments
   - Add doctor availability/schedule model
   - Add notifications model

3. **Business Logic**
   - Appointment validation (prevent double-booking)
   - Doctor availability checking
   - Email notifications for appointments
   - Appointment reminders

### Phase 3: Advanced Features (Week 4-6)

1. **API Enhancements**
   - Add filtering, searching, pagination
   - Implement appointment status transitions
   - Add bulk operations
   - Add export functionality (CSV, PDF)

2. **Testing**
   - Increase test coverage to >80%
   - Add integration tests
   - Add API endpoint tests
   - Performance testing

3. **Documentation**
   - Generate API documentation (Swagger/OpenAPI)
   - Add inline code documentation
   - Create developer onboarding guide

### Phase 4: Production Readiness (Week 7-8)

1. **Security**
   - Security audit
   - Add rate limiting
   - Implement CORS properly
   - Add security headers
   - Set up Sentry for error tracking

2. **Performance**
   - Database query optimization
   - Add caching (Redis)
   - Add database indexes
   - Load testing

3. **Monitoring**
   - Set up application monitoring
   - Add logging strategy
   - Set up alerts for errors
   - Performance monitoring

---

## 📋 Verification Checklist

Before considering the setup complete, verify:

- [ ] GitHub Actions runs on PRs to `feature` and `main`
- [ ] All three CI jobs (test, lint, format) execute
- [ ] Branch protection prevents direct pushes to `main` and `feature`
- [ ] Branch protection blocks merging with failing CI
- [ ] Render deploys automatically when merging to `main`
- [ ] Health check endpoint responds successfully
- [ ] Local development environment works
- [ ] Tests pass locally and in CI
- [ ] Code formatting and linting tools work

---

## 🆘 Troubleshooting

### CI Pipeline Issues

**Problem**: GitHub Actions not running
- **Solution**: Check `.github/workflows/ci.yml` is in the repository
- **Solution**: Verify GitHub Actions are enabled in repository settings

**Problem**: Tests fail in CI but pass locally
- **Solution**: Check environment variables in CI
- **Solution**: Verify database configuration in CI workflow
- **Solution**: Check Python version matches (3.11)

### Render Deployment Issues

**Problem**: Build fails on Render
- **Solution**: Check build logs in Render dashboard
- **Solution**: Verify `requirements.txt` includes all dependencies
- **Solution**: Check Python version in `render.yaml`

**Problem**: Database connection fails
- **Solution**: Verify `DATABASE_URL` is set correctly
- **Solution**: Check PostgreSQL database is created and connected
- **Solution**: Verify migrations ran successfully

**Problem**: Static files not loading
- **Solution**: Check `STATIC_ROOT` and `STATICFILES_STORAGE` settings
- **Solution**: Verify `collectstatic` runs in build command
- **Solution**: Check WhiteNoise middleware is enabled

### Local Development Issues

**Problem**: `ModuleNotFoundError`
- **Solution**: Ensure virtual environment is activated
- **Solution**: Run `pip install -r requirements/dev.txt`

**Problem**: Database errors
- **Solution**: Run `python manage.py migrate`
- **Solution**: Check `DATABASE_URL` in `.env` file
- **Solution**: Verify PostgreSQL is running (if using PostgreSQL locally)

**Problem**: Import errors
- **Solution**: Verify `DJANGO_SETTINGS_MODULE` points to correct settings
- **Solution**: Check app is in `INSTALLED_APPS`

---

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the comprehensive `README.md`
3. Check `BRANCHING.md` for workflow questions
4. Open a GitHub issue with details

---

## 🎉 You're Ready!

Once the manual setup steps are complete, your development workflow is:

```
1. Create feature branch from 'feature'
2. Develop and test locally
3. Open PR to 'feature' branch
4. CI runs automatically
5. Get code review
6. Merge to 'feature'
7. When ready for production: PR 'feature' → 'main'
8. Render deploys automatically
```

Happy coding! 🚀
