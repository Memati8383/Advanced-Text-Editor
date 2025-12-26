"""
Ayarlar Penceresi (Settings Dialog)

Uygulamanın tüm ayarlarını merkezi bir yerden yönetmek için kullanılır.
Clean Code prensiplerine uygun olarak yapılandırılmıştır.

Modül Yapısı:
    - SettingsConstants: Tüm sabitler ve magic number'lar
    - SettingsConfig: Kategori ve varsayılan ayar yapılandırmaları
    - SettingsFileManager: Dosya okuma/yazma işlemleri
    - SettingsUIBuilder: UI bileşenlerinin oluşturulması
    - SettingsDialog: Ana pencere sınıfı

Author: Memati Editör Team
Version: 2.0.0
"""

from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, font as tkfont
import json
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List, Optional, Tuple, Union, Final
from pathlib import Path
from enum import Enum

# Harici bağımlılıklar
from text_editor.utils.shortcut_manager import ShortcutManager
from text_editor.theme_config import get_available_themes, get_theme
from text_editor.utils.language_manager import LanguageManager

# Panel Imports
from text_editor.ui.settings.general_panel import GeneralSettingsPanel
from text_editor.ui.settings.editor_panel import EditorSettingsPanel
from text_editor.ui.settings.view_panel import ViewSettingsPanel
from text_editor.ui.settings.theme_panel import ThemeSettingsPanel
from text_editor.ui.settings.shortcuts_panel import ShortcutsSettingsPanel
from text_editor.ui.settings.terminal_panel import TerminalSettingsPanel
from text_editor.ui.settings.advanced_panel import AdvancedSettingsPanel

# Logger ayarı
logger = logging.getLogger(__name__)


# =============================================================================
# Sabitler ve Enum Tanımları
# =============================================================================

class SettingsConstants:
    """
    Tüm sabitler ve magic number'ları tek bir yerde toplar.
    Bu sınıf, kodun okunabilirliğini ve bakımını kolaylaştırır.
    """
    
    # Pencere Boyutları
    WINDOW_WIDTH: Final[int] = 1050
    WINDOW_HEIGHT: Final[int] = 780
    WINDOW_MIN_WIDTH: Final[int] = 950
    WINDOW_MIN_HEIGHT: Final[int] = 720
    
    # Sidebar Boyutları
    SIDEBAR_WIDTH: Final[int] = 260
    SIDEBAR_CORNER_RADIUS: Final[int] = 16
    SIDEBAR_BORDER_WIDTH: Final[int] = 1
    
    # Buton Boyutları
    CATEGORY_BUTTON_HEIGHT: Final[int] = 48
    CATEGORY_BUTTON_CORNER_RADIUS: Final[int] = 12
    ACTION_BUTTON_HEIGHT: Final[int] = 42
    ACTION_BUTTON_CORNER_RADIUS: Final[int] = 21
    
    # Animasyon Süreleri (ms)
    FADE_IN_DURATION: Final[int] = 15
    FADE_IN_STEP: Final[float] = 0.08
    ANIMATION_DELAY: Final[int] = 50
    
    # Font Boyutları
    TITLE_FONT_SIZE: Final[int] = 28
    HEADER_FONT_SIZE: Final[int] = 24
    SUBHEADER_FONT_SIZE: Final[int] = 14
    BODY_FONT_SIZE: Final[int] = 13
    SMALL_FONT_SIZE: Final[int] = 12
    FOOTER_FONT_SIZE: Final[int] = 11
    
    # Arama
    SEARCH_ENTRY_HEIGHT: Final[int] = 38
    SEARCH_CORNER_RADIUS: Final[int] = 10
    SEARCH_BORDER_WIDTH: Final[int] = 2
    SEARCH_DEBOUNCE_MS: Final[int] = 300
    
    # Değişiklik Badge Renkleri
    BADGE_COLOR_LOW: Final[str] = "#27ae60"      # 1-2 değişiklik
    BADGE_COLOR_MEDIUM: Final[str] = "#f39c12"   # 3-4 değişiklik
    BADGE_COLOR_HIGH: Final[str] = "#e74c3c"     # 5+ değişiklik
    BADGE_THRESHOLD_MEDIUM: Final[int] = 3
    BADGE_THRESHOLD_HIGH: Final[int] = 5
    
    # Aksiyon Buton Renkleri
    APPLY_BUTTON_FG: Final[Tuple[str, str]] = ("#2ecc71", "#27ae60")
    APPLY_BUTTON_HOVER: Final[Tuple[str, str]] = ("#27ae60", "#1e8449")
    CANCEL_BUTTON_FG: Final[Tuple[str, str]] = ("gray88", "gray28")
    CANCEL_BUTTON_HOVER: Final[Tuple[str, str]] = ("gray80", "gray35")
    
    # Varsayılan Renk Değerleri
    DEFAULT_ACCENT_COLOR: Final[str] = "#0098ff"
    DEFAULT_BG_COLOR: Final[str] = "#2b2b2b"
    
    # Dosya Yolu
    SETTINGS_FOLDER_NAME: Final[str] = ".memati_editor"
    SETTINGS_FILE_NAME: Final[str] = "settings.json"


class CategoryType(Enum):
    """Ayar kategorileri için tip-güvenli enum."""
    GENERAL = "Genel"
    EDITOR = "Editör"
    VIEW = "Görünüm"
    THEME = "Tema"
    SHORTCUTS = "Klavye Kısayolları"
    TERMINAL = "Terminal"
    ADVANCED = "Gelişmiş"


# =============================================================================
# Yapılandırma Sınıfları
# =============================================================================

@dataclass(frozen=True)
class SettingInfo:
    """Tek bir ayar hakkında meta bilgi."""
    category: str
    icon: str


class SettingsConfig:
    """
    Ayarlar penceresi için kategori ve varsayılan ayar yapılandırmaları.
    
    Bu sınıf, tüm ayar metadatasını ve varsayılan değerleri merkezi bir
    noktada tutar.
    """
    
    # Tüm ayarlar listesi (arama optimizasyonu için)
    ALL_SETTINGS: Final[Dict[str, SettingInfo]] = {
        "app_name": SettingInfo("Genel", "🌐"),
        "font_family": SettingInfo("Genel", "🔤"),
        "font_size": SettingInfo("Genel", "📏"),
        "language": SettingInfo("Genel", "🗣️"),
        "show_line_numbers": SettingInfo("Editör", "🔢"),
        "word_wrap": SettingInfo("Editör", "↩️"),
        "show_minimap": SettingInfo("Editör", "🗺️"),
        "tab_size": SettingInfo("Editör", "⏩"),
        "auto_save": SettingInfo("Editör", "💾"),
        "auto_save_interval": SettingInfo("Editör", "⏱️"),
        "bracket_matching": SettingInfo("Editör", "🔗"),
        "syntax_highlighting": SettingInfo("Editör", "🎨"),
        "highlight_current_line": SettingInfo("Editör", "📍"),
        "show_whitespace": SettingInfo("Editör", "⬜"),
        "auto_indent": SettingInfo("Editör", "📐"),
        "show_status_bar": SettingInfo("Görünüm", "📊"),
        "show_file_explorer": SettingInfo("Görünüm", "📁"),
        "show_terminal": SettingInfo("Görünüm", "💻"),
        "start_fullscreen": SettingInfo("Görünüm", "🖥️"),
        "window_opacity": SettingInfo("Görünüm", "👁️"),
        "sidebar_width": SettingInfo("Görünüm", "↔️"),
        "theme": SettingInfo("Tema", "🎨"),
        "accent_color": SettingInfo("Tema", "🌈"),
        "terminal_type": SettingInfo("Terminal", "⌨️"),
        "terminal_font_size": SettingInfo("Terminal", "📏"),
        "terminal_history": SettingInfo("Terminal", "📜"),
        "terminal_cursor_blink": SettingInfo("Terminal", "▌"),
        "performance_mode": SettingInfo("Gelişmiş", "⚡"),
        "auto_backup": SettingInfo("Gelişmiş", "🔄"),
        "max_file_size": SettingInfo("Gelişmiş", "📦"),
        "error_reporting": SettingInfo("Gelişmiş", "🐛"),
        "cache_size": SettingInfo("Gelişmiş", "💿"),
        "log_level": SettingInfo("Gelişmiş", "📝"),
    }
    
    CATEGORIES: Final[Dict[str, str]] = {
        "Genel": "🌐",
        "Editör": "📝",
        "Görünüm": "👁️",
        "Tema": "🎨",
        "Klavye Kısayolları": "⌨️",
        "Terminal": "💻",
        "Gelişmiş": "⚡"
    }
    
    CATEGORY_DESCRIPTIONS: Final[Dict[str, str]] = {
        "Genel": "Uygulama adı, dil ve yazı tipi ayarları",
        "Editör": "Kod düzenleme deneyiminizi özelleştirin",
        "Görünüm": "Arayüz görünürlük ve düzen ayarları",
        "Tema": "Renk şemaları ve görsel tema seçenekleri",
        "Klavye Kısayolları": "Kısayol tuşlarını özelleştirin",
        "Terminal": "Entegre terminal yapılandırması",
        "Gelişmiş": "Performans ve sistem ayarları"
    }

    @staticmethod
    def get_default_settings() -> Dict[str, Any]:
        """
        Varsayılan ayarları döndürür.
        
        Returns:
            Dict[str, Any]: Tüm varsayılan ayarları içeren sözlük
        """
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
            "highlight_current_line": True,
            "show_whitespace": False,
            "auto_indent": True,
            "show_status_bar": True,
            "show_file_explorer": True,
            "show_terminal": False,
            "start_fullscreen": False,
            "window_opacity": 100,
            "sidebar_width": 250,
            "theme": "Dark",
            "accent_color": SettingsConstants.DEFAULT_ACCENT_COLOR,
            "terminal_type": "PowerShell",
            "terminal_font_size": 12,
            "terminal_history": 1000,
            "terminal_cursor_blink": True,
            "performance_mode": False,
            "auto_backup": True,
            "max_file_size": 10,
            "error_reporting": True,
            "cache_size": 100,
            "log_level": "INFO"
        }


# =============================================================================
# Dosya Yönetimi Sınıfı
# =============================================================================

class SettingsFileManager:
    """
    Ayarların dosya sisteminden okuma/yazma işlemlerini yönetir.
    
    Single Responsibility: Sadece dosya I/O işlemleri ile ilgilenir.
    """
    
    @staticmethod
    def _get_settings_path() -> Path:
        """Ayar dosyasının yolunu döndürür."""
        home_dir = Path.home()
        return home_dir / SettingsConstants.SETTINGS_FOLDER_NAME / SettingsConstants.SETTINGS_FILE_NAME
    
    @classmethod
    def save(cls, settings: Dict[str, Any]) -> bool:
        """
        Ayarları dosyaya kaydeder.
        
        Args:
            settings: Kaydedilecek ayarlar sözlüğü
            
        Returns:
            bool: Başarılı ise True, aksi halde False
        """
        path = cls._get_settings_path()
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)
            
            logger.info(f"Ayarlar başarıyla kaydedildi: {path}")
            return True
            
        except PermissionError:
            logger.error(f"Ayar dosyası yazılamadı - izin hatası: {path}")
            return False
        except IOError as e:
            logger.error(f"Ayar dosyası yazma hatası: {e}")
            return False
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """
        Ayarları dosyadan yükler.
        
        Returns:
            Dict[str, Any]: Yüklenen ayarlar veya varsayılanlar
        """
        path = cls._get_settings_path()
        
        if not path.exists():
            logger.info("Ayar dosyası bulunamadı, varsayılanlar kullanılıyor")
            return SettingsConfig.get_default_settings()
        
        try:
            with open(path, "r", encoding="utf-8") as file:
                loaded_settings = json.load(file)
            
            # Eksik anahtarları varsayılanlarla tamamla
            defaults = SettingsConfig.get_default_settings()
            for key, value in defaults.items():
                if key not in loaded_settings:
                    loaded_settings[key] = value
            
            logger.info(f"Ayarlar başarıyla yüklendi: {path}")
            return loaded_settings
            
        except json.JSONDecodeError as e:
            logger.error(f"Ayar dosyası JSON formatı hatalı: {e}")
            return SettingsConfig.get_default_settings()
        except IOError as e:
            logger.error(f"Ayar dosyası okuma hatası: {e}")
            return SettingsConfig.get_default_settings()
    
    @classmethod
    def export(cls, settings: Dict[str, Any], filepath: str) -> bool:
        """
        Ayarları belirtilen dosyaya dışa aktarır.
        
        Args:
            settings: Dışa aktarılacak ayarlar
            filepath: Hedef dosya yolu
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)
            logger.info(f"Ayarlar dışa aktarıldı: {filepath}")
            return True
        except IOError as e:
            logger.error(f"Dışa aktarma hatası: {e}")
            return False
    
    @classmethod
    def import_settings(cls, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Belirtilen dosyadan ayarları içe aktarır.
        
        Args:
            filepath: Kaynak dosya yolu
            
        Returns:
            Optional[Dict[str, Any]]: Yüklenen ayarlar veya None
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"İçe aktarma hatası: {e}")
            return None


# =============================================================================
# Renk Yardımcı Fonksiyonları
# =============================================================================

class ColorUtils:
    """Renk manipülasyonu için yardımcı fonksiyonlar."""
    
    @staticmethod
    def create_light_color(hex_color: str, opacity: float) -> str:
        """
        Bir hex rengin hafif (açık) versiyonunu oluşturur.
        
        Tkinter RGBA desteklemediği için rengi beyaz ile karıştırarak 
        transparan görünüm efekti simüle edilir.
        
        Args:
            hex_color: Kaynak renk (#RRGGBB formatında)
            opacity: 0.0-1.0 arası opaklık değeri (düşük = daha açık)
        
        Returns:
            str: Yeni hex renk (#RRGGBB formatında)
        """
        try:
            # Hex'ten RGB'ye dönüştür
            hex_color = hex_color.lstrip('#')
            
            if len(hex_color) != 6:
                logger.warning(f"Geçersiz hex renk formatı: #{hex_color}")
                return f"#{hex_color[:6]}" if len(hex_color) >= 6 else "#ffffff"
            
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Beyaz ile karıştır (transparan efekti simüle et)
            white = 255
            new_r = int(r * opacity + white * (1 - opacity))
            new_g = int(g * opacity + white * (1 - opacity))
            new_b = int(b * opacity + white * (1 - opacity))
            
            # RGB değerlerini sınırla
            new_r = max(0, min(255, new_r))
            new_g = max(0, min(255, new_g))
            new_b = max(0, min(255, new_b))
            
            return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Renk dönüşüm hatası: {e}, orijinal renk döndürülüyor")
            return hex_color if hex_color.startswith('#') else f"#{hex_color}"


# =============================================================================
# Ana Ayarlar Penceresi Sınıfı
# =============================================================================

class SettingsDialog(ctk.CTkToplevel):
    """
    Kapsamlı ayarlar penceresi.
    
    Tüm uygulama ayarlarını kategorilere ayırarak gösterir ve 
    düzenlemeye olanak tanır. Modern UI/UX tasarımı ile
    kullanıcı deneyimini optimize eder.
    
    Attributes:
        parent: Ana pencere referansı
        current_settings: Mevcut ayarlar sözlüğü
        original_settings: Orijinal ayarlar (değişiklik takibi için)
        on_apply_callback: Ayarlar uygulandığında çağrılacak fonksiyon
    """
    
    # Kategori -> Panel sınıfı eşlemesi
    CATEGORY_PANELS: Final[Dict[str, type]] = {
        "Genel": GeneralSettingsPanel,
        "Editör": EditorSettingsPanel,
        "Görünüm": ViewSettingsPanel,
        "Tema": ThemeSettingsPanel,
        "Klavye Kısayolları": ShortcutsSettingsPanel,
        "Terminal": TerminalSettingsPanel,
        "Gelişmiş": AdvancedSettingsPanel
    }
    
    def __init__(
        self, 
        parent: ctk.CTk, 
        current_settings: Dict[str, Any], 
        on_apply: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        SettingsDialog başlatıcı.
        
        Args:
            parent: Ana pencere referansı
            current_settings: Mevcut ayarlar sözlüğü
            on_apply: Ayarlar uygulandığında çağrılacak callback
        """
        super().__init__(parent)
        
        # Temel referanslar
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.original_settings = current_settings.copy()
        self.on_apply_callback = on_apply
        
        # Durum değişkenleri
        self.modified_settings: Dict[str, Any] = {}
        self._current_category: Optional[str] = None
        self._search_active: bool = False
        self._search_job: Optional[str] = None
        self._hover_animation_ids: Dict[str, str] = {}
        
        # UI Referansları
        self.category_buttons: Dict[str, ctk.CTkButton] = {}
        self.search_var: tk.StringVar = tk.StringVar()
        
        # Dil Yöneticisi
        self.lang_manager = LanguageManager.get_instance()
        self.current_lang = current_settings.get("language", "Türkçe")
        self.lang_manager.load_language(self.current_lang)
        
        # Arayüz Kurulumu
        self._setup_window()
        self._create_layout()
        
        # Başlangıç Durumu
        self.show_category(CategoryType.GENERAL.value)
        self._apply_theme_integration()
        
        # Açılış animasyonu
        self._animate_open()
    
    # =========================================================================
    # Pencere Kurulumu
    # =========================================================================
    
    def _setup_window(self) -> None:
        """Pencere özelliklerini yapılandırır."""
        self.title(self.lang_manager.get("window_title"))
        self.geometry(
            f"{SettingsConstants.WINDOW_WIDTH}x{SettingsConstants.WINDOW_HEIGHT}"
        )
        self.minsize(
            SettingsConstants.WINDOW_MIN_WIDTH, 
            SettingsConstants.WINDOW_MIN_HEIGHT
        )
        
        self._center_window()
        self.transient(self.parent)
        self.grab_set()
        
        # Pencere şeffaflığı (Animasyon için başlangıçta görünmez)
        self._set_window_alpha(0.0)
    
    def _center_window(self) -> None:
        """Pencereyi ana pencereye göre ortalar."""
        self.update_idletasks()
        
        # Pencere boyutlarını al
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Varsayılan boyutlar (ilk açılışta)
        if width < 100:
            width = SettingsConstants.WINDOW_WIDTH
        if height < 100:
            height = SettingsConstants.WINDOW_HEIGHT
        
        # Ana pencere konumunu al
        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Parent'ın merkezine göre hesapla
            x = parent_x + (parent_width // 2) - (width // 2)
            y = parent_y + (parent_height // 2) - (height // 2)
            
            # Ekran sınırları kontrolü
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))
            
        except tk.TclError:
            # Fallback: ekran merkezine göre
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _set_window_alpha(self, alpha: float) -> None:
        """
        Pencere şeffaflığını ayarlar.
        
        Args:
            alpha: 0.0 (görünmez) ile 1.0 (opak) arası değer
        """
        try:
            self.attributes('-alpha', alpha)
        except tk.TclError:
            # Platform alfa desteği yoksa sessizce atla
            pass
    
    def _animate_open(self) -> None:
        """Fade-in açılış animasyonu."""
        def fade_in(alpha: float = 0.0) -> None:
            if alpha < 1.0:
                self._set_window_alpha(alpha)
                self.after(
                    SettingsConstants.FADE_IN_DURATION, 
                    lambda: fade_in(alpha + SettingsConstants.FADE_IN_STEP)
                )
            else:
                self._set_window_alpha(1.0)
        
        self.after(SettingsConstants.ANIMATION_DELAY, lambda: fade_in(0.0))
    
    # =========================================================================
    # Layout Oluşturma
    # =========================================================================
    
    def _create_layout(self) -> None:
        """Ana düzeni oluşturur."""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Sol Panel (Navigasyon)
        self._create_sidebar()
        
        # Sağ Panel (İçerik)
        self._create_content_area()
        
        # Alt Panel (Aksiyonlar)
        self._create_action_bar()
    
    def _create_sidebar(self) -> None:
        """Sol taraftaki kategori panelini oluşturur."""
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=SettingsConstants.SIDEBAR_WIDTH, 
            corner_radius=SettingsConstants.SIDEBAR_CORNER_RADIUS, 
            fg_color=("gray95", "gray13"),
            border_width=SettingsConstants.SIDEBAR_BORDER_WIDTH,
            border_color=("gray85", "gray22")
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 16))
        self.sidebar.pack_propagate(False)
        
        # Başlık Bölümü
        self._create_sidebar_header()
        
        # Arama Alanı
        self._create_search_field()
        
        # Ayırıcı
        self._create_separator(self.sidebar)
        
        # Kategori Butonları
        self._create_category_buttons()
        
        # Alt Bilgi
        self._create_sidebar_footer()
    
    def _create_sidebar_header(self) -> None:
        """Sidebar başlık bölümünü oluşturur."""
        header_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_container.pack(fill="x", padx=0, pady=0)
        
        header_frame = ctk.CTkFrame(
            header_container, 
            fg_color=("gray90", "gray18"),
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(
            header_inner,
            text=self.lang_manager.get("panel_title"),
            font=ctk.CTkFont(size=SettingsConstants.HEADER_FONT_SIZE, weight="bold")
        ).pack(side="left")
        
        # Değişiklik Badge
        self.changes_badge = ctk.CTkLabel(
            header_inner, 
            text="", 
            font=ctk.CTkFont(size=SettingsConstants.FOOTER_FONT_SIZE, weight="bold"),
            fg_color=(SettingsConstants.BADGE_COLOR_HIGH, SettingsConstants.BADGE_COLOR_HIGH), 
            corner_radius=12, 
            width=28, 
            height=28,
            text_color="white"
        )
        # Başlangıçta gizli
    
    def _create_search_field(self) -> None:
        """Arama alanını oluşturur."""
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=14, pady=(12, 8))
        
        self.search_var.trace_add("write", self._on_search_change)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.lang_manager.get("search_placeholder"),
            textvariable=self.search_var,
            height=SettingsConstants.SEARCH_ENTRY_HEIGHT,
            corner_radius=SettingsConstants.SEARCH_CORNER_RADIUS,
            border_width=SettingsConstants.SEARCH_BORDER_WIDTH,
            border_color=("gray80", "gray28"),
            fg_color=("white", "gray20")
        )
        search_entry.pack(fill="x")
    
    def _create_separator(self, parent: ctk.CTkFrame) -> None:
        """İnce bir ayırıcı çizgi oluşturur."""
        separator = ctk.CTkFrame(parent, height=1, fg_color=("gray75", "gray28"))
        separator.pack(fill="x", padx=20, pady=(10, 12))
    
    def _create_category_buttons(self) -> None:
        """Kategori butonlarını oluşturur."""
        category_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        category_container.pack(fill="both", expand=True, padx=8)
        
        for category, icon in SettingsConfig.CATEGORIES.items():
            display_name = self.lang_manager.get(f"categories.{category}", category)
            
            btn = ctk.CTkButton(
                category_container,
                text=f"{icon}  {display_name}",
                command=lambda c=category: self.show_category(c),
                anchor="w",
                height=SettingsConstants.CATEGORY_BUTTON_HEIGHT,
                corner_radius=SettingsConstants.CATEGORY_BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=SettingsConstants.SUBHEADER_FONT_SIZE, weight="bold"),
                fg_color="transparent",
                hover_color=("gray85", "gray22"),
                text_color=("gray15", "gray90")
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.category_buttons[category] = btn
    
    def _create_sidebar_footer(self) -> None:
        """Sidebar alt bilgi bölümünü oluşturur."""
        footer_frame = ctk.CTkFrame(
            self.sidebar, 
            fg_color=("gray90", "gray18"), 
            corner_radius=0
        )
        footer_frame.pack(side="bottom", fill="x")
        
        footer_inner = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_inner.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(
            footer_inner, 
            text="🪐 " + self.lang_manager.get("messages.version_text"),
            font=ctk.CTkFont(size=SettingsConstants.FOOTER_FONT_SIZE, weight="bold"), 
            text_color=("gray45", "gray55")
        ).pack(anchor="center")
    
    def _create_content_area(self) -> None:
        """Sağ taraftaki içerik panelini oluşturur."""
        self.content_frame = ctk.CTkFrame(
            self.main_container, 
            corner_radius=SettingsConstants.SIDEBAR_CORNER_RADIUS,
            fg_color=("white", "gray16"),
            border_width=SettingsConstants.SIDEBAR_BORDER_WIDTH,
            border_color=("gray85", "gray22")
        )
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Başlık container
        header_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_container.pack(fill="x", padx=28, pady=(24, 0))
        
        # Başlık
        self.content_title = ctk.CTkLabel(
            header_container, 
            text="", 
            font=ctk.CTkFont(size=SettingsConstants.TITLE_FONT_SIZE, weight="bold")
        )
        self.content_title.pack(anchor="w")
        
        # Kategori açıklaması
        self.content_description = ctk.CTkLabel(
            header_container, 
            text="",
            font=ctk.CTkFont(size=SettingsConstants.BODY_FONT_SIZE),
            text_color=("gray50", "gray55")
        )
        self.content_description.pack(anchor="w", pady=(4, 0))
        
        # Modern ayırıcı
        separator_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=3)
        separator_frame.pack(fill="x", padx=28, pady=(16, 0))
        
        sep_inner = ctk.CTkFrame(
            separator_frame, 
            height=2, 
            fg_color=("gray80", "gray28"),
            corner_radius=1
        )
        sep_inner.pack(fill="x")
        
        # Kaydırılabilir Alan
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame, 
            fg_color="transparent",
            scrollbar_button_color=("gray70", "gray35"),
            scrollbar_button_hover_color=("gray60", "gray45")
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(16, 20))
    
    def _create_action_bar(self) -> None:
        """Alt kısımdaki buton panelini oluşturur."""
        bar = ctk.CTkFrame(
            self, 
            fg_color=("gray96", "gray14"),
            corner_radius=0,
            height=70
        )
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        
        inner_bar = ctk.CTkFrame(bar, fg_color="transparent")
        inner_bar.pack(fill="both", expand=True, padx=16, pady=12)
        
        # Sol taraf - Durum göstergesi
        left_group = ctk.CTkFrame(inner_bar, fg_color="transparent")
        left_group.pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            left_group,
            text="",
            font=ctk.CTkFont(size=SettingsConstants.SMALL_FONT_SIZE),
            text_color=("gray50", "gray55")
        )
        self.status_label.pack(side="left")
        
        # Sağ taraf - Butonlar
        right_group = ctk.CTkFrame(inner_bar, fg_color="transparent")
        right_group.pack(side="right")
        
        # Varsayılana Dön butonu
        self._create_action_button(
            right_group,
            text=self.lang_manager.get("buttons.reset"),
            command=self._reset_to_defaults,
            width=150,
            is_ghost=True
        )
        
        # İptal butonu
        self._create_action_button(
            right_group,
            text=self.lang_manager.get("buttons.cancel"),
            command=self._cancel,
            width=130,
            fg_color=SettingsConstants.CANCEL_BUTTON_FG,
            hover_color=SettingsConstants.CANCEL_BUTTON_HOVER,
            text_color=("gray20", "gray85")
        )
        
        # Uygula butonu
        self._create_action_button(
            right_group,
            text=self.lang_manager.get("buttons.apply"),
            command=self._apply_settings,
            width=160,
            fg_color=SettingsConstants.APPLY_BUTTON_FG,
            hover_color=SettingsConstants.APPLY_BUTTON_HOVER,
            text_color="white",
            font_weight="bold"
        )
    
    def _create_action_button(
        self,
        parent: ctk.CTkFrame,
        text: str,
        command: Callable,
        width: int,
        is_ghost: bool = False,
        fg_color: Optional[Tuple[str, str]] = None,
        hover_color: Optional[Tuple[str, str]] = None,
        text_color: Union[str, Tuple[str, str]] = ("gray45", "gray55"),
        font_weight: str = "normal"
    ) -> ctk.CTkButton:
        """
        Aksiyon butonu oluşturur.
        
        Args:
            parent: Üst widget
            text: Buton metni
            command: Tıklama komutu
            width: Buton genişliği
            is_ghost: Ghost stil mi?
            fg_color: Arka plan rengi
            hover_color: Hover rengi
            text_color: Metin rengi
            font_weight: Font ağırlığı
            
        Returns:
            ctk.CTkButton: Oluşturulan buton
        """
        btn_config = {
            "text": text,
            "command": command,
            "width": width,
            "height": SettingsConstants.ACTION_BUTTON_HEIGHT,
            "corner_radius": SettingsConstants.ACTION_BUTTON_CORNER_RADIUS,
            "font": ctk.CTkFont(size=SettingsConstants.BODY_FONT_SIZE, weight=font_weight),
            "text_color": text_color
        }
        
        if is_ghost:
            btn_config.update({
                "fg_color": "transparent",
                "border_width": 2,
                "border_color": ("gray70", "gray45"),
                "hover_color": ("gray90", "gray25")
            })
        else:
            if fg_color:
                btn_config["fg_color"] = fg_color
            if hover_color:
                btn_config["hover_color"] = hover_color
        
        btn = ctk.CTkButton(parent, **btn_config)
        btn.pack(side="left", padx=8)
        return btn
    
    # =========================================================================
    # Kategori Yönetimi
    # =========================================================================
    
    def show_category(self, category: str) -> None:
        """
        Seçilen kategoriyi gösterir.
        
        Args:
            category: Gösterilecek kategori adı
        """
        if self._current_category == category and not self._search_active:
            return
        
        self._search_active = False
        self._current_category = category
        
        # Sidebar buton stillerini güncelle
        self._update_category_button_styles(category)
        
        # İçerik başlığını güncelle
        self._update_content_header(category)
        
        # İçeriği temizle ve yeni paneli oluştur
        self._clear_content()
        self._create_panel_for_category(category)
    
    def _update_category_button_styles(self, active_category: str) -> None:
        """Kategori butonlarının stillerini günceller."""
        # Önce tüm butonları varsayılan stile döndür
        for cat_name, btn in self.category_buttons.items():
            btn.configure(
                fg_color="transparent",
                text_color=("gray15", "gray90")
            )
        
        # Aktif kategoriyi vurgula
        if active_category in self.category_buttons:
            theme_name = self.current_settings.get("theme", "Dark")
            theme = get_theme(theme_name)
            accent = theme.get("accent_color", SettingsConstants.DEFAULT_ACCENT_COLOR)
            
            # Accent rengin hafif versiyonlarını oluştur
            light_accent = ColorUtils.create_light_color(accent, 0.15)
            dark_accent = ColorUtils.create_light_color(accent, 0.25)
            
            self.category_buttons[active_category].configure(
                fg_color=(light_accent, dark_accent),
                text_color=(accent, accent)
            )
    
    def _update_content_header(self, category: str) -> None:
        """İçerik bölümü başlığını günceller."""
        icon = SettingsConfig.CATEGORIES.get(category, "")
        display_name = self.lang_manager.get(f"categories.{category}", category)
        self.content_title.configure(text=f"{icon} {display_name}")
        
        # Açıklama
        description_key = f"categories_desc.{category}"
        default_desc = SettingsConfig.CATEGORY_DESCRIPTIONS.get(category, "")
        description = self.lang_manager.get(description_key, default_desc)
        self.content_description.configure(text=description)
    
    def _clear_content(self) -> None:
        """İçerik alanını temizler."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def _create_panel_for_category(self, category: str) -> None:
        """
        Kategori için uygun paneli oluşturur.
        
        Args:
            category: Panel oluşturulacak kategori
        """
        panel_class = self.CATEGORY_PANELS.get(category)
        if panel_class:
            panel_class(self.scrollable_frame, self).pack(fill="both", expand=True)
        else:
            logger.warning(f"Bilinmeyen kategori: {category}")
    
    # =========================================================================
    # Arama İşlemleri
    # =========================================================================
    
    def _on_search_change(self, *args) -> None:
        """Arama alanı değişikliğini işler (Debounced)."""
        # Mevcut zamanlayıcıyı iptal et
        if hasattr(self, '_search_job') and self._search_job:
            self.after_cancel(self._search_job)
        
        # Yeni zamanlayıcı başlat
        self._search_job = self.after(
            SettingsConstants.SEARCH_DEBOUNCE_MS, 
            self._perform_search
        )
        
    def _perform_search(self) -> None:
        """Gerçek arama işlemini yürütür."""
        query = self.search_var.get().lower().strip()
        
        if not query:
            self.show_category(self._current_category or CategoryType.GENERAL.value)
            return
        
        self._search_active = True
        self.content_title.configure(text=f"🔍 {query}")
        self._clear_content()
        
        results = self._search_settings(query)
        self._display_search_results(results)
    
    def _search_settings(self, query: str) -> List[Tuple[str, str, str, str, str, Any]]:
        """
        Ayarlar içinde arama yapar.
        
        Args:
            query: Arama sorgusu
            
        Returns:
            Eşleşen sonuçların listesi
        """
        results = []
        
        for key, data in SettingsConfig.ALL_SETTINGS.items():
            cat = data.category
            icon = data.icon
            
            # Dinamik çevirileri al
            name_localized = self.lang_manager.get(f"settings.{key}.label", key)
            cat_localized = self.lang_manager.get(f"categories.{cat}", cat)
            
            # Arama kriterleri
            if (query in name_localized.lower() or 
                query in cat_localized.lower() or 
                query in key.lower()):
                
                val = self.current_settings.get(key, "—")
                results.append((name_localized, cat, cat_localized, key, icon, val))
        
        return results
    
    def _display_search_results(
        self, 
        results: List[Tuple[str, str, str, str, str, Any]]
    ) -> None:
        """
        Arama sonuçlarını görüntüler.
        
        Args:
            results: Görüntülenecek sonuçlar
        """
        # Sonuç sayısı
        count_text = self.lang_manager.get("messages.search_results", "").format(
            count=len(results)
        )
        ctk.CTkLabel(
            self.scrollable_frame, 
            text=count_text, 
            text_color="gray"
        ).pack(anchor="w", pady=(0, 10))
        
        # Sonuç kartları
        for name, cat_key, cat_name, key, icon, val in results:
            self._create_search_result_card(name, cat_key, cat_name, icon, val)
        
        # Sonuç yoksa mesaj göster
        if not results:
            no_res = self.lang_manager.get("messages.no_results", "Sonuç bulunamadı")
            ctk.CTkLabel(
                self.scrollable_frame, 
                text=f"🔍\n{no_res}", 
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
    
    def _create_search_result_card(
        self,
        name: str,
        cat_key: str,
        cat_name: str,
        icon: str,
        value: Any
    ) -> None:
        """
        Tek bir arama sonucu kartı oluşturur.
        
        Args:
            name: Ayar adı
            cat_key: Kategori anahtarı
            cat_name: Kategori görünen adı
            icon: Ayar ikonu
            value: Ayar değeri
        """
        card = ctk.CTkFrame(
            self.scrollable_frame, 
            corner_radius=10, 
            fg_color=("gray95", "gray20")
        )
        card.pack(fill="x", pady=6)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            header, 
            text=f"{icon} {name}", 
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left")
        
        # Değer gösterimi
        display_val = self._format_setting_value(value)
        ctk.CTkLabel(
            header, 
            text=f"= {display_val[:30]}", 
            text_color="gray"
        ).pack(side="right")
        
        # Kategoriye git butonu
        goto_text = self.lang_manager.get("messages.goto_category", "").format(
            category=cat_name
        )
        ctk.CTkButton(
            card, 
            text=goto_text, 
            fg_color="transparent",
            hover_color=("gray80", "gray25"), 
            anchor="w", 
            height=30,
            command=lambda c=cat_key: self._goto_category(c)
        ).pack(fill="x", padx=10, pady=(0, 10))
    
    def _format_setting_value(self, value: Any) -> str:
        """
        Ayar değerini görüntüleme için formatlar.
        
        Args:
            value: Formatlanacak değer
            
        Returns:
            str: Formatlanmış değer
        """
        if isinstance(value, bool):
            return self.lang_manager.get(
                "values.active" if value else "values.inactive", 
                "Aktif" if value else "Pasif"
            )
        return str(value)
    
    def _goto_category(self, category: str) -> None:
        """Aramayı temizleyip kategoriye gider."""
        self.search_var.set("")
        self.show_category(category)
    
    # =========================================================================
    # Ayar Değişiklik Yönetimi
    # =========================================================================
    
    def update_setting(self, key: str, value: Any) -> None:
        """
        Bir ayarı günceller ve değişiklik takibi yapar.
        
        Args:
            key: Ayar anahtarı
            value: Yeni değer
        """
        original_value = self.original_settings.get(key)
        
        if value == original_value:
            self.modified_settings.pop(key, None)
        else:
            self.modified_settings[key] = value
        
        self.current_settings[key] = value
        self._update_changes_badge()
    
    def _update_changes_badge(self) -> None:
        """Değişiklik rozeti görünümünü günceller."""
        # Gerçek değişiklik sayısını hesapla
        change_count = sum(
            1 for key, val in self.modified_settings.items()
            if val != self.original_settings.get(key)
        )
        
        if change_count > 0:
            # Rengi belirle
            if change_count >= SettingsConstants.BADGE_THRESHOLD_HIGH:
                badge_color = SettingsConstants.BADGE_COLOR_HIGH
            elif change_count >= SettingsConstants.BADGE_THRESHOLD_MEDIUM:
                badge_color = SettingsConstants.BADGE_COLOR_MEDIUM
            else:
                badge_color = SettingsConstants.BADGE_COLOR_LOW
            
            self.changes_badge.configure(text=str(change_count), fg_color=badge_color)
            self.changes_badge.pack(side="right", padx=(5, 0))
            
            # Pencere başlığını güncelle
            suffix = self.lang_manager.get(
                "messages.changes_title_suffix", ""
            ).format(count=change_count)
            self.title(f"{self.lang_manager.get('window_title')} {suffix}")
        else:
            self.changes_badge.pack_forget()
            self.title(self.lang_manager.get("window_title"))
    
    def _get_setting_info(self, key: str) -> Tuple[str, str]:
        """
        Ayar anahtarından etiket ve açıklama döndürür.
        
        Args:
            key: Ayar anahtarı
            
        Returns:
            Tuple[str, str]: (etiket, açıklama)
        """
        label = self.lang_manager.get(f"settings.{key}.label", key)
        desc = self.lang_manager.get(f"settings.{key}.desc", "")
        return label, desc
    
    # =========================================================================
    # Aksiyon Metodları
    # =========================================================================
    
    def _apply_settings(self) -> None:
        """Değişiklikleri uygular ve pencereyi kapatır."""
        if self.modified_settings:
            self.current_settings.update(self.modified_settings)
            
            if self.on_apply_callback:
                self.on_apply_callback(self.current_settings)
            
            SettingsFileManager.save(self.current_settings)
        
        self.destroy()
    
    def _reset_to_defaults(self) -> None:
        """Tüm ayarları varsayılana döndürür."""
        confirm = messagebox.askyesno(
            self.lang_manager.get("dialogs.reset_title", "Sıfırla"),
            self.lang_manager.get("dialogs.reset_confirm", "Tüm ayarlar varsayılana dönecek?"),
            parent=self
        )
        
        if confirm:
            self.current_settings = SettingsConfig.get_default_settings()
            self.modified_settings = self.current_settings.copy()
            self.show_category(self._current_category or CategoryType.GENERAL.value)
    
    def _cancel(self) -> None:
        """Değişiklikleri iptal eder ve pencereyi kapatır."""
        # Dil değişikliğini geri al
        original_lang = self.original_settings.get("language", "Türkçe")
        current_lang = self.current_settings.get("language", "Türkçe")
        
        if original_lang != current_lang:
            self.lang_manager.load_language(original_lang)
        
        self.destroy()
    
    # =========================================================================
    # Dışa/İçe Aktarma
    # =========================================================================
    
    def export_settings(self) -> None:
        """Ayarları JSON dosyasına dışa aktarır."""
        filepath = filedialog.asksaveasfilename(
            parent=self, 
            defaultextension=".json", 
            filetypes=[("JSON", "*.json")]
        )
        
        if filepath:
            if SettingsFileManager.export(self.current_settings, filepath):
                messagebox.showinfo(
                    self.lang_manager.get("dialogs.success", "Başarılı"),
                    self.lang_manager.get("dialogs.export_success", "Ayarlar dışa aktarıldı."),
                    parent=self
                )
            else:
                messagebox.showerror(
                    self.lang_manager.get("dialogs.error", "Hata"),
                    self.lang_manager.get("dialogs.export_error", "Dışa aktarma başarısız."),
                    parent=self
                )
    
    def import_settings(self) -> None:
        """JSON dosyasından ayarları içe aktarır."""
        filepath = filedialog.askopenfilename(
            parent=self, 
            filetypes=[("JSON", "*.json")]
        )
        
        if filepath:
            data = SettingsFileManager.import_settings(filepath)
            
            if data:
                self.current_settings.update(data)
                self.modified_settings = self.current_settings.copy()
                self.show_category(self._current_category or CategoryType.GENERAL.value)
                
                messagebox.showinfo(
                    self.lang_manager.get("dialogs.success", "Başarılı"),
                    self.lang_manager.get("dialogs.import_success", "Ayarlar içe aktarıldı."),
                    parent=self
                )
            else:
                messagebox.showerror(
                    self.lang_manager.get("dialogs.error", "Hata"),
                    self.lang_manager.get("dialogs.import_error", "İçe aktarma başarısız."),
                    parent=self
                )
    
    # =========================================================================
    # Tema Entegrasyonu
    # =========================================================================
    
    def _apply_theme_integration(self) -> None:
        """Pencereye mevcut temayı uygular."""
        theme_name = self.current_settings.get("theme", "Dark")
        theme = get_theme(theme_name)
        
        self.configure(fg_color=theme.get("bg", SettingsConstants.DEFAULT_BG_COLOR))
        self.main_container.configure(fg_color="transparent")
        
        # Sidebar renklendirmesi
        if hasattr(self, 'sidebar'):
            side_bg = theme.get("sidebar_bg", ("gray95", "gray15"))
            self.sidebar.configure(fg_color=side_bg)
    
    # =========================================================================
    # UI Yenileme
    # =========================================================================
    
    def _reload_ui(self) -> None:
        """Tüm arayüz metinlerini günceller (dil değişikliği sonrası)."""
        current_cat = self._current_category
        
        # Pencere Başlığı
        self.title(self.lang_manager.get("window_title"))
        
        # Ana container içindekileri temizle
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Action Bar'ı temizle
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.main_container:
                widget.destroy()
        
        # Bileşenleri Yeniden Oluştur
        self.category_buttons = {}
        self._create_sidebar()
        self._create_content_area()
        self._create_action_bar()
        
        # Kategoriyi Geri Yükle
        self._current_category = None
        self.show_category(current_cat or CategoryType.GENERAL.value)
    
    # =========================================================================
    # Geriye Uyumluluk Metodları (Deprecated)
    # =========================================================================
    
    # Bu metodlar eski API uyumluluğu için korunuyor
    def center_window(self) -> None:
        """Deprecated: Use _center_window instead."""
        self._center_window()
    
    def apply_theme_integration(self) -> None:
        """Deprecated: Use _apply_theme_integration instead."""
        self._apply_theme_integration()
    
    def reset_to_defaults(self) -> None:
        """Deprecated: Use _reset_to_defaults instead."""
        self._reset_to_defaults()
    
    def cancel(self) -> None:
        """Deprecated: Use _cancel instead."""
        self._cancel()
    
    def apply_settings(self) -> None:
        """Deprecated: Use _apply_settings instead."""
        self._apply_settings()
    
    def create_sidebar(self) -> None:
        """Deprecated: Use _create_sidebar instead."""
        self._create_sidebar()
    
    def create_content_area(self) -> None:
        """Deprecated: Use _create_content_area instead."""
        self._create_content_area()
    
    def create_action_bar(self) -> None:
        """Deprecated: Use _create_action_bar instead."""
        self._create_action_bar()
    
    def save_settings(self) -> None:
        """Deprecated: Use SettingsFileManager.save instead."""
        SettingsFileManager.save(self.current_settings)
    
    def load_settings(self) -> Dict[str, Any]:
        """Deprecated: Use SettingsFileManager.load instead."""
        return SettingsFileManager.load()
    
    def _create_light_color(self, hex_color: str, opacity: float) -> str:
        """Deprecated: Use ColorUtils.create_light_color instead."""
        return ColorUtils.create_light_color(hex_color, opacity)
