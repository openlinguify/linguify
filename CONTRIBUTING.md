# Contributing to Open Linguify

Welcome to OpenLinguify! We're thrilled you're interested in contributing to our open-source language learning platform.

## 📌 Before You Start

Please read the [README.md](./README.md) to understand the project's vision, structure, and current features.

## 🧰 Requirements

Make sure you have the following installed on your system:

- **Python 3.11+**
- **Poetry** (for dependency management)
- **PostgreSQL 13+**
- **Git**
- **Node.js 16+** (for frontend dependencies)

## 🚀 Getting Started Locally

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/linguify.git
cd linguify

# Add upstream remote to keep your fork synced
git remote add upstream https://github.com/openlinguify/linguify.git
```

### 2. Environment Setup

```bash
# Copy environment configuration
cp .env.clean .env
# Edit .env with your local database settings if needed

# Set up backend environment
cd backend
poetry install
cd ..
```

### 3. Database Setup

```bash
# Create PostgreSQL databases
createdb db_linguify_dev
createdb linguify_public

# Run migrations for all projects
make migrate-all

# Load initial data (optional)
make loaddata
```

### 4. Start Development Servers

```bash
# Start all services (Backend, Portal, LMS, CMS)
make all

# Or start individual services:
make backend    # http://localhost:8000
make portal     # http://localhost:8080  
make lms        # http://localhost:8001
make cms        # http://localhost:8002
```

### 5. Verify Installation

Visit http://localhost:8000 to access the main backend API and admin interface.

## 🏗️ Project Structure

Linguify is a multi-Django project architecture:

```
linguify/
├── backend/     # Main API and core functionality
├── portal/      # User portal and learning interface  
├── lms/         # Learning Management System
├── cms/         # Content Management System
├── docs/        # Documentation
└── scripts/     # Utility scripts
```

### Key Directories in Backend:
- `apps/` - Django applications (course, authentication, etc.)
- `core/` - Core functionality and settings
- `static/` - Static files and assets
- `templates/` - HTML templates

## 🔧 Development Workflow

### Branch Strategy
- `main` - Production branch (protected)
- `develop` - Main development branch  
- `dev` - Current active development
- `feature/feature-name` - Feature branches
- `bugfix/issue-description` - Bug fix branches

### Making Changes

1. **Create a feature branch:**
```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

2. **Make your changes and test:**

**Linux/macOS:**
```bash
# Run tests
make test

# Check code style
make lint

# Run specific app tests
cd backend && poetry run python ../manage.py test apps.course
```

**Windows PowerShell:**
```powershell
# Run tests
make test

# Check code style
make lint

# Run specific app tests
cd backend; poetry run python ../manage.py test apps.course
```

3. **Commit with clear messages:**
```bash
git add .
git commit -m "feat: add course progress tracking

- Add progress tracking models
- Implement progress calculation logic
- Add API endpoints for progress data"
```

4. **Push and create Pull Request:**
```bash
git push origin feature/your-feature-name
# Then create a PR on GitHub targeting the 'develop' branch
```

## 📋 Coding Standards

### Python/Django Guidelines
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for classes and functions
- Keep functions small and focused (max 20-30 lines)
- Use meaningful variable and function names

### Code Quality Tools
```bash
# Format code with black
poetry run black .

# Sort imports with isort  
poetry run isort .

# Check with flake8
poetry run flake8 .

# Type checking with mypy
poetry run mypy .
```

### Django Best Practices
- Use Django's built-in features (ORM, forms, admin)
- Follow the "fat models, thin views" principle
- Use Django REST Framework for API endpoints
- Write comprehensive tests for models, views, and API endpoints
- Use Django's translation framework for internationalization

### Database Guidelines
- Always create migrations for model changes
- Use descriptive migration names
- Never edit existing migrations (create new ones)
- Use database constraints when possible
- Index frequently queried fields

### Frontend Guidelines
- Use **Bootstrap 5** classes for styling
- Keep JavaScript vanilla or use minimal libraries
- Follow progressive enhancement principles
- Ensure accessibility (ARIA labels, semantic HTML)
- Test across different browsers and devices

## 🧪 Testing

### Running Tests

**Linux/macOS (bash):**
```bash
# Run all tests
make test

# Run tests for specific app
cd backend && poetry run python ../manage.py test apps.course

# Run with coverage
poetry run coverage run --source='.' ../manage.py test
poetry run coverage report
```

**Windows (PowerShell):**
```powershell
# Run all tests
make test

# Run tests for specific app
cd backend; poetry run python ../manage.py test apps.course

# Run with coverage
poetry run coverage run --source='.' ../manage.py test; poetry run coverage report
```

### Writing Tests
- Write tests for all new features
- Include unit tests for models and utility functions
- Add integration tests for API endpoints
- Test both happy path and edge cases
- Use Django's TestCase and APITestCase

### Test Structure
```python
# Example test file: tests/test_models.py
from django.test import TestCase
from apps.course.models import CourseEnrollment

class CourseEnrollmentModelTest(TestCase):
    def setUp(self):
        # Set up test data
        pass
    
    def test_enrollment_creation(self):
        # Test model creation and validation
        pass
```

## 🚀 Pull Request Process

### Before Submitting
- [ ] All tests pass (`make test`)
- [ ] Code follows style guidelines (`make lint`)
- [ ] New features have tests
- [ ] Documentation is updated if needed
- [ ] Migrations are included for model changes

### PR Guidelines
1. **Title**: Use clear, descriptive titles
   - ✅ "feat: add course progress tracking API"
   - ❌ "updates"

2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Screenshots for UI changes

3. **Size**: Keep PRs focused and reasonably sized
   - Aim for < 400 lines changed
   - Split large features into multiple PRs

### Review Process
- All PRs require at least one review
- Address feedback promptly and respectfully
- Keep discussions focused on the code
- Update your branch if conflicts arise

## 🐛 Bug Reports

When reporting bugs, please include:
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, browser)
- **Error messages** or logs
- **Screenshots** if applicable

Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

## 💡 Feature Requests

For new features:
- Check existing issues to avoid duplicates
- Explain the **use case** and **benefit**
- Provide **mockups** or **examples** if helpful
- Be open to discussion about implementation

## 🌍 Translation Contributions

Help us expand language support:
- Review existing translations in `locale/` directories
- Add new language translations
- Test UI with different languages
- Report translation issues or improvements needed

Currently supported: **English, Spanish, Dutch, French**
Priority languages: **German, Italian, Portuguese, Russian**

## 📚 Documentation

- Update docstrings for new/changed functions
- Add or update API documentation
- Include code examples in documentation
- Keep README.md up to date
- Write clear commit messages

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Give constructive feedback
- Celebrate contributions from others

## 🙋‍♀️ Getting Help

- **GitHub Discussions**: For questions and general discussion
- **Issues**: For bug reports and feature requests
- **Discord**: [Join our community](https://discord.gg/openlinguify)
- **Documentation**: Check the `docs/` directory

## 📄 License

By contributing to Linguify, you agree that your contributions will be licensed under the [GPL v3 License](LICENSE).

---

Thank you for contributing to OpenLinguify! Together, we're making language learning accessible to everyone. 🌟