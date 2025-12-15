# Markdown Engine

This submodule powers the Markdown Live Preview feature of the editor. It provides a robust, customizable rendering pipeline that converts Markdown text into formatted Tkinter text.

## Modules

- **`renderer.py`**: The core class that orchestrates the conversion process. It parses the Markdown stream and delegates to `Styler` for visual application.
- **`styler.py`**: Handles the application of font styles, colors, lists, headings, and other visual attributes to the output widget.
- **`highlighter.py`**: specialized syntax highlighting for code blocks *within* the Markdown preview.
- **`exporter.py`**: Functionality to export the rendered markdown to HTML or PDF formats.
- **`utils.py`**: Helper functions for parsing and text processing specific to Markdown syntax.

## Usage

This package is primarily used by `text_editor/ui/markdown_preview.py` to render content in the side panel.
