import tkinter as tk
from text_editor.config import FONT_FAMILY
from text_editor.utils.highlighter import SyntaxHighlighter
from pygments.lexers import get_lexer_by_name

class Minimap(tk.Text):
    def __init__(self, master, main_text, **kwargs):
        super().__init__(master, width=20, wrap="none", bd=0, highlightthickness=0, state="disabled", **kwargs)
        self.main_text = main_text
        
        # Minimap efekti için mikro yazı tipi
        self.configure(font=(FONT_FAMILY, 2))
        
        # Olmaması gereken etkileşimleri devre dışı bırak
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_wheel)
        
        self.highlighter = SyntaxHighlighter(self)
        self.current_lexer = get_lexer_by_name("text")
        
    def update_content(self, event=None):
        # Ana metinden içeriği al
        content = self.main_text.get("1.0", "end")
        
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", content)
        self.configure(state="disabled")
        
        # Sözdizimi vurgulamasını uygula
        if self.highlighter and self.current_lexer:
            self.highlighter.highlight(content, self.current_lexer)
    
    def on_scroll(self, *args):
        # Ana metin kaydırıldığında çağrılır
        self.yview_moveto(args[0])

    def on_click(self, event):
        self.jump_to(event.y)
        return "break"

    def on_drag(self, event):
        self.jump_to(event.y)
        return "break"

    def on_wheel(self, event):
        # Tekerlek hareketini ana metne ilet
        self.main_text.event_generate("<MouseWheel>", delta=event.delta)
        return "break"

    def jump_to(self, y):
        # Yüzdeyi hesapla
        height = self.winfo_height()
        if height == 0: return
        
        fraction = y / height
        self.main_text.yview_moveto(fraction)
        
    def configure_colors(self, bg, fg):
        self.configure(bg=bg, fg=fg)

    def set_lexer(self, lexer):
        self.current_lexer = lexer
        self.update_content() # Yeni lexer ile yeniden vurgula

    def update_style(self, style_name):
        if self.highlighter:
            self.highlighter.update_style(style_name)
            self.update_content() # Yeni stille yeniden vurgula
