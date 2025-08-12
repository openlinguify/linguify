# Linguify Documentation Site

Independent Django project for the Linguify developer documentation.

## Quick Start

### Option 1: Using the Makefile (Recommended)

From the root directory of Linguify:

```bash
# Start only the documentation server
make docs

# Start all 5 servers (Portal, LMS, Backend, CMS, Documentation)
make all

# Show all available URLs
make urls

# Check the status of all projects
make status
```

The documentation will be available at **http://127.0.0.1:8003**

### Option 2: Manual startup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start the development server:**
   ```bash
   python manage.py runserver 8003
   ```

4. **Visit the documentation:**
   Open http://127.0.0.1:8003 in your browser

## Project Structure

```
docs/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── docs_site/            # Django project settings
├── docs_app/             # Django app for documentation
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS, images)
├── backend/             # Backend documentation
├── frontend/            # Frontend documentation
├── development/         # Development guides
├── setup/              # Setup and installation guides
└── translations/       # Translation documentation
```

## Features

- 📖 Markdown and HTML documentation support
- 🎨 Responsive Bootstrap design
- 🔍 Easy navigation with sidebar
- 📱 Mobile-friendly interface
- 🌐 Ready for multi-language support

## Adding Documentation

1. **Markdown files:** Place `.md` files in the appropriate directories
2. **HTML files:** Add `.html` files for custom layouts
3. **Navigation:** Update the sidebar in `templates/docs/base.html`

## Development

This site serves the existing documentation structure while providing a clean, navigable interface for developers working on Linguify.