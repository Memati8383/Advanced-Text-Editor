import customtkinter as ctk
import tkinter as tk

class ModernDropdownMenu(ctk.CTkToplevel):
    """
    Modern, stilize dropdown menü.
    CustomTkinter ile oluşturulmuş özel menü sistemi.
    """
    def __init__(self, parent, items, x, y, theme=None):
        """
        Args:
            parent: Ana pencere
            items: Menü öğeleri listesi [{"label": "...", "command": func, "icon": "emoji", "separator": bool}, ...]
            x, y: Menü pozisyonu
            theme: Tema sözlüğü (opsiyonel)
        """
        super().__init__(parent)
        
        self.parent = parent
        self.items = items
        self.theme = theme or {}
        
        # Pencere ayarları
        self.overrideredirect(True)  # Başlık çubuğu yok
        self.attributes("-topmost", True)  # Her zaman üstte
        
        # Şeffaflık efekti (Windows'da)
        try:
            self.attributes("-alpha", 0.97)
        except:
            pass
        
        # Ana çerçeve
        bg_color = self.theme.get("menu_bg", "#2b2b2b")
        
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=bg_color,
            border_width=2,
            border_color=self.theme.get("accent_color", "#404040")
        )
        self.main_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Menü öğelerini oluştur
        self.create_menu_items()
        
        # Pozisyonla
        self.geometry(f"+{x}+{y}")
        
        # Dışarı tıklandığında kapat
        self.bind("<FocusOut>", lambda e: self.destroy_menu())
        self.focus_force()
        
        # Animasyon için başlangıç boyutu
        self.attributes("-alpha", 0.0)
        self.fade_in()
    
    def create_menu_items(self):
        """Menü öğelerini oluşturur"""
        for i, item in enumerate(self.items):
            if item.get("separator"):
                # Ayırıcı çizgi
                separator = ctk.CTkFrame(
                    self.main_frame,
                    height=1,
                    fg_color=self.theme.get("menu_hover", "#404040")
                )
                separator.pack(fill="x", padx=8, pady=3)
            else:
                # Normal menü öğesi
                self.create_menu_button(item)
    
    def create_menu_button(self, item):
        """Tek bir menü butonu oluşturur"""
        icon = item.get("icon", "")
        label = item.get("label", "")
        command = item.get("command")
        shortcut = item.get("shortcut", "")
        submenu = item.get("submenu")
        
        # Buton çerçevesi - daha kompakt
        btn_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=4,
            height=28
        )
        btn_frame.pack(fill="x", padx=4, pady=1)
        btn_frame.pack_propagate(False)
        
        # Grid yapılandırması
        btn_frame.grid_columnconfigure(0, weight=0)  # İkon
        btn_frame.grid_columnconfigure(1, weight=1)  # Etiket
        btn_frame.grid_columnconfigure(2, weight=0)  # Kısayol
        btn_frame.grid_columnconfigure(3, weight=0)  # Sil / Alt Menü
        
        # İkon - daha küçük
        if icon:
            icon_label = ctk.CTkLabel(
                btn_frame,
                text=icon,
                font=("Segoe UI", 12),
                width=24
            )
            icon_label.grid(row=0, column=0, padx=(6, 3), pady=4, sticky="w")
        
        # Etiket - daha küçük font
        label_widget = ctk.CTkLabel(
            btn_frame,
            text=label,
            font=("Segoe UI", 11),
            anchor="w"
        )
        label_widget.grid(row=0, column=1, padx=3, pady=4, sticky="ew")
        
        # Kısayol metni - daha küçük
        if shortcut:
            shortcut_label = ctk.CTkLabel(
                btn_frame,
                text=shortcut,
                font=("Segoe UI", 9),
                text_color=("gray50", "gray60"),
                anchor="e"
            )
            shortcut_label.grid(row=0, column=2, padx=(3, 6), pady=4, sticky="e")
        
        # Alt menü işareti
        if submenu:
            arrow_label = ctk.CTkLabel(
                btn_frame,
                text="▶",
                font=("Segoe UI", 9),
                text_color=("gray50", "gray60"),
                width=16
            )
            arrow_label.grid(row=0, column=3, padx=(0, 6), pady=4, sticky="e")
            
        # Silme / Eylem butonu
        on_delete = item.get("on_delete")
        if on_delete:
            delete_icon = item.get("delete_icon", "✕")
            delete_hover = item.get("delete_hover", ("#ff4d4d", "#cc0000"))
            
            delete_btn = ctk.CTkButton(
                btn_frame,
                text=delete_icon,
                width=18,
                height=18,
                corner_radius=4,
                fg_color="transparent",
                hover_color=delete_hover,
                text_color=("gray50", "white"),
                font=("Segoe UI", 8, "bold"),
                command=lambda: (self.destroy_menu(), on_delete())
            )
            delete_btn.grid(row=0, column=3, padx=(0, 6), pady=2, sticky="e")
        
        # Hover efektleri
        def on_enter(e):
            if item.get("enabled", True) and not item.get("is_header", False):
                btn_frame.configure(fg_color=self.theme.get("menu_hover", "#404040"))
                if submenu:
                    # Alt menüyü göster
                    self.show_submenu(btn_frame, submenu)
        
        def on_leave(e):
            if not item.get("is_header", False):
                btn_frame.configure(fg_color="transparent")
                
        # Header stili
        if item.get("is_header"):
            btn_frame.configure(fg_color=self.theme.get("menu_hover", "#404040"), height=32)
            label_widget.configure(font=("Segoe UI", 11, "bold"), text_color=self.theme.get("accent_color", "#00d4ff"))
            if icon:
                icon_label.configure(text_color=self.theme.get("accent_color", "#00d4ff"))
        
        def on_click(e):
            if item.get("enabled", True) and command:
                self.destroy_menu()
                command()
        
        # Devre dışı kalmış görünümü
        if not item.get("enabled", True):
            label_widget.configure(text_color=("gray60", "gray40"))
            if icon:
                icon_label.configure(text_color=("gray60", "gray40"))
        
        # Tüm widget'lara event bind et
        for widget in [btn_frame, label_widget]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
        
        if icon:
            icon_label.bind("<Enter>", on_enter)
            icon_label.bind("<Leave>", on_leave)
            icon_label.bind("<Button-1>", on_click)
        
        if shortcut:
            shortcut_label.bind("<Enter>", on_enter)
            shortcut_label.bind("<Leave>", on_leave)
            shortcut_label.bind("<Button-1>", on_click)
    
    def show_submenu(self, parent_widget, submenu_items):
        """Alt menüyü gösterir"""
        # TODO: Alt menü implementasyonu
        pass
    
    def fade_in(self):
        """Fade-in animasyonu"""
        alpha = self.attributes("-alpha")
        if alpha < 0.97:
            self.attributes("-alpha", alpha + 0.15)
            self.after(20, self.fade_in)
    
    def destroy_menu(self):
        """Menüyü yok eder"""
        try:
            self.destroy()
        except:
            pass


class ModernMenuBar:
    """
    Modern menü çubuğu için yardımcı sınıf.
    Dropdown menüleri yönetir.
    """
    def __init__(self, parent, theme=None):
        self.parent = parent
        self.theme = theme or {}
        self.active_menu = None
    
    def show_dropdown(self, button, items):
        """
        Dropdown menü gösterir.
        
        Args:
            button: Menüyü tetikleyen buton
            items: Menü öğeleri
        """
        # Önceki menüyü kapat
        if self.active_menu and self.active_menu.winfo_exists():
            self.active_menu.destroy()
        
        # Buton pozisyonunu al
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height() + 2
        
        # Yeni menü oluştur
        self.active_menu = ModernDropdownMenu(
            self.parent,
            items,
            x,
            y,
            self.theme
        )
    
    def close_active_menu(self):
        """Aktif menüyü kapatır"""
        if self.active_menu and self.active_menu.winfo_exists():
            self.active_menu.destroy()
            self.active_menu = None
