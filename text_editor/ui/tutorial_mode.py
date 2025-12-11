import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, List, Tuple
from dataclasses import dataclass, field
import platform

# --- Yapılandırma & Sabitler ---
class TutorialConfig:
    """Eğitim görünümü ve davranışı için merkezi yapılandırma."""
    COLORS = {
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
        "transparent_key": "#000001", # Çok koyu, neredeyse siyah (transparan anahtarı)
    }
    
    FONTS = {
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
    
    ANIMATION = {
        "fade_step_in": 0.08,
        "fade_step_out": 0.12,
        "fade_delay": 20,
        "pulse_min": 0.0,
        "pulse_max": 9.0,
        "pulse_speed": 0.8,
    }

    DIMENSIONS = {
        "spotlight_msg_w": 480,
        "spotlight_msg_h": 200,
        "window_size": "650x750",
        "padding_std": 24,
        "corner_radius": 16,
    }


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


# --- İçerik Sağlayıcısı ---
class TutorialContent:
    """Eğitim için içerik sağlar."""
    
    @staticmethod
    def get_steps(app_instance) -> List[TutorialStep]:
        return [
            TutorialStep(
                title="Memati Editör'e Hoş Geldiniz!", 
                message="Merhaba! 👋\n\nEditörünüzü profesyonelce kullanmanız için hazırladığımız bu interaktif rehbere hoş geldiniz.\n\n🚀 Bu turda şunları keşfedeceksiniz:\n• Arayüzün gizli güçleri\n• Şimşek hızında kodlama teknikleri\n• Proje yönetim ipuçları\n\nHazırsanız başlayalım!", 
                icon="🚀", 
                auto_advance=False,
                tips=["Öğretici penceresini ekranın rahat bir köşesine taşıyabilirsiniz."]
            ),
            TutorialStep(
                title="Menüler ve Komutlar", 
                message="Her şeyin merkezi burası.\n\nDosya işlemlerinden tema ayarlarına kadar her şeye buradan ulaşabilirsiniz.\n\n💡 Kısayolları (örn. Ctrl+N) menülerden öğrenerek zaman kazanabilirsiniz.", 
                icon="🎛️",
                target_widget=lambda: getattr(app_instance, 'menu_frame', None),
                highlight_pos="bottom", 
                auto_advance=True, 
                wait_time=6000
            ),
            TutorialStep(
                title="Dosya Gezgini", 
                message="Projeleriniz burada yaşar.\n\nDosyalarınızı ağaç yapısında görüntüleyin. Klasörleri açıp kapamak için çift tıklayabilirsiniz.\n\n🎯 Görev: Sol paneldeki 'Dosya Gezgini'ni inceleyin.", 
                icon="📂",
                target_widget=lambda: getattr(app_instance, 'file_explorer', None),
                highlight_pos="right",
                validation=lambda: hasattr(app_instance.file_explorer, 'root_path') and app_instance.file_explorer.root_path,
                tips=["Ctrl+Shift+O ile yeni bir klasör açabilirsiniz.", "Paneli gizlemek için Ctrl+B'yi kullanın."]
            ),
            TutorialStep(
                title="Resim Görüntüleyici", 
                message="Editörünüz artık resim dosyalarını da açabiliyor!\n\nDesteklenen formatlar: PNG, JPG, JPEG, BMP, GIF.\n\n🎯 Görev: Dosya gezgininden bir resim dosyası açın.", 
                icon="🖼️", 
                validation=lambda: any(type(editor).__name__ == 'ImageViewer' for editor in app_instance.tab_manager.editors.values()),
                tips=["Resmi yakınlaştırmak için tekerleği kullanın.", "Yön tuşları ile resim içinde gezinebilirsiniz."]
            ),
            TutorialStep(
                title="Yeni Bir Başlangıç", 
                message="Kodlamaya başlamak için temiz bir sayfa açın.\n\n🎯 Görev: Ctrl+N kısayolunu kullanarak veya Dosya menüsünden yeni bir sekme oluşturun.", 
                icon="📝",
                validation=lambda: len(app_instance.tab_manager.editors) > 0,
                tips=["Sekmeleri sürükleyerek sırasını değiştirebilirsiniz."]
            ),
            TutorialStep(
                title="Editörün Kalbi", 
                message="Burası sizin oyun alanınız.\n\n✨ Özellikler:\n• Otomatik Tamamlama (Ctrl+Space)\n• Kod Renklendirme\n• Akıllı Girinti\n\n🎯 Görev: Editöre rastgele bir şeyler yazın!", 
                icon="✨", 
                target_widget=lambda: app_instance.tab_manager.get_active_editor().text_area if app_instance.tab_manager.get_active_editor() else None,
                highlight_pos="bottom",
                validation=lambda: len(app_instance.tab_manager.get_active_editor().text_area.get("1.0", "end-1c")) > 5 if app_instance.tab_manager.get_active_editor() else False,
                tips=["Yazı boyutunu değiştirmek için Ctrl + Tekerlek kullanın."]
            ),
            TutorialStep(
                title="Minimap (Kod Haritası)", 
                message="Kodunuzun kuş bakışı görünümü.\n\nUzun dosyalarda hızla gezinmek için sağdaki haritayı kullanın.\n\nKlavye Kısayolu: Ctrl+M", 
                icon="🗺️", 
                target_widget=lambda: getattr(app_instance, 'minimap', None),
                highlight_pos="left",
                auto_advance=True, 
                wait_time=7000
            ),
            TutorialStep(
                title="Çoklu İmleç Sihirbazlığı", 
                message="Aynı anda birden fazla yeri düzenleyin!\n\n🎯 Görev: Klavyede 'Alt' tuşuna basılı tutarak editörde farklı yerlere tıklayın. Birden fazla imleç yanıp sönmeli!", 
                icon="🖱️", 
                auto_advance=False,
                tips=["İmleçleri iptal etmek için 'Escape' tuşuna basın.", "Listeleri düzenlerken harikalar yaratır."]
            ),
            TutorialStep(
                title="Akıllı Seçim (Ctrl+D)", 
                message="Değişken adlarını değiştirmek hiç bu kadar kolay olmamıştı.\n\n1. Bir kelimeyi seçin.\n2. Ctrl+D'ye basarak bir sonraki aynısını seçin.\n3. Yazmaya başlayın; hepsi değişecek!\n\n🎯 Görev: Bunu deneyin!", 
                icon="⚡", 
                auto_advance=False
            ),
            TutorialStep(
                title="Bul ve Yok Et (Değiştir)", 
                message="Güçlü arama motoru emrinizde.\n\n🎯 Görev: Ctrl+F tuşuna basarak arama panelini açın. Regex desteği bile var!", 
                icon="🔍",
                target_widget=lambda: app_instance.tab_manager.notebook, # Genel bölgeyi göster
                highlight_pos="top",
                                  app_instance.tab_manager.find_replace_window.winfo_exists()
            ),
            TutorialStep(
                title="Satıra Git (Ctrl+G)", 
                message="Uzun dosyalarda kaybolmayın.\n\n🎯 Görev: Ctrl+G tuşuna basarak 'Satıra Git' penceresini açın.", 
                icon="🔢",
                validation=lambda: hasattr(app_instance, 'goto_line_dialog') and app_instance.goto_line_dialog and app_instance.goto_line_dialog.winfo_exists(),
                tips=["Sadece sayı girerek istediğiniz satıra ışınlanın."]
            ),
            TutorialStep(
                title="Terminal Entegrasyonu", 
                message="Editörden çıkmadan komut çalıştırın.\n\n🎯 Görev: Ctrl+` (Tab'ın üstündeki tuş) ile terminali açın/kapatın.", 
                icon="💻",
                validation=lambda: hasattr(app_instance, '_terminal_visible') and app_instance._terminal_visible,
                tips=["Terminali 'exit' yazarak da kapatabilirsiniz."]
            ),
            TutorialStep(
                title="Markdown Önizleme", 
                message="Doküman yazarları için harika bir özellik.\n\nEğer bir .md dosyasındaysanız, Ctrl+Shift+V ile canlı önizlemeyi açabilirsiniz.\n\n💡 Editörde kaydırdıkça önizleme de kayar (Sync Scroll).", 
                icon="eye", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Zen Modu", 
                message="Sadece koda odaklanmak istediğinizde...\n\n🧘 Ctrl+K, ardından Z tuşuna basın.\n\nTüm paneller gizlenir, sadece kod kalır. Geri dönmek için aynısı.", 
                icon="🧘", 
                auto_advance=True, 
                wait_time=8000
            ),
            TutorialStep(
                title="Tebrikler! 🎉", 
                message="Temel eğitimi başarıyla tamamladınız!\n\nArtık Memati Editör'ün gücü parmaklarınızın ucunda. Keşfedilecek daha çok özellik var (Temalar, Git entegrasyonu, vb.).\n\nİyi kodlamalar!", 
                icon="🏆", 
                auto_advance=False,
                tips=["Bu tura istediğiniz zaman Yardım menüsünden ulaşabilirsiniz."]
            )
        ]


# --- Arayüz Sınıfları ---
class ModernSpotlight(ctk.CTkToplevel):
    """Windows'ta tıkla-geç (click-through) özelliği destekleyen interaktif spotlight."""
    
    def __init__(self, parent, target_widget, title, position="bottom", step_num=1, total=20):
        super().__init__(parent)
        self.target_widget = target_widget
        self.title_text = title
        self.position = position
        
        self.pulse_val = 0
        self.pulse_dir = 1
        
        self._setup_window(parent)
        
        # Canvas oluştur
        self.canvas = tk.Canvas(
            self, 
            bg="black", # Asıl arka plan
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Animasyonları başlat
        # Fade-in yerine direkt açılıp pulse efektine odaklanıyoruz, 
        # çünkü transparan key ile fade-in sorunlu olabilir.
        self.attributes("-alpha", 0.75) # Genel karartma seviyesi
        
        # Windows için şeffaflık anahtarı
        if platform.system() == "Windows":
            self.attributes("-transparentcolor", TutorialConfig.COLORS["transparent_key"])

        self.pulse()
        
        # Pencere boyutu değişimlerini izle
        self.bind("<Configure>", self._on_configure)

    def _setup_window(self, parent):
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

    def _on_configure(self, event):
        # Pencere taşınırsa vs. spotlight'ı yeniden çiz
        self.draw_spotlight()

    def _get_target_rect(self):
        try:
            if not self.target_widget.winfo_exists():
                return None
            x = self.target_widget.winfo_rootx()
            y = self.target_widget.winfo_rooty()
            w = self.target_widget.winfo_width()
            h = self.target_widget.winfo_height()
            return (x, y, w, h)
        except Exception:
            return None

    def draw_spotlight(self):
        self.canvas.delete("all")
        rect = self._get_target_rect()
        
        # Tüm ekranı kapsayan yarı saydam siyah (Canvas bg zaten black, ama delik açacağız)
        # Transparan key yönteminde: Tüm ekranı boya, deliği KEY rengi ile boya.
        
        # 1. Arka plan dolgusu (Siyah - ama alpha ile dimmed görünecek)
        w_screen = self.winfo_screenwidth()
        h_screen = self.winfo_screenheight()
        
        self.canvas.create_rectangle(0, 0, w_screen, h_screen, fill="black", outline="")
        
        if rect:
            x, y, w, h = rect
            pad = 5
            
            # 2. Deliği aç (Windows transparent key rengi ile)
            # Bu renk, pencere alpha değerinden bağımsız olarak %100 şeffaf ve TIKLANABİLİR olur.
            key_color = TutorialConfig.COLORS["transparent_key"]
            self.canvas.create_rectangle(
                x - pad, y - pad, x + w + pad, y + h + pad, 
                fill=key_color, outline=""
            )
            
            # 3. Vurgu Çerçevesi (Glow efekti için birden fazla katman)
            pulse_offset = self.pulse_val
            
            # Dış glow
            self.canvas.create_rectangle(
                x - pad - pulse_offset, y - pad - pulse_offset, 
                x + w + pad + pulse_offset, y + h + pad + pulse_offset,
                outline=TutorialConfig.COLORS["primary"][0], width=2,
                tags="pulse_rect"
            )
            
            # İç keskin kenar
            self.canvas.create_rectangle(
                x - pad, y - pad, x + w + pad, y + h + pad,
                outline="white", width=1
            )
            
            # Başlık etiketi (Spotlight'ın neyi gösterdiğini belirtmek için)
            label_y = y - 40 if y > 50 else y + h + 20
            
            # Etiket arka planı
            text_id = self.canvas.create_text(
                x, label_y, 
                text=self.title_text, 
                fill="white", 
                anchor="w",
                font=("Segoe UI", 12, "bold")
            )
            bbox = self.canvas.bbox(text_id)
            if bbox:
                # Metnin arkasına şık bir kutu
                padding_x = 10
                padding_y = 5
                self.canvas.create_rectangle(
                    bbox[0] - padding_x, bbox[1] - padding_y,
                    bbox[2] + padding_x, bbox[3] + padding_y,
                    fill=TutorialConfig.COLORS["primary"][1],
                    outline="white",
                    width=1
                )
                self.canvas.tag_raise(text_id) # Metni üste çıkar

    def pulse(self):
        if not self.winfo_exists():
            return
            
        # Basit nefes alma efekti
        anim = TutorialConfig.ANIMATION
        self.pulse_val += self.pulse_dir * anim["pulse_speed"]
        
        if self.pulse_val >= anim["pulse_max"]:
            self.pulse_dir = -1
        elif self.pulse_val <= anim["pulse_min"]:
            self.pulse_dir = 1
            
        # Sadece pulse rect'i güncelle (performans için tümünü yeniden çizme)
        # Ama rect koordinatları targeta bağlı, o yüzden şimdilik redraw çağırabiliriz
        # veya tag tabanlı optimize edebiliriz. Basit olması için redraw (target hareket edebilir).
        self.draw_spotlight()
        
        self.after(30, self.pulse)
    
    def fade_out(self, callback: Optional[Callable] = None):
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
        
        # Sürükleme için değişkenler
        self._drag_data = {"x": 0, "y": 0}
        
        self._setup_window()
        self._init_ui()
        
        self.steps = TutorialContent.get_steps(app_instance)
        
        self.after(100, self.fade_in)
        self.after(300, self.show_step)

    def _setup_window(self):
        self.title("Memati Editör - Öğretici")
        self.geometry(TutorialConfig.DIMENSIONS["window_size"])
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)
        
        # Özel başlık çubuğu için OS çubuğunu kaldır
        self.overrideredirect(True)
        
        # Grid yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # İçerik alanı esner

        # Ekranın ortasına yerleştir
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = 650
        win_h = 750
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        # Arkaplan
        self.configure(fg_color=TutorialConfig.COLORS["bg_main"])
        
        # Ana bir çerçeve
        self.main_container = ctk.CTkFrame(self, fg_color=TutorialConfig.COLORS["bg_main"], corner_radius=TutorialConfig.DIMENSIONS["corner_radius"], border_width=1, border_color="gray30")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

    def _init_ui(self):
        self._create_custom_title_bar()
        self._create_header_area()
        self._create_content_area()
        self._create_footer_controls()

    def _create_custom_title_bar(self):
        title_bar = ctk.CTkFrame(self.main_container, height=40, corner_radius=0, fg_color="transparent")
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.grid_propagate(False)
        
        title_bar.bind("<Button-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)
        
        title_lbl = ctk.CTkLabel(
            title_bar, text="MEMATI EDITÖR", 
            font=("Segoe UI", 12, "bold"), 
            text_color=TutorialConfig.COLORS["text_sub"]
        )
        title_lbl.pack(side="left", padx=20)
        title_lbl.bind("<Button-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)
        
        close_btn = ctk.CTkButton(
            title_bar, text="✕", width=40, height=40,
            fg_color="transparent", hover_color="#c42b1c",
            font=("Arial", 14),
            command=self.finish
        )
        close_btn.pack(side="right")

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_drag(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def _create_header_area(self):
        header = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 20))
        
        head_top = ctk.CTkFrame(header, fg_color="transparent")
        head_top.pack(fill="x")
        
        self.title_lbl = ctk.CTkLabel(
            head_top, text="Hoş Geldiniz!", 
            font=TutorialConfig.FONTS["header_title"], 
            text_color=TutorialConfig.COLORS["text_main"],
            anchor="w"
        )
        self.title_lbl.pack(side="left", fill="x", expand=True)

        self.step_badge = ctk.CTkLabel(
            head_top, text="1 / 14", 
            font=TutorialConfig.FONTS["step_badge"], 
            text_color=TutorialConfig.COLORS["primary"],
            fg_color=TutorialConfig.COLORS["bg_badge"],
            corner_radius=8, width=80, height=30
        )
        self.step_badge.pack(side="right")
        
        self.prog = ctk.CTkProgressBar(header, height=6, corner_radius=3, progress_color=TutorialConfig.COLORS["primary"])
        self.prog.pack(fill="x", pady=(15, 0))
        self.prog.set(0)

    def _create_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self.main_container, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.content.grid(row=2, column=0, sticky="nsew", padx=20, pady=0)
        
        self.icon_lbl = ctk.CTkLabel(self.content, text="💡", font=TutorialConfig.FONTS["content_icon"])
        self.icon_lbl.pack(pady=(20, 15))
        
        self.msg_lbl = ctk.CTkLabel(
            self.content, text="", 
            font=TutorialConfig.FONTS["content_body"], 
            text_color=TutorialConfig.COLORS["text_main"],
            wraplength=540, justify="center"
        )
        self.msg_lbl.pack(fill="x", padx=10, pady=(0, 30))
        
        self.task_card = ctk.CTkFrame(
            self.content, corner_radius=12, 
            fg_color=TutorialConfig.COLORS["task_bg"],
            border_width=1, 
            border_color=TutorialConfig.COLORS["task_border"]
        )
        
        ctk.CTkLabel(
            self.task_card, text="GÖREV", 
            font=TutorialConfig.FONTS["ui_small"],
            text_color=TutorialConfig.COLORS["task_border"]
        ).pack(anchor="w", padx=20, pady=(15, 0))
        
        self.task_lbl = ctk.CTkLabel(
            self.task_card, text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["task_text"], 
            wraplength=500, justify="left"
        )
        self.task_lbl.pack(anchor="w", padx=20, pady=(5, 15))
        
        self.tips_card = ctk.CTkFrame(
            self.content, corner_radius=12, 
            fg_color=TutorialConfig.COLORS["tips_bg"],
            border_width=0
        )
        
        ctk.CTkLabel(
            self.tips_card, text="İPUCU", 
            font=TutorialConfig.FONTS["ui_small"],
            text_color=TutorialConfig.COLORS["tips_border"]
        ).pack(anchor="w", padx=20, pady=(15, 0))
        
        self.tips_lbl = ctk.CTkLabel(
            self.tips_card, text="", 
            font=TutorialConfig.FONTS["card_body"],
            text_color=TutorialConfig.COLORS["tips_text"], 
            wraplength=500, justify="left"
        )
        self.tips_lbl.pack(anchor="w", padx=20, pady=(5, 15))

    def _create_footer_controls(self):
        ctrl = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=TutorialConfig.COLORS["bg_secondary"], height=90)
        ctrl.grid(row=3, column=0, sticky="ew")
        ctrl.grid_propagate(False)
        
        btn_container = ctk.CTkFrame(ctrl, fg_color="transparent")
        btn_container.pack(expand=True, fill="both", padx=30, pady=20)
        
        self.prev_btn = ctk.CTkButton(
            btn_container, text="Geri", width=100, height=45, corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color="transparent", border_width=1, border_color=TutorialConfig.COLORS["text_sub"],
            text_color=TutorialConfig.COLORS["text_main"], hover_color=("gray85", "gray25"),
            command=self.prev_step, state="disabled"
        )
        self.prev_btn.pack(side="left", padx=0)
        
        self.pause_btn = ctk.CTkButton(
            btn_container, text="Duraklat", width=120, height=45, corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["warning"], hover_color="#d97706", 
            text_color="white",
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=15)
        
        self.next_btn = ctk.CTkButton(
            btn_container, text="Devam Et", width=160, height=45, corner_radius=8,
            font=TutorialConfig.FONTS["button_bold"], 
            fg_color=TutorialConfig.COLORS["primary"], hover_color=TutorialConfig.COLORS["primary_dark"], 
            text_color="white",
            command=self.next_step
        )
        self.next_btn.pack(side="right", padx=0)
        
        self.skip_btn = ctk.CTkButton(
            btn_container, text="Öğreticiyi Atla", width=100,
            font=TutorialConfig.FONTS["ui_small"],
            fg_color="transparent", hover_color=("gray90", "gray25"),
            text_color=TutorialConfig.COLORS["text_sub"],
            command=self.skip_tutorial
        )
        self.skip_btn.place(relx=0.5, rely=0.5, anchor="center")

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
        
        total = len(self.steps)
        current = self.current_step_index + 1
        progress = current / total
        
        self.prog.set(progress)
        self.step_badge.configure(text=f"{current} / {total}")

    def _handle_cards(self, step: TutorialStep):
        self.task_card.pack_forget()
        self.tips_card.pack_forget()
        
        if step.validation:
            self.task_card.pack(fill="x", padx=10, pady=(0, 20))
            self.task_lbl.configure(text="İlerlemek için yukarıdaki görevi tamamlayın.")
            self.check_validation_loop()
        
        if step.tips:
            self.tips_card.pack(fill="x", padx=10, pady=(0, 20))
            self.tips_lbl.configure(text="\n".join([f"• {t}" for t in step.tips]))

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
            self.next_btn.configure(text="Tamamla 🎉", command=self.finish)
        else:
            self.next_btn.configure(text="Devam Et", command=self.next_step)

    def show_spotlight(self, step: TutorialStep):
        self.hide_spotlight()
        
        target = step.target_widget() if callable(step.target_widget) else step.target_widget
        
        if target and target.winfo_exists():
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
        if self.spotlight and self.spotlight.winfo_exists():
            self.spotlight.fade_out()
            self.spotlight = None

    def check_validation_loop(self):
        if self.is_paused or self.current_step_index >= len(self.steps):
            return
            
        step = self.steps[self.current_step_index]
        if step.validation:
            if step.validation():
                self.task_lbl.configure(text="✅ Harika! Görev tamamlandı!", text_color=TutorialConfig.COLORS["success"])
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
            self.pause_btn.configure(text="Devam", fg_color=TutorialConfig.COLORS["success"])
            self.hide_spotlight()
        else:
            self.pause_btn.configure(text="Duraklat", fg_color=TutorialConfig.COLORS["warning"])
            self.show_step()

    def skip_tutorial(self):
        if tk.messagebox.askyesno("Atla", "Öğreticiyi kapatmak istediğinizden emin misiniz?", parent=self):
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
