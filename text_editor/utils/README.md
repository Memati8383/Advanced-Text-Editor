# Utilities

This directory contains utility modules that provide core functionality, logic, and background services for the editor, separating concerns from the UI layer.

## Modules

- **`autocompleter.py`**: Handles code completion logic. manages the suggestion popup and specific language strategies (Python, JavaScript, etc.).
- **`file_icons.py`**: specific library or mapping logic to provide file type icons for the `FileExplorer` and tabs.
- **`file_monitor.py`**: Watches for external changes to open files and triggers reload prompts.
- **`highlighter.py`**: The syntax highlighting engine. Parses code using Regex and applies tags to the `Text` widget.
- **`language_manager.py`**: Manages internationalization (i18n). Loads JSON translation files and provides a static `get()` method for localized strings.
- **`performance_monitor.py`**: Monitors system resources (CPU, RAM) and internal application metrics for the debug/performance report.
- **`shortcut_manager.py`**: Central registry for keyboard shortcuts. Handles binding creation and looking up active keymaps.
