# 🌍 OpenLinguify Translation Guide

This comprehensive guide will help you contribute translations to OpenLinguify and make the platform accessible to learners worldwide.

## 📋 Table of Contents

1. [Understanding the Translation Structure](#understanding-the-translation-structure)
2. [Prerequisites](#prerequisites)
3. [Setting Up Your Environment](#setting-up-your-environment)
4. [How to Translate](#how-to-translate)
5. [Testing Your Translations](#testing-your-translations)
6. [Submitting Your Translations](#submitting-your-translations)
7. [Translation Guidelines](#translation-guidelines)
8. [Tools and Resources](#tools-and-resources)
9. [Common Issues and Solutions](#common-issues-and-solutions)

## Understanding the Translation Structure

OpenLinguify uses Django's internationalization (i18n) framework. Each module has its own translation files:

```
backend/
├── apps/
│   ├── course/
│   │   └── i18n/
│   │       ├── en.po          # English (source)
│   │       ├── fr.po          # French
│   │       ├── es.po          # Spanish  
│   │       ├── nl.po          # Dutch
│   │       └── [your-lang].po # Your language
│   ├── chat/
│   │   └── i18n/
│   ├── revision/
│   │   └── i18n/
│   └── [other-apps]/
│       └── i18n/
└── portal/
    └── public_web/
        └── locale/
            ├── en/
            ├── fr/
            ├── es/
            └── nl/
```

### File Types
- **`.po` files**: Editable translation files (Portable Object)
- **`.mo` files**: Compiled binary files (Machine Object) - auto-generated

## Prerequisites

- **Python 3.8+** with Django installed
- **gettext utilities** for .po file compilation
- **Text editor** or **Poedit** (recommended for beginners)
- **Git** for version control

### Installing gettext

**Ubuntu/Debian:**
```bash
sudo apt-get install gettext
```

**macOS:**
```bash
brew install gettext
```

**Windows:**
Download from: https://mlocati.github.io/articles/gettext-iconv-windows.html

## Setting Up Your Environment

1. **Fork and clone the repository:**
```bash
git clone https://github.com/YOUR-USERNAME/linguify.git
cd linguify
```

2. **Set up the development environment:**
```bash
cd backend
poetry install
poetry run python manage.py migrate
```

3. **Install Poedit (optional but recommended):**
- Download from: https://poedit.net/
- Poedit provides a user-friendly interface for editing .po files

## How to Translate

### Method 1: Using Poedit (Recommended for Beginners)

1. **Open Poedit** and select "Create new translation"
2. **Choose the .po file** you want to translate from (e.g., `en.po`)
3. **Select your target language** (e.g., German - de)
4. **Start translating** each string:
   - Source text appears on the left
   - Your translation goes on the right
   - Add comments for context if needed
5. **Save the file** as `[language-code].po` (e.g., `de.po`)

### Method 2: Manual Text Editing

1. **Navigate to the app's i18n folder:**
```bash
cd backend/apps/course/i18n/
```

2. **Copy an existing .po file:**
```bash
cp en.po de.po  # For German translation
```

3. **Edit the header information:**
```po
# GERMAN TRANSLATION FOR COURSE APP
# Copyright (C) 2024 Open Linguify
# This file is distributed under the same license as the Open Linguify package.
#
msgid ""
msgstr ""
"Project-Id-Version: Open Linguify Course\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2024-06-17 00:00+0000\n"
"PO-Revision-Date: 2024-12-XX XX:XX+0000\n"
"Last-Translator: Your Name <your.email@example.com>\n"
"Language-Team: German\n"
"Language: de\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
```

4. **Translate each msgstr:**
```po
# Course navigation
msgid "Courses"
msgstr "Kurse"

msgid "Lessons"
msgstr "Lektionen"

msgid "Progress"
msgstr "Fortschritt"
```

### Method 3: Using Django Commands

1. **Generate .po files for a new language:**
```bash
cd backend
poetry run python manage.py makemessages -l de  # For German
```

2. **Update existing translations:**
```bash
poetry run python manage.py makemessages -a  # Update all languages
```

## Testing Your Translations

1. **Compile your translations:**
```bash
cd backend/apps/course/i18n/
msgfmt de.po -o de.mo
```

Or use Django command:
```bash
poetry run python manage.py compilemessages
```

2. **Test in the application:**
```bash
cd backend
poetry run python manage.py runserver
```

3. **Change language in browser** or add `?lang=de` to the URL

4. **Verify your translations appear correctly**

## Submitting Your Translations

1. **Create a feature branch:**
```bash
git checkout -b translations/add-german-support
```

2. **Add your files:**
```bash
git add backend/apps/*/i18n/de.po
git add backend/apps/*/i18n/de.mo
```

3. **Commit with a clear message:**
```bash
git commit -m "Add German translations for course, chat, and revision apps

- Translated 247 strings across core educational modules
- Maintained consistent terminology for learning concepts
- Tested UI layout with longer German phrases"
```

4. **Push and create a Pull Request:**
```bash
git push origin translations/add-german-support
```

## Translation Guidelines

### 1. Tone and Style
- **Friendly and encouraging**: OpenLinguify is about learning
- **Clear and simple**: Avoid overly technical language
- **Consistent**: Use the same terms throughout the platform

### 2. Educational Terminology
Keep these terms consistent:
- **Course** → Preserve educational context
- **Lesson** → Main learning unit
- **Exercise** → Practice activity
- **Progress** → Learning advancement
- **Flashcard** → Memory tool

### 3. UI Text Guidelines
- **Button text**: Keep short and actionable
- **Error messages**: Be helpful, not alarming
- **Navigation**: Use familiar terms in your language
- **Forms**: Make labels clear and specific

### 4. Cultural Adaptation
- **Examples**: Adapt to local context when appropriate
- **References**: Localize cultural references
- **Currency**: Use local currency symbols where relevant
- **Dates**: Follow local date formats

### 5. Technical Considerations
- **Placeholders**: Keep `{variable}` unchanged
- **HTML**: Don't translate HTML tags or attributes
- **URLs**: Translate only if creating localized versions

## Tools and Resources

### Translation Tools
- **[Poedit](https://poedit.net/)**: User-friendly .po file editor
- **[Lokalize](https://userbase.kde.org/Lokalize)**: KDE translation tool
- **[OmegaT](https://omegat.org/)**: Free CAT tool
- **[Weblate](https://weblate.org/)**: Web-based translation platform

### Language Resources
- **[Django i18n docs](https://docs.djangoproject.com/en/stable/topics/i18n/)**: Official documentation
- **[GNU gettext manual](https://www.gnu.org/software/gettext/manual/)**: Comprehensive guide
- **[Language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)**: ISO 639-1 reference

### Community
- **[Discord #translations](https://discord.gg/PJ8uTzSS)**: Real-time help
- **[GitHub Discussions](https://github.com/openlinguify/linguify/discussions)**: Longer discussions
- **Email**: translations@openlinguify.com

## Common Issues and Solutions

### Issue: Text too long for UI elements
**Solution**: 
- Test with longer phrases
- Suggest UI adjustments if needed
- Use abbreviations when culturally appropriate

### Issue: Missing context for translation
**Solution**:
- Check the code where the string is used
- Ask in Discord #translations channel
- Add translator comments in .po files

### Issue: Plural forms not working
**Solution**:
- Verify `Plural-Forms` header is correct for your language
- Check Django pluralization rules
- Test with different numbers

### Issue: Compilation errors
**Solution**:
- Check for syntax errors in .po file
- Ensure proper escaping of quotes
- Validate with `msgfmt --check file.po`

### Issue: Translations not appearing
**Solution**:
- Ensure .mo files are compiled
- Check Django `LANGUAGES` setting
- Verify language code matches directory name
- Clear browser cache

## Apps to Translate (Priority Order)

### Phase 1: Core Interface
1. **`backend/apps/course/`** - Main learning interface
2. **`portal/public_web/`** - Public website
3. **`backend/saas_web/`** - User dashboard

### Phase 2: Educational Features
4. **`backend/apps/revision/`** - Spaced repetition
5. **`backend/apps/notebook/`** - Note-taking
6. **`backend/apps/quizz/`** - Assessment system

### Phase 3: Communication
7. **`backend/apps/chat/`** - Messaging system
8. **`backend/apps/community/`** - Social features

### Phase 4: Advanced Features
9. **`backend/apps/language_ai/`** - AI interactions
10. **`backend/apps/documents/`** - Collaboration

## Recognition and Contribution

### Translator Credits
- Your name will be added to the contributors list
- Recognition in release notes for new language additions
- Special "Translator" role in Discord community
- Invitation to translation coordination team

### Maintaining Translations
- Help review translations from other contributors
- Keep translations updated with new features
- Participate in translation consistency discussions

---

## Need Help?

Don't hesitate to reach out:
- **Discord**: Join #translations channel
- **Email**: translations@openlinguify.com  
- **GitHub**: Open an issue with "translation" label

Thank you for helping make OpenLinguify accessible to learners worldwide! 🌍

---

*This guide is maintained by the OpenLinguify community. Last updated: July 2025*