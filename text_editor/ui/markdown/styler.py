from tkinter import font as tkfont

class MarkdownStyler:
    """Markdown önizleme stillerini ve temaları yönetir."""
    
    def __init__(self, text_widget, theme=None):
        self.text_widget = text_widget
        self.theme = theme or {}
        self.colors = {}
        self.fonts = {}
        self._update_colors()
        
    def update_theme(self, theme):
        """Temayı günceller ve stilleri yeniden uygular."""
        self.theme = theme
        self._update_colors()
        
    def _update_colors(self):
        """Tema renklerini günceller."""
        is_dark = self.theme.get("type") == "Dark"
        
        self.colors = {
            "bg": self.theme.get("editor_bg", "#1e1e1e"),
            "fg": self.theme.get("editor_fg", "#d4d4d4"),
            "h1": self.theme.get("accent_color", "#569cd6"),
            "h2": "#4ec9b0",
            "h3": "#dcdcaa",
            "h4": "#ce9178",
            "h5": "#c586c0",
            "h6": "#808080",
            "code_bg": self.theme.get("line_num_bg", "#2d2d30"),
            "code_fg": "#ce9178",
            "link": "#3794ff",
            "link_hover": "#61afef",
            "bold": "#ffffff" if is_dark else "#000000",
            "italic": "#9cdcfe",
            "quote_bg": self.theme.get("tab_bg", "#252526"),
            "quote_fg": "#6a9955",
            "quote_border": "#569cd6",
            "list_marker": "#c586c0",
            "hr": self.theme.get("menu_hover", "#3c3c3c"),
            "table_border": "#4d4d4d",
            "table_header_bg": "#2d2d30",
            "highlight_bg": "#5e4b3d",
            "highlight_fg": "#f0c674",
            "checkbox_checked": "#4ec9b0",
            "checkbox_unchecked": "#808080",
            # Kod renkleri (sözdizimi vurgulama)
            "code_keyword": "#569cd6",
            "code_string": "#ce9178",
            "code_number": "#b5cea8",
            "code_comment": "#6a9955",
            "code_function": "#dcdcaa",
            "code_class": "#4ec9b0",
            "code_operator": "#d4d4d4",
            # Alert Colors (GFM)
            "alert_note_bg": "#1d3a5f" if is_dark else "#ddf4ff",
            "alert_note_border": "#3794ff" if is_dark else "#0969da",
            "alert_tip_bg": "#1f3a2d" if is_dark else "#dafbe1",
            "alert_tip_border": "#3fb950" if is_dark else "#1a7f37",
            "alert_warning_bg": "#3d321c" if is_dark else "#fff8c5",
            "alert_warning_border": "#d29922" if is_dark else "#9a6700",
            "alert_important_bg": "#2d2640" if is_dark else "#f6e4ff",
            "alert_important_border": "#a371f7" if is_dark else "#8250df",
            "alert_caution_bg": "#3e1f1f" if is_dark else "#ffebe9",
            "alert_caution_border": "#f85149" if is_dark else "#cf222e",
            # Math
            "math_bg": self.theme.get("line_num_bg", "#2d2d30"),
            "math_fg": "#dcdcaa",
            # Mermaid/Diagram
            "diagram_bg": "#1a2332" if is_dark else "#f0f6fc",
            "diagram_border": "#58a6ff" if is_dark else "#0969da",
            "diagram_fg": "#58a6ff" if is_dark else "#0969da",
        }

    def setup_tags(self, base_font_size=12, zoom_level=100):
        """Markdown elementleri için stil tag'lerini oluşturur."""
        # Font boyutunu zoom'a göre hesapla
        font_size = int(base_font_size * zoom_level / 100)
        
        # Font ailesi
        base_font = "Segoe UI"
        mono_font = "Consolas"
        
        # Başlıklar
        h_sizes = {
            "h1": int(font_size * 2.2),
            "h2": int(font_size * 1.8),
            "h3": int(font_size * 1.5),
            "h4": int(font_size * 1.3),
            "h5": int(font_size * 1.1),
            "h6": font_size
        }
        
        for level, size in h_sizes.items():
            self.text_widget.tag_configure(level, 
                font=(base_font, size, "bold"), 
                foreground=self.colors.get(level, self.colors["h1"]),
                spacing1=20 - (int(level[1]) * 2), 
                spacing3=10 - int(level[1])
            )
        
        # Alt çizgili başlıklar (H1 ve H2 için)
        self.text_widget.tag_configure("h1_underline",
            font=(base_font, 2),
            foreground=self.colors["h1"],
            spacing3=15
        )
        self.text_widget.tag_configure("h2_underline",
            font=(base_font, 2),
            foreground=self.colors["h2"],
            spacing3=12
        )
        
        # Metin stilleri
        self.text_widget.tag_configure("bold", 
            font=(base_font, font_size, "bold"), 
            foreground=self.colors["bold"]
        )
        self.text_widget.tag_configure("italic", 
            font=(base_font, font_size, "italic"), 
            foreground=self.colors["italic"]
        )
        self.text_widget.tag_configure("bold_italic", 
            font=(base_font, font_size, "bold italic"), 
            foreground=self.colors["bold"]
        )
        self.text_widget.tag_configure("strikethrough", 
            font=(base_font, font_size), 
            overstrike=True,
            foreground="#808080"
        )
        self.text_widget.tag_configure("highlight",
            font=(base_font, font_size),
            background=self.colors["highlight_bg"],
            foreground=self.colors["highlight_fg"]
        )
        
        # Inline kod
        self.text_widget.tag_configure("code", 
            font=(mono_font, font_size - 1), 
            foreground=self.colors["code_fg"],
            background=self.colors["code_bg"]
        )
        
        # Kod bloğu
        self.text_widget.tag_configure("code_block", 
            font=(mono_font, font_size - 1), 
            foreground=self.colors["code_fg"],
            background=self.colors["code_bg"],
            spacing1=5, spacing3=5,
            lmargin1=20, lmargin2=20,
            rmargin=20
        )
        
        # Kod bloğu başlığı
        self.text_widget.tag_configure("code_block_header",
            font=(mono_font, font_size - 2),
            foreground=self.colors["h2"],
            background=self.colors["code_bg"],
            spacing1=10
        )
        
        # Sözdizimi renklendirme tag'leri
        for key in ["code_keyword", "code_string", "code_number", "code_comment", "code_function", "code_class"]:
            self.text_widget.tag_configure(key,
                font=(mono_font, font_size - 1),
                foreground=self.colors[key],
                background=self.colors["code_bg"]
            )
        
        # Linkler
        self.text_widget.tag_configure("link", 
            font=(base_font, font_size, "underline"), 
            foreground=self.colors["link"]
        )
        
        # Listeler
        self.text_widget.tag_configure("list_item", 
            font=(base_font, font_size),
            lmargin1=25, lmargin2=40
        )
        self.text_widget.tag_configure("list_marker", 
            font=(base_font, font_size, "bold"),
            foreground=self.colors["list_marker"]
        )
        
        # Checkbox
        self.text_widget.tag_configure("checkbox_checked",
            font=(base_font, font_size),
            foreground=self.colors["checkbox_checked"]
        )
        self.text_widget.tag_configure("checkbox_unchecked",
            font=(base_font, font_size),
            foreground=self.colors["checkbox_unchecked"]
        )
        
        # Nested listeler için
        for i in range(1, 5):
            self.text_widget.tag_configure(f"list_item_l{i}",
                font=(base_font, font_size),
                lmargin1=25 + (i * 20), 
                lmargin2=40 + (i * 20)
            )
        
        # Alıntılar
        self.text_widget.tag_configure("blockquote", 
            font=(base_font, font_size, "italic"),
            foreground=self.colors["quote_fg"],
            background=self.colors["quote_bg"],
            lmargin1=25, lmargin2=25,
            spacing1=5, spacing3=5,
            borderwidth=2,
            relief="flat"
        )
        
        # Yatay çizgi
        self.text_widget.tag_configure("hr", 
            font=(base_font, 4),
            foreground=self.colors["hr"],
            spacing1=15, spacing3=15,
            justify="center"
        )
        
        # Normal paragraf
        self.text_widget.tag_configure("paragraph", 
            font=(base_font, font_size),
            spacing1=5, spacing3=5,
            lmargin1=5, lmargin2=5
        )
        
        # Tablo
        self.text_widget.tag_configure("table", 
            font=(mono_font, font_size - 1),
            foreground=self.colors["fg"]
        )
        self.text_widget.tag_configure("table_header", 
            font=(mono_font, font_size - 1, "bold"),
            foreground=self.colors["h2"],
            background=self.colors["table_header_bg"]
        )
        self.text_widget.tag_configure("table_border",
            font=(mono_font, font_size - 1),
            foreground=self.colors["table_border"]
        )
        
        # Footnote
        self.text_widget.tag_configure("footnote_ref",
            font=(base_font, font_size - 2),
            foreground=self.colors["link"],
            offset=5
        )
        self.text_widget.tag_configure("footnote_content",
            font=(base_font, font_size - 1),
            foreground=self.colors["quote_fg"],
            lmargin1=20, lmargin2=30
        )
        
        # Resim placeholder
        self.text_widget.tag_configure("image_placeholder",
            font=(base_font, font_size),
            foreground=self.colors["h2"],
            justify="center"
        )
        
        # Math Blokları
        self.text_widget.tag_configure("math_block",
            font=("Consolas", font_size, "italic"),
            foreground=self.colors["math_fg"],
            background=self.colors["math_bg"],
            justify="center",
            spacing1=10, spacing3=10,
            lmargin1=40, lmargin2=40
        )
        
        # Mermaid/Diagram blokları
        self.text_widget.tag_configure("diagram_block",
            font=(base_font, font_size),
            foreground=self.colors["diagram_fg"],
            background=self.colors["diagram_bg"],
            justify="center",
            spacing1=15, spacing3=15,
            lmargin1=30, lmargin2=30
        )
        
        # Details/Summary (daraltılabilir bölümler)
        self.text_widget.tag_configure("details_summary",
            font=(base_font, font_size, "bold"),
            foreground=self.colors["h3"],
            spacing1=10, spacing3=5
        )
        self.text_widget.tag_configure("details_content",
            font=(base_font, font_size),
            foreground=self.colors["fg"],
            lmargin1=30, lmargin2=30,
            spacing3=10
        )
        
        # Görev ilerleme çubuğu
        self.text_widget.tag_configure("task_progress",
            font=(base_font, font_size - 1),
            foreground=self.colors["h2"],
            spacing1=5, spacing3=5
        )
        
        # GFM Alerts
        for alert_type in ["note", "tip", "warning", "important", "caution"]:
            # Border (sol çizgi)
            self.text_widget.tag_configure(f"alert_{alert_type}_border",
                font=(base_font, font_size, "bold"),
                foreground=self.colors[f"alert_{alert_type}_border"],
                background=self.colors[f"alert_{alert_type}_bg"],
                lmargin1=15, lmargin2=15
            )
            # Header
            self.text_widget.tag_configure(f"alert_{alert_type}_header",
                font=(base_font, font_size, "bold"),
                foreground=self.colors[f"alert_{alert_type}_border"],
                background=self.colors[f"alert_{alert_type}_bg"]
            )
            # Body
            self.text_widget.tag_configure(f"alert_{alert_type}_body",
                font=(base_font, font_size),
                foreground=self.colors["fg"],
                background=self.colors[f"alert_{alert_type}_bg"],
                lmargin1=25, lmargin2=25
            )
            
        # HTML tag support
        self.text_widget.tag_configure("html_center", justify="center")
        self.text_widget.tag_configure("html_sub", 
            font=(base_font, font_size - 2),
            offset=-3)
        self.text_widget.tag_configure("html_sup",
            font=(base_font, font_size - 2),
            offset=5)

