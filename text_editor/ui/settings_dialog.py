"""
Ayarlar Penceresi
Uygulamanın tüm ayarlarını merkezi bir yerden yönetmek için kullanılır.
Clean Code prensiplerine uygun olarak yeniden düzenlenmiştir.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, colorchooser, font as tkfont
import json
import os
from typing import Dict, Any, Callable, List, Optional, Tuple, Union

# Harici bağımlılıklar
from text_editor.utils.shortcut_manager import ShortcutManager
from text_editor.theme_config import get_available_themes, get_theme
from text_editor.utils.language_manager import LanguageManager

# -----------------------------------------------------------------------------
# Yapılandırma ve Sabitler
# -----------------------------------------------------------------------------

class SettingsConfig:
    """Ayarlar penceresi için sabitleri ve yapılandırma verilerini tutar."""
    
    # Tüm ayarlar listesi (arama optimizasyonu için)
    # Format: "Ekranda Görünen Ad": ("Kategori", "ayar_anahtari", "İkon")
    ALL_SETTINGS = {
        "app_name": {"category": "Genel", "icon": "🌐"},
        "font_family": {"category": "Genel", "icon": "🔤"},
        "font_size": {"category": "Genel", "icon": "📏"},
        "show_line_numbers": {"category": "Editör", "icon": "🔢"},
        "word_wrap": {"category": "Editör", "icon": "↩️"},
        "show_minimap": {"category": "Editör", "icon": "🗺️"},
        "tab_size": {"category": "Editör", "icon": "⏩"},
        "auto_save": {"category": "Editör", "icon": "💾"},
        "auto_save_interval": {"category": "Editör", "icon": "⏱️"},
        "bracket_matching": {"category": "Editör", "icon": "🔗"},
        "syntax_highlighting": {"category": "Editör", "icon": "🎨"},
        "show_status_bar": {"category": "Görünüm", "icon": "📊"},
        "show_file_explorer": {"category": "Görünüm", "icon": "📁"},
        "show_terminal": {"category": "Görünüm", "icon": "💻"},
        "start_fullscreen": {"category": "Görünüm", "icon": "🖥️"},
        "theme": {"category": "Tema", "icon": "🎨"},
        "terminal_type": {"category": "Terminal", "icon": "⌨️"},
        "terminal_font_size": {"category": "Terminal", "icon": "📏"},
        "terminal_history": {"category": "Terminal", "icon": "📜"},
        "performance_mode": {"category": "Gelişmiş", "icon": "⚡"},
        "auto_backup": {"category": "Gelişmiş", "icon": "🔄"},
        "max_file_size": {"category": "Gelişmiş", "icon": "📦"},
        "error_reporting": {"category": "Gelişmiş", "icon": "🐛"},
    }
    
    CATEGORIES = {
        "Genel": "🌐",
        "Editör": "📝",
        "Görünüm": "👁️",
        "Tema": "🎨",
        "Klavye Kısayolları": "⌨️",
        "Terminal": "💻",
        "Gelişmiş": "⚡"
    }

    @staticmethod
    def get_default_settings() -> Dict[str, Any]:
        """Varsayılan ayarları döndürür."""
        return {
            "app_name": "Memati Editör",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "Türkçe",
            "show_line_numbers": True,
            "word_wrap": False,
            "show_minimap": True,
            "tab_size": 4,
            "auto_save": True,
            "auto_save_interval": 30,
            "bracket_matching": True,
            "syntax_highlighting": True,
            "show_status_bar": True,
            "show_file_explorer": True,
            "show_terminal": False,
            "start_fullscreen": False,
            "theme": "Dark",
            "terminal_type": "PowerShell",
            "terminal_font_size": 12,
            "terminal_history": 1000,
            "performance_mode": False,
            "auto_backup": True,
            "max_file_size": 10,
            "error_reporting": True
        }

# -----------------------------------------------------------------------------
# Ana Ayarlar Penceresi Sınıfı
# -----------------------------------------------------------------------------

class SettingsDialog(ctk.CTkToplevel):
    """
    Kapsamlı ayarlar penceresi.
    Tüm uygulama ayarlarını kategorilere ayırarak gösterir ve düzenlemeye olanak tanır.
    """
    
    def __init__(self, parent, current_settings: Dict[str, Any], on_apply: Callable):
        super().__init__(parent)
        
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.original_settings = current_settings.copy()
        self.on_apply_callback = on_apply
        
        # Durum
        self.modified_settings = {}
        self._current_category = None
        self._search_active = False
        # Dil Yöneticisi
        self.lang_manager = LanguageManager.get_instance()
        self.current_lang = current_settings.get("language", "Türkçe")
        self.lang_manager.load_language(self.current_lang)
        
        # Arayüz Kurulumu
        self._setup_window()
        self.category_buttons = {}  # _init_panels'i buraya inline ettik
        self._create_layout()
        # self._init_panels() # Artık gerek yok
        
        # Başlangıç Durumu
        self.show_category("Genel")
        self.apply_theme_integration()

    def _setup_window(self):
        """Pencere özelliklerini ayarlar."""
        self.title(self.lang_manager.get("window_title"))
        self.geometry("1000x750")
        self.minsize(900, 700)
        self.center_window()
        self.transient(self.parent)
        self.grab_set()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_layout(self):
        """Ana düzeni oluşturur."""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sol Panel (Navigasyon)
        self.create_sidebar()
        
        # Sağ Panel (İçerik)
        self.create_content_area()
        
        # Alt Panel (Aksiyonlar)
        self.create_action_bar()

    def _reload_ui(self):
        """Tüm arayüz metinlerini günceller."""
        # 1. Pencere Başlığı
        self.title(self.lang_manager.get("window_title"))
        
        # 2. Sidebar'ı yeniden oluştur (Buton metinleri için)
        for widget in self.sidebar.winfo_children():
            widget.destroy()
    def _reload_ui(self):
        """Tüm arayüz metinlerini günceller."""
        # Mevcut kategoriyi sakla
        current_cat = self._current_category
        
        # Pencere Başlığı
        self.title(self.lang_manager.get("window_title"))
        
        # 1. Ana container içindekileri (Sidebar + Content) temizle
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        # 2. Action Bar'ı (pencereye doğrudan pack edilen frame) temizle
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.main_container:
                widget.destroy()
        
        # 3. Bileşenleri Yeniden Oluştur
        self.category_buttons = {}
        self.create_sidebar()
        self.create_content_area()
        self.create_action_bar()
        
        # 4. Kategoriyi Geri Yükle (Force refresh için önce sıfırla)
        self._current_category = None
        self.show_category(current_cat or "Genel")


    # -------------------------------------------------------------------------
    # Arayüz Oluşturma Metodları
    # -------------------------------------------------------------------------

    def create_sidebar(self):
        """Sol taraftaki kategori panelini oluşturur."""
        self.sidebar = ctk.CTkFrame(self.main_container, width=240, corner_radius=15, fg_color=("gray95", "gray15"))
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        self.sidebar.pack_propagate(False)
        
        # Başlık Bölümü
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text=self.lang_manager.get("panel_title"),
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")
        
        # Değişiklik Badge
        self.changes_badge = ctk.CTkLabel(
            header_frame, text="", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#ff6b6b", "#cc5555"), corner_radius=10, width=24, height=24
        )
        # Başlangıçta gizli
        
        # Arama
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkEntry(
            search_frame,
            placeholder_text=self.lang_manager.get("search_placeholder"),
            textvariable=self.search_var,
            height=32,
            corner_radius=8
        ).pack(fill="x")
        
        # Ayırıcı
        ctk.CTkFrame(self.sidebar, height=2, fg_color=("gray70", "gray30")).pack(fill="x", padx=10, pady=(0, 10))
        
        # Kategorileri Listele
        for category, icon in SettingsConfig.CATEGORIES.items():
            display_name = self.lang_manager.get(f"categories.{category}", category)
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {display_name}",
                command=lambda c=category: self.show_category(c),
                anchor="w",
                height=45,
                corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.category_buttons[category] = btn
            
        # Alt Bilgi
        version_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        version_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            version_frame, text=self.lang_manager.get("messages.version_text"),
            font=ctk.CTkFont(size=10), text_color=("gray50", "gray60")
        ).pack()

    def create_content_area(self):
        """Sağ taraftaki içerik panelini oluşturur."""
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Başlık ve Açıklama
        self.content_title = ctk.CTkLabel(
            self.content_frame, text="", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.content_title.pack(pady=(25, 15), padx=25, anchor="w")
        
        # Ayırıcı
        ctk.CTkFrame(self.content_frame, height=2, fg_color=("gray70", "gray30")).pack(fill="x", padx=20, pady=(0, 15))
        
        # Kaydırılabilir Alan
        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_action_bar(self):
        """Alt kısımdaki buton panelini oluşturur."""
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=10, pady=(0, 10))
        
        right_grp = ctk.CTkFrame(bar, fg_color="transparent")
        right_grp.pack(side="right")
        
        ctk.CTkButton(
            right_grp, text=self.lang_manager.get("buttons.reset"), command=self.reset_to_defaults,
            width=140, height=40, corner_radius=20, fg_color="transparent",
            border_width=1, border_color=("gray70", "gray50"), text_color=("gray40", "gray60"),
            hover_color=("gray90", "gray20")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            right_grp, text=self.lang_manager.get("buttons.cancel"), command=self.cancel,
            width=120, height=40, corner_radius=20, fg_color=("gray85", "gray25"),
            text_color=("gray10", "gray90"), hover_color=("gray75", "gray35")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            right_grp, text=self.lang_manager.get("buttons.apply"), command=self.apply_settings,
            width=140, height=40, corner_radius=20, font=ctk.CTkFont(weight="bold"),
            fg_color=("#4CAF50", "#2ecc71"), hover_color=("#45a049", "#27ae60")
        ).pack(side="left", padx=10)

    # -------------------------------------------------------------------------
    # Ayar Bileşenleri İçin Yardımcı Metodlar ("Oluşturucu" Mantığı)
    # -------------------------------------------------------------------------
    
    def _create_row_frame(self, label_text: str, description: str = "") -> ctk.CTkFrame:
        """Standart bir ayar satırı çerçevesi oluşturur."""
        row = ctk.CTkFrame(self.scrollable_frame, fg_color=("gray95", "gray20"), corner_radius=8)
        row.pack(fill="x", pady=8, padx=10)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=15, pady=12)
        
        ctk.CTkLabel(left, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(anchor="w")
        if description:
            ctk.CTkLabel(
                left, text=description, font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60"), anchor="w", wraplength=350, justify="left"
            ).pack(anchor="w", pady=(2, 0))
            
        right = ctk.CTkFrame(row, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=15, pady=12)
        
        return right

    def _get_setting_info(self, key: str) -> Tuple[str, str]:
        """Ayar anahtarından etiket ve açıklama döndürür."""
        label = self.lang_manager.get(f"settings.{key}.label", key)
        desc = self.lang_manager.get(f"settings.{key}.desc", "")
        return label, desc

    def add_switch(self, key: str):
        """Boolean ayar için switch ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        var = tk.BooleanVar(value=self.current_settings.get(key, False))
        ctk.CTkSwitch(
            container, text="", variable=var,
            command=lambda: self.update_setting(key, var.get())
        ).pack(side="right")

    def add_combo(self, key: str, values: List[str], width: int = 200, is_int: bool = False):
        """Seçenek listesi için ComboBox ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key)
        var = tk.StringVar(value=str(current_val))
        
        def callback(choice):
            val = int(choice) if is_int else choice
            self.update_setting(key, val)

        ctk.CTkComboBox(
            container, values=[str(v) for v in values], variable=var,
            width=width, command=callback
        ).pack(side="right")

    def add_slider(self, key: str, from_: int, to: int, steps: int = None, show_value: bool = True):
        """Sayısal değerler için Slider ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, from_)
        var = tk.IntVar(value=current_val)
        
        if show_value:
            ctk.CTkLabel(
                container, textvariable=var, width=40,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right")

        if steps is None:
            steps = to - from_ 

        ctk.CTkSlider(
            container, from_=from_, to=to, number_of_steps=steps,
            variable=var, width=150,
            command=lambda val: self.update_setting(key, int(val))
        ).pack(side="right", padx=(0, 10 if show_value else 0))

    def add_entry(self, key: str, placeholder: str = "", width: int = 200, readonly: bool = False):
        """Metin girişi ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        entry = ctk.CTkEntry(container, width=width, placeholder_text=placeholder)
        entry.insert(0, str(self.current_settings.get(key, "")))
        
        if readonly:
            entry.configure(state="readonly")
        else:
            # Entry değiştiğinde tetiklemek için trace veya bind kullanılabilir
            # Basit olması için FocusOut kullanacağız
            entry.bind("<FocusOut>", lambda e: self.update_setting(key, entry.get()))
            
        entry.pack(side="right")

    # -------------------------------------------------------------------------
    # Panel İçerik Oluşturucuları
    # -------------------------------------------------------------------------

    def show_category(self, category: str):
        """Seçilen kategoriyi gösterir."""
        if self._current_category == category and not self._search_active:
            return

        self._search_active = False
        self._current_category = category
        
        # Sidebar butonunu güncelle
        for btn in self.category_buttons.values():
            btn.configure(fg_color="transparent")
        if category in self.category_buttons:
            self.category_buttons[category].configure(fg_color=("gray75", "gray28"))
        
        # İçerik Başlığı
        icon = SettingsConfig.CATEGORIES.get(category, "")
        display_name = self.lang_manager.get(f"categories.{category}", category)
        self.content_title.configure(text=f"{icon} {display_name}")
        
        # İçeriği Temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Kategoriye Göre İçerik Oluştur
        if category == "Genel":
            self.build_general_panel()
        elif category == "Editör":
            self.build_editor_panel()
        elif category == "Görünüm":
            self.build_view_panel()
        elif category == "Tema":
            self.build_theme_panel()
        elif category == "Klavye Kısayolları":
            self.build_shortcuts_panel()
        elif category == "Terminal":
            self.build_terminal_panel()
        elif category == "Gelişmiş":
            self.build_advanced_panel()

    def build_general_panel(self):
        # Uygulama Adı
        self.add_entry("app_name")
        
        # Dil Seçimi
        
        def on_lang_change(choice):
            self.update_setting("language", choice)
            self.lang_manager.load_language(choice)
            # Tüm arayüzü yeniden çiz
            self._reload_ui()
            
        lang_var = tk.StringVar(value=self.current_settings.get("language", "Türkçe"))
        
        label, desc = self._get_setting_info("language")
        container = self._create_row_frame(label, desc)
        ctk.CTkComboBox(
            container, values=["Türkçe", "English"], variable=lang_var,
            width=200, command=on_lang_change
        ).pack(side="right")

        # Yazı Tipi
        font_families = list(tkfont.families())
        font_families.sort()
        self.add_combo("font_family", font_families)
        
        # Yazı Boyutu (Özel kontrol butonlu yapı)
        label, desc = self._get_setting_info("font_size")
        container = self._create_row_frame(label, desc)
        
        font_size_var = tk.IntVar(value=self.current_settings.get("font_size", 14))
        
        def change_font(delta):
            new_val = font_size_var.get() + delta
            if 8 <= new_val <= 32:
                font_size_var.set(new_val)
                self.update_setting("font_size", new_val)
                
        ctk.CTkButton(container, text="+", width=30, command=lambda: change_font(1)).pack(side="right", padx=(5, 0))
        ctk.CTkLabel(container, textvariable=font_size_var, width=30, font=ctk.CTkFont(weight="bold")).pack(side="right")
        ctk.CTkButton(container, text="-", width=30, command=lambda: change_font(-1)).pack(side="right")

    def build_editor_panel(self):
        self.add_switch("show_line_numbers")
        self.add_switch("word_wrap")
        self.add_switch("show_minimap")
        self.add_combo("tab_size", ["2", "4", "8"], width=100, is_int=True)
        self.add_switch("auto_save")
        self.add_slider("auto_save_interval", 10, 120, steps=11)
        self.add_switch("bracket_matching")
        self.add_switch("syntax_highlighting")

    def build_view_panel(self):
        self.add_switch("show_status_bar")
        self.add_switch("show_file_explorer")
        self.add_switch("show_terminal")
        self.add_switch("start_fullscreen")

    def build_terminal_panel(self):
        shells = ["PowerShell", "Command Prompt", "Bash"] if os.name == "nt" else ["Bash", "Sh", "Zsh"]
        self.add_combo("terminal_type", shells)
        self.add_slider("terminal_font_size", 8, 24, steps=16)
        self.add_slider("terminal_history", 100, 5000, steps=49)

    def build_advanced_panel(self):
        self.add_switch("performance_mode")
        self.add_switch("auto_backup")
        # Max dosya boyutu (Entry + Label)
        label, desc = self._get_setting_info("max_file_size")
        container = self._create_row_frame(label, desc)
        ctk.CTkLabel(container, text="MB", font=ctk.CTkFont(size=12)).pack(side="right", padx=(5, 0))
        
        size_var = tk.IntVar(value=self.current_settings.get("max_file_size", 10))
        entry = ctk.CTkEntry(container, textvariable=size_var, width=60)
        entry.pack(side="right")
        entry.bind("<FocusOut>", lambda e: self.update_setting("max_file_size", size_var.get()))
        
        self.add_switch("error_reporting")
        
        # İçe/Dışa Aktar Butonları
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color=("gray70", "gray30")).pack(fill="x", pady=20)
        
        ctk.CTkButton(
            self.scrollable_frame, text=self.lang_manager.get("buttons.export"), command=self.export_settings,
            height=35, corner_radius=8
        ).pack(pady=(20, 5), fill="x")
        
        ctk.CTkButton(
            self.scrollable_frame, text=self.lang_manager.get("buttons.import"), command=self.import_settings,
            height=35, corner_radius=8, fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40")
        ).pack(pady=5, fill="x")

    def build_theme_panel(self):
        """Tema seçimi için özel ızgara yapısı."""
        themes = get_available_themes()
        current_theme = self.current_settings.get("theme", "Dark")
        self.theme_var = tk.StringVar(value=current_theme)
        self.theme_cards = {}
        
        label, desc = self._get_setting_info("theme_select")
        
        header = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text=label, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(header, text=desc, font=ctk.CTkFont(size=12), text_color="gray60", anchor="w").pack(anchor="w")
        
        grid = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        for i, theme_name in enumerate(themes):
            self._create_theme_card(grid, theme_name, i)

    def _create_theme_card(self, parent, theme_name, index):
        """Tema kartı oluşturucu."""
        theme_data = get_theme(theme_name)
        is_selected = (theme_name == self.theme_var.get())
        
        border_color = theme_data["accent_color"] if is_selected else ("gray40" if theme_data.get("type") == "Dark" else "gray60")
        
        card = ctk.CTkFrame(
            parent, fg_color=theme_data["bg"], corner_radius=12,
            border_width=3 if is_selected else 1, border_color=border_color, cursor="hand2"
        )
        card.grid(row=index//3, column=index%3, padx=12, pady=12, sticky="nsew")
        
        self.theme_cards[theme_name] = card
        
        # Etkileşim
        def on_click(_=None): self._select_theme(theme_name)
        card.bind("<Button-1>", on_click)
        
        # Önizleme
        preview = ctk.CTkFrame(card, fg_color="transparent", height=90)
        preview.pack(fill="x", padx=10, pady=10)
        preview.pack_propagate(False)
        preview.bind("<Button-1>", on_click)
        
        code_view = ctk.CTkFrame(preview, fg_color=theme_data["editor_bg"], corner_radius=6)
        code_view.pack(fill="both", expand=True)
        code_view.bind("<Button-1>", on_click)
        
        # Kod Örnekleri
        ctk.CTkLabel(code_view, text=f"def {theme_name.lower()}():", text_color=theme_data["fg"],
                     font=("Consolas", 10), anchor="w").pack(padx=8, pady=(8,0), fill="x")
        ctk.CTkLabel(code_view, text='    return "UI"', text_color=theme_data.get("string", "#f1fa8c"),
                     font=("Consolas", 10), anchor="w").pack(padx=8, pady=(2,8), fill="x")
                     
        # Footer
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=(0, 12))
        footer.bind("<Button-1>", on_click)
        
        ctk.CTkLabel(footer, text=theme_name, font=ctk.CTkFont(weight="bold"), text_color=theme_data["fg"]).pack(side="left")
        
        if is_selected:
            lbl = ctk.CTkLabel(footer, text="✅", text_color=theme_data["accent_color"])
            lbl.pack(side="right")
            card.check_icon = lbl

    def _select_theme(self, theme_name):
        """Tema seçim lojiği."""
        prev = self.theme_var.get()
        if prev == theme_name: return
        
        self.theme_var.set(theme_name)
        self.update_setting("theme", theme_name)
        
        if hasattr(self.parent, 'apply_theme'):
            self.parent.apply_theme(theme_name)
            
        # Görsel güncelleme
        self.show_category("Tema") # Yeniden çizmek en temizi

    def build_shortcuts_panel(self):
        """Klavye kısayolları paneli."""
        manager = ShortcutManager.get_instance()
        shortcuts = manager.shortcuts
        metadata = manager.SHORTCUT_METADATA
        
        grouped = {}
        for aid, seq in shortcuts.items():
            meta = metadata.get(aid, {"category": "Diğer", "label": aid})
            cat = meta["category"]
            if cat not in grouped: grouped[cat] = []
            grouped[cat].append((aid, meta["label"], seq))
            
        for cat, items in grouped.items():
            ctk.CTkLabel(self.scrollable_frame, text=cat, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(15, 5))
            ctk.CTkFrame(self.scrollable_frame, height=1, fg_color=("gray70", "gray30")).pack(fill="x", pady=(0, 10))
            
            for aid, lbl, seq in items:
                frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                frame.pack(fill="x", pady=3)
                
                ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=12)).pack(side="left")
                
                display = manager.get_display_string(seq) or "Yok"
                ctk.CTkButton(
                    frame, text=display, font=("Consolas", 12, "bold"),
                    fg_color=("gray90", "gray15"), text_color=("gray10", "gray90"),
                    width=120, height=28, border_width=1, border_color=("gray70", "gray40"),
                    command=lambda i=aid: self.start_shortcut_recording(i)
                ).pack(side="right")
                
        # Sıfırlama Butonu
        ctk.CTkButton(
            self.scrollable_frame, text=self.lang_manager.get("buttons.reset_shortcuts"), fg_color="transparent",
            border_width=1, border_color="#dc3545", text_color="#dc3545",
            hover_color=("#fee2e2", "#5c0000"), width=160,
            command=self._reset_shortcuts
        ).pack(pady=30, anchor="e")

    def start_shortcut_recording(self, action_id):
        """Kısayol atama diyaloğu."""
        # Clean Code: Bu mantığı ayrı bir sınıfa veya metoda almak daha iyi olurdu ama
        # dosya bütünlüğü için burada tutuyoruz, ancak kısaltılmış ve düzenlenmiş haliyle.
        
        manager = ShortcutManager.get_instance()
        current_seq = manager.get(action_id)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Kısayol Ata")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Ortalama
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()//2) - 200
        y = self.winfo_y() + (self.winfo_height()//2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="Yeni Kısayol Tuşlayın", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="İptal için ESC", text_color="gray").pack()
        
        display_lbl = ctk.CTkLabel(
            dialog, text=manager.get_display_string(current_seq),
            font=("Courier New", 24, "bold"), width=200, height=50,
            fg_color=("gray90", "gray20"), corner_radius=8
        )
        display_lbl.pack(pady=20)
        
        def on_key(event):
            # Modifier kontrolü
            keys = []
            if event.state & 0x4: keys.append("Control")
            if event.state & 0x20000 or event.state & 0x20: keys.append("Alt")
            if event.state & 0x1: keys.append("Shift")
            
            if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
                if event.keysym == "Escape": 
                    dialog.destroy()
                    return
                keys.append(event.keysym)
            
            if not keys or (len(keys) == 1 and keys[0] in ("Control", "Alt", "Shift")):
                display_lbl.configure(text=" + ".join(keys) + " ...")
                return

            # Sequence oluştur
            parts = [k for k in ["Control", "Alt", "Shift"] if k in keys]
            if keys[-1] not in parts: parts.append(keys[-1])
            
            sequence = f"<{'-'.join(parts)}>"
            display_lbl.configure(text=manager.get_display_string(sequence))
            
            # Kaydet Butonunu Aktif Et
            save_btn.configure(state="normal", command=lambda: self._apply_shortcut_change(action_id, sequence, dialog))

        save_btn = ctk.CTkButton(dialog, text="Kaydet", state="disabled", width=100)
        save_btn.pack(side="left", padx=20, expand=True)
        ctk.CTkButton(dialog, text="İptal", command=dialog.destroy, 
                      fg_color="transparent", border_width=1, width=100).pack(side="right", padx=20, expand=True)
        
        dialog.bind("<Key>", on_key)
        dialog.focus_set()

    def _apply_shortcut_change(self, action_id, sequence, dialog):
        ShortcutManager.get_instance().set(action_id, sequence)
        dialog.destroy()
        self.show_category("Klavye Kısayolları")

    def _reset_shortcuts(self):
        ShortcutManager.get_instance().reset_to_defaults()
        self.show_category("Klavye Kısayolları")

    # -------------------------------------------------------------------------
    # Çekirdek Mantık
    # -------------------------------------------------------------------------

    def _on_search_change(self, *args):
        query = self.search_var.get().lower().strip()
        if not query:
            self.show_category(self._current_category or "Genel")
            return
            
        self._search_active = True
        self.content_title.configure(text=f"🔍 {query}")
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        
        results = []
        for key, data in SettingsConfig.ALL_SETTINGS.items():
            cat = data["category"]
            icon = data["icon"]
            
            # Dinamik çevirileri al
            name_localized = self.lang_manager.get(f"settings.{key}.label", key)
            cat_localized = self.lang_manager.get(f"categories.{cat}", cat)
            
            if (query in name_localized.lower() or 
                query in cat_localized.lower() or 
                query in key.lower()):
                
                val = self.current_settings.get(key, "—")
                results.append((name_localized, cat, cat_localized, key, icon, val))
                
        # Sonuç başlığı
        count_text = self.lang_manager.get("messages.search_results", "").format(count=len(results))
        ctk.CTkLabel(self.scrollable_frame, text=count_text, text_color="gray").pack(anchor="w", pady=(0, 10))
        
        for name, cat_key, cat_name, key, icon, val in results:
            card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, fg_color=("gray95", "gray20"))
            card.pack(fill="x", pady=6)
            
            h = ctk.CTkFrame(card, fg_color="transparent")
            h.pack(fill="x", padx=15, pady=10)
            ctk.CTkLabel(h, text=f"{icon} {name}", font=ctk.CTkFont(weight="bold")).pack(side="left")
            
            # Değer gösterimi
            display_val = str(val)
            if isinstance(val, bool):
                display_val = "Aktif" if val else "Pasif" # Basit çeviri, geliştirilebilir
            
            ctk.CTkLabel(h, text=f"= {display_val[:30]}", text_color="gray").pack(side="right")
            
            # Kategoriye git butonu
            goto_text = self.lang_manager.get("messages.goto_category", "").format(category=cat_name)
            ctk.CTkButton(
                card, text=goto_text, fg_color="transparent",
                hover_color=("gray80", "gray25"), anchor="w", height=30,
                command=lambda c=cat_key: self._goto_category(c)
            ).pack(fill="x", padx=10, pady=(0, 10))
            
        if not results:
            no_res = self.lang_manager.get("messages.no_results", "Sonuç bulunamadı")
            ctk.CTkLabel(self.scrollable_frame, text=f"🔍\n{no_res}", font=ctk.CTkFont(size=16)).pack(pady=50)

    def _goto_category(self, category):
        self.search_var.set("")
        self.show_category(category)

    def update_setting(self, key: str, value: Any):
        """Ayarı günceller ve değişiklik takibi yapar."""
        original_value = self.original_settings.get(key)
        
        if value == original_value:
            self.modified_settings.pop(key, None)
        else:
            self.modified_settings[key] = value
            
        self.current_settings[key] = value
        self._update_changes_badge()

    def _update_changes_badge(self):
        count = 0
        for k, v in self.modified_settings.items():
            if v != self.original_settings.get(k):
                count += 1
                
        if count > 0:
            color = "#e74c3c" if count >= 5 else ("#f39c12" if count >= 3 else "#27ae60")
            self.changes_badge.configure(text=str(count), fg_color=color)
            self.changes_badge.pack(side="right", padx=(5, 0))
            suffix = self.lang_manager.get("messages.changes_title_suffix", "").format(count=count)
            self.title(f"{self.lang_manager.get('window_title')} {suffix}")
        else:
            self.changes_badge.pack_forget()
            self.title(self.lang_manager.get("window_title"))

    def apply_settings(self):
        if self.modified_settings:
            self.current_settings.update(self.modified_settings)
            if self.on_apply_callback:
                self.on_apply_callback(self.current_settings)
            self.save_settings()
        self.destroy()

    def save_settings(self):
        path = os.path.join(os.path.expanduser("~"), ".memati_editor", "settings.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.current_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Hata: {e}")

    def load_settings(self) -> Dict[str, Any]:
        path = os.path.join(os.path.expanduser("~"), ".memati_editor", "settings.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return SettingsConfig.get_default_settings()

    def export_settings(self):
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.current_settings, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Başarılı", "Ayarlar dışa aktarıldı.", parent=self)
            except Exception as e:
                messagebox.showerror("Hata", str(e), parent=self)

    def import_settings(self):
        from tkinter import filedialog, messagebox
        path = filedialog.askopenfilename(parent=self, filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.current_settings.update(data)
                self.modified_settings = self.current_settings.copy()
                self.show_category(self._current_category or "Genel") # Refresh
                messagebox.showinfo("Başarılı", "Ayarlar içe aktarıldı.", parent=self)
            except Exception as e:
                messagebox.showerror("Hata", str(e), parent=self)

    def reset_to_defaults(self):
        from tkinter import messagebox
        if messagebox.askyesno("Sıfırla", "Tüm ayarlar varsayılana dönecek?", parent=self):
            self.current_settings = SettingsConfig.get_default_settings()
            self.modified_settings = self.current_settings.copy()
            self.show_category(self._current_category or "Genel")

    def cancel(self):
        self.destroy()

    def apply_theme_integration(self):
        pass # Parent handles this
