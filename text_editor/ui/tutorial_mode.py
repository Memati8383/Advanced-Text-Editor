import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, List, Tuple
from dataclasses import dataclass, field

# --- Yapılandırma & Sabitler ---
class TutorialConfig:
    """Eğitim görünümü ve davranışı için merkezi yapılandırma."""
    COLORS = {
        "primary": ("#00d4ff", "#00d4ff"),
        "primary_dark": ("#0096c7", "#0096c7"), 
        "primary_light": ("#00b8e6", "#0096c7"),
        "bg_glass": ("rgba(255,255,255,0.95)", "rgba(30,30,30,0.95)"),
        "bg_badge": ("rgba(0,212,255,0.1)", "rgba(0,212,255,0.2)"),
        "text_white": "white",
        "task_bg": ("#e3f2fd", "#1a3a52"),
        "task_border": ("#00d4ff", "#00d4ff"),
        "task_text": ("#1976d2", "#64b5f6"),
        "tips_bg": ("#fff3e0", "#3a2a1a"),
        "tips_border": ("#ff9800", "#ff9800"),
        "tips_text": ("#e65100", "#ffb74d"),
        "success": ("#4caf50", "#388e3c"),
        "warning": ("#ff9800", "#f57c00"),
        "arrow_text": "white",
    }
    
    FONTS = {
        "header_icon": ("Segoe UI", 48),
        "header_title": ("Segoe UI", 24, "bold"),
        "header_subtitle": ("Segoe UI", 12),
        "step_badge": ("Segoe UI", 11, "bold"),
        "content_icon": ("Segoe UI", 42),
        "content_body": ("Segoe UI", 14),
        "card_header": ("Segoe UI", 13, "bold"),
        "card_body": ("Segoe UI", 12),
        "spotlight_icon": ("Segoe UI", 32),
        "button_bold": ("Segoe UI", 13, "bold"),
    }
    
    ANIMATION = {
        "fade_step_in": 0.08,
        "fade_step_out": 0.12,
        "fade_delay": 25,
        "pulse_min": 0.3,
        "pulse_max": 0.8,
        "pulse_speed": 0.05,
    }

    DIMENSIONS = {
        "spotlight_msg_w": 450,
        "spotlight_msg_h": 180,
        "window_size": "600x700",
        "padding_std": 20,
    }


# --- Veri Yapıları ---
@dataclass
class TutorialStep:
    """Eğitim dizisindeki tek bir adımı temsil eder."""
    title: str
    message: str
    icon: str = "💡"
    target_widget: Optional[Callable[[], Optional[tk.Widget]]] = None  # Tembel değerlendirme
    action: Optional[Callable] = None
    validation: Optional[Callable[[], bool]] = None
    highlight_pos: str = "bottom"  # üst, alt, sol, sağ
    auto_advance: bool = False
    wait_time: int = 8000
    tips: List[str] = field(default_factory=list)


# --- İçerik Sağlayıcısı ---
class TutorialContent:
    """Eğitim için içerik sağlar."""
    
    @staticmethod
    def get_steps(app_instance) -> List[TutorialStep]:
        return [
            TutorialStep(
                title="Memati Editör'e Hoş Geldiniz!", 
                message="Merhaba! 👋\n\nBu interaktif öğretici, Memati Editör'ün tüm özelliklerini öğrenmenize yardımcı olacak.\n\n📚 20 adımda şunları öğreneceksiniz:\n• Temel dosya işlemleri\n• Gelişmiş düzenleme araçları\n• Çoklu imleç kullanımı\n• Tema ve görünüm ayarları\n• Terminal ve önizleme özellikleri\n\n⏱️ Süre: Yaklaşık 7 dakika\n🎯 Hedef: Editörü profesyonelce kullanmak\n\nHazır mısınız? Hadi başlayalım! 🚀", 
                icon="🎉", 
                auto_advance=False,
                tips=["İstediğiniz zaman duraklatabilirsiniz", "Her adımda görevleri tamamlayın"]
            ),
            TutorialStep(
                title="Arayüz Genel Bakış", 
                message="Memati Editör modern ve kullanıcı dostu bir arayüze sahip.\n\n🎨 Ana Bileşenler:\n• Üst: Menü çubuğu\n• Sol: Dosya Gezgini\n• Orta: Editör alanı\n• Sağ: Minimap\n• Alt: Durum çubuğu\n\n💡 Tüm paneller gösterilebilir/gizlenebilir!", 
                icon="🖥️", 
                auto_advance=True, 
                wait_time=10000,
                tips=["F11 ile tam ekran", "Ctrl+K, Z ile Zen Mode"]
            ),
            TutorialStep(
                title="Menü Çubuğu", 
                message="Ana menü çubuğunuz. Tüm işlemler burada!\n\n📁 Dosya, ✏️ Düzenle, 👁️ Görünüm, 🎨 Tema, 🎓 Öğretici, ❓ Yardım\n\n💡 Her menüde emoji ikonlar ve kısayollar var!", 
                icon="📁",
                target_widget=lambda: getattr(app_instance, 'menu_frame', None),
                highlight_pos="bottom", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Dosya Gezgini", 
                message="Sol panel: Dosya Gezgini\n\n🌳 Ağaç yapısı, özel ikonlar, çift tıkla aç\n\n⌨️ Ctrl+B: aç/kapat\n\n🎯 Görev: Ctrl+Shift+O ile klasör açın!", 
                icon="📂",
                target_widget=lambda: getattr(app_instance, 'file_explorer', None),
                highlight_pos="right",
                validation=lambda: hasattr(app_instance.file_explorer, 'root_path') and app_instance.file_explorer.root_path,
                tips=["100+ dosya formatı desteklenir"]
            ),
            TutorialStep(
                title="Yeni Dosya", 
                message="Yeni dosya oluşturun!\n\n🎯 Ctrl+N veya Dosya > Yeni Sekme\n\n📝 Python, JS, HTML, CSS, Markdown...\n\n🎯 Görev: Ctrl+N ile yeni sekme açın!", 
                icon="📄",
                validation=lambda: len(app_instance.tab_manager.editors) > 1,
                tips=["Ctrl+S ile kaydedin", "Otomatik kayıt 30sn"]
            ),
            TutorialStep(
                title="Editör - Kod Yazma", 
                message="Editör alanındasınız!\n\n✨ Syntax highlighting, autocomplete, auto-close, smart indent\n\n🎯 Görev: Birkaç satır kod yazın!", 
                icon="✏️", 
                auto_advance=False,
                tips=["Tab: girinti", "Shift+Tab: azalt", "Ctrl+/: yorum"]
            ),
            TutorialStep(
                title="Satır Numaraları & Minimap", 
                message="Yardımcı araçlar!\n\n📊 Sol: Satır numaraları, kod katlama\n🗺️ Sağ: Minimap (kod haritası)\n\n⌨️ Ctrl+M: Minimap, Ctrl+Shift+L: Satır no", 
                icon="🔢", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Çoklu İmleç - Alt+Click", 
                message="En güçlü özellik!\n\n🎯 Alt+Click: İmleç ekle/kaldır\nEscape: Temizle\n\n🎯 Görev: Alt+Click ile 3 imleç ekleyin!", 
                icon="🖱️", 
                auto_advance=False,
                tips=["100+ imleç yavaşlatır"]
            ),
            TutorialStep(
                title="Çoklu İmleç - Ctrl+D", 
                message="Aynı kelimeleri seçin!\n\n🎯 Ctrl+D: Kelime seç, tekrar bas: sonraki\n\n💡 Değişken adı değiştirmek için ideal!\n\n🎯 Görev: Bir kelimeyi Ctrl+D ile seçin!", 
                icon="🎯", 
                auto_advance=False
            ),
            TutorialStep(
                title="Bul ve Değiştir", 
                message="Güçlü arama!\n\n⌨️ Ctrl+F\n\n🔍 Regex, case-sensitive, toplu değiştir\n\n🎯 Görev: Ctrl+F ile arama açın!", 
                icon="🔍",
                validation=lambda: hasattr(app_instance.tab_manager, 'find_replace_window') and 
                                  app_instance.tab_manager.find_replace_window and
                                  app_instance.tab_manager.find_replace_window.winfo_exists()
            ),
            TutorialStep(
                title="Satıra Git", 
                message="Hızlı gezinme!\n\n⌨️ Ctrl+G\n\n🎯 Satır numarası yaz, Enter\n\n🎯 Görev: Ctrl+G ile satır 1'e git!", 
                icon="🎯",
                validation=lambda: hasattr(app_instance.tab_manager, 'goto_window') and 
                                  app_instance.tab_manager.goto_window and
                                  app_instance.tab_manager.goto_window.winfo_exists(),
                tips=["Çok kullanışlı!", "Undo (Ctrl+Z) her zaman çalışır"]
            ),
            TutorialStep(
                title="Satır İşlemleri", 
                message="Satırları düzenleyin!\n\n🔢 Ctrl+Shift+D: Çoğalt\nAlt+↑/↓: Taşı\nCtrl+Shift+K: Sil\nCtrl+J: Birleştir\n\n💡 Çok kullanışlı!", 
                icon="🔢", 
                auto_advance=True, 
                wait_time=10000
            ),
            TutorialStep(
                title="Dosya Yolu Kopyalama", 
                message="Yol kopyalamak çok kolay!\n\n📋 Sekme başlığına sağ tıklayın veya:\nCtrl+Shift+C: Tam Yolu Kopyala\nCtrl+Alt+C: Göreli Yolu Kopyala\n\nTargets: Dosya yolu panosu için ideal!", 
                icon="📋", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Temalar", 
                message="17 premium tema!\n\n🌑 Dark, ☀️ Light\n🧛 Dracula, 🌅 Solarized\n🔥 Monokai, ❄️ Nord\n🍂 Gruvbox, ⚫ One Dark\n🐙 GitHub, 🌃 Synthwave\n🦉 Night Owl, 🗼 Tokyo Night\n\n🎯 Görev: 🎨 Tema menüsünden tema değiştirin!", 
                icon="🎨",
                target_widget=lambda: app_instance.menu_buttons[3] if hasattr(app_instance, 'menu_buttons') and len(app_instance.menu_buttons) > 3 else None,
                highlight_pos="bottom", 
                auto_advance=False,
                tips=["Gece: koyu temalar", "Tema her zaman değiştirilebilir"]
            ),
            TutorialStep(
                title="Terminal", 
                message="Entegre terminal!\n\n⌨️ Ctrl+`\n\n💻 PowerShell/CMD/Bash, ANSI colors, tema uyumlu\n\n🎯 Görev: Ctrl+` ile terminali açın!", 
                icon="⌨️",
                validation=lambda: hasattr(app_instance, '_terminal_visible') and app_instance._terminal_visible,
                tips=["Yeniden boyutlandırılabilir"]
            ),
            TutorialStep(
                title="Markdown Önizleme", 
                message="Markdown dosyaları için!\n\n⌨️ Ctrl+Shift+V\n\n📄 Canlı önizleme, Sync Scroll\n\n📊 Kelime sayacı, Okuma süresi\n\n🔍 Önizleme içinde arama (Ctrl+F)\n\n💡 .md dosyalarında çalışır", 
                icon="📄", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Zoom", 
                message="Yazı boyutunu ayarlayın!\n\n⌨️ Ctrl+Tekerlek: Zoom in/out\nCtrl+0: Sıfırla\n\n💡 8-72 arası", 
                icon="🔎", 
                auto_advance=True, 
                wait_time=6000
            ),
            TutorialStep(
                title="Görünüm Ayarları", 
                message="Panelleri özelleştirin!\n\n🎛️ Ctrl+B: Dosya Gezgini\nCtrl+M: Minimap\nCtrl+Shift+L: Satır no\nAlt+Z: Word Wrap\n\n🧘 Ctrl+K, Z: Zen Mode\nF11: Tam Ekran", 
                icon="👁️", 
                auto_advance=True, 
                wait_time=10000
            ),
            TutorialStep(
                title="Kod Katlama", 
                message="Fonksiyonları katlayın!\n\n📁 Satır numaralarındaki ▼ ▶ işaretleri\n\n💡 Uzun kodlarda çok kullanışlı!", 
                icon="📁", 
                auto_advance=True, 
                wait_time=6000
            ),
            TutorialStep(
                title="Otomatik Kayıt", 
                message="Kodunuz güvende!\n\n💾 Her 30 saniyede otomatik kayıt\n\n💡 Ctrl+S ile manuel kayıt\n\n✅ Dosya değişikliklerini izler", 
                icon="💾", 
                auto_advance=True, 
                wait_time=6000
            ),
            TutorialStep(
                title="Klavye Kısayolları", 
                message="Verimliliği artırın!\n\n⌨️ Yardım > Klavye Kısayolları\n\n💡 En çok kullanılanlar:\nCtrl+N/O/S/F/G\nAlt+Click, Ctrl+D\nCtrl+B/M/`\n\n🎯 Kısayolları ezberleyin!", 
                icon="⌨️", 
                auto_advance=True, 
                wait_time=10000
            ),
            TutorialStep(
                title="Tebrikler! 🎊", 
                message="Harika! Tutorial'ı tamamladınız!\n\n✅ Öğrendikleriniz:\n• Arayüz ve menüler\n• Dosya işlemleri\n• Editör özellikleri\n• Çoklu imleç\n• Bul/değiştir, satıra git\n• Satır işlemleri\n• Temalar\n• Terminal, önizleme\n• Görünüm ayarları\n• Kod katlama\n• Otomatik kayıt\n\n🚀 Sonraki adımlar:\n• Kısayolları ezberleyin\n• Temaları deneyin\n• Çoklu imleç pratik yapın\n• Yardım menüsünü keşfedin\n\nKeyifli kodlamalar! 🎉", 
                icon="🏆", 
                auto_advance=False,
                tips=["Tutorial'ı tekrar başlatabilirsiniz", "Yardım menüsünde daha fazla bilgi"]
            )
        ]


# --- Arayüz Sınıfları ---
class ModernSpotlight(ctk.CTkToplevel):
    """Glassmorphism ve neon parıltılı ultra modern spot ışığı katmanı."""
    
    def __init__(self, parent, target_widget, message, position="bottom", step_num=1, total=20):
        super().__init__(parent)
        self.target_widget = target_widget
        self.message = message
        self.position = position
        self.step_num = step_num
        self.total = total
        
        self.pulse_alpha = 0.3
        self.pulse_dir = 1
        
        self._setup_window(parent)
        self._create_canvas()
        self._create_message_box()
        
        # Animasyonları başlat
        self.after(50, self.fade_in)
    
    def _setup_window(self, parent):
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
    
    def _create_canvas(self):
        self.canvas = tk.Canvas(self, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _create_message_box(self):
        target_coords = self._get_target_coordinates()
        if not target_coords:
            target_coords = self._get_default_center()
            
        msg_x, msg_y = self._calculate_msg_position(*target_coords)
        
        self.msg_frame = ctk.CTkFrame(
            self, 
            corner_radius=20, 
            fg_color=TutorialConfig.COLORS["bg_glass"],
            border_width=2, 
            border_color=TutorialConfig.COLORS["primary"],
            width=TutorialConfig.DIMENSIONS["spotlight_msg_w"], 
            height=TutorialConfig.DIMENSIONS["spotlight_msg_h"]
        )
        
        self._add_msg_content()
        self.msg_frame.place(x=msg_x, y=msg_y)
        
    def _get_target_coordinates(self) -> Optional[Tuple[int, int, int, int]]:
        try:
            return (
                self.target_widget.winfo_rootx(),
                self.target_widget.winfo_rooty(),
                self.target_widget.winfo_width(),
                self.target_widget.winfo_height()
            )
        except (AttributeError, tk.TclError):
            return None

    def _get_default_center(self) -> Tuple[int, int, int, int]:
        return (
            self.winfo_screenwidth() // 2 - 250,
            self.winfo_screenheight() // 2,
            500,
            100
        )

    def _calculate_msg_position(self, x, y, w, h) -> Tuple[int, int]:
        msg_w = TutorialConfig.DIMENSIONS["spotlight_msg_w"]
        msg_h = TutorialConfig.DIMENSIONS["spotlight_msg_h"]
        
        mx, my = 0, 0
        if self.position == "bottom":
            mx = max(20, min(x, self.winfo_screenwidth() - msg_w - 20))
            my = min(y + h + 30, self.winfo_screenheight() - msg_h - 20)
        elif self.position == "top":
            mx = max(20, min(x, self.winfo_screenwidth() - msg_w - 20))
            my = max(20, y - msg_h - 30)
        elif self.position == "right":
            mx = min(x + w + 30, self.winfo_screenwidth() - msg_w - 20)
            my = max(20, min(y, self.winfo_screenheight() - msg_h - 20))
        else: # sol veya varsayılan
            mx = max(20, x - msg_w - 30)
            my = max(20, min(y, self.winfo_screenheight() - msg_h - 20))
            
        return mx, my

    def _add_msg_content(self):
        # Rozet
        badge = ctk.CTkLabel(
            self.msg_frame, 
            text=f"Adım {self.step_num}/{self.total}", 
            font=TutorialConfig.FONTS["step_badge"],
            text_color=TutorialConfig.COLORS["primary"], 
            fg_color=TutorialConfig.COLORS["bg_badge"],
            corner_radius=12, padx=15, pady=5
        )
        badge.pack(anchor="ne", padx=15, pady=15)
        
        # İkon
        icon = ctk.CTkLabel(self.msg_frame, text="💡", font=TutorialConfig.FONTS["spotlight_icon"])
        icon.pack(pady=(10, 5))
        
        # Mesaj
        msg = ctk.CTkLabel(
            self.msg_frame, 
            text=self.message, 
            font=TutorialConfig.FONTS["card_body"], 
            wraplength=400, 
            justify="center"
        )
        msg.pack(padx=20, pady=(5, 20))
        
        # Ok
        arrow_map = {"bottom": "⬆️", "top": "⬇️", "right": "⬅️", "left": "➡️"}
        arrow = ctk.CTkLabel(
            self.msg_frame, 
            text=arrow_map.get(self.position, "👆"), 
            font=("Segoe UI", 20)
        )
        arrow.pack(pady=(0, 10))

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 0.92:
            self.attributes("-alpha", alpha + TutorialConfig.ANIMATION["fade_step_in"])
            self.after(TutorialConfig.ANIMATION["fade_delay"], self.fade_in)
        else:
            self.attributes("-alpha", 0.92)
            self.draw_spotlight()
            self.pulse()
    
    def draw_spotlight(self):
        coords = self._get_target_coordinates()
        if not coords:
            return
            
        x, y, w, h = coords
        padding = 15
        x -= padding
        y -= padding
        w += padding * 2
        h += padding * 2
        
        self.canvas.create_rectangle(
            0, 0, self.winfo_screenwidth(), self.winfo_screenheight(), 
            fill="black", stipple="gray50"
        )
        
        # Parıltı efekti
        glow_colors = ["#00d4ff", "#00b8e6", "#0096c7", "#007ea7"]
        for i, color in enumerate(glow_colors):
            offset = (i + 1) * 8
            self.canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset, 
                outline=color, width=3 - i, tags="glow"
            )
        
        # Vurgu kutusu
        self.canvas.create_rectangle(
            x, y, x + w, y + h, 
            outline="#00ffff", width=4, fill="", tags="highlight"
        )
    
    def pulse(self):
        if not self.winfo_exists():
            return
            
        try:
            self.pulse_alpha += self.pulse_dir * TutorialConfig.ANIMATION["pulse_speed"]
            if self.pulse_alpha >= TutorialConfig.ANIMATION["pulse_max"]:
                self.pulse_dir = -1
            elif self.pulse_alpha <= TutorialConfig.ANIMATION["pulse_min"]:
                self.pulse_dir = 1
                
            self.canvas.itemconfig("glow", width=int(3 + self.pulse_alpha * 2))
        except tk.TclError:
            pass # Widget yok edildi
            
        self.after(50, self.pulse)
    
    def fade_out(self, callback: Optional[Callable] = None):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            self.attributes("-alpha", alpha - TutorialConfig.ANIMATION["fade_step_out"])
            self.after(TutorialConfig.ANIMATION["fade_delay"], lambda: self.fade_out(callback))
        else:
            self.destroy()
            if callback:
                callback()


class ModernTutorialWindow(ctk.CTkToplevel):
    """Adımları ve kullanıcı etkileşimini yöneten ana eğitim arayüzü."""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance
        self.current_step_index = 0
        self.spotlight = None
        self.is_paused = False
        self.completed_steps = set()
        
        self._setup_window()
        self._init_ui()
        
        self.steps = TutorialContent.get_steps(app_instance)
        
        self.after(100, self.fade_in)
        self.after(200, self.show_step)

    def _setup_window(self):
        self.title("🎓 Memati Editör - İnteraktif Öğretici")
        self.geometry(TutorialConfig.DIMENSIONS["window_size"])
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _init_ui(self):
        self._create_header()
        self._create_content_area()
        self._create_controls()

    def _create_header(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=TutorialConfig.COLORS["primary_light"], height=180)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        ctk.CTkLabel(header, text="🎓", font=TutorialConfig.FONTS["header_icon"]).pack(pady=(20, 5))
        
        self.title_lbl = ctk.CTkLabel(
            header, text="Hoş Geldiniz!", 
            font=TutorialConfig.FONTS["header_title"], 
            text_color=TutorialConfig.COLORS["text_white"]
        )
        self.title_lbl.pack(pady=(0, 5))
        
        ctk.CTkLabel(
            header, text="Memati Editör'ü 7 dakikada öğrenin", 
            font=TutorialConfig.FONTS["header_subtitle"], 
            text_color=TutorialConfig.COLORS["text_white"]
        ).pack(pady=(0, 15))
        
        # İlerleme Çubuğu
        prog_cont = ctk.CTkFrame(header, fg_color="transparent")
        prog_cont.pack(fill="x", padx=40, pady=(0, 10))
        
        self.prog = ctk.CTkProgressBar(prog_cont, height=12, corner_radius=6, progress_color="white")
        self.prog.pack(fill="x")
        self.prog.set(0)
        
        self.step_info = ctk.CTkLabel(
            header, text="Adım 1 / 20", 
            font=TutorialConfig.FONTS["step_badge"], 
            text_color=TutorialConfig.COLORS["text_white"]
        )
        self.step_info.pack(pady=(5, 10))

    def _create_content_area(self):
        # Ayırıcı
        ctk.CTkFrame(self, height=2, fg_color=("#e0e0e0", "#3a3a3a")).grid(row=1, column=0, sticky="ew")
        
        self.content = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color=("white", "#1e1e1e"))
        self.content.grid(row=2, column=0, sticky="nsew")
        
        self.icon_lbl = ctk.CTkLabel(self.content, text="💡", font=TutorialConfig.FONTS["content_icon"])
        self.icon_lbl.pack(pady=(30, 10))
        
        self.msg_lbl = ctk.CTkLabel(
            self.content, text="", 
            font=TutorialConfig.FONTS["content_body"], 
            wraplength=520, justify="left"
        )
        self.msg_lbl.pack(fill="x", padx=30, pady=(0, 20))
        
        # Görev Kartı
        self.task_card = ctk.CTkFrame(
            self.content, corner_radius=15, 
            fg_color=TutorialConfig.COLORS["task_bg"],
            border_width=2, 
            border_color=TutorialConfig.COLORS["task_border"]
        )
        
        ctk.CTkLabel(
            self.task_card, text="📌 Görev", 
            font=TutorialConfig.FONTS["card_header"],
            text_color=TutorialConfig.COLORS["task_text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.task_lbl = ctk.CTkLabel(
            self.task_card, text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["task_text"], 
            wraplength=480, justify="left"
        )
        self.task_lbl.pack(anchor="w", padx=20, pady=(0, 15))
        
        # İpuçları Kartı
        self.tips_card = ctk.CTkFrame(
            self.content, corner_radius=15, 
            fg_color=TutorialConfig.COLORS["tips_bg"],
            border_width=2, 
            border_color=TutorialConfig.COLORS["tips_border"]
        )
        
        ctk.CTkLabel(
            self.tips_card, text="💡 İpuçları", 
            font=TutorialConfig.FONTS["card_header"],
            text_color=TutorialConfig.COLORS["tips_text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.tips_lbl = ctk.CTkLabel(
            self.tips_card, text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["tips_text"], 
            wraplength=480, justify="left"
        )
        self.tips_lbl.pack(anchor="w", padx=20, pady=(0, 15))

    def _create_controls(self):
        ctrl = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f5f5f5", "#2b2b2b"), height=80)
        ctrl.grid(row=3, column=0, sticky="ew")
        ctrl.grid_propagate(False)
        
        btn_container = ctk.CTkFrame(ctrl, fg_color="transparent")
        btn_container.pack(expand=True, fill="both", padx=20, pady=15)
        
        self.prev_btn = ctk.CTkButton(
            btn_container, text="◀ Önceki", width=130, height=45, corner_radius=10,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"), 
            command=self.prev_step, state="disabled"
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.pause_btn = ctk.CTkButton(
            btn_container, text="⏸ Duraklat", width=130, height=45, corner_radius=10,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["warning"], hover_color=("#fb8c00", "#ef6c00"), 
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=5)
        
        self.skip_btn = ctk.CTkButton(
            btn_container, text="⏭ Atla", width=100, height=45, corner_radius=10,
            font=("Segoe UI", 12), 
            fg_color=("gray60", "gray35"), hover_color=("gray50", "gray45"), 
            command=self.skip_tutorial
        )
        self.skip_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            btn_container, text="İleri ▶", width=140, height=45, corner_radius=10,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["primary"], hover_color=TutorialConfig.COLORS["primary_light"], 
            command=self.next_step
        )
        self.next_btn.pack(side="right", padx=5)

    def show_step(self):
        if self.current_step_index >= len(self.steps):
            self.finish()
            return
        
        step = self.steps[self.current_step_index]
        self._update_step_ui(step)
        self._handle_cards(step)
        self._handle_step_logic(step)
        self._update_buttons()

    def _update_step_ui(self, step: TutorialStep):
        self.title_lbl.configure(text=step.title)
        self.icon_lbl.configure(text=step.icon)
        self.msg_lbl.configure(text=step.message)
        
        progress = (self.current_step_index + 1) / len(self.steps)
        self.prog.set(progress)
        self.step_info.configure(text=f"Adım {self.current_step_index + 1} / {len(self.steps)}")

    def _handle_cards(self, step: TutorialStep):
        # Doğrulama Görev Kartı
        if step.validation:
            self.task_card.pack(fill="x", padx=30, pady=(0, 15))
            self.task_lbl.configure(text="Yukarıdaki talimatları uygulayın!")
            self.check_validation_loop()
        else:
            self.task_card.pack_forget()
        
        # İpuçları Kartı
        if step.tips:
            self.tips_card.pack(fill="x", padx=30, pady=(0, 20))
            self.tips_lbl.configure(text="\n".join([f"• {t}" for t in step.tips]))
        else:
            self.tips_card.pack_forget()

    def _handle_step_logic(self, step: TutorialStep):
        if step.target_widget:
            self.show_spotlight(step)
        else:
            self.hide_spotlight()
        
        if step.action:
            self.after(500, step.action)
        
        if step.auto_advance and not step.validation:
            self.after(step.wait_time, self.next_step)

    def _update_buttons(self):
        self.prev_btn.configure(state="normal" if self.current_step_index > 0 else "disabled")
        
        if self.current_step_index == len(self.steps) - 1:
            self.next_btn.configure(text="🏁 Kapat", command=self.finish)
        else:
            self.next_btn.configure(text="İleri ▶", command=self.next_step)

    def show_spotlight(self, step: TutorialStep):
        self.hide_spotlight()
        
        # Tembel ise hedef widget'ı değerlendir
        target = step.target_widget() if callable(step.target_widget) else step.target_widget
        
        if target and target.winfo_exists():
            try:
                self.spotlight = ModernSpotlight(
                    self.app, 
                    target, 
                    "👆 Dikkat!", 
                    step.highlight_pos,
                    self.current_step_index + 1, 
                    len(self.steps)
                )
                self.lift()
            except Exception:
                pass # UI sağlamlığı için sessizce başarısız ol

    def hide_spotlight(self):
        if self.spotlight and self.spotlight.winfo_exists():
            self.spotlight.fade_out()
            self.spotlight = None

    def check_validation_loop(self):
        if self.is_paused or self.current_step_index >= len(self.steps):
            return
            
        step = self.steps[self.current_step_index]
        if step.validation and step.validation():
            self.task_lbl.configure(text="✅ Harika! Görev tamamlandı!")
            self.completed_steps.add(self.current_step_index)
            self.after(1500, self.next_step)
        else:
            self.after(500, self.check_validation_loop)

    def next_step(self):
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.show_step()

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_step()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="▶ Devam", fg_color=TutorialConfig.COLORS["success"])
            self.hide_spotlight()
        else:
            self.pause_btn.configure(text="⏸ Duraklat", fg_color=TutorialConfig.COLORS["warning"])
            self.show_step()

    def skip_tutorial(self):
        if tk.messagebox.askyesno("Atla", "Öğreticiyi atlamak istediğinizden emin misiniz?", parent=self):
            self.finish()

    def finish(self):
        self.hide_spotlight()
        if self.current_step_index == len(self.steps) - 1:
            validation_count = sum(1 for s in self.steps if s.validation)
            tk.messagebox.showinfo(
                "Tamamlandı", 
                f"🎉 Tebrikler!\n\nTutorial tamamlandı!\nGörevler: {len(self.completed_steps)}/{validation_count}", 
                parent=self
            )
        self.fade_out()

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.1)
            self.after(25, self.fade_in)

    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            self.attributes("-alpha", alpha - 0.1)
            self.after(25, self.fade_out)
        else:
            self.destroy()


class TutorialSystem:
    """Eğitim oturumunu yönetir."""
    
    def __init__(self, master_window):
        self.master = master_window
        self.tutorial_window: Optional[ModernTutorialWindow] = None
    
    def start_tutorial(self):
        if self.tutorial_window is None or not self.tutorial_window.winfo_exists():
            self.tutorial_window = ModernTutorialWindow(self.master, self.master)
        else:
            self.tutorial_window.lift()
            self.tutorial_window.focus()
