import pygments
import re
from pygments import lex
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, PythonLexer, MarkdownLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from typing import Optional, Any, List, Dict
import tkinter as tk

class SyntaxHighlighter:
    """
    Sözdizimi vurgulama işlemlerini yöneten sınıf.
    Pygments kütüphanesini kullanarak metin renklendirmesi yapar.
    Ayrıca Markdown gibi diller için özel regex desenleri ile hızlı vurgulama sağlar.
    """
    
    TAG_PREFIX = "syntax_"
    
    # Markdown için özel regex desenleri
    MARKDOWN_PATTERNS = {
        "header": r'^#{1,6}\s.*$',
        "bold": r'\*\*.*?\*\*|__.*?__',
        "italic": r'\*.*?\*|_.*?_',
        "link": r'\[.*?\]\(.*?\)',
        "code": r'`.*?`',
        "list": r'^\s*[\*\-\+]\s.*$|^\s*\d+\.\s.*$',
        "blockquote": r'^\s*>.*$'
    }

    def __init__(self, text_widget: tk.Text, style_name: str = "monokai"):
        self.text_widget = text_widget
        self.style_name = style_name
        self.current_lexer = PythonLexer()
        self.setup_tags()

    def setup_tags(self) -> None:
        """Stile dayalı Tkinter etiketlerini (tags) yapılandırır."""
        try:
            style = get_style_by_name(self.style_name)
        except pygments.util.ClassNotFound:
            style = get_style_by_name("monokai")
            
        for token, opts in style:
            start = opts.get('color')
            background = opts.get('bgcolor')
            
            fg = f"#{start}" if start else None
            bg = f"#{background}" if background else None

            kwargs = {}
            if fg: kwargs['foreground'] = fg
            if bg: kwargs['background'] = bg

            # Editörün geçerli fontunu al
            try:
                # Tkinter'da font bazen tuple bazen string döner
                font_info = self.text_widget.cget("font")
                if isinstance(font_info, str):
                    import tkinter.font as tkfont
                    actual_font = tkfont.Font(font=font_info)
                    base_font_family = actual_font.actual("family")
                    base_font_size = actual_font.actual("size")
                else:
                    # Tuple varsayımı: (family, size, weight)
                    base_font_family = font_info[0]
                    base_font_size = font_info[1]
            except Exception:
                from text_editor.config import FONT_FAMILY, FONT_SIZE
                base_font_family = FONT_FAMILY
                base_font_size = FONT_SIZE

            if opts.get('bold'): kwargs['font'] = (base_font_family, base_font_size, "bold")
            if opts.get('italic'): kwargs['font'] = (base_font_family, base_font_size, "italic")
            
            tag_name = f"{self.TAG_PREFIX}{str(token)}"
            self.text_widget.tag_config(tag_name, **kwargs)
            
        # Geçerli satır etiketini yapılandır
        self.text_widget.tag_config("current_line", background="#2d2d30")
        
        # Markdown özel etiketleri (Eğer stilde yoksa varsayılanlar)
        self._setup_markdown_tags()

    def _setup_markdown_tags(self) -> None:
        """Markdown'a özel görsel iyileştirmeler için etiketleri yapılandırır."""
        from text_editor.config import FONT_FAMILY, FONT_SIZE
        
        # Editörün geçerli fontunu al
        try:
            font_info = self.text_widget.cget("font")
            if isinstance(font_info, str):
                import tkinter.font as tkfont
                actual_font = tkfont.Font(font=font_info)
                base_font_family = actual_font.actual("family")
                base_font_size = actual_font.actual("size")
            else:
                base_font_family = font_info[0]
                base_font_size = font_info[1]
        except Exception:
            base_font_family = FONT_FAMILY
            base_font_size = FONT_SIZE

        self.text_widget.tag_config("md_header", foreground="#569cd6", font=(base_font_family, base_font_size + 2, "bold"))
        self.text_widget.tag_config("md_bold", font=(base_font_family, base_font_size, "bold"))
        self.text_widget.tag_config("md_italic", font=(base_font_family, base_font_size, "italic"))
        self.text_widget.tag_config("md_link", foreground="#3794ff", underline=True)
        self.text_widget.tag_config("md_code", background="#2d2d30", foreground="#ce9178")
        self.text_widget.tag_config("md_list", foreground="#c586c0")

    def highlight(self, content: Optional[str] = None, lexer: Any = None) -> None:
        """
        Metni analiz eder ve ilgili etiketleri uygulayarak renklendirir.
        """
        if content is None:
            content = self.text_widget.get("1.0", "end-1c")
        
        if lexer is None:
            lexer = self.current_lexer

        # Eski etiketleri temizle
        self._clear_tags()

        # Eğer Markdown ise özel hızlı vurgulama yapabiliriz
        if isinstance(lexer, MarkdownLexer):
            self._highlight_markdown(content)
            # Pygments ile detaylı vurgulama devam etsin mi? 
            # Evet, çünkü kod blokları vb. Pygments ile daha iyi olur.

        self.text_widget.mark_set("range_start", "1.0")
        for token, text in lex(content, lexer):
            tag_name = f"{self.TAG_PREFIX}{str(token)}"
            self.text_widget.mark_set("range_end", f"range_start + {len(text)}c")
            self.text_widget.tag_add(tag_name, "range_start", "range_end")
            self.text_widget.mark_set("range_start", "range_end")

    def _highlight_markdown(self, content: str) -> None:
        """Markdown için regex tabanlı hızlı vurgulama yapar."""
        for tag, pattern in self.MARKDOWN_PATTERNS.items():
            tag_name = f"md_{tag}"
            for match in re.finditer(pattern, content, re.MULTILINE):
                start = f"1.0 + {match.start()}c"
                end = f"1.0 + {match.end()}c"
                self.text_widget.tag_add(tag_name, start, end)

    def _clear_tags(self) -> None:
        """Tüm sözdizimi etiketlerini metinden kaldırır."""
        for tag in self.text_widget.tag_names():
            if tag.startswith(self.TAG_PREFIX) or tag.startswith("md_"):
                self.text_widget.tag_remove(tag, "1.0", "end")

    def highlight_current_line(self) -> None:
        """İmlecin bulunduğu satırı görsel olarak vurgular."""
        self.text_widget.tag_remove("current_line", "1.0", "end")
        self.text_widget.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def set_lexer_from_filename(self, filename: str) -> Any:
        """Dosya uzantısına göre uygun lexer'ı seçer ve vurgular."""
        try:
            lexer = get_lexer_for_filename(filename)
        except pygments.util.ClassNotFound:
            lexer = PythonLexer()
        self.current_lexer = lexer
        self.highlight()
        return lexer

    def set_lexer_by_name(self, name: str) -> Any:
        """Dil adına göre lexer'ı seçer ve vurgular."""
        try:
            lexer = get_lexer_by_name(name)
        except pygments.util.ClassNotFound:
            lexer = PythonLexer()
        self.current_lexer = lexer
        self.highlight()
        return lexer

    def set_lexer(self, lexer: Any) -> None:
        self.current_lexer = lexer

    def update_style(self, style_name: str) -> None:
        """Vurgulama stilini günceller ve metni yeniden renklendirir."""
        self.style_name = style_name
        self.setup_tags()
        self.highlight()

