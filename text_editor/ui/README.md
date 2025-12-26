# UI Components

This directory contains the User Interface components for the Advanced Text Editor. The application is built using `customtkinter` for a modern, dark-themed aesthetic.

## Components Breakdown

### Core Windows & Dialogs
- **`main_window.py`**: The main application window controller. Integrates all other UI components, handles window lifecycle, and manages the main layout (sidebar, editor area, status bar, terminal).
- **`settings_dialog.py`**: A comprehensive settings modal. Handles configuration for General, Editor, Appearance, Theme, Shortcuts, Terminal, and Advanced settings.
- **`search_dialog.py`**: Find and replace dialog with regex and case-sensitive support.
- **`goto_line.py`**: A "Go to Line" dialog for quick navigation.

### Editor & Content Areas
- **`editor.py`**: The core text editing component. Wraps the `tkinter.Text` widget with modern features like syntax highlighting, line numbers, and event handling.
- **`image_viewer.py`**: A component to view image files directly within the editor tabs. Supports zooming and image analysis.
- **`tab_manager.py`**: Manages open files (tabs). Handles file switching, closing tabs, and determining which viewer (Code Editor or Image Viewer) to launch.

### Helper Components
- **`file_explorer.py`**: The file tree view on the sidebar and "Open File" functionality. Localized context menus and file management.
- **`minimap.py`**: A visual code minimap for quick scrolling and code overview.
- **`status_bar.py`**: Displays cursor position, encoding, file stats, and git branch information.
- **`terminal.py`**: An integrated embedded terminal drawer.
- **`context_menu.py`**: Custom context menus for the editor and file explorer.
- **`markdown_preview.py`**: A live preview panel for Markdown files.

### Help & Onboarding
- **`help_system.py`**: The main help window containing documentation and shortcuts.
- **`help_content.py`**: Content provider for the help system.
- **`tutorial_mode.py`**: An interactive tutorial mode to guide new users.

### Sub-packages
- **`markdown/`**: Contains specialized classes for the Markdown rendering engine.
- **`settings/`**: Modular setting panels for the settings dialog.
- **`features/`**: Modular editor features like code folding and multi-cursor support.
