import customtkinter as ctk

class TabBar(ctk.CTkScrollableFrame):
    """
    Sekme butonlarını yöneten kaydırılabilir çubuk.
    TabManager'dan görsel mantığı ayırmak için.
    """
    def __init__(self, master, on_tab_click, **kwargs):
        super().__init__(master, orientation="horizontal", height=32, corner_radius=0, **kwargs)
        self.on_tab_click = on_tab_click
        self.tab_buttons = {}
        
        # Varsayılan stil (tema uygulanana kadar)
        self.style = {
            "tab_bg": "transparent",
            "tab_hover": "#2d2d2d",
            "tab_selected": "#1e1e1e",
            "tab_text": "#d4d4d4",
            "accent_color": "#007acc"
        }

    def add_tab_button(self, name, font=("Segoe UI", 13)):
        if name in self.tab_buttons:
            return

        btn = ctk.CTkButton(
            self,
            text=name,
            font=font,
            width=120,
            height=30,
            corner_radius=6,
            fg_color=self.style["tab_bg"],
            hover_color=self.style["tab_hover"],
            text_color=self.style["tab_text"],
            command=lambda n=name: self.on_tab_click(n)
        )
        btn.pack(side="left", padx=2, pady=2)
        self.tab_buttons[name] = btn
        
        # Olayları bağla mekanizması (dışarıdan erişim gerekir)
        return btn

    def remove_tab_button(self, name):
        if name in self.tab_buttons:
            self.tab_buttons[name].destroy()
            del self.tab_buttons[name]

    def set_active_tab(self, name):
        # Tüm butonları güncelle
        for btn_name, btn in self.tab_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=self.style["tab_selected"],
                    hover_color=self.style["tab_selected"], # Seçiliyken hover rengi değişmesin
                    border_width=2,
                    border_color=self.style["accent_color"]
                )
            else:
                btn.configure(
                    fg_color=self.style["tab_bg"],
                    hover_color=self.style["tab_hover"],
                    border_width=0
                )

    def update_tab_text(self, name, text):
        if name in self.tab_buttons:
            self.tab_buttons[name].configure(text=text)

    def apply_theme(self, theme):
        self.configure(fg_color=theme.get("tab_bg", "transparent"))
        
        self.style["tab_selected"] = theme.get("tab_selected", "#1e1e1e")
        self.style["tab_hover"] = theme.get("tab_hover", "#2d2d2d")
        self.style["tab_text"] = theme.get("fg", "#d4d4d4")
        self.style["tab_bg"] = "transparent"
        self.style["accent_color"] = theme.get("accent_color", "#007acc")
        
        # Butonları güncelle (mevcut aktif durumu korumak zor, TabManager yeniden set çağırabilir)
        # Sadece renkleri güncellemek güvenlidir
        for btn in self.tab_buttons.values():
             btn.configure(text_color=self.style["tab_text"])
