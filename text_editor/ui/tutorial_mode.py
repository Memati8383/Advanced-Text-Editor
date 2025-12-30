import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, field
import platform
import weakref
from contextlib import suppress

# --- Yapılandırma & Sabitler ---
class TutorialConfig:
    """Eğitim görünümü ve davranışı için merkezi yapılandırma."""
    
    # Renk paletleri (light, dark)
    COLORS: Dict[str, tuple] = {
        "primary": ("#3b8ed0", "#1f6aa5"),
        "primary_dark": ("#1f6aa5", "#144870"), 
        "primary_light": ("#5fa8e6", "#3685c5"),
        "bg_main": ("#f8f9fa", "#18181b"),
        "bg_secondary": ("#e9ecef", "#27272a"),
        "bg_glass": ("#ffffff", "#18181b"),
        "text_main": ("#212529", "#f4f4f5"),
        "text_sub": ("#6c757d", "#a1a1aa"),
        "bg_badge": ("#e0f2fe", "#1e293b"),
        "task_bg": ("#e8f5fb", "#1e293b"),
        "task_border": ("#3b8ed0", "#0ea5e9"),
        "task_text": ("#0c5460", "#e0f2fe"),
        "tips_bg": ("#fff8e1", "#422006"),
        "tips_border": ("#ffc107", "#f59e0b"),
        "tips_text": ("#856404", "#fef3c7"),
        "success": ("#28a745", "#22c55e"),
        "warning": ("#ffc107", "#eab308"),
        "error": ("#dc3545", "#ef4444"),
        "separator": ("#dee2e6", "#3f3f46"),
        "transparent_key": "#000001",
    }
    
    # Font tanımları
    FONTS: Dict[str, tuple] = {
        "header_icon": ("Segoe UI Emoji", 54),
        "header_title": ("Segoe UI", 28, "bold"),
        "header_subtitle": ("Segoe UI", 14),
        "step_badge": ("Segoe UI", 12, "bold"),
        "content_icon": ("Segoe UI Emoji", 48),
        "content_body": ("Segoe UI", 15),
        "card_header": ("Segoe UI", 14, "bold"),
        "card_body": ("Segoe UI", 13),
        "spotlight_icon": ("Segoe UI Emoji", 36),
        "button_bold": ("Segoe UI", 14, "bold"),
        "ui_regular": ("Segoe UI", 12),
        "ui_small": ("Segoe UI", 11),
    }
    
    # Animasyon parametreleri
    ANIMATION: Dict[str, float] = {
        "fade_step_in": 0.08,
        "fade_step_out": 0.12,
        "fade_delay": 20,
        "pulse_min": 0.0,
        "pulse_max": 9.0,
        "pulse_speed": 0.8,
        "validation_interval": 500,
        "auto_advance_delay": 1500,
    }

    # Boyut sabitleri
    DIMENSIONS: Dict[str, Any] = {
        "spotlight_msg_w": 480,
        "spotlight_msg_h": 200,
        "window_width": 650,
        "window_height": 750,
        "padding_std": 24,
        "corner_radius": 16,
    }
    
    # Klavye kısayolları
    KEYBINDINGS: Dict[str, str] = {
        "next": "<Right>",
        "prev": "<Left>",
        "skip": "<Escape>",
        "pause": "<space>",
    }


# --- Yardımcı Fonksiyonlar ---
def safe_widget_exists(widget: Optional[tk.Widget]) -> bool:
    """Widget'ın güvenli bir şekilde var olup olmadığını kontrol eder."""
    if widget is None:
        return False
    try:
        return widget.winfo_exists()
    except (tk.TclError, AttributeError):
        return False


def safe_call(func: Optional[Callable], *args, default=None, **kwargs):
    """Fonksiyonu güvenli bir şekilde çağırır, hata durumunda default değer döner."""
    if func is None:
        return default
    try:
        return func(*args, **kwargs)
    except Exception:
        return default


def get_widget_rect(widget: Optional[tk.Widget]) -> Optional[tuple]:
    """Widget'ın ekran koordinatlarını güvenli bir şekilde alır."""
    if not safe_widget_exists(widget):
        return None
    try:
        return (
            widget.winfo_rootx(),
            widget.winfo_rooty(),
            widget.winfo_width(),
            widget.winfo_height()
        )
    except (tk.TclError, AttributeError):
        return None


# --- Veri Yapıları ---
@dataclass
class TutorialStep:
    """Eğitim dizisindeki tek bir adımı temsil eder."""
    title: str
    message: str
    icon: str = "💡"
    target_widget: Optional[Callable[[], Optional[tk.Widget]]] = None
    action: Optional[Callable] = None
    validation: Optional[Callable[[], bool]] = None
    highlight_pos: str = "bottom"
    auto_advance: bool = False
    wait_time: int = 8000
    tips: List[str] = field(default_factory=list)
    
    def get_target(self) -> Optional[tk.Widget]:
        """Hedef widget'ı güvenli bir şekilde alır."""
        return safe_call(self.target_widget) if callable(self.target_widget) else self.target_widget
    
    def check_validation(self) -> bool:
        """Validation'ı güvenli bir şekilde çalıştırır."""
        return safe_call(self.validation, default=False) if self.validation else False


# --- İçerik Sağlayıcısı ---
class TutorialContent:
    """Eğitim için içerik sağlar."""
    
    # Adım tanımları için önbellek
    _steps_cache: Optional[List[TutorialStep]] = None
    
    @classmethod
    def clear_cache(cls):
        """Önbelleği temizler."""
        cls._steps_cache = None
    
    @staticmethod
    def _create_safe_validation(app, check_func: Callable[[], bool]) -> Callable[[], bool]:
        """Güvenli validation wrapper oluşturur."""
        def safe_validation():
            try:
                return check_func()
            except (AttributeError, TypeError, KeyError, tk.TclError):
                return False
        return safe_validation
    
    @staticmethod
    def get_steps(app_instance) -> List[TutorialStep]:
        """Eğitim adımlarını oluşturur ve döndürür."""
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        
        # Sık kullanılan validation'lar için yardımcı fonksiyonlar
        def has_tab_manager() -> bool:
            return hasattr(app_instance, 'tab_manager') and app_instance.tab_manager is not None
        
        def get_current_editor():
            if not has_tab_manager():
                return None
            return safe_call(app_instance.tab_manager.get_current_editor)
        
        def has_editors() -> bool:
            if not has_tab_manager():
                return False
            return len(getattr(app_instance.tab_manager, 'editors', {})) > 0
        
        def has_image_viewer() -> bool:
            if not has_tab_manager():
                return False
            editors = getattr(app_instance.tab_manager, 'editors', {})
            return any(type(ed).__name__ == 'ImageViewer' for ed in editors.values())
        
        def has_text_content() -> bool:
            editor = get_current_editor()
            if not editor:
                return False
            text_area = getattr(editor, 'text_area', None)
            if not safe_widget_exists(text_area):
                return False
            try:
                content = text_area.get("1.0", "end-1c")
                return len(content) > 5
            except tk.TclError:
                return False
        
        def is_find_replace_open() -> bool:
            if not has_tab_manager():
                return False
            frw = getattr(app_instance.tab_manager, 'find_replace_window', None)
            return safe_widget_exists(frw)
        
        def is_goto_dialog_open() -> bool:
            dialog = getattr(app_instance, 'goto_line_dialog', None)
            return safe_widget_exists(dialog)
        
        def is_terminal_visible() -> bool:
            return getattr(app_instance, '_terminal_visible', False)
        
        # Widget getter fonksiyonları
        def get_menu_frame():
            return getattr(app_instance, 'menu_frame', None)
        
        def get_file_explorer():
            return getattr(app_instance, 'file_explorer', None)
        
        def get_editor_text_area():
            editor = get_current_editor()
            if not editor:
                return None
            return getattr(editor, 'text_area', None)
        
        def get_minimap():
            return getattr(app_instance, 'minimap', None)
        
        def get_tab_manager():
            return getattr(app_instance, 'tab_manager', None)
        
        def get_status_bar():
            return getattr(app_instance, 'status_bar', None)
        
        # Adımları oluştur
        steps = [
            TutorialStep(
                title=lang.get("tutorial.steps.welcome.title"), 
                message=lang.get("tutorial.steps.welcome.message"), 
                icon="🚀", 
                auto_advance=False,
                tips=lang.get("tutorial.steps.welcome.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.menus.title"), 
                message=lang.get("tutorial.steps.menus.message"), 
                icon="🎛️",
                target_widget=get_menu_frame,
                highlight_pos="bottom", 
                auto_advance=True, 
                wait_time=6000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.file_explorer.title"), 
                message=lang.get("tutorial.steps.file_explorer.message"), 
                icon="📂",
                target_widget=get_file_explorer,
                highlight_pos="right",
                validation=None,
                tips=lang.get("tutorial.steps.file_explorer.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.image_viewer.title"), 
                message=lang.get("tutorial.steps.image_viewer.message"), 
                icon="🖼️", 
                validation=has_image_viewer,
                tips=lang.get("tutorial.steps.image_viewer.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.new_tab.title"), 
                message=lang.get("tutorial.steps.new_tab.message"), 
                icon="📝",
                validation=has_editors,
                tips=lang.get("tutorial.steps.new_tab.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.editor_area.title"), 
                message=lang.get("tutorial.steps.editor_area.message"), 
                icon="✨", 
                target_widget=get_editor_text_area,
                highlight_pos="bottom",
                validation=has_text_content,
                tips=lang.get("tutorial.steps.editor_area.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.minimap.title"), 
                message=lang.get("tutorial.steps.minimap.message"), 
                icon="🗺️", 
                target_widget=get_minimap,
                highlight_pos="left",
                auto_advance=True, 
                wait_time=7000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.multi_cursor.title"), 
                message=lang.get("tutorial.steps.multi_cursor.message"), 
                icon="🖱️", 
                auto_advance=False,
                tips=lang.get("tutorial.steps.multi_cursor.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.smart_select.title"), 
                message=lang.get("tutorial.steps.smart_select.message"), 
                icon="⚡", 
                auto_advance=False
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.find_replace.title"), 
                message=lang.get("tutorial.steps.find_replace.message"), 
                icon="🔍",
                target_widget=get_tab_manager, 
                highlight_pos="top",
                validation=is_find_replace_open
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.goto_line.title"),
                message=lang.get("tutorial.steps.goto_line.message"), 
                icon="🔢",
                validation=is_goto_dialog_open,
                tips=lang.get("tutorial.steps.goto_line.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.terminal.title"), 
                message=lang.get("tutorial.steps.terminal.message"), 
                icon="💻",
                validation=is_terminal_visible,
                tips=lang.get("tutorial.steps.terminal.tips") or []
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.settings.title"),
                message=lang.get("tutorial.steps.settings.message"),
                icon="⚙️",
                auto_advance=True,
                wait_time=6000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.theme.title"),
                message=lang.get("tutorial.steps.theme.message"),
                icon="🎨",
                tips=lang.get("tutorial.steps.theme.tips") or [],
                auto_advance=True,
                wait_time=6000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.code_folding.title"),
                message=lang.get("tutorial.steps.code_folding.message"),
                icon="📁",
                auto_advance=True,
                wait_time=6000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.status_bar.title"),
                message=lang.get("tutorial.steps.status_bar.message"),
                icon="ℹ️",
                target_widget=get_status_bar,
                highlight_pos="top",
                auto_advance=True,
                wait_time=6000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.markdown.title"), 
                message=lang.get("tutorial.steps.markdown.message"), 
                icon="👁️", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.zen_mode.title"), 
                message=lang.get("tutorial.steps.zen_mode.message"), 
                icon="🧘", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title=lang.get("tutorial.steps.congrats.title"), 
                message=lang.get("tutorial.steps.congrats.message"), 
                icon="🏆", 
                auto_advance=False,
                tips=lang.get("tutorial.steps.congrats.tips") or []
            )
        ]
        
        return steps


# --- Arayüz Sınıfları ---
class ModernSpotlight(ctk.CTkToplevel):
    """Windows'ta tıkla-geç (click-through) özelliği destekleyen interaktif spotlight."""
    
    # Canvas öğe etiketleri
    _TAGS = ("overlay", "hole", "pulse_rect", "inner_rect", "label_bg", "label_text")
    
    def __init__(self, parent, target_widget: tk.Widget, title: str, 
                 position: str = "bottom", step_num: int = 1, total: int = 20):
        super().__init__(parent)
        
        self.target_widget = target_widget
        self.title_text = title
        self.position = position
        
        # Animasyon durumu
        self.pulse_val = 0.0
        self.pulse_dir = 1
        self._is_destroyed = False
        self._pulse_job_id: Optional[str] = None
        
        # Önceki koordinatlar (gereksiz yeniden çizimi önlemek için)
        self._last_rect: Optional[tuple] = None
        
        self._setup_window(parent)
        self._create_canvas()
        self._configure_transparency()
        self._start_pulse()
        
        # Pencere boyutu değişimlerini izle
        self.bind("<Configure>", self._on_configure)

    def _setup_window(self, parent):
        """Pencere özelliklerini yapılandırır."""
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

    def _create_canvas(self):
        """Canvas'ı oluşturur."""
        self.canvas = tk.Canvas(
            self, 
            bg="black",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

    def _configure_transparency(self):
        """Şeffaflık ayarlarını yapılandırır."""
        self.attributes("-alpha", 0.75)
        
        if platform.system() == "Windows":
            self.attributes("-transparentcolor", TutorialConfig.COLORS["transparent_key"])

    def _start_pulse(self):
        """Pulse animasyonunu başlatır."""
        self._pulse()

    def _on_configure(self, event):
        """Pencere değişikliklerinde spotlight'ı yeniden çizer."""
        self._schedule_redraw()

    def _schedule_redraw(self):
        """Yeniden çizimi planlar (performans için debounce)."""
        self.draw_spotlight()

    def _get_target_rect(self) -> Optional[tuple]:
        """Hedef widget'ın dikdörtgen koordinatlarını alır."""
        return get_widget_rect(self.target_widget)

    def draw_spotlight(self):
        """Spotlight efektini çizer veya günceller."""
        if self._is_destroyed:
            return
            
        rect = self._get_target_rect()
        w_screen = self.winfo_screenwidth()
        h_screen = self.winfo_screenheight()
        
        # Overlay oluştur veya güncelle
        self._ensure_overlay(w_screen, h_screen)
        
        if rect:
            # Koordinatlar değişmediyse sadece pulse'ı güncelle
            if self._last_rect != rect:
                self._update_spotlight_elements(rect)
                self._last_rect = rect
            else:
                self._update_pulse_only(rect)
        else:
            self._hide_spotlight_elements()

    def _ensure_overlay(self, w: int, h: int):
        """Overlay'in var olduğundan emin olur."""
        if not self.canvas.find_withtag("overlay"):
            self.canvas.create_rectangle(0, 0, w, h, fill="black", outline="", tags="overlay")
        else:
            self.canvas.coords("overlay", 0, 0, w, h)

    def _update_spotlight_elements(self, rect: tuple):
        """Tüm spotlight öğelerini günceller."""
        x, y, w, h = rect
        pad = 5
        key_color = TutorialConfig.COLORS["transparent_key"]
        pulse_color = TutorialConfig.COLORS["primary"][0]
        
        # Delik
        if not self.canvas.find_withtag("hole"):
            self.canvas.create_rectangle(0, 0, 0, 0, fill=key_color, outline="", tags="hole")
        self.canvas.coords("hole", x - pad, y - pad, x + w + pad, y + h + pad)
        
        # Pulse çerçevesi
        if not self.canvas.find_withtag("pulse_rect"):
            self.canvas.create_rectangle(0, 0, 0, 0, outline=pulse_color, width=2, tags="pulse_rect")
        self._update_pulse_rect(rect)
        
        # İç çerçeve
        if not self.canvas.find_withtag("inner_rect"):
            self.canvas.create_rectangle(0, 0, 0, 0, outline="white", width=1, tags="inner_rect")
        self.canvas.coords("inner_rect", x - pad, y - pad, x + w + pad, y + h + pad)
        
        # Etiket
        self._update_label(rect)

    def _update_pulse_only(self, rect: tuple):
        """Sadece pulse efektini günceller."""
        self._update_pulse_rect(rect)

    def _update_pulse_rect(self, rect: tuple):
        """Pulse dikdörtgenini günceller."""
        x, y, w, h = rect
        pad = 5
        offset = self.pulse_val
        
        self.canvas.coords(
            "pulse_rect",
            x - pad - offset, y - pad - offset,
            x + w + pad + offset, y + h + pad + offset
        )

    def _update_label(self, rect: tuple):
        """Etiketi günceller."""
        x, y, w, h = rect
        label_y = y - 40 if y > 50 else y + h + 20
        
        # Metin
        if not self.canvas.find_withtag("label_text"):
            self.canvas.create_text(
                0, 0, text=self.title_text, fill="white", 
                anchor="w", font=("Segoe UI", 12, "bold"), 
                tags="label_text"
            )
        
        self.canvas.itemconfigure("label_text", text=self.title_text)
        self.canvas.coords("label_text", x, label_y)
        
        # Arka plan
        bbox = self.canvas.bbox("label_text")
        if bbox:
            padding_x, padding_y = 10, 5
            
            if not self.canvas.find_withtag("label_bg"):
                self.canvas.create_rectangle(
                    0, 0, 0, 0, 
                    fill=TutorialConfig.COLORS["primary"][1], 
                    outline="white", width=1, 
                    tags="label_bg"
                )
                self.canvas.tag_lower("label_bg", "label_text")
            
            self.canvas.coords(
                "label_bg",
                bbox[0] - padding_x, bbox[1] - padding_y,
                bbox[2] + padding_x, bbox[3] + padding_y
            )

    def _hide_spotlight_elements(self):
        """Overlay hariç tüm spotlight öğelerini gizler."""
        for tag in ("hole", "pulse_rect", "inner_rect", "label_bg", "label_text"):
            with suppress(tk.TclError):
                self.canvas.coords(tag, -500, -500, -500, -500)

    def _pulse(self):
        """Pulse animasyonunu çalıştırır."""
        if self._is_destroyed or not self.winfo_exists():
            return
        
        anim = TutorialConfig.ANIMATION
        self.pulse_val += self.pulse_dir * anim["pulse_speed"]
        
        if self.pulse_val >= anim["pulse_max"]:
            self.pulse_dir = -1
        elif self.pulse_val <= anim["pulse_min"]:
            self.pulse_dir = 1
        
        self.draw_spotlight()
        self._pulse_job_id = self.after(50, self._pulse)
    
    def fade_out(self, callback: Optional[Callable] = None):
        """Spotlight'ı kapatır."""
        self._cleanup()
        if callback:
            callback()

    def _cleanup(self):
        """Kaynakları temizler."""
        if hasattr(self, '_cleaned_up') and self._cleaned_up:
            return
        self._cleaned_up = True
        
        self._is_destroyed = True
        
        # Bekleyen animasyonları iptal et
        if self._pulse_job_id:
            with suppress(tk.TclError):
                self.after_cancel(self._pulse_job_id)
            self._pulse_job_id = None
            
        # self.destroy() ÇAĞIRMIYORUZ - Recursion önlemek için

    def destroy(self):
        """Pencereyi kapatırken temizlik yapar."""
        self._cleanup()
        with suppress(tk.TclError):
            super().destroy()


class ModernTutorialWindow(ctk.CTkToplevel):
    """Adımları ve kullanıcı etkileşimini yöneten ana eğitim arayüzü."""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        
        from text_editor.utils.language_manager import LanguageManager
        self.lang = LanguageManager.get_instance()
        
        # Uygulama referansı (weak reference ile bellek sızıntısını önle)
        self._app_ref = weakref.ref(app_instance)
        
        # Durum değişkenleri
        self.current_step_index = 0
        self.spotlight: Optional[ModernSpotlight] = None
        self.is_paused = False
        self.completed_steps: set = set()
        self._is_destroyed = False
        
        # Planlanmış işler
        self._scheduled_jobs: Dict[str, str] = {}
        
        # Sürükleme verileri
        self._drag_data = {"x": 0, "y": 0}
        
        # Arayüzü oluştur
        self._setup_window()
        self._init_ui()
        self._bind_keys()
        
        # Adımları yükle
        self.steps = TutorialContent.get_steps(app_instance)
        
        # Başlangıç animasyonları
        self._schedule("fade_in", 100, self.fade_in)
        self._schedule("show_step", 300, self.show_step)
    
    @property
    def app(self):
        """Uygulama örneğine erişim."""
        return self._app_ref() if self._app_ref else None

    def _schedule(self, name: str, delay: int, callback: Callable):
        """Zamanlı işi kaydet ve planla."""
        self._cancel_scheduled(name)
        self._scheduled_jobs[name] = self.after(delay, callback)

    def _cancel_scheduled(self, name: str):
        """Planlanmış işi iptal et."""
        if name in self._scheduled_jobs:
            with suppress(tk.TclError):
                self.after_cancel(self._scheduled_jobs[name])
            del self._scheduled_jobs[name]

    def _cancel_all_scheduled(self):
        """Tüm planlanmış işleri iptal et."""
        for job_id in list(self._scheduled_jobs.values()):
            with suppress(tk.TclError):
                self.after_cancel(job_id)
        self._scheduled_jobs.clear()

    def _setup_window(self):
        """Pencere özelliklerini yapılandırır."""
        self.title(self.lang.get("tutorial.title"))
        
        dims = TutorialConfig.DIMENSIONS
        self.geometry(f"{dims['window_width']}x{dims['window_height']}")
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        # Grid yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Ekranın ortasına yerleştir
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w, win_h = dims['window_width'], dims['window_height']
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        # Arkaplan
        self.configure(fg_color=TutorialConfig.COLORS["bg_main"])
        
        # Ana container
        self.main_container = ctk.CTkFrame(
            self, 
            fg_color=TutorialConfig.COLORS["bg_main"], 
            corner_radius=dims["corner_radius"], 
            border_width=1, 
            border_color="gray30"
        )
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

    def _init_ui(self):
        """UI bileşenlerini oluşturur."""
        self._create_custom_title_bar()
        self._create_header_area()
        self._create_content_area()
        self._create_footer_controls()

    def _bind_keys(self):
        """Klavye kısayollarını bağlar."""
        bindings = TutorialConfig.KEYBINDINGS
        self.bind(bindings["next"], lambda e: self.next_step())
        self.bind(bindings["prev"], lambda e: self.prev_step())
        self.bind(bindings["skip"], lambda e: self.skip_tutorial())
        self.bind(bindings["pause"], lambda e: self.toggle_pause())

    def _create_custom_title_bar(self):
        """Özel başlık çubuğunu oluşturur."""
        title_bar = ctk.CTkFrame(self.main_container, height=40, corner_radius=0, fg_color="transparent")
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.grid_propagate(False)
        
        # Sürükleme olayları
        title_bar.bind("<Button-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)
        
        # Başlık etiketi
        title_lbl = ctk.CTkLabel(
            title_bar, 
            text="MEMATI EDITÖR", 
            font=("Segoe UI", 12, "bold"), 
            text_color=TutorialConfig.COLORS["text_sub"]
        )
        title_lbl.pack(side="left", padx=20)
        title_lbl.bind("<Button-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)
        
        # Kapat butonu
        close_btn = ctk.CTkButton(
            title_bar, 
            text="✕", 
            width=40, 
            height=40,
            fg_color="transparent", 
            hover_color="#c42b1c",
            font=("Arial", 14),
            command=self.finish
        )
        close_btn.pack(side="right")

    def _start_drag(self, event):
        """Sürüklemeyi başlatır."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_drag(self, event):
        """Pencereyi sürükler."""
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def _create_header_area(self):
        """Header alanını oluşturur."""
        header = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 20))
        
        head_top = ctk.CTkFrame(header, fg_color="transparent")
        head_top.pack(fill="x")
        
        self.title_lbl = ctk.CTkLabel(
            head_top, 
            text=self.lang.get("tutorial.header_welcome"), 
            font=TutorialConfig.FONTS["header_title"], 
            text_color=TutorialConfig.COLORS["text_main"],
            anchor="w"
        )
        self.title_lbl.pack(side="left", fill="x", expand=True)

        self.step_badge = ctk.CTkLabel(
            head_top, 
            text="1 / 14", 
            font=TutorialConfig.FONTS["step_badge"], 
            text_color=TutorialConfig.COLORS["primary"],
            fg_color=TutorialConfig.COLORS["bg_badge"],
            corner_radius=8, 
            width=80, 
            height=30
        )
        self.step_badge.pack(side="right")
        
        self.prog = ctk.CTkProgressBar(
            header, 
            height=6, 
            corner_radius=3, 
            progress_color=TutorialConfig.COLORS["primary"]
        )
        self.prog.pack(fill="x", pady=(15, 0))
        self.prog.set(0)

    def _create_content_area(self):
        """İçerik alanını oluşturur."""
        self.content = ctk.CTkScrollableFrame(
            self.main_container, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.content.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        
        # İkon etiketi
        self.icon_lbl = ctk.CTkLabel(
            self.content, 
            text="💡", 
            font=TutorialConfig.FONTS["content_icon"]
        )
        self.icon_lbl.pack(pady=(20, 15))
        
        # Mesaj etiketi
        self.msg_lbl = ctk.CTkLabel(
            self.content, 
            text="", 
            font=TutorialConfig.FONTS["content_body"], 
            text_color=TutorialConfig.COLORS["text_main"],
            wraplength=540, 
            justify="center"
        )
        self.msg_lbl.pack(fill="x", padx=10, pady=(0, 30))
        
        # Görev kartı
        self.task_card = ctk.CTkFrame(
            self.content, 
            corner_radius=12, 
            fg_color=TutorialConfig.COLORS["task_bg"],
            border_width=1, 
            border_color=TutorialConfig.COLORS["task_border"]
        )
        
        ctk.CTkLabel(
            self.task_card, 
            text=self.lang.get("tutorial.labels.task"), 
            font=TutorialConfig.FONTS["ui_small"],
            text_color=TutorialConfig.COLORS["task_border"]
        ).pack(anchor="w", padx=20, pady=(15, 0))
        
        self.task_lbl = ctk.CTkLabel(
            self.task_card, 
            text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["task_text"], 
            wraplength=500, 
            justify="left"
        )
        self.task_lbl.pack(anchor="w", padx=20, pady=(5, 15))
        
        # İpuçları kartı
        self.tips_card = ctk.CTkFrame(
            self.content, 
            corner_radius=12, 
            fg_color=TutorialConfig.COLORS["tips_bg"],
            border_width=0
        )
        
        ctk.CTkLabel(
            self.tips_card, 
            text=self.lang.get("tutorial.labels.tip"), 
            font=TutorialConfig.FONTS["ui_small"],
            text_color=TutorialConfig.COLORS["tips_border"]
        ).pack(anchor="w", padx=20, pady=(15, 0))
        
        self.tips_lbl = ctk.CTkLabel(
            self.tips_card, 
            text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["tips_text"], 
            wraplength=500, 
            justify="left"
        )
        self.tips_lbl.pack(anchor="w", padx=20, pady=(5, 15))

    def _create_footer_controls(self):
        """Alt kontrol butonlarını oluşturur."""
        ctrl = ctk.CTkFrame(
            self.main_container, 
            corner_radius=0, 
            fg_color=TutorialConfig.COLORS["bg_secondary"], 
            height=90
        )
        ctrl.grid(row=3, column=0, sticky="ew")
        ctrl.grid_propagate(False)
        
        btn_container = ctk.CTkFrame(ctrl, fg_color="transparent")
        btn_container.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Geri butonu
        self.prev_btn = ctk.CTkButton(
            btn_container, 
            text=self.lang.get("tutorial.buttons.back"), 
            width=100, 
            height=45, 
            corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color="transparent", 
            border_width=1, 
            border_color=TutorialConfig.COLORS["text_sub"],
            text_color=TutorialConfig.COLORS["text_main"], 
            hover_color=("gray85", "gray25"),
            command=self.prev_step, 
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=0)
        
        # Duraklat butonu
        self.pause_btn = ctk.CTkButton(
            btn_container, 
            text=self.lang.get("tutorial.buttons.pause"), 
            width=120, 
            height=45, 
            corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["warning"], 
            hover_color="#d97706", 
            text_color="white",
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=15)
        
        # İleri butonu
        self.next_btn = ctk.CTkButton(
            btn_container, 
            text=self.lang.get("tutorial.buttons.next"), 
            width=160, 
            height=45, 
            corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["primary"], 
            hover_color=TutorialConfig.COLORS["primary_dark"], 
            text_color="white",
            command=self.next_step
        )
        self.next_btn.pack(side="right", padx=0)
        
        # Atla butonu
        self.skip_btn = ctk.CTkButton(
            btn_container, 
            text=self.lang.get("tutorial.buttons.skip"), 
            width=100,
            font=TutorialConfig.FONTS["ui_small"],
            fg_color="transparent", 
            hover_color=("gray90", "gray25"),
            text_color=TutorialConfig.COLORS["text_sub"],
            command=self.skip_tutorial
        )
        self.skip_btn.place(relx=0.5, rely=0.5, anchor="center")

    def show_step(self):
        """Mevcut adımı gösterir."""
        if self._is_destroyed:
            return
            
        if self.current_step_index >= len(self.steps):
            self.finish()
            return
        
        step = self.steps[self.current_step_index]
        self._update_step_ui(step)
        self._handle_cards(step)
        self._handle_step_logic(step)
        self._update_buttons()

    def _update_step_ui(self, step: TutorialStep):
        """Adım UI'ını günceller."""
        self.title_lbl.configure(text=step.title)
        self.icon_lbl.configure(text=step.icon)
        self.msg_lbl.configure(text=step.message)
        
        total = len(self.steps)
        current = self.current_step_index + 1
        progress = current / total
        
        self.prog.set(progress)
        self.step_badge.configure(text=f"{current} / {total}")

    def _handle_cards(self, step: TutorialStep):
        """Kartları yönetir."""
        self.task_card.pack_forget()
        self.tips_card.pack_forget()
        
        if step.validation:
            self.task_card.pack(fill="x", padx=10, pady=(0, 20))
            self.task_lbl.configure(
                text=self.lang.get("tutorial.labels.task_pending"),
                text_color=TutorialConfig.COLORS["task_text"]
            )
            self._start_validation_loop()
        
        if step.tips:
            self.tips_card.pack(fill="x", padx=10, pady=(0, 20))
            tips_text = "\n".join([f"• {t}" for t in step.tips if t])
            self.tips_lbl.configure(text=tips_text)

    def _handle_step_logic(self, step: TutorialStep):
        """Adım mantığını yönetir."""
        # Spotlight yönetimi
        if step.target_widget:
            self.show_spotlight(step)
        else:
            self.hide_spotlight()
        
        # Aksiyon çalıştırma
        if step.action:
            self._schedule("action", 500, step.action)
        
        # Otomatik ilerleme
        if step.auto_advance and not step.validation:
            self._schedule("auto_advance", step.wait_time, self.next_step)

    def _update_buttons(self):
        """Buton durumlarını günceller."""
        self.prev_btn.configure(
            state="normal" if self.current_step_index > 0 else "disabled"
        )
        
        is_last = self.current_step_index == len(self.steps) - 1
        if is_last:
            self.next_btn.configure(
                text=self.lang.get("tutorial.buttons.complete"), 
                command=self.finish
            )
        else:
            self.next_btn.configure(
                text=self.lang.get("tutorial.buttons.next"), 
                command=self.next_step
            )

    def show_spotlight(self, step: TutorialStep):
        """Spotlight'ı gösterir."""
        self.hide_spotlight()
        
        target = step.get_target()
        
        if safe_widget_exists(target):
            try:
                self.spotlight = ModernSpotlight(
                    self.app, 
                    target, 
                    step.title, 
                    step.highlight_pos,
                    self.current_step_index + 1, 
                    len(self.steps)
                )
                self.lift()
            except Exception:
                pass

    def hide_spotlight(self):
        """Spotlight'ı gizler."""
        if self.spotlight:
            with suppress(tk.TclError, AttributeError):
                if safe_widget_exists(self.spotlight):
                    self.spotlight.fade_out()
            self.spotlight = None

    def _start_validation_loop(self):
        """Validation döngüsünü başlatır."""
        self._check_validation()

    def _check_validation(self):
        """Validation'ı kontrol eder."""
        if self._is_destroyed or self.is_paused:
            return
            
        if self.current_step_index >= len(self.steps):
            return
        
        step = self.steps[self.current_step_index]
        if not step.validation:
            return
        
        if step.check_validation():
            self.task_lbl.configure(
                text=self.lang.get("tutorial.labels.task_completed"), 
                text_color=TutorialConfig.COLORS["success"]
            )
            self.completed_steps.add(self.current_step_index)
            self._schedule(
                "validation_advance", 
                int(TutorialConfig.ANIMATION["auto_advance_delay"]), 
                self.next_step
            )
        else:
            self._schedule(
                "validation_check", 
                int(TutorialConfig.ANIMATION["validation_interval"]), 
                self._check_validation
            )

    def next_step(self):
        """Sonraki adıma geçer."""
        if self._is_destroyed:
            return
            
        # Önceki zamanlı işleri temizle
        self._cancel_scheduled("auto_advance")
        self._cancel_scheduled("validation_check")
        self._cancel_scheduled("validation_advance")
        
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.show_step()

    def prev_step(self):
        """Önceki adıma döner."""
        if self._is_destroyed:
            return
            
        # Zamanlı işleri temizle
        self._cancel_scheduled("auto_advance")
        self._cancel_scheduled("validation_check")
        self._cancel_scheduled("validation_advance")
        
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_step()

    def toggle_pause(self):
        """Duraklatma durumunu değiştirir."""
        if self._is_destroyed:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_btn.configure(
                text=self.lang.get("tutorial.buttons.resume"), 
                fg_color=TutorialConfig.COLORS["success"]
            )
            self.hide_spotlight()
            self._cancel_scheduled("auto_advance")
            self._cancel_scheduled("validation_check")
        else:
            self.pause_btn.configure(
                text=self.lang.get("tutorial.buttons.pause"), 
                fg_color=TutorialConfig.COLORS["warning"]
            )
            self.show_step()

    def skip_tutorial(self):
        """Eğitimi atlar."""
        if self._is_destroyed:
            return
            
        result = messagebox.askyesno(
            self.lang.get("tutorial.messages.skip_confirm_title"), 
            self.lang.get("tutorial.messages.skip_confirm_msg"), 
            parent=self
        )
        if result:
            self.finish()

    def finish(self):
        """Eğitimi bitirir."""
        if self._is_destroyed:
            return
            
        self._is_destroyed = True
        self.hide_spotlight()
        
        # Tamamlanma mesajı
        if self.current_step_index == len(self.steps) - 1:
            validation_count = sum(1 for s in self.steps if s.validation)
            messagebox.showinfo(
                self.lang.get("tutorial.messages.completed_title"), 
                self.lang.get("tutorial.messages.completed_msg").format(
                    completed=len(self.completed_steps), 
                    total=validation_count
                ), 
                parent=self
            )
        
        self.fade_out()

    def fade_in(self):
        """Fade-in animasyonu."""
        if self._is_destroyed:
            return
            
        try:
            alpha = self.attributes("-alpha")
            if alpha < 1.0:
                self.attributes("-alpha", alpha + 0.1)
                self._schedule("fade_in", 25, self.fade_in)
        except tk.TclError:
            pass

    def fade_out(self):
        """Fade-out animasyonu."""
        try:
            alpha = self.attributes("-alpha")
            if alpha > 0:
                self.attributes("-alpha", alpha - 0.1)
                self.after(25, self.fade_out)
            else:
                # Animasyon bitti, pencereyi kapat (bu da _cleanup'ı çağırır)
                self.destroy()
        except tk.TclError:
            self.destroy()

    def _cleanup(self):
        """Kaynakları temizler."""
        if hasattr(self, '_cleaned_up') and self._cleaned_up:
            return
        self._cleaned_up = True
            
        self._is_destroyed = True
        self._cancel_all_scheduled()
        self.hide_spotlight()
        
        # self.destroy() ÇAĞIRMIYORUZ - Recursion önlemek için

    def destroy(self):
        """Pencereyi kapatırken temizlik yapar."""
        self._cleanup()
        with suppress(tk.TclError):
            super().destroy()


class TutorialSystem:
    """Eğitim oturumunu yönetir."""
    
    def __init__(self, master_window):
        self.master = master_window
        self.tutorial_window: Optional[ModernTutorialWindow] = None
    
    def start_tutorial(self):
        """Eğitimi başlatır."""
        if self.tutorial_window is None or not safe_widget_exists(self.tutorial_window):
            self.tutorial_window = ModernTutorialWindow(self.master, self.master)
        else:
            with suppress(tk.TclError):
                self.tutorial_window.lift()
                self.tutorial_window.focus()
    
    def stop_tutorial(self):
        """Eğitimi durdurur."""
        if self.tutorial_window and safe_widget_exists(self.tutorial_window):
            with suppress(tk.TclError):
                self.tutorial_window.finish()
        self.tutorial_window = None
    
    def is_running(self) -> bool:
        """Eğitimin çalışıp çalışmadığını kontrol eder."""
        return self.tutorial_window is not None and safe_widget_exists(self.tutorial_window)
