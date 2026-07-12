# Git Branching & Workflow Guide

## Overview

This project uses a **two-tier feature branch workflow** to ensure code quality and controlled deployments.

## Branch Structure

```
main (production)
│
└── feature (integration/staging)
      │
      ├── feature/appointments
      ├── feature/doctors  
      ├── feature/patients
      └── feature/[description]
```

## Branch Descriptions

### `main` Branch
- **Purpose**: Production-ready code
- **Protection**: ✅ Protected with required status checks
- **Auto-Deploy**: ✅ Automatically deploys to Render on merge
- **Who can merge**: Maintainers only
- **Requires**: All CI checks passing + code review

### `feature` Branch
- **Purpose**: Integration/staging environment
- **Protection**: ✅ Protected with required status checks
- **Auto-Deploy**: ❌ Does not trigger deployment
- **Who can merge**: Team members with approval
- **Requires**: All CI checks passing

### `feature/*` Branches
- **Purpose**: Individual feature development
- **Protection**: ❌ Not protected
- **Naming Convention**: 
  - `feature/appointments` - App-specific features
  - `feature/authentication` - Cross-cutting features
  - `feature/render` - Deployment/infrastructure work

## Workflow Steps

### 1️⃣ Start New Feature

```bash
# Ensure you're up to date
git checkout feature
git pull origin feature

# Create your feature branch
git checkout -b feature/your-feature-name

# Work on your feature
# ... make changes ...
```

### 2️⃣ Commit & Push

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add appointment cancellation endpoint"

# Push to GitHub
git push origin feature/your-feature-name
```

### 3️⃣ Open Pull Request (feature/* → feature)

1. Go to GitHub repository
2. Click "Pull requests" → "New pull request"
3. **Base**: `feature` | **Compare**: `feature/your-feature-name`
4. Fill out PR template:
   - Description of changes
   - Type of change
   - Testing performed
   - Checklist completion
5. Click "Create pull request"

### 4️⃣ CI Checks Run Automatically

GitHub Actions will automatically run:
- ✅ **Tests** (pytest)
- ✅ **Linting** (ruff)
- ✅ **Formatting** (black)

**Status**: All must pass ✅ for merge to be allowed

### 5️⃣ Code Review

- Request review from team members
- Address feedback if requested
- Make changes on your `feature/*` branch
- Push updates (CI will re-run)

### 6️⃣ Merge into `feature`

Once approved and CI passes:
1. Click "Merge pull request"
2. Choose merge strategy (recommended: **Squash and merge**)
3. Delete the `feature/*` branch after merge

### 7️⃣ Deploy to Production (feature → main)

When ready to deploy to production:

```bash
# Ensure feature branch is up to date
git checkout feature
git pull origin feature

# Create PR from feature to main
# This is typically done via GitHub UI
```

1. Open PR: **Base**: `main` | **Compare**: `feature`
2. CI checks run again
3. Get approval from maintainer
4. Merge into `main`
5. 🚀 **Render automatically deploys**

## CI/CD Pipeline

### Pull Request Checks

Every PR triggers GitHub Actions:

```yaml
Jobs:
  ├── Test (pytest with coverage)
  ├── Lint (ruff)
  └── Format (black --check)
```

**All jobs must pass** before merge is allowed.

### Deployment Trigger

Only merges to `main` trigger Render deployment:

```
Merge to main → Render build → Migrations → Deploy
```

## Branch Protection Rules

### `main` Branch
- ✅ Require pull request reviews (1+)
- ✅ Require status checks to pass
  - ✅ Test
  - ✅ Lint
  - ✅ Format
- ✅ Require branches to be up to date
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

### `feature` Branch
- ✅ Require status checks to pass
  - ✅ Test
  - ✅ Lint
  - ✅ Format
- ✅ Require branches to be up to date
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

## Pre-Commit Checks (Local)

Before pushing, run these locally:

```bash
# Format code
black .

# Check linting
ruff check .

# Run tests
pytest

# If all pass, you're ready to push!
git push origin feature/your-feature-name
```

## Common Scenarios

### Scenario 1: Feature Ready
```bash
feature/my-feature → PR → feature → (tests pass) → merge → delete branch
```

### Scenario 2: Multiple Features Ready for Production
```bash
feature/feature-a → feature (merged)
feature/feature-b → feature (merged)
feature → PR → main → (tests pass) → merge → 🚀 Deploy
```

### Scenario 3: Hotfix Needed
```bash
# Branch from main for urgent fixes
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# ... fix bug ...
# ... test thoroughly ...

# PR directly to main
hotfix/critical-bug → PR → main → (tests pass) → merge → 🚀 Deploy

# Backport to feature
git checkout feature
git merge main
git push origin feature
```

### Scenario 4: CI Fails
```bash
# Fix the issue locally
# ... make changes ...

# Push again (triggers new CI run)
git add .
git commit -m "fix: resolve linting issues"
git push origin feature/my-feature

# CI runs again - must pass before merge
```

## Best Practices

### Commits
- ✅ Use conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- ✅ Keep commits atomic (one logical change per commit)
- ✅ Write descriptive commit messages

### Pull Requests
- ✅ Keep PRs focused and reasonably sized
- ✅ Fill out the PR template completely
- ✅ Link related issues
- ✅ Respond to review feedback promptly
- ✅ Don't merge your own PRs without approval

### Testing
- ✅ Write tests for new features
- ✅ Update tests when modifying existing code
- ✅ Ensure tests pass locally before pushing
- ✅ Aim for high test coverage

### Code Quality
- ✅ Run `black` before committing
- ✅ Fix `ruff` warnings
- ✅ Follow Django/DRF best practices
- ✅ Add docstrings for complex functions

## Troubleshooting

### "CI checks failed"
1. Click on "Details" next to the failed check
2. Read the error message
3. Fix locally and push again

### "Branch is out of date"
```bash
git checkout feature/your-feature
git pull origin feature
git push origin feature/your-feature
```

### "Merge conflicts"
```bash
git checkout feature/your-feature
git pull origin feature
# Resolve conflicts in your editor
git add .
git commit -m "chore: resolve merge conflicts"
git push origin feature/your-feature
```

## Summary

```
Development: feature/* branches
    ↓ (PR + CI)
Integration: feature branch
    ↓ (PR + CI)
Production: main branch
    ↓ (auto)
Deployment: Render
```

**Remember**: Never push directly to `main` or `feature` - always use Pull Requests!
