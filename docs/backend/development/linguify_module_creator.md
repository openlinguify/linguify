# Linguify Module Creator

A utility script that automates the creation of new modules for the Linguify language learning platform, handling both the Django backend and React frontend components.

## Features

- Creates a complete Django app structure with models, views, serializers, and URLs
- Generates React frontend components in the addons directory
- Updates necessary configuration files (Django settings, URL patterns)
- Adds the module to the dashboard menu with the specified icon
- Creates Next.js app routes if using the app directory structure

## Requirements

- Python 3.8+
- A Linguify project with the standard directory structure:
  - backend/ - Django backend
  - frontend/ - React/Next.js frontend

## Usage

```bash
python create_new_module.py <module_name> <module_icon> [--description "Module description"]
```

### Arguments

- `module_name`: Name of the module (lowercase, no spaces, e.g., quiz, flashcard)
- `module_icon`: Name of a Lucide icon to use (PascalCase, e.g., Brain, BookOpen)
- `--description` (optional): Description of the module

### Examples

```bash
# Create a Quiz module with the Brain icon
python create_new_module.py quiz Brain --description "Quiz module for language learning"

# Create a Flashcard module with the NotebookPen icon
python create_new_module.py flashcard NotebookPen --description "Flashcard module for vocabulary practice"
```

## What Gets Created

### Django Backend

- `backend/apps/<module_name>/` directory with:
  - `__init__.py`
  - `admin.py` - Admin configuration
  - `apps.py` - App configuration
  - `models.py` - Data models
  - `serializers.py` - API serializers
  - `views.py` - API endpoints
  - `urls.py` - URL routing
  - `tests.py` - Test cases
  - `migrations/` directory

- Updates to configuration files:
  - Adds app to `INSTALLED_APPS` in `settings.py`
  - Adds URL patterns to the main `urls.py`

### React Frontend

- `frontend/src/addons/<module_name>/` directory with:
  - `components/` - React components
    - `<ModuleName>View.tsx` - Main component
    - `index.ts` - Export file
  - `api/` - API client
    - `<module_name>API.ts` - API methods
  - `types/` - TypeScript types
    - `index.ts` - Type definitions
  - `index.ts` - Main export file

- Next.js app route (if applicable):
  - `frontend/src/app/<module_name>/page.tsx`
  - `frontend/src/app/<module_name>/layout.tsx`

- Updates to the Dashboard component to include the new module in the menu

## After Creation

After creating the module, you'll need to:

1. Run migrations for the Django app:
   ```bash
   python manage.py makemigrations <module_name>
   python manage.py migrate <module_name>
   ```

2. Verify imports and module integration in the frontend

3. Access your new module at `http://localhost:3000/<module_name>`

## Customization

After the module is created, you can customize the generated code to add additional features:

- Add more fields to the Django model
- Create additional components in the React frontend
- Extend the API endpoints as needed

## Troubleshooting

If the script encounters issues modifying existing files, it will display warnings and instructions for manual updates.

Common issues:

- File structure differences: If your project structure differs from the standard layout, you may need to manually update some files
- Import errors: Verify that all imports are correct after generation
- Icon not found: Make sure to use valid Lucide icon names (see [Lucide icons](https://lucide.dev/icons/))

## License

This script is provided under the MIT License.