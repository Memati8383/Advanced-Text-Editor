"""
Drop Zone - Sürükle Bırak Sistemi

Bu modül, dosya ve klasörlerin sürükle-bırak ile açılması için
görsel geri bildirim sağlayan overlay widget'ını içerir.

Clean Code Prensipleri:
    - Single Responsibility: Her sınıf ve metot tek bir göreve odaklanır
    - DRY: Tekrarlayan kodlar ortak metotlara çıkarılmıştır
    - KISS: Karmaşık mantık basitleştirilmiştir
    - Sabitler ve yapılandırma ayrı bölümlerde tutulur
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

import customtkinter as ctk

# Type checking için import (runtime'da yüklenmez)
if TYPE_CHECKING:
    from text_editor.utils.language_manager import LanguageManager


# =============================================================================
# SABITLER VE YAPILANDIRMA
# =============================================================================

class AnimationConfig:
    """Animasyon sabitleri."""
    
    PULSE_SPEED: float = 0.1
    PULSE_INTERVAL_MS: int = 50
    PULSE_AMPLITUDE: int = 30
    
    GLOW_SPEED: float = 0.15
    GLOW_INTERVAL_MS: int = 80
    GLOW_MIN_INTENSITY: int = 10
    GLOW_MAX_INTENSITY: int = 15
    
    BOUNCE_SPEED: float = 0.15
    BOUNCE_INTERVAL_MS: int = 50
    BOUNCE_AMPLITUDE: int = 5
    
    DROP_FLASH_DURATION_MS: int = 500


class UIConfig:
    """UI bileşenleri sabitleri."""
    
    # Kart özellikleri
    CARD_CORNER_RADIUS: int = 28
    CARD_BORDER_WIDTH: int = 3
    GLOW_CORNER_RADIUS: int = 32
    
    # İkon dairesi özellikleri
    ICON_CIRCLE_SIZE: int = 120
    ICON_CIRCLE_RADIUS: int = 60
    ICON_CIRCLE_BORDER_WIDTH: int = 3
    
    # Font boyutları
    ICON_FONT_SIZE: int = 48
    TITLE_FONT_SIZE: int = 26
    SUBTITLE_FONT_SIZE: int = 15
    FILE_NAME_FONT_SIZE: int = 13
    FILE_TYPE_FONT_SIZE: int = 10
    BADGE_FONT_SIZE: int = 11
    MORE_FILES_FONT_SIZE: int = 12
    
    # İçerik padding
    CARD_PADDING: int = 8
    INNER_PADDING_X: int = 50
    INNER_PADDING_Y: int = 40
    
    # Dosya kartı
    FILE_CARD_CORNER_RADIUS: int = 10
    FILE_CARD_BORDER_WIDTH: int = 1
    MAX_VISIBLE_FILES: int = 5
    MAX_FILE_NAME_LENGTH: int = 35
    TRUNCATED_NAME_LENGTH: int = 32
    
    # Badge
    BADGE_CORNER_RADIUS: int = 12


@dataclass
class ThemeColors:
    """Hesaplanmış tema renkleri."""
    
    overlay_bg: str = "#1a1a1a"
    card_bg: str = "#252526"
    card_border: str = "#0098ff"
    icon_circle_bg: str = "#002d4d"
    icon_circle_border: str = "#0098ff"
    icon_color: str = "#4db8ff"
    title_color: str = "#d4d4d4"
    subtitle_color: str = "#949494"
    file_card_bg: str = "#1a1a1a"
    file_card_border: str = "#3c3c3c"
    file_name_color: str = "#d4d4d4"
    file_type_color: str = "#7f7f7f"
    badge_bg: str = "#1e1e1e"
    badge_text: str = "#949494"
    separator_color: str = "#333333"
    glow_color: str = "#0098ff"


# =============================================================================
# RENK YARDIMCI FONKSİYONLARI
# =============================================================================

class ColorUtils:
    """Renk dönüşüm ve manipülasyon yardımcı sınıfı."""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Hex rengi RGB tuple'a dönüştürür.
        
        Args:
            hex_color: Hex renk kodu (örn: "#0098ff")
            
        Returns:
            RGB değerleri tuple'ı (0-255 aralığında)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        RGB değerlerini hex renge dönüştürür.
        
        Args:
            r: Kırmızı değeri (0-255)
            g: Yeşil değeri (0-255)
            b: Mavi değeri (0-255)
            
        Returns:
            Hex renk kodu
        """
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @classmethod
    def lighten(cls, hex_color: str, factor: float = 0.2) -> str:
        """
        Rengi belirtilen faktör kadar açar.
        
        Args:
            hex_color: Orijinal hex renk
            factor: Açma faktörü (0.0-1.0)
            
        Returns:
            Açılmış rengin hex kodu
        """
        r, g, b = cls.hex_to_rgb(hex_color)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return cls.rgb_to_hex(r, g, b)
    
    @classmethod
    def darken(cls, hex_color: str, factor: float = 0.2) -> str:
        """
        Rengi belirtilen faktör kadar koyulaştırır.
        
        Args:
            hex_color: Orijinal hex renk
            factor: Koyulaştırma faktörü (0.0-1.0)
            
        Returns:
            Koyulaştırılmış rengin hex kodu
        """
        r, g, b = cls.hex_to_rgb(hex_color)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return cls.rgb_to_hex(r, g, b)
    
    @classmethod
    def adjust_by_theme(
        cls, 
        color: str, 
        is_dark_mode: bool, 
        dark_factor: float = 0.7, 
        light_factor: float = 0.8
    ) -> str:
        """
        Temaya göre rengi ayarlar.
        
        Args:
            color: Orijinal renk
            is_dark_mode: Karanlık mod aktif mi
            dark_factor: Karanlık modda koyulaştırma faktörü
            light_factor: Açık modda açma faktörü
            
        Returns:
            Ayarlanmış renk
        """
        if is_dark_mode:
            return cls.darken(color, dark_factor)
        return cls.lighten(color, light_factor)


# =============================================================================
# DOSYA TÜRLERİ VERİLERİ
# =============================================================================

class FileTypeRegistry:
    """Dosya türleri ve ikonları için merkezi kayıt sınıfı."""
    
    # Dosya uzantısına göre ikon eşleşmeleri
    ICONS: Dict[str, str] = {
        # Programlama dilleri
        '.py': '🐍', '.js': '📜', '.ts': '📘', '.jsx': '⚛️', '.tsx': '⚛️',
        '.java': '☕', '.cpp': '⚡', '.c': '⚡', '.h': '📑', '.cs': '🔷',
        '.go': '🔵', '.rs': '🦀', '.rb': '💎', '.php': '🐘', '.swift': '🍎',
        '.kt': '🟣', '.scala': '🔴', '.r': '📊', '.lua': '🌙',
        # Web
        '.html': '🌐', '.css': '🎨', '.scss': '🎀', '.sass': '🎀',
        '.vue': '💚', '.svelte': '🧡',
        # Veri
        '.json': '📋', '.xml': '📰', '.yaml': '⚙️', '.yml': '⚙️',
        '.toml': '🔧', '.ini': '🔩', '.env': '🔐',
        # Döküman
        '.md': '📝', '.txt': '📄', '.rst': '📜', '.log': '📃',
        '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗', '.xlsx': '📗',
        # Medya
        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🎞️',
        '.svg': '🎨', '.ico': '🎯', '.webp': '🖼️', '.bmp': '🖼️',
        '.mp3': '🎵', '.wav': '🎵', '.mp4': '🎬', '.avi': '🎬',
        # Arşiv
        '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
        # Diğer
        '.exe': '⚙️', '.msi': '💿', '.sh': '🖥️', '.bat': '🖥️',
        '.sql': '🗃️', '.db': '🗄️', '.graphql': '◼️', '.dockerfile': '🐳',
        '.gitignore': '🚫', '.lock': '🔒'
    }
    
    # Dosya uzantısına göre tür adları
    TYPE_NAMES: Dict[str, str] = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React JSX', '.tsx': 'React TSX',
        '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
        '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
        '.md': 'Markdown', '.txt': 'Metin', '.log': 'Log',
        '.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.gif': 'GIF',
        '.svg': 'SVG', '.pdf': 'PDF', '.webp': 'WebP',
        '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
        '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
        '.swift': 'Swift', '.kt': 'Kotlin', '.vue': 'Vue',
        '.zip': 'ZIP', '.exe': 'Executable', '.sql': 'SQL'
    }
    
    # Desteklenen dosya uzantıları
    SUPPORTED_EXTENSIONS: Set[str] = {
        # Kod dosyaları
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        # Web dosyaları
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        # Veri dosyaları
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        # Metin dosyaları
        '.txt', '.md', '.markdown', '.rst', '.log',
        # Script dosyaları
        '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
        # Diğer
        '.sql', '.graphql', '.env', '.gitignore', '.dockerfile'
    }
    
    # Resim uzantıları
    IMAGE_EXTENSIONS: Set[str] = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp', '.svg'
    }
    
    DEFAULT_ICON: str = '📄'
    DEFAULT_TYPE_NAME: str = 'Dosya'
    
    @classmethod
    def get_icon(cls, file_path: str) -> str:
        """
        Dosya uzantısına göre ikon döndürür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya ikonu (emoji)
        """
        ext = os.path.splitext(file_path)[1].lower()
        return cls.ICONS.get(ext, cls.DEFAULT_ICON)
    
    @classmethod
    def get_type_name(cls, file_path: str) -> str:
        """
        Dosya uzantısına göre tür adı döndürür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya türü adı
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext in cls.TYPE_NAMES:
            return cls.TYPE_NAMES[ext]
        # Bilinmeyen uzantı için büyük harfle göster
        return ext.upper()[1:] if ext else cls.DEFAULT_TYPE_NAME
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Dosyanın desteklenip desteklenmediğini kontrol eder."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS or ext in cls.IMAGE_EXTENSIONS
    
    @classmethod
    def is_image(cls, file_path: str) -> bool:
        """Dosyanın resim dosyası olup olmadığını kontrol eder."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.IMAGE_EXTENSIONS


# =============================================================================
# DOSYA BOYUTU FORMATLAYICI
# =============================================================================

class FileSizeFormatter:
    """Dosya boyutunu okunabilir formata çevirir."""
    
    UNITS: List[Tuple[int, str]] = [
        (1024 * 1024 * 1024, "GB"),
        (1024 * 1024, "MB"),
        (1024, "KB"),
        (1, "B")
    ]
    
    @classmethod
    def format(cls, size_bytes: int) -> str:
        """
        Dosya boyutunu okunabilir formata çevirir.
        
        Args:
            size_bytes: Byte cinsinden boyut
            
        Returns:
            Okunabilir format (örn: "1.5 MB")
        """
        for threshold, unit in cls.UNITS:
            if size_bytes >= threshold:
                if unit == "B":
                    return f"{size_bytes} {unit}"
                return f"{size_bytes / threshold:.1f} {unit}"
        return f"{size_bytes} B"


# =============================================================================
# TEMA HESAPLAYICI
# =============================================================================

class ThemeCalculator:
    """Tema değerlerine göre renkleri hesaplar."""
    
    DEFAULT_THEME: Dict[str, str] = {
        "type": "Dark",
        "accent_color": "#0098ff",
        "editor_bg": "#1e1e1e",
        "editor_fg": "#d4d4d4",
        "tab_bg": "#252526",
        "menu_bg": "#333333",
        "menu_fg": "#cccccc",
        "status_bg": "#1a73e8",
        "status_fg": "#ffffff"
    }
    
    @classmethod
    def calculate(cls, theme: Dict[str, str], is_dark_mode: bool) -> ThemeColors:
        """
        Tema değerlerine göre renkleri hesaplar.
        
        Args:
            theme: Tema sözlüğü
            is_dark_mode: Karanlık mod aktif mi
            
        Returns:
            Hesaplanmış tema renkleri
        """
        accent = theme.get("accent_color", "#0098ff")
        editor_bg = theme.get("editor_bg", "#1e1e1e")
        editor_fg = theme.get("editor_fg", "#d4d4d4")
        
        if is_dark_mode:
            return cls._calculate_dark_colors(accent, editor_bg, editor_fg)
        return cls._calculate_light_colors(accent, editor_bg, editor_fg)
    
    @classmethod
    def _calculate_dark_colors(
        cls, 
        accent: str, 
        editor_bg: str, 
        editor_fg: str
    ) -> ThemeColors:
        """Karanlık tema için renkleri hesaplar."""
        return ThemeColors(
            overlay_bg=ColorUtils.darken(editor_bg, 0.3),
            card_bg=ColorUtils.lighten(editor_bg, 0.1),
            card_border=accent,
            icon_circle_bg=ColorUtils.darken(accent, 0.7),
            icon_circle_border=accent,
            icon_color=ColorUtils.lighten(accent, 0.3),
            title_color=editor_fg,
            subtitle_color=ColorUtils.darken(editor_fg, 0.3),
            file_card_bg=ColorUtils.darken(editor_bg, 0.2),
            file_card_border=ColorUtils.lighten(editor_bg, 0.2),
            file_name_color=editor_fg,
            file_type_color=ColorUtils.darken(editor_fg, 0.4),
            badge_bg=ColorUtils.darken(editor_bg, 0.1),
            badge_text=ColorUtils.darken(editor_fg, 0.3),
            separator_color=ColorUtils.lighten(editor_bg, 0.15),
            glow_color=accent
        )
    
    @classmethod
    def _calculate_light_colors(
        cls, 
        accent: str, 
        editor_bg: str, 
        editor_fg: str
    ) -> ThemeColors:
        """Açık tema için renkleri hesaplar."""
        return ThemeColors(
            overlay_bg=ColorUtils.darken(editor_bg, 0.1),
            card_bg=editor_bg,
            card_border=accent,
            icon_circle_bg=ColorUtils.lighten(accent, 0.8),
            icon_circle_border=accent,
            icon_color=ColorUtils.darken(accent, 0.2),
            title_color=editor_fg,
            subtitle_color=ColorUtils.lighten(editor_fg, 0.3),
            file_card_bg=ColorUtils.darken(editor_bg, 0.05),
            file_card_border=ColorUtils.darken(editor_bg, 0.15),
            file_name_color=editor_fg,
            file_type_color=ColorUtils.lighten(editor_fg, 0.4),
            badge_bg=ColorUtils.darken(editor_bg, 0.08),
            badge_text=ColorUtils.lighten(editor_fg, 0.3),
            separator_color=ColorUtils.darken(editor_bg, 0.1),
            glow_color=accent
        )


# =============================================================================
# ANİMASYON YÖNETİCİSİ
# =============================================================================

class AnimationManager:
    """Overlay animasyonlarını yöneten sınıf."""
    
    def __init__(self, widget: ctk.CTkFrame):
        """
        AnimationManager'ı başlatır.
        
        Args:
            widget: Animasyonların uygulanacağı widget
        """
        self._widget = widget
        self._is_running = False
        
        # Animasyon durumları
        self._pulse_state: float = 0.0
        self._pulse_job: Optional[str] = None
        
        self._glow_state: float = 0.0
        self._glow_job: Optional[str] = None
        
        self._bounce_state: float = 0.0
        self._bounce_job: Optional[str] = None
    
    def start_all(self) -> None:
        """Tüm animasyonları başlatır."""
        self._is_running = True
        self._start_pulse()
        self._start_glow()
        self._start_bounce()
    
    def stop_all(self) -> None:
        """Tüm animasyonları durdurur."""
        self._is_running = False
        self._stop_pulse()
        self._stop_glow()
        self._stop_bounce()
    
    # Pulse Animasyonu
    def _start_pulse(self) -> None:
        """Border pulse animasyonunu başlatır."""
        self._cancel_job(self._pulse_job)
        self._pulse_state = 0.0
        self._animate_pulse()
    
    def _stop_pulse(self) -> None:
        """Border pulse animasyonunu durdurur."""
        self._pulse_job = self._cancel_job(self._pulse_job)
    
    def _animate_pulse(self) -> None:
        """Pulse animasyonu frame'i."""
        if not self._is_running:
            return
        
        self._pulse_state += AnimationConfig.PULSE_SPEED
        offset = int(AnimationConfig.PULSE_AMPLITUDE * math.sin(self._pulse_state))
        
        # Accent rengini al ve modifiye et
        overlay = self._get_overlay()
        if overlay:
            accent = overlay._theme.get("accent_color", "#0098ff")
            r, g, b = ColorUtils.hex_to_rgb(accent)
            
            new_r = max(0, min(255, r + offset))
            new_g = max(0, min(255, g + offset))
            new_b = max(0, min(255, b + offset))
            color = ColorUtils.rgb_to_hex(new_r, new_g, new_b)
            
            try:
                overlay.content_frame.configure(border_color=color)
                overlay.icon_circle.configure(border_color=color)
            except Exception:
                pass
        
        self._pulse_job = self._widget.after(
            AnimationConfig.PULSE_INTERVAL_MS, 
            self._animate_pulse
        )
    
    # Glow Animasyonu
    def _start_glow(self) -> None:
        """Dış glow animasyonunu başlatır."""
        self._cancel_job(self._glow_job)
        self._glow_state = 0.0
        self._animate_glow()
    
    def _stop_glow(self) -> None:
        """Dış glow animasyonunu durdurur."""
        self._glow_job = self._cancel_job(self._glow_job)
    
    def _animate_glow(self) -> None:
        """Glow animasyonu frame'i."""
        if not self._is_running:
            return
        
        self._glow_state += AnimationConfig.GLOW_SPEED
        intensity = int(
            AnimationConfig.GLOW_MIN_INTENSITY + 
            (AnimationConfig.GLOW_MAX_INTENSITY - AnimationConfig.GLOW_MIN_INTENSITY) * 
            (0.5 + 0.5 * math.sin(self._glow_state))
        )
        
        overlay = self._get_overlay()
        if overlay:
            accent = overlay._theme.get("accent_color", "#0098ff")
            glow_color = (
                ColorUtils.lighten(accent, 0.3) 
                if overlay._is_dark_mode 
                else ColorUtils.darken(accent, 0.3)
            )
            
            try:
                overlay.glow_frame.configure(
                    border_width=intensity,
                    border_color=glow_color
                )
            except Exception:
                pass
        
        self._glow_job = self._widget.after(
            AnimationConfig.GLOW_INTERVAL_MS, 
            self._animate_glow
        )
    
    # Bounce Animasyonu
    def _start_bounce(self) -> None:
        """İkon bounce animasyonunu başlatır."""
        self._cancel_job(self._bounce_job)
        self._bounce_state = 0.0
        self._animate_bounce()
    
    def _stop_bounce(self) -> None:
        """İkon bounce animasyonunu durdurur."""
        self._bounce_job = self._cancel_job(self._bounce_job)
    
    def _animate_bounce(self) -> None:
        """İkon bounce animasyonu frame'i."""
        if not self._is_running:
            return
        
        self._bounce_state += AnimationConfig.BOUNCE_SPEED
        offset = int(AnimationConfig.BOUNCE_AMPLITUDE * math.sin(self._bounce_state))
        
        overlay = self._get_overlay()
        if overlay:
            try:
                overlay.icon_label.place(
                    relx=0.5, 
                    rely=0.5 + offset / 100, 
                    anchor="center"
                )
            except Exception:
                pass
        
        self._bounce_job = self._widget.after(
            AnimationConfig.BOUNCE_INTERVAL_MS, 
            self._animate_bounce
        )
    
    # Yardımcı Metodlar
    def _cancel_job(self, job: Optional[str]) -> None:
        """Zamanlanmış işi iptal eder."""
        if job:
            try:
                self._widget.after_cancel(job)
            except Exception:
                pass
        return None
    
    def _get_overlay(self) -> Optional['DropZoneOverlay']:
        """Widget'ın DropZoneOverlay olup olmadığını kontrol eder."""
        if isinstance(self._widget, DropZoneOverlay):
            return self._widget
        return None


# =============================================================================
# DROP ZONE OVERLAY
# =============================================================================

class DropZoneOverlay(ctk.CTkFrame):
    """
    Modern, glassmorphism tarzı sürükle-bırak overlay'ı.
    
    Dosya veya klasör sürüklendiğinde pencere üzerinde belirir
    ve kullanıcıya görsel geri bildirim sağlar.
    Renkler tamamen temaya göre dinamik olarak ayarlanır.
    
    Attributes:
        on_file_drop: Dosya bırakıldığında çağrılacak callback
        on_folder_drop: Klasör bırakıldığında çağrılacak callback
    """
    
    def __init__(
        self,
        master,
        on_file_drop: Optional[Callable[[str], None]] = None,
        on_folder_drop: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        DropZoneOverlay'ı başlatır.
        
        Args:
            master: Ana widget
            on_file_drop: Dosya bırakma callback'i
            on_folder_drop: Klasör bırakma callback'i
            **kwargs: CTkFrame'e iletilecek argümanlar
        """
        super().__init__(master, **kwargs)
        
        # Callback fonksiyonları
        self.on_file_drop = on_file_drop
        self.on_folder_drop = on_folder_drop
        
        # Dil yöneticisi
        self._lang = self._get_language_manager()
        
        # Overlay varsayılan olarak gizli
        self._is_visible = False
        
        # Tema değerleri
        self._theme: Dict[str, str] = ThemeCalculator.DEFAULT_THEME.copy()
        self._is_dark_mode = True
        
        # Hesaplanmış renkler
        self._colors = ThemeCalculator.calculate(self._theme, self._is_dark_mode)
        
        # Görünüm ayarları
        self.configure(
            fg_color=self._colors.overlay_bg,
            corner_radius=0
        )
        
        # UI bileşenlerini oluştur
        self._setup_ui()
        
        # Animasyon yöneticisi
        self._animation_manager = AnimationManager(self)
        
        # ESC tuşu ile kapatma
        self._bind_escape_key()
        
        # Başlangıçta gizle
        self.place_forget()
    
    # -------------------------------------------------------------------------
    # Başlatma Yardımcıları
    # -------------------------------------------------------------------------
    
    def _get_language_manager(self) -> 'LanguageManager':
        """Dil yöneticisini döndürür."""
        from text_editor.utils.language_manager import LanguageManager
        return LanguageManager.get_instance()
    
    def _bind_escape_key(self) -> None:
        """ESC tuşu binding'ini ayarlar."""
        try:
            self.master.bind("<Escape>", self._on_escape, add="+")
        except Exception:
            pass
    
    # -------------------------------------------------------------------------
    # UI Kurulumu
    # -------------------------------------------------------------------------
    
    def _setup_ui(self) -> None:
        """Modern overlay UI bileşenlerini oluşturur."""
        self._create_glow_frame()
        self._create_content_frame()
        self._create_inner_container()
        self._create_icon_section()
        self._create_text_section()
        self._create_separator()
        self._create_file_list_frame()
        self._create_badges_section()
    
    def _create_glow_frame(self) -> None:
        """Dış glow efekti çerçevesini oluşturur."""
        self.glow_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=UIConfig.GLOW_CORNER_RADIUS
        )
        self.glow_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_content_frame(self) -> None:
        """Ana kart çerçevesini oluşturur."""
        self.content_frame = ctk.CTkFrame(
            self.glow_frame,
            fg_color=self._colors.card_bg,
            corner_radius=UIConfig.CARD_CORNER_RADIUS,
            border_width=UIConfig.CARD_BORDER_WIDTH,
            border_color=self._colors.card_border
        )
        self.content_frame.pack(padx=UIConfig.CARD_PADDING, pady=UIConfig.CARD_PADDING)
    
    def _create_inner_container(self) -> None:
        """İçerik container'ını oluşturur."""
        self.inner_container = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.inner_container.pack(
            padx=UIConfig.INNER_PADDING_X, 
            pady=UIConfig.INNER_PADDING_Y
        )
    
    def _create_icon_section(self) -> None:
        """Animasyonlu ikon bölümünü oluşturur."""
        self.icon_circle = ctk.CTkFrame(
            self.inner_container,
            width=UIConfig.ICON_CIRCLE_SIZE,
            height=UIConfig.ICON_CIRCLE_SIZE,
            corner_radius=UIConfig.ICON_CIRCLE_RADIUS,
            fg_color=self._colors.icon_circle_bg,
            border_width=UIConfig.ICON_CIRCLE_BORDER_WIDTH,
            border_color=self._colors.icon_circle_border
        )
        self.icon_circle.pack(pady=(0, 25))
        self.icon_circle.pack_propagate(False)
        
        self.icon_label = ctk.CTkLabel(
            self.icon_circle,
            text="📁",
            font=("Segoe UI Emoji", UIConfig.ICON_FONT_SIZE),
            text_color=self._colors.icon_color
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_text_section(self) -> None:
        """Başlık ve alt başlık bölümünü oluşturur."""
        self.title_label = ctk.CTkLabel(
            self.inner_container,
            text=self._lang.get("drop_zone.title", "Dosyaları Buraya Bırakın"),
            font=("Segoe UI", UIConfig.TITLE_FONT_SIZE, "bold"),
            text_color=self._colors.title_color
        )
        self.title_label.pack(pady=(0, 8))
        
        self.subtitle_label = ctk.CTkLabel(
            self.inner_container,
            text=self._lang.get("drop_zone.subtitle", "Dosya veya klasör açmak için bırakın"),
            font=("Segoe UI", UIConfig.SUBTITLE_FONT_SIZE),
            text_color=self._colors.subtitle_color
        )
        self.subtitle_label.pack(pady=(0, 25))
    
    def _create_separator(self) -> None:
        """Ayırıcı çizgiyi oluşturur."""
        self.separator = ctk.CTkFrame(
            self.inner_container,
            height=2,
            fg_color=self._colors.separator_color,
            corner_radius=1
        )
        self.separator.pack(fill="x", pady=(0, 20))
    
    def _create_file_list_frame(self) -> None:
        """Dosya listesi çerçevesini oluşturur."""
        self.file_list_frame = ctk.CTkFrame(
            self.inner_container,
            fg_color="transparent"
        )
        self.file_list_frame.pack(fill="x")
    
    def _create_badges_section(self) -> None:
        """Badge'ler bölümünü oluşturur."""
        self.badges_frame = ctk.CTkFrame(
            self.inner_container,
            fg_color="transparent"
        )
        self.badges_frame.pack(pady=(20, 0))
        self._create_badges()
    
    def _create_badges(self) -> None:
        """Desteklenen dosya türleri badge'lerini oluşturur."""
        # Mevcut badge'leri temizle
        for widget in self.badges_frame.winfo_children():
            widget.destroy()
        
        badges = [
            ("📄", self._lang.get("drop_zone.badge_files", "Dosyalar")),
            ("📂", self._lang.get("drop_zone.badge_folders", "Klasörler")),
            ("🖼️", self._lang.get("drop_zone.badge_images", "Görseller"))
        ]
        
        for icon, text in badges:
            self._create_single_badge(icon, text)
    
    def _create_single_badge(self, icon: str, text: str) -> None:
        """Tek bir badge oluşturur."""
        badge = ctk.CTkFrame(
            self.badges_frame,
            fg_color=self._colors.badge_bg,
            corner_radius=UIConfig.BADGE_CORNER_RADIUS
        )
        badge.pack(side="left", padx=5)
        
        badge_label = ctk.CTkLabel(
            badge,
            text=f"{icon} {text}",
            font=("Segoe UI", UIConfig.BADGE_FONT_SIZE),
            text_color=self._colors.badge_text
        )
        badge_label.pack(padx=12, pady=6)
    
    # -------------------------------------------------------------------------
    # Görünürlük Kontrolü
    # -------------------------------------------------------------------------
    
    def show(self, files: Optional[List[str]] = None) -> None:
        """
        Overlay'ı gösterir.
        
        Args:
            files: Sürüklenen dosya yollarının listesi
        """
        self._is_visible = True
        
        # Tam ekran yerleşim
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        
        # Dosya önizlemesini güncelle
        if files:
            self._update_file_preview(files)
        
        # Animasyonları başlat
        self._animation_manager.start_all()
    
    def hide(self) -> None:
        """Overlay'ı gizler."""
        self._is_visible = False
        
        # Animasyonları durdur
        self._animation_manager.stop_all()
        
        # Gizle
        self.place_forget()
        
        # Dosya listesini temizle
        self._clear_file_list()
    
    def _clear_file_list(self) -> None:
        """Dosya listesini temizler."""
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
    
    def _on_escape(self, event=None) -> None:
        """ESC tuşuna basıldığında overlay'ı gizler."""
        if self._is_visible:
            self.hide()
    
    # -------------------------------------------------------------------------
    # Dosya Önizleme
    # -------------------------------------------------------------------------
    
    def _update_file_preview(self, files: List[str]) -> None:
        """
        Sürüklenen dosyaların önizlemesini günceller.
        
        Args:
            files: Dosya yollarının listesi
        """
        self._clear_file_list()
        
        # Dosya/klasör sayılarını hesapla
        folder_count = sum(1 for f in files if os.path.isdir(f))
        file_count = len(files) - folder_count
        
        # İkon ve başlığı güncelle
        self._update_icon_and_title(file_count, folder_count)
        
        # Dosya kartlarını oluştur
        self._create_file_cards(files)
        
        # Daha fazla dosya varsa göster
        self._show_more_files_indicator(files)
    
    def _update_icon_and_title(self, file_count: int, folder_count: int) -> None:
        """İkon ve başlığı dosya türlerine göre günceller."""
        accent = self._theme.get("accent_color", "#0098ff")
        
        if folder_count > 0 and file_count == 0:
            self._configure_folder_mode(folder_count, accent)
        elif file_count > 0 and folder_count == 0:
            self._configure_file_mode(file_count, accent)
        else:
            self._configure_mixed_mode(file_count, folder_count, accent)
    
    def _configure_folder_mode(self, count: int, accent: str) -> None:
        """Sadece klasör modu için yapılandırma."""
        self.icon_label.configure(text="📂")
        self._configure_icon_circle_colors(accent)
        
        title = (
            self._lang.get("drop_zone.folder_single", "Klasör Açılacak")
            if count == 1
            else self._lang.get("drop_zone.folder_multiple", f"{count} Klasör Açılacak")
        )
        self.title_label.configure(text=title)
    
    def _configure_file_mode(self, count: int, accent: str) -> None:
        """Sadece dosya modu için yapılandırma."""
        self.icon_label.configure(text="📄")
        self._configure_icon_circle_colors(accent)
        
        title = (
            self._lang.get("drop_zone.file_single", "Dosya Açılacak")
            if count == 1
            else self._lang.get("drop_zone.file_multiple", f"{count} Dosya Açılacak")
        )
        self.title_label.configure(text=title)
    
    def _configure_mixed_mode(self, file_count: int, folder_count: int, accent: str) -> None:
        """Karışık mod (dosya + klasör) için yapılandırma."""
        self.icon_label.configure(text="📁")
        self._configure_icon_circle_colors(accent)
        self.title_label.configure(
            text=self._lang.get(
                "drop_zone.mixed", 
                f"{file_count} Dosya, {folder_count} Klasör"
            )
        )
    
    def _configure_icon_circle_colors(self, color: str) -> None:
        """İkon dairesi renklerini yapılandırır."""
        bg_color = ColorUtils.adjust_by_theme(color, self._is_dark_mode)
        text_color = (
            ColorUtils.lighten(color, 0.3) 
            if self._is_dark_mode 
            else ColorUtils.darken(color, 0.2)
        )
        
        self.icon_circle.configure(fg_color=bg_color, border_color=color)
        self.icon_label.configure(text_color=text_color)
    
    def _create_file_cards(self, files: List[str]) -> None:
        """Dosya kartlarını oluşturur."""
        display_files = files[:UIConfig.MAX_VISIBLE_FILES]
        
        for file_path in display_files:
            self._create_file_card(file_path)
    
    def _create_file_card(self, file_path: str) -> None:
        """Tek bir dosya kartı oluşturur."""
        is_folder = os.path.isdir(file_path)
        icon = "📂" if is_folder else FileTypeRegistry.get_icon(file_path)
        name = os.path.basename(file_path)
        
        # Kart çerçevesi
        file_card = ctk.CTkFrame(
            self.file_list_frame,
            fg_color=self._colors.file_card_bg,
            corner_radius=UIConfig.FILE_CARD_CORNER_RADIUS,
            border_width=UIConfig.FILE_CARD_BORDER_WIDTH,
            border_color=self._colors.file_card_border
        )
        file_card.pack(fill="x", pady=3)
        
        # İçerik container
        content = ctk.CTkFrame(file_card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=8)
        
        # İkon
        self._create_file_icon_label(content, icon)
        
        # Dosya adı
        self._create_file_name_label(content, name)
        
        # Dosya boyutu (klasörler için gösterme)
        if not is_folder:
            self._create_file_size_label(content, file_path)
        
        # Tür etiketi
        self._create_file_type_label(content, file_path, is_folder)
    
    def _create_file_icon_label(self, parent: ctk.CTkFrame, icon: str) -> None:
        """Dosya ikonu etiketini oluşturur."""
        ctk.CTkLabel(
            parent,
            text=icon,
            font=("Segoe UI Emoji", 16),
            width=30
        ).pack(side="left")
    
    def _create_file_name_label(self, parent: ctk.CTkFrame, name: str) -> None:
        """Dosya adı etiketini oluşturur."""
        display_name = (
            name 
            if len(name) <= UIConfig.MAX_FILE_NAME_LENGTH 
            else name[:UIConfig.TRUNCATED_NAME_LENGTH] + "..."
        )
        
        ctk.CTkLabel(
            parent,
            text=display_name,
            font=("Segoe UI", UIConfig.FILE_NAME_FONT_SIZE),
            text_color=self._colors.file_name_color,
            anchor="w"
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))
    
    def _create_file_size_label(self, parent: ctk.CTkFrame, file_path: str) -> None:
        """Dosya boyutu etiketini oluşturur."""
        try:
            file_size = os.path.getsize(file_path)
            ctk.CTkLabel(
                parent,
                text=FileSizeFormatter.format(file_size),
                font=("Segoe UI", UIConfig.FILE_TYPE_FONT_SIZE),
                text_color=self._colors.file_type_color
            ).pack(side="right", padx=(5, 10))
        except Exception:
            pass
    
    def _create_file_type_label(
        self, 
        parent: ctk.CTkFrame, 
        file_path: str, 
        is_folder: bool
    ) -> None:
        """Dosya türü etiketini oluşturur."""
        type_text = (
            self._lang.get("drop_zone.type_folder", "Klasör") 
            if is_folder 
            else FileTypeRegistry.get_type_name(file_path)
        )
        
        ctk.CTkLabel(
            parent,
            text=type_text,
            font=("Segoe UI", UIConfig.FILE_TYPE_FONT_SIZE),
            text_color=self._colors.file_type_color
        ).pack(side="right")
    
    def _show_more_files_indicator(self, files: List[str]) -> None:
        """Daha fazla dosya göstergesini oluşturur."""
        if len(files) <= UIConfig.MAX_VISIBLE_FILES:
            return
        
        remaining = len(files) - UIConfig.MAX_VISIBLE_FILES
        accent = self._theme.get("accent_color", "#0098ff")
        
        more_frame = ctk.CTkFrame(
            self.file_list_frame,
            fg_color=self._colors.badge_bg,
            corner_radius=8
        )
        more_frame.pack(fill="x", pady=(8, 0))
        
        more_label = ctk.CTkLabel(
            more_frame,
            text=f"➕ {self._lang.get('drop_zone.more_files', f'... ve {remaining} dosya daha')}",
            font=("Segoe UI", UIConfig.MORE_FILES_FONT_SIZE),
            text_color=accent
        )
        more_label.pack(pady=8)
    
    # -------------------------------------------------------------------------
    # Tema Güncelleme
    # -------------------------------------------------------------------------
    
    def update_theme(self, theme: Dict[str, str]) -> None:
        """
        Temayı günceller ve tüm UI bileşenlerini yeniden renklendirir.
        
        Args:
            theme: Tema sözlüğü
        """
        self._theme = theme.copy()
        self._is_dark_mode = theme.get("type", "Dark") == "Dark"
        self._colors = ThemeCalculator.calculate(self._theme, self._is_dark_mode)
        
        self._apply_theme_to_components()
    
    def _apply_theme_to_components(self) -> None:
        """Tema renklerini tüm bileşenlere uygular."""
        # Ana arka plan
        self.configure(fg_color=self._colors.overlay_bg)
        
        # Kart
        self.content_frame.configure(
            fg_color=self._colors.card_bg,
            border_color=self._colors.card_border
        )
        
        # İkon dairesi
        self.icon_circle.configure(
            fg_color=self._colors.icon_circle_bg,
            border_color=self._colors.icon_circle_border
        )
        self.icon_label.configure(text_color=self._colors.icon_color)
        
        # Metin
        self.title_label.configure(text_color=self._colors.title_color)
        self.subtitle_label.configure(text_color=self._colors.subtitle_color)
        
        # Ayırıcı
        self.separator.configure(fg_color=self._colors.separator_color)
        
        # Badge'leri yeniden oluştur
        self._create_badges()


# =============================================================================
# DRAG DROP MANAGER
# =============================================================================

class DragDropManager:
    """
    Sürükle-bırak işlemlerini yöneten ana sınıf.
    
    MainWindow ile entegre çalışır ve dosya/klasör
    sürükle-bırak işlemlerini koordine eder.
    
    Attributes:
        master: Ana pencere referansı
        on_file_open: Dosya açma callback'i
        on_folder_open: Klasör açma callback'i
        overlay: DropZoneOverlay instance'ı
    """
    
    def __init__(
        self,
        master,
        on_file_open: Optional[Callable[[str], None]] = None,
        on_folder_open: Optional[Callable[[str], None]] = None
    ):
        """
        DragDropManager'ı başlatır.
        
        Args:
            master: Ana pencere referansı
            on_file_open: Dosya açma callback'i
            on_folder_open: Klasör açma callback'i
        """
        self.master = master
        self.on_file_open = on_file_open
        self.on_folder_open = on_folder_open
        
        # Overlay oluştur
        self.overlay = DropZoneOverlay(
            master,
            on_file_drop=on_file_open,
            on_folder_drop=on_folder_open
        )
        
        # Dil yöneticisi
        self._lang = self._get_language_manager()
        
        # Sürükleme durumu
        self._dragging = False
        self._pending_files: List[str] = []
    
    def _get_language_manager(self) -> 'LanguageManager':
        """Dil yöneticisini döndürür."""
        from text_editor.utils.language_manager import LanguageManager
        return LanguageManager.get_instance()
    
    # -------------------------------------------------------------------------
    # Drag & Drop Event Handler'ları
    # -------------------------------------------------------------------------
    
    def on_drag_enter(self, event) -> None:
        """
        Sürükleme pencereye girdiğinde çağrılır.
        
        Args:
            event: TkinterDnD event objesi
        """
        self._dragging = True
        
        try:
            files = self.master.tk.splitlist(event.data)
            self._pending_files = list(files)
            self.overlay.show(self._pending_files)
        except Exception:
            self.overlay.show()
    
    def on_drag_leave(self, event) -> None:
        """
        Sürükleme pencereden çıktığında çağrılır.
        
        Args:
            event: TkinterDnD event objesi
        """
        self._dragging = False
        self._pending_files = []
        self.overlay.hide()
    
    def on_drop(self, event) -> List[str]:
        """
        Dosya/klasör bırakıldığında çağrılır.
        
        Args:
            event: TkinterDnD event objesi
            
        Returns:
            Açılan dosyaların listesi
        """
        self._dragging = False
        
        if not event.data:
            self.overlay.hide()
            return []
        
        # Dosya listesini ayrıştır
        try:
            files = self.master.tk.splitlist(event.data)
        except Exception:
            self.overlay.hide()
            return []
        
        # Flash efekti veya overlay gizle
        self._handle_drop_visual(list(files))
        
        # Dosyaları işle
        return self._process_dropped_files(files)
    
    def _handle_drop_visual(self, files: List[str]) -> None:
        """Bırakma işlemi için görsel geri bildirimi yönetir."""
        if not self.overlay._is_visible:
            self._show_drop_flash(files)
        else:
            self.overlay.hide()
    
    def _show_drop_flash(self, files: List[str]) -> None:
        """
        Drop işlemi için kısa süreli görsel bildirim gösterir.
        
        Args:
            files: Bırakılan dosyaların listesi
        """
        self.overlay.show(files)
        self.master.after(AnimationConfig.DROP_FLASH_DURATION_MS, self.overlay.hide)
    
    def _process_dropped_files(self, files: tuple) -> List[str]:
        """
        Bırakılan dosyaları işler.
        
        Args:
            files: Dosya yolları tuple'ı
            
        Returns:
            Açılan tüm öğelerin listesi
        """
        opened_files: List[str] = []
        opened_folders: List[str] = []
        
        for file_path in files:
            file_path = self._clean_file_path(file_path)
            
            if os.path.isdir(file_path):
                if self.on_folder_open:
                    self.on_folder_open(file_path)
                    opened_folders.append(file_path)
            elif os.path.isfile(file_path):
                if self.on_file_open:
                    self.on_file_open(file_path)
                    opened_files.append(file_path)
        
        self._report_status(opened_files, opened_folders)
        return opened_files + opened_folders
    
    def _clean_file_path(self, file_path: str) -> str:
        """Dosya yolunu temizler (Windows {} karakterleri)."""
        return file_path.strip('{}')
    
    # -------------------------------------------------------------------------
    # Durum Raporlama
    # -------------------------------------------------------------------------
    
    def _report_status(self, files: List[str], folders: List[str]) -> None:
        """
        Açılan dosya/klasör durumunu bildirir.
        
        Args:
            files: Açılan dosyalar
            folders: Açılan klasörler
        """
        if not (files or folders):
            return
        
        if not self._has_visible_status_bar():
            return
        
        message = self._create_status_message(files, folders)
        self.master.status_bar.set_message(message, "success")
    
    def _has_visible_status_bar(self) -> bool:
        """Status bar'ın görünür olup olmadığını kontrol eder."""
        return (
            hasattr(self.master, 'status_bar') and 
            hasattr(self.master, '_status_bar_visible') and
            self.master._status_bar_visible
        )
    
    def _create_status_message(self, files: List[str], folders: List[str]) -> str:
        """Durum mesajını oluşturur."""
        if len(files) == 1 and not folders:
            return self._format_message(
                "drop_zone.file_opened",
                "📄 {name} açıldı",
                name=os.path.basename(files[0])
            )
        
        if len(folders) == 1 and not files:
            return self._format_message(
                "drop_zone.folder_opened",
                "📂 {name} açıldı",
                name=os.path.basename(folders[0])
            )
        
        total = len(files) + len(folders)
        return self._format_message(
            "drop_zone.items_opened",
            "✅ {count} öğe açıldı",
            count=total,
            file_count=len(files),
            folder_count=len(folders)
        )
    
    def _format_message(self, key: str, default: str, **kwargs) -> str:
        """Lokalize mesajı formatlar."""
        template = self._lang.get(key, default)
        try:
            return template.format(**kwargs)
        except Exception:
            return default.format(**kwargs)
    
    # -------------------------------------------------------------------------
    # Dosya Kontrolleri
    # -------------------------------------------------------------------------
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Dosyanın desteklenip desteklenmediğini kontrol eder.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Destekleniyorsa True
        """
        return FileTypeRegistry.is_supported(file_path)
    
    def is_image_file(self, file_path: str) -> bool:
        """
        Dosyanın resim dosyası olup olmadığını kontrol eder.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Resim dosyasıysa True
        """
        return FileTypeRegistry.is_image(file_path)
    
    # -------------------------------------------------------------------------
    # Tema Güncelleme
    # -------------------------------------------------------------------------
    
    def update_theme(self, theme: Dict[str, str]) -> None:
        """
        Temayı günceller.
        
        Args:
            theme: Tema sözlüğü
        """
        self.overlay.update_theme(theme)


# =============================================================================
# GERİYE DÖNÜK UYUMLULUK
# =============================================================================

# Eski API'yi desteklemek için fonksiyonları dışa aktar
def hex_to_rgb(hex_color: str) -> tuple:
    """Eski API uyumluluğu için wrapper."""
    return ColorUtils.hex_to_rgb(hex_color)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Eski API uyumluluğu için wrapper."""
    return ColorUtils.rgb_to_hex(r, g, b)


def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Eski API uyumluluğu için wrapper."""
    return ColorUtils.lighten(hex_color, factor)


def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """Eski API uyumluluğu için wrapper."""
    return ColorUtils.darken(hex_color, factor)
