import customtkinter as ctk
from typing import Callable, List, Dict, Union, Tuple

class ModernContextMenu(ctk.CTkToplevel):
    """Modern görünümlü, temalı sağ tık menüsü."""
    def __init__(self, master, commands: List[Union[Tuple[str, Callable], str]], x: int, y: int, theme: Dict[str, str] = None):
        super().__init__(master)
        
        # Pencere Özellikleri
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        
        # Varsayılan Tema
        self.theme = theme or {
            "bg": "#2b2b2b",
            "border": "#454545",
            "hover": "#094771", # VS Code mavi tonu
            "text": "#cccccc",
            "separator": "#454545"
        }
        
        # Konumlandırma
        self.geometry(f"+{x}+{y}")
        
        # Ana Çerçeve (Border efekti için)
        self.border_frame = ctk.CTkFrame(
            self, 
            corner_radius=6, 
            border_width=1, 
            border_color=self.theme.get("border", "#454545"),
            fg_color=self.theme.get("bg", "#2b2b2b")
        )
        self.border_frame.pack(fill="both", expand=True)
        
        # İçerik
        self._create_menu_items(commands)
        
        # Olaylar
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Escape>", lambda e: self.close())
        
        # Odaklan
        self.after(10, self.focus_force)

    def _create_menu_items(self, commands):
        for item in commands:
            if item == "-":
                # Ayırıcı
                sep = ctk.CTkFrame(
                    self.border_frame, 
                    height=2, 
                    fg_color=self.theme.get("separator", "#454545")
                )
                sep.pack(fill="x", padx=4, pady=2)
            else:
                text, command = item
                btn = ctk.CTkButton(
                    self.border_frame,
                    text=text,
                    command=lambda c=command: self._execute_command(c),
                    anchor="w",
                    fg_color="transparent",
                    text_color=self.theme.get("text", "#cccccc"),
                    hover_color=self.theme.get("hover", "#094771"),
                    height=28,
                    corner_radius=4,
                    font=("Segoe UI", 12)
                )
                btn.pack(fill="x", padx=4, pady=2)

    def _execute_command(self, command):
        self.close()
        command()

    def _on_focus_out(self, event):
        # Sadece ana pencere focus kaybettiğinde
        if event.widget == self:
            self.close()

    def close(self):
        try:
            self.destroy()
        except:
            pass
