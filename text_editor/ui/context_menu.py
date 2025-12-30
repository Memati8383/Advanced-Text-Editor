"""
Modern Context Menu - Gelişmiş Sağ Tık Menüsü

Premium tasarım:
- Glassmorphism efekti
- Smooth animasyonlar (fade-in, scale)
- İkon desteği
- Kısayol tuşu gösterimi
- Hover efektleri ile mikro-etkileşimler
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, List, Dict, Union, Tuple, Optional


class ModernContextMenu(ctk.CTkToplevel):
    """
    Premium görünümlü, animasyonlu sağ tık menüsü.
    
    Özellikler:
    - Glassmorphism efekti (yarı saydam arka plan)
    - Fade-in animasyonu
    - İkon ve kısayol tuşu desteği
    - Hover efektleri
    - Alt menü (submenu) desteği
    - Tooltip desteği
    """
    
    # Varsayılan tema renkleri (VS Code Dark+ teması)
    DEFAULT_THEME = {
        "bg": "#1e1e1e",                    # Ana arka plan
        "bg_hover": "#2a2d2e",              # Hover arka plan
        "bg_active": "#094771",             # Aktif/seçili arka plan
        "border": "#454545",                # Kenarlık rengi
        "text": "#cccccc",                  # Normal metin
        "text_hover": "#ffffff",            # Hover metin
        "text_disabled": "#6e6e6e",         # Devre dışı metin
        "shortcut": "#858585",              # Kısayol rengi
        "separator": "#404040",             # Ayırıcı rengi
        "icon": "#75beff",                  # İkon rengi
        "accent": "#007acc",                # Vurgu rengi
        "shadow": "#000000",                # Gölge rengi
    }
    
    def __init__(
        self, 
        master, 
        commands: List[Union[Tuple, str, Dict]], 
        x: int, 
        y: int, 
        theme: Dict[str, str] = None
    ):
        """
        Args:
            master: Ana pencere
            commands: Menü öğeleri listesi. Her öğe şu formatlarda olabilir:
                - Tuple: (text, command) veya (icon, text, command) veya (icon, text, command, shortcut)
                - String: "-" ayırıcı için
                - Dict: {"icon": "🔍", "text": "Ara", "command": func, "shortcut": "Ctrl+F", "enabled": True}
            x, y: Menü pozisyonu
            theme: Tema sözlüğü (opsiyonel)
        """
        super().__init__(master)
        
        # Master referansı (global binding için)
        self._master = master
        self._is_closed = False
        
        # Tema ayarları
        self.theme = {**self.DEFAULT_THEME, **(theme or {})}
        
        # Pencere özellikleri
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        
        # Şeffaflık (başlangıçta tamamen şeffaf - animasyon için)
        try:
            self.attributes('-alpha', 0.0)
        except:
            pass
        
        # Tooltip için değişkenler
        self._tooltip_window: Optional[tk.Toplevel] = None
        self._tooltip_after_id: Optional[str] = None
        
        # Alt menü referansı
        self._submenu: Optional['ModernContextMenu'] = None
        
        # Ana container (gölge efekti için)
        self._create_shadow_container()
        
        # Menü öğelerini oluştur
        self._create_menu_items(commands)
        
        # Pozisyonlama (ekran sınırları kontrolü ile)
        self._position_menu(x, y)
        
        # Escape tuşu
        self.bind("<Escape>", lambda e: self.close())
        
        # Global click handler - herhangi bir yere tıklandığında kapat
        self._bind_global_click()
        
        # Odaklan
        self.after(10, self._focus_menu)
        
        # Animasyonlu açılış
        self._animate_open()
    
    def _create_shadow_container(self):
        """Gölge efekti ile ana container oluşturur."""
        # Dış çerçeve (gölge efekti için)
        self.outer_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            fg_color=self.theme["shadow"],
            border_width=0
        )
        self.outer_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Ana menü çerçevesi
        self.main_frame = ctk.CTkFrame(
            self.outer_frame,
            corner_radius=6,
            fg_color=self.theme["bg"],
            border_width=1,
            border_color=self.theme["border"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # İç padding çerçevesi
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=4, pady=4)
    
    def _create_menu_items(self, commands: List):
        """Menü öğelerini oluşturur."""
        for item in commands:
            if isinstance(item, str) and item == "-":
                self._create_separator()
            elif isinstance(item, dict):
                self._create_menu_button_from_dict(item)
            elif isinstance(item, tuple):
                self._create_menu_button_from_tuple(item)
    
    def _create_separator(self):
        """Ayırıcı çizgi oluşturur."""
        separator_frame = ctk.CTkFrame(
            self.content_frame,
            height=1,
            fg_color=self.theme["separator"]
        )
        separator_frame.pack(fill="x", padx=8, pady=4)
    
    def _create_menu_button_from_tuple(self, item: tuple):
        """Tuple formatından menü butonu oluşturur."""
        if len(item) == 2:
            text, command = item
            icon, shortcut = None, None
        elif len(item) == 3:
            if callable(item[2]):
                icon, text, command = item
                shortcut = None
            else:
                text, command, shortcut = item
                icon = None
        elif len(item) >= 4:
            icon, text, command, shortcut = item[:4]
        else:
            return
        
        self._create_menu_button(
            icon=icon,
            text=text,
            command=command,
            shortcut=shortcut
        )
    
    def _create_menu_button_from_dict(self, item: dict):
        """Dict formatından menü butonu oluşturur."""
        self._create_menu_button(
            icon=item.get("icon"),
            text=item.get("text", ""),
            command=item.get("command"),
            shortcut=item.get("shortcut"),
            enabled=item.get("enabled", True),
            tooltip=item.get("tooltip"),
            submenu=item.get("submenu")
        )
    
    def _create_menu_button(
        self,
        icon: Optional[str] = None,
        text: str = "",
        command: Optional[Callable] = None,
        shortcut: Optional[str] = None,
        enabled: bool = True,
        tooltip: Optional[str] = None,
        submenu: Optional[List] = None
    ):
        """Tek bir menü butonu oluşturur."""
        # Buton container
        btn_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=4,
            height=28
        )
        btn_frame.pack(fill="x", pady=1)
        btn_frame.pack_propagate(False)
        
        # Grid yapılandırması
        btn_frame.grid_columnconfigure(0, weight=0, minsize=28)  # İkon
        btn_frame.grid_columnconfigure(1, weight=1)               # Metin
        btn_frame.grid_columnconfigure(2, weight=0)               # Kısayol / Alt menü oku
        
        # Renk belirle
        text_color = self.theme["text"] if enabled else self.theme["text_disabled"]
        icon_color = self.theme["icon"] if enabled else self.theme["text_disabled"]
        
        # İkon
        if icon:
            icon_label = ctk.CTkLabel(
                btn_frame,
                text=icon,
                font=("Segoe UI Emoji", 12),
                text_color=icon_color,
                width=24
            )
            icon_label.grid(row=0, column=0, padx=(4, 0), pady=0, sticky="w")
        else:
            # İkon yoksa boş alan
            spacer = ctk.CTkFrame(btn_frame, width=24, height=1, fg_color="transparent")
            spacer.grid(row=0, column=0, padx=(4, 0))
        
        # Metin
        text_label = ctk.CTkLabel(
            btn_frame,
            text=text,
            font=("Segoe UI", 11),
            text_color=text_color,
            anchor="w"
        )
        text_label.grid(row=0, column=1, padx=(4, 8), pady=0, sticky="ew")
        
        # Kısayol veya alt menü oku
        if submenu:
            arrow_label = ctk.CTkLabel(
                btn_frame,
                text="▶",
                font=("Segoe UI", 8),
                text_color=self.theme["shortcut"],
                width=16
            )
            arrow_label.grid(row=0, column=2, padx=(0, 8), pady=0, sticky="e")
        elif shortcut:
            shortcut_label = ctk.CTkLabel(
                btn_frame,
                text=shortcut,
                font=("Segoe UI", 9),
                text_color=self.theme["shortcut"],
                anchor="e"
            )
            shortcut_label.grid(row=0, column=2, padx=(0, 8), pady=0, sticky="e")
        
        # Hover efektleri
        def on_enter(e):
            if enabled:
                btn_frame.configure(fg_color=self.theme["bg_hover"])
                text_label.configure(text_color=self.theme["text_hover"])
                if icon:
                    icon_label.configure(text_color=self.theme["text_hover"])
                
                # Alt menü varsa göster
                if submenu:
                    self._show_submenu(btn_frame, submenu)
            
            # Tooltip
            if tooltip:
                self._show_tooltip(btn_frame, tooltip)
        
        def on_leave(e):
            if enabled:
                btn_frame.configure(fg_color="transparent")
                text_label.configure(text_color=self.theme["text"])
                if icon:
                    icon_label.configure(text_color=self.theme["icon"])
            
            self._hide_tooltip()
        
        def on_click(e):
            if enabled and command:
                self.close()
                command()
        
        # Eventleri bağla
        widgets = [btn_frame, text_label]
        if icon:
            widgets.append(icon_label)
        if shortcut:
            widgets.append(shortcut_label)
        
        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            if not submenu:  # Alt menü varsa tıklama devre dışı
                widget.bind("<Button-1>", on_click)
    
    def _show_submenu(self, parent_widget, submenu_items: List):
        """Alt menüyü gösterir."""
        # Önceki alt menüyü kapat
        if self._submenu:
            try:
                self._submenu.destroy()
            except:
                pass
        
        # Pozisyon hesapla
        x = parent_widget.winfo_rootx() + parent_widget.winfo_width() - 5
        y = parent_widget.winfo_rooty()
        
        # Yeni alt menü oluştur
        self._submenu = ModernContextMenu(
            self.master,
            submenu_items,
            x,
            y,
            self.theme
        )
    
    def _show_tooltip(self, widget, text: str):
        """Tooltip gösterir."""
        if not text:
            return
        
        def show():
            if self._tooltip_window:
                return
            
            self._tooltip_window = tk.Toplevel(self)
            self._tooltip_window.wm_overrideredirect(True)
            self._tooltip_window.attributes("-topmost", True)
            
            # Tooltip çerçevesi
            frame = tk.Frame(
                self._tooltip_window,
                bg=self.theme["border"],
                padx=1,
                pady=1
            )
            frame.pack()
            
            # Tooltip içeriği
            label = tk.Label(
                frame,
                text=text,
                bg=self.theme["bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 9),
                padx=8,
                pady=4
            )
            label.pack()
            
            # Pozisyon
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            
            # Ekran sınırları kontrolü
            screen_width = self.winfo_screenwidth()
            tooltip_width = label.winfo_reqwidth() + 10
            if x + tooltip_width > screen_width:
                x = screen_width - tooltip_width - 10
            
            self._tooltip_window.geometry(f"+{x}+{y}")
        
        self._tooltip_after_id = self.after(500, show)
    
    def _hide_tooltip(self):
        """Tooltip'i gizler."""
        if self._tooltip_after_id:
            self.after_cancel(self._tooltip_after_id)
            self._tooltip_after_id = None
        
        if self._tooltip_window:
            try:
                self._tooltip_window.destroy()
            except:
                pass
            self._tooltip_window = None
    
    def _position_menu(self, x: int, y: int):
        """Menüyü ekran sınırları içinde konumlandırır."""
        # Pencereyi güncelle (boyut bilgisi için)
        self.update_idletasks()
        
        # Menü boyutları
        menu_width = self.winfo_reqwidth()
        menu_height = self.winfo_reqheight()
        
        # Ekran boyutları
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Sağ kenar kontrolü
        if x + menu_width > screen_width - 10:
            x = screen_width - menu_width - 10
        
        # Alt kenar kontrolü
        if y + menu_height > screen_height - 40:
            y = screen_height - menu_height - 40
        
        # Sol ve üst kenar kontrolü
        x = max(10, x)
        y = max(10, y)
        
        self.geometry(f"+{x}+{y}")
    
    def _animate_open(self):
        """Açılış animasyonu."""
        def fade_in(alpha=0.0):
            if alpha < 0.98:
                try:
                    self.attributes('-alpha', alpha)
                    self.after(15, lambda: fade_in(alpha + 0.12))
                except:
                    pass
            else:
                try:
                    self.attributes('-alpha', 0.98)
                except:
                    pass
        
        fade_in()
    
    def _focus_menu(self):
        """Menüyü odaklar."""
        try:
            self.focus_force()
        except:
            pass
    
    def _bind_global_click(self):
        """Ana pencereye ve tüm üst pencerelere global click handler bağlar."""
        try:
            # Kendi penceremize de bağla (dışarı tıklama için)
            self.bind("<Button-1>", self._on_self_click)
            self.bind("<Button-3>", self._on_self_click)
            
            # Root pencereye global binding
            root = self._master.winfo_toplevel()
            root.bind("<Button-1>", self._on_root_click, add="+")
            root.bind("<Button-3>", self._on_root_click, add="+")
            
            # Belirli bir süre sonra FocusOut kontrolü başlat
            self._focus_check_id = self.after(200, self._check_focus_loop)
        except:
            pass
    
    def _check_focus_loop(self):
        """Periyodik odak kontrolü."""
        if self._is_closed:
            return
        
        try:
            # Menü hala var mı?
            if not self.winfo_exists():
                return
            
            # Fare menü üzerinde mi?
            pointer_x = self.winfo_pointerx()
            pointer_y = self.winfo_pointery()
            
            menu_x = self.winfo_rootx()
            menu_y = self.winfo_rooty()
            menu_width = self.winfo_width()
            menu_height = self.winfo_height()
            
            # Fare menü dışındaysa ve sol tık basılıysa kapat
            # (Bu loop sadece izleme için, asıl kapama _on_root_click'te)
            
            # Odak kontrolü
            if not self.focus_get():
                # Odak başka yere geçti, kısa süre sonra kontrol et
                self.after(100, self._delayed_focus_check)
            else:
                # Döngüye devam
                self._focus_check_id = self.after(200, self._check_focus_loop)
        except:
            pass
    
    def _delayed_focus_check(self):
        """Gecikmeli odak kontrolü."""
        if self._is_closed:
            return
        try:
            if not self.winfo_exists():
                return
            
            # Fare pozisyonunu kontrol et
            if not self._is_pointer_over_menu():
                self.close()
            else:
                # Döngüye devam
                self._focus_check_id = self.after(200, self._check_focus_loop)
        except:
            self.close()
    
    def _is_pointer_over_menu(self) -> bool:
        """Fare imleci menü üzerinde mi kontrol eder."""
        try:
            pointer_x = self.winfo_pointerx()
            pointer_y = self.winfo_pointery()
            
            menu_x = self.winfo_rootx()
            menu_y = self.winfo_rooty()
            menu_width = self.winfo_width()
            menu_height = self.winfo_height()
            
            return (menu_x <= pointer_x <= menu_x + menu_width and
                    menu_y <= pointer_y <= menu_y + menu_height)
        except:
            return False
    
    def _on_self_click(self, event):
        """Menü penceresine tıklandığında."""
        # Tıklama koordinatlarını kontrol et
        # Frame'in padding'i dışına tıklandıysa kapat
        try:
            x, y = event.x, event.y
            width = self.winfo_width()
            height = self.winfo_height()
            
            # Kenar boşlukları (shadow frame)
            margin = 5
            if x < margin or x > width - margin or y < margin or y > height - margin:
                self.close()
        except:
            pass
    
    def _on_root_click(self, event):
        """Root pencereye tıklandığında çağrılır."""
        if self._is_closed:
            return
        
        try:
            # Tıklama koordinatlarını ekran koordinatlarına çevir
            click_x = event.x_root
            click_y = event.y_root
            
            # Menü sınırlarını al
            menu_x = self.winfo_rootx()
            menu_y = self.winfo_rooty()
            menu_width = self.winfo_width()
            menu_height = self.winfo_height()
            
            # Tıklama menü içinde mi?
            if (menu_x <= click_x <= menu_x + menu_width and
                menu_y <= click_y <= menu_y + menu_height):
                return  # Menü içinde, kapama
            
            # Menü dışına tıklandı, kapat
            self.close()
        except:
            self.close()
    
    def close(self):
        """Menüyü kapatır."""
        if self._is_closed:
            return
        
        self._is_closed = True
        
        try:
            # Focus check timer'ı iptal et
            if hasattr(self, '_focus_check_id'):
                try:
                    self.after_cancel(self._focus_check_id)
                except:
                    pass
            
            self._hide_tooltip()
            
            # Alt menüyü kapat
            if self._submenu:
                try:
                    self._submenu.close()
                except:
                    pass
            
            self.destroy()
        except:
            pass


class ModernEditorContextMenu:
    """
    Editör için özelleştirilmiş context menu yardımcı sınıfı.
    Metin düzenleme işlemleri için hazır komutlar içerir.
    """
    
    @staticmethod
    def create_for_editor(
        master,
        x: int,
        y: int,
        theme: Dict[str, str] = None,
        # Callbacks
        on_cut: Callable = None,
        on_copy: Callable = None,
        on_paste: Callable = None,
        on_select_all: Callable = None,
        on_undo: Callable = None,
        on_redo: Callable = None,
        # Ek komutlar
        extra_commands: List = None
    ) -> ModernContextMenu:
        """Editör için standart context menu oluşturur."""
        commands = [
            {"icon": "↩️", "text": "Geri Al", "command": on_undo, "shortcut": "Ctrl+Z", "enabled": on_undo is not None},
            {"icon": "↪️", "text": "Yinele", "command": on_redo, "shortcut": "Ctrl+Y", "enabled": on_redo is not None},
            "-",
            {"icon": "✂️", "text": "Kes", "command": on_cut, "shortcut": "Ctrl+X", "enabled": on_cut is not None},
            {"icon": "📋", "text": "Kopyala", "command": on_copy, "shortcut": "Ctrl+C", "enabled": on_copy is not None},
            {"icon": "📌", "text": "Yapıştır", "command": on_paste, "shortcut": "Ctrl+V", "enabled": on_paste is not None},
            "-",
            {"icon": "☑️", "text": "Tümünü Seç", "command": on_select_all, "shortcut": "Ctrl+A", "enabled": on_select_all is not None},
        ]
        
        if extra_commands:
            commands.append("-")
            commands.extend(extra_commands)
        
        return ModernContextMenu(master, commands, x, y, theme)


class ModernTerminalContextMenu:
    """Terminal için özelleştirilmiş context menu yardımcı sınıfı."""
    
    @staticmethod
    def create(
        master,
        x: int,
        y: int,
        theme: Dict[str, str] = None,
        on_copy: Callable = None,
        on_paste: Callable = None,
        on_select_all: Callable = None,
        on_clear: Callable = None,
        on_open_folder: Callable = None,
        on_save_output: Callable = None
    ) -> ModernContextMenu:
        """Terminal için context menu oluşturur."""
        commands = [
            {"icon": "📋", "text": "Kopyala", "command": on_copy, "shortcut": "Ctrl+C", "enabled": on_copy is not None},
            {"icon": "📌", "text": "Yapıştır", "command": on_paste, "shortcut": "Ctrl+V", "enabled": on_paste is not None},
            "-",
            {"icon": "🔍", "text": "Tümünü Seç", "command": on_select_all, "enabled": on_select_all is not None},
            {"icon": "🗑️", "text": "Temizle", "command": on_clear, "enabled": on_clear is not None},
            "-",
            {"icon": "📂", "text": "Klasörü Aç", "command": on_open_folder, "enabled": on_open_folder is not None},
            {"icon": "💾", "text": "Çıktıyı Kaydet", "command": on_save_output, "enabled": on_save_output is not None},
        ]
        
        return ModernContextMenu(master, commands, x, y, theme)


class ModernFileExplorerContextMenu:
    """Dosya gezgini için özelleştirilmiş context menu yardımcı sınıfı."""
    
    @staticmethod
    def create(
        master,
        x: int,
        y: int,
        theme: Dict[str, str] = None,
        is_file: bool = True,
        on_open: Callable = None,
        on_new_file: Callable = None,
        on_new_folder: Callable = None,
        on_rename: Callable = None,
        on_delete: Callable = None,
        on_copy_path: Callable = None,
        on_show_in_explorer: Callable = None,
        on_refresh: Callable = None
    ) -> ModernContextMenu:
        """Dosya gezgini için context menu oluşturur."""
        commands = [
            {"icon": "📄", "text": "Yeni Dosya", "command": on_new_file, "enabled": on_new_file is not None},
            {"icon": "📁", "text": "Yeni Klasör", "command": on_new_folder, "enabled": on_new_folder is not None},
            "-",
        ]
        
        if is_file:
            commands.append({"icon": "📂", "text": "Aç", "command": on_open, "shortcut": "Enter", "enabled": on_open is not None})
            commands.append("-")
        
        commands.extend([
            {"icon": "✏️", "text": "Yeniden Adlandır", "command": on_rename, "shortcut": "F2", "enabled": on_rename is not None},
            {"icon": "🗑️", "text": "Sil", "command": on_delete, "shortcut": "Del", "enabled": on_delete is not None},
            "-",
            {"icon": "📋", "text": "Yolu Kopyala", "command": on_copy_path, "enabled": on_copy_path is not None},
        ])
        
        if on_show_in_explorer:
            commands.append({"icon": "🔍", "text": "Klasörde Göster", "command": on_show_in_explorer})
        
        if on_refresh:
            commands.append("-")
            commands.append({"icon": "🔄", "text": "Yenile", "command": on_refresh, "shortcut": "F5"})
        
        return ModernContextMenu(master, commands, x, y, theme)
