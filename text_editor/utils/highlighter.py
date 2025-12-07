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
        # Stile dayalı etiketler oluştur
        style = get_style_by_name(self.style_name)
        for token, opts in style:
            start = opts.get('color')
            background = opts.get('bgcolor')
            # Yazı tipi stilleri
            font_opts = []
            if opts.get('bold'): font_opts.append('bold')
            if opts.get('italic'): font_opts.append('italic')
            if opts.get('underline'): font_opts.append('underline')
            font_str = " ".join(font_opts) if font_opts else None
            
            # Gerekirse hex'i #hex'e dönüştürmek için yardımcı (pygments genellikle # olmadan veya # ile dize döndürür)
            fg = f"#{start}" if start else None
            bg = f"#{background}" if background else None

            # Metin aracında etiketi yapılandır
            # Etiket adı str(token)
            kwargs = {}
            if fg: kwargs['foreground'] = fg
            if bg: kwargs['background'] = bg
            # Not: tk.Text içindeki yazı tipleri zordur, genellikle yazı tipi niteliği değiştirilerek yönetilir,
            # ancak tag_config 'font'a izin verir. Temel yazı tipiyle başlamalı ve stil uygulamalıyız.
            # Basitlik için, V1'de kalın/italik atlayabilir veya bir yazı tipi dizesi oluşturmayı deneyebiliriz.
            # Yaygın yazı tipi formatı: ("Consolas", 12, "bold")
            # Kararlılığı sağlamak için şimdilik sadece renkleri ayarlayacağız.
            
            self.text_widget.tag_config(str(token), **kwargs)
            
        # Geçerli satır etiketini yapılandır
        self.text_widget.tag_config("current_line", background="#2d2d30")

    def highlight(self, content=None, lexer=None):
        if content is None:
            content = self.text_widget.get("1.0", "end-1c")
        
        if lexer is None:
            if hasattr(self, 'current_lexer') and self.current_lexer:
                lexer = self.current_lexer
            else:
                lexer = PythonLexer()

        # Tüm etiketleri TEMİZLEMEMELİYİZ çünkü katlama etiketleri olabilir!
        # Bunun yerine, sadece sözdizimi etiketlerini kaldırmalıyız.
        # Ama şimdilik, tanımlayabilirsek sadece sözdizimi etiketlerini temizleyelim?
        # Veya "sel", "fold_*" ve "current_line" dışındaki tüm etiketleri körü körüne temizle
        
        # Performans optimizasyonu: Sadece değişen aralığı yeniden vurgula?
        # V1'de basitlik için: tüm belirteçleri temizle.
        # İdeal olarak, bir belirteç etiketleri listemiz var mı?
        
        # str(token) etiket adı olarak kullandığımızdan (örn. Token.Keyword), filtreleyebiliriz.
        # Ama şimdilik, "fold_" etiketlerini temizlemekten kaçınalım.
        for tag in self.text_widget.tag_names():
            if not tag.startswith("fold_") and tag != "sel" and tag != "current_line":
                self.text_widget.tag_remove(tag, "1.0", "end")

        self.text_widget.mark_set("range_start", "1.0")
        for token, text in lex(content, lexer):
            self.text_widget.mark_set("range_end", f"range_start + {len(text)}c")
            self.text_widget.tag_add(str(token), "range_start", "range_end")
            self.text_widget.mark_set("range_start", "range_end")

    def highlight_current_line(self):
        # Etiketi her yerden kaldır
        self.text_widget.tag_remove("current_line", "1.0", "end")
        
        # Geçerli satıra ekle
        self.text_widget.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def set_lexer_from_filename(self, filename):
        try:
            lexer = get_lexer_for_filename(filename)
        except pygments.util.ClassNotFound:
            lexer = PythonLexer() # Yedek
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
