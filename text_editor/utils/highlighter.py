import pygments
from pygments import lex
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, PythonLexer
from pygments.styles import get_style_by_name

class SyntaxHighlighter:
    def __init__(self, text_widget, style_name="monokai"):
        self.text_widget = text_widget
        self.style_name = style_name
        self.setup_tags()

    def setup_tags(self):
        # Create tags based on the style
        style = get_style_by_name(self.style_name)
        for token, opts in style:
            start = opts.get('color')
            background = opts.get('bgcolor')
            # Font styles
            font_opts = []
            if opts.get('bold'): font_opts.append('bold')
            if opts.get('italic'): font_opts.append('italic')
            if opts.get('underline'): font_opts.append('underline')
            font_str = " ".join(font_opts) if font_opts else None
            
            # Helper to convert hex to #hex if needed (pygments usually returns string without # or with)
            fg = f"#{start}" if start else None
            bg = f"#{background}" if background else None

            # Configure tag in text widget
            # Tag name is str(token)
            kwargs = {}
            if fg: kwargs['foreground'] = fg
            if bg: kwargs['background'] = bg
            # Note: fonts in tk.Text are tricky, usually handled by changing the font attribute, 
            # but tag_config allows 'font'. We need to start with the base font and apply styling.
            # For simplicity, we might skip bold/italic in V1 or try to construct a font string.
            # Common font format: ("Consolas", 12, "bold")
            # We'll just set colors for now to ensure stability.
            
            self.text_widget.tag_config(str(token), **kwargs)
            
        # Configure current line tag
        self.text_widget.tag_config("current_line", background="#2d2d30")

    def highlight(self, content=None, lexer=None):
        if content is None:
            content = self.text_widget.get("1.0", "end-1c")
        
        if lexer is None:
            if hasattr(self, 'current_lexer') and self.current_lexer:
                lexer = self.current_lexer
            else:
                lexer = PythonLexer()

        # We must NOT clear all tags because fold tags might exist!
        # Instead, we should remove only syntax tags.
        # But for now, let's just clear syntax tags if we can identify them?
        # Or blindly clear all tags except "sel" and "fold_*" and "current_line"
        
        # Performance optimization: Only re-highlight changed range?
        # For simplicity in V1: clear all tokens.
        # Ideally, we have a list of token tags?
        
        # Since we use str(token) as tag name (e.g. Token.Keyword), we can filter.
        # But for now, let's just avoid clearning "fold_" tags.
        for tag in self.text_widget.tag_names():
            if not tag.startswith("fold_") and tag != "sel" and tag != "current_line":
                self.text_widget.tag_remove(tag, "1.0", "end")

        self.text_widget.mark_set("range_start", "1.0")
        for token, text in lex(content, lexer):
            self.text_widget.mark_set("range_end", f"range_start + {len(text)}c")
            self.text_widget.tag_add(str(token), "range_start", "range_end")
            self.text_widget.mark_set("range_start", "range_end")

    def highlight_current_line(self):
        # Remove tag from everywhere
        self.text_widget.tag_remove("current_line", "1.0", "end")
        
        # Add to current line
        self.text_widget.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def set_lexer_from_filename(self, filename):
        try:
            lexer = get_lexer_for_filename(filename)
        except pygments.util.ClassNotFound:
            lexer = PythonLexer() # Fallback
        self.current_lexer = lexer
        self.highlight()
        return lexer

    def set_lexer_by_name(self, name):
        try:
            lexer = get_lexer_by_name(name)
        except pygments.util.ClassNotFound:
            lexer = PythonLexer()
        self.current_lexer = lexer
        self.highlight()
        return lexer

    def set_lexer(self, lexer):
        self.current_lexer = lexer

    def update_style(self, style_name):
        self.style_name = style_name
        self.setup_tags()
        self.highlight()
