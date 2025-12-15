# Localization (Locales)

This directory stores the translation files for the application's internationalization (i18n) system.

## Supported Languages

The application currently supports the following languages:

- **Turkish (`tr.json`)** - Default / Native
- **English (`en.json`)**
- **Spanish (`es.json`)**
- **German (`de.json`)**
- **Azerbaijani (`az.json`)**

## Structure

Each file is a JSON object where the keys are internal identifiers used in the code (e.g., `"menu_file"`) and values are the translated strings (e.g., `"Dosya"`).

### Example (`en.json`)
```json
{
    "menu_file": "File",
    "menu_new": "New File",
    "menu_open": "Open...",
    ...
}
```

## Adding a New Language

1. Create a new `.json` file with the appropriate ISO 639-1 language code (e.g., `fr.json` for French).
2. Copy the contents of `en.json` or `tr.json` into your new file.
3. Translate the values to the target language.
4. Open `text_editor/utils/language_manager.py`.
5. Add the new language to the `LanguageManager` supported list or ensure the loader picks it up.
6. The new language will automatically appear in the Settings dialog.
