# Settings JavaScript Architecture

## Overview

The settings JavaScript has been refactored from a monolithic file into a modular architecture where each app manages its own settings-specific JavaScript.

## File Structure

```
backend/
├── saas_web/static/src/js/
│   ├── settings-core.js      # Core navigation and auto-save functionality
│   └── settings-utils.js     # Shared utility functions
│
├── apps/
│   ├── authentication/static/apps/authentication/js/settings.js
│   ├── chat/static/apps/chat/js/settings.js
│   ├── community/static/apps/community/js/settings.js
│   ├── course/static/apps/course/js/settings.js
│   ├── notebook/static/apps/notebook/js/settings.js
│   ├── notification/static/apps/notification/js/settings.js
│   └── quizz/static/apps/quizz/js/settings.js
│
└── core/
    └── vocal/static/core/vocal/js/settings.js
```

## Module Descriptions

### Core Modules (saas_web)

1. **settings-core.js**
   - Main SettingsManager class
   - Tab navigation
   - Auto-save functionality
   - Search functionality
   - Keyboard shortcuts

2. **settings-utils.js**
   - CSRF token handling
   - Temporary message display
   - Form validation utilities
   - Theme preview
   - Generic form submission

### App-Specific Modules

Each app has its own `settings.js` file that handles:
- App-specific form validations
- Interactive UI elements
- Real-time preview features
- App-specific business logic

## Usage

### In Templates

```django
{% block extra_js %}
<!-- Core settings functionality -->
<script src="{% static 'src/js/settings-utils.js' %}"></script>
<script src="{% static 'src/js/settings-core.js' %}"></script>

<!-- App-specific settings scripts -->
<script src="{% static 'apps/authentication/js/settings.js' %}"></script>
<!-- ... other app scripts ... -->
{% endblock %}
```

### Accessing Utilities

All utility functions are available globally via `window.settingsUtils`:

```javascript
// Show a temporary message
showTemporaryMessage('Settings saved!', 'success');

// Get CSRF token
const token = getCsrfToken();

// Validate a field
validateField(inputElement);

// Handle form submission
await handleFormSubmission(formElement);
```

### Creating New App Settings

When adding settings to a new app:

1. Create the static directory structure:
   ```
   apps/your_app/static/apps/your_app/js/
   ```

2. Create `settings.js` with initialization function:
   ```javascript
   function initializeYourAppSettings() {
       console.log('[YourApp Settings] Initializing...');
       // Your app-specific logic here
   }

   document.addEventListener('DOMContentLoaded', () => {
       initializeYourAppSettings();
   });
   ```

3. Add to the settings template:
   ```django
   <script src="{% static 'apps/your_app/js/settings.js' %}"></script>
   ```

## Benefits

1. **Separation of Concerns**: Each app manages its own settings logic
2. **Maintainability**: Easier to find and modify app-specific code
3. **Performance**: Only load JavaScript for apps that have settings
4. **Consistency**: Shared utilities ensure consistent behavior
5. **Scalability**: Easy to add new apps without modifying core files

## Migration from Old System

The old monolithic `settings.js` (794 lines) has been split into:
- Core navigation and utilities (~400 lines total)
- App-specific files (~100 lines each)

Key functions are now distributed:
- Profile/Account management → `authentication/settings.js`
- Voice testing → `vocal/settings.js`
- Theme preview → `settings-utils.js`
- Navigation → `settings-core.js`