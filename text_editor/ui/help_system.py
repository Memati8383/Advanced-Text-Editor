import customtkinter as ctk
import tkinter as tk
import platform
import sys
from text_editor.config import APP_NAME
from text_editor.ui.help_content import HelpContentProvider

class HelpWindow(ctk.CTkToplevel):
    """
    Kullanıcıya yardımcı bilgiler sunan ve öğretici modunu başlatan ana yardım penceresi.
    UI logic ve içerik (Content) birbirinden ayrılmıştır.
    """
    
    def __init__(self, master, app_instance, start_section="Hızlı Başlangıç"):
        super().__init__(master)
        self.app = app_instance
        
        self._setup_window_properties()
        self._init_variables()
        self._setup_ui_layout()
        self._setup_sections()
        
        # Başlangıç bölümünü seç
        self._select_initial_section(start_section)
        
        # Animasyonları başlat
        self.after(50, self.start_fade_in_animation)
        self.after(2000, self.animate_logo_pulse)
        self.focus()

    def _setup_window_properties(self):
        """Pencere temel özelliklerini ayarlar."""
        self.title(f"🪐 {APP_NAME} - Yardım Merkezi")
        self.geometry("1000x700")
        self.attributes("-alpha", 0.0) # Başlangıçta görünmez (fade-in için)
        self.attributes("-topmost", True)
        self.lift()

    def _init_variables(self):
        """Sınıf değişkenlerini başlatır."""
        # Animasyon değişkenleri
        self.animation_running = False
        self.fade_alpha = 0.0
        self.content_offset = 30
        self.logo_pulse_size = 32
        self.logo_pulse_direction = 1
        self.title_slide_offset = 0
        
        # Navigasyon geçmişi
        self.history = []
        self.history_index = -1
        self.buttons = {}

    def _setup_ui_layout(self):
        """Ana grid ve UI bileşenlerini yerleştirir."""
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_toolbar()
        self.create_sidebar()
        self.create_content_area()

    def create_toolbar(self):
        """Üst araç çubuğunu oluşturur (Geri, İleri, Ana Sayfa)."""
        toolbar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color=("gray95", "#2b2b2b"))
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Geri Butonu
        self.back_btn = self._create_toolbar_button(toolbar, "◀ Geri", 80, self.go_back, state="disabled")
        self.back_btn.pack(side="left", padx=(10, 5), pady=7)
        
        # İleri Butonu
        self.forward_btn = self._create_toolbar_button(toolbar, "İleri ▶", 80, self.go_forward, state="disabled")
        self.forward_btn.pack(side="left", padx=5, pady=7)
        
        # Ayırıcı
        ctk.CTkLabel(toolbar, text="|", text_color=("gray60", "gray50")).pack(side="left", padx=10)
        
        # Ana Sayfa Butonu
        home_btn = self._create_toolbar_button(
            toolbar, 
            "🏠 Ana Sayfa", 
            100, 
            lambda: self.select_section("🚀 Hızlı Başlangıç")
        )
        home_btn.pack(side="left", padx=5, pady=7)

    def _create_toolbar_button(self, parent, text, width, command, state="normal"):
        """Toolbar butonu oluşturmak için yardımcı metod."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            width=width,
            height=32,
            corner_radius=6,
            command=command,
            state=state
        )
        self.create_hover_effect(btn)
        return btn

    def create_sidebar(self):
        """Sol kenar çubuğunu oluşturur."""
        self.sidebar = ctk.CTkScrollableFrame(
            self, 
            corner_radius=0, 
            fg_color=("gray92", "#2b2b2b"),
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 1))
        
        self._create_sidebar_logo()
        self._create_tutorial_button()
        self._create_search_box()

    def _create_sidebar_logo(self):
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.logo_label = ctk.CTkLabel(logo_frame, text="🪐", font=("Segoe UI", 32))
        self.logo_label.pack()
        
        ctk.CTkLabel(logo_frame, text="Yardım Merkezi", font=("Segoe UI", 14, "bold")).pack()

    def _create_tutorial_button(self):
        tutorial_btn = ctk.CTkButton(
            self.sidebar,
            text="🎓 İnteraktif Öğreticiyi Başlat",
            height=45,
            corner_radius=10,
            fg_color=("#00d4ff", "#0096c7"),
            hover_color=("#00b8e6", "#007ea7"),
            font=("Segoe UI", 13, "bold"),
            command=self.start_tutorial
        )
        tutorial_btn.pack(fill="x", padx=10, pady=(10, 5))

    def _create_search_box(self):
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="🔍 Ara...",
            height=35,
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        self._add_search_focus_animation()

    def create_content_area(self):
        """Sağ taraftaki içerik alanını oluşturur."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.content_title = ctk.CTkLabel(
            self.content_frame, 
            text="", 
            font=("Segoe UI", 24, "bold"), 
            anchor="w"
        )
        self.content_title.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.content_text = ctk.CTkTextbox(
            self.content_frame, 
            wrap="word", 
            font=("Segoe UI", 13),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.content_text.grid(row=1, column=0, sticky="nsew")

    def _setup_sections(self):
        """Bölümleri ve içerik sağlayıcıları tanımlar."""
        self.sections = {
            "🚀 Hızlı Başlangıç": HelpContentProvider.get_quick_start,
            "⌨️ Klavye Kısayolları": HelpContentProvider.get_shortcuts,
            "🖱️ Çoklu İmleç Rehberi": HelpContentProvider.get_multi_cursor_guide,
            "🎨 Tema Rehberi": HelpContentProvider.get_theme_guide,
            "📁 Dosya Formatları": HelpContentProvider.get_supported_formats,
            "📄 Markdown Rehberi": HelpContentProvider.get_markdown_guide,
            "💡 İpuçları ve Püf Noktaları": HelpContentProvider.get_tips_and_tricks,
            "❓ SSS": HelpContentProvider.get_faq,
            "📊 Performans Raporu": lambda: HelpContentProvider.get_performance_report(self.app),
            "🐛 Hata Bildir": HelpContentProvider.get_report_bug,
            "ℹ️ Hakkında": HelpContentProvider.get_about
        }
        self.create_sidebar_buttons()

    def create_sidebar_buttons(self):
        """Kenar çubuğundaki navigasyon butonlarını oluşturur."""
        for name in self.sections.keys():
            btn = ctk.CTkButton(
                self.sidebar, 
                text=name, 
                anchor="w", 
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray35"),
                height=40,
                corner_radius=8,
                font=("Segoe UI", 12),
                command=lambda n=name: self.select_section(n)
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.buttons[name] = btn
            
            self.create_hover_effect(btn)
            self._add_button_hover_animation(btn)

    def _select_initial_section(self, start_section):
        """Başlangıç bölümünü belirler ve seçer."""
        initial = "🚀 Hızlı Başlangıç"
        for section in self.sections.keys():
            if start_section in section:
                initial = section
                break
        self.select_section(initial)

    # --- Actions ---

    def start_tutorial(self):
        """Tutorial Mode'u başlatır."""
        from text_editor.ui.tutorial_mode import TutorialSystem
        
        if not hasattr(self.app, 'tutorial_system'):
            self.app.tutorial_system = TutorialSystem(self.app)
        
        self.app.tutorial_system.start_tutorial()

    def select_section(self, name):
        """İlgili yardım bölümünü seçer ve gösterir."""
        if self.history_index == -1 or self.history[self.history_index] != name:
            self.history = self.history[:self.history_index + 1]
            self.history.append(name)
            self.history_index = len(self.history) - 1
        
        self.update_navigation_buttons()
        self._update_ui_state(name)

    def select_section_without_history(self, name):
        """Geçmişe eklemeden bölüm seçer (Geri/İleri işlemleri için)."""
        self._update_ui_state(name)

    def _update_ui_state(self, name):
        """UI durumunu (butonlar ve içerik) günceller."""
        self.animation_running = True
        self.content_offset = 30
        
        for btn_name, btn in self.buttons.items():
            is_selected = (btn_name == name)
            self.animate_button_selection(btn, is_selected)
        
        self._update_content_with_animation(name)

    def _update_content_with_animation(self, name):
        """İçeriği animasyonlu olarak yeniler."""
        self.title_slide_offset = -20
        self.content_title.configure(text=name)
        
        self._animate_title_slide()
        
        # İçeriği HelpContentProvider'dan al
        content = self.sections[name]()
        
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
        self.content_text.configure(state="disabled")
        
        self.content_text.yview_moveto(0)
        self.animate_content_fade_in()
        self.animation_running = False

    def go_back(self):
        """Geri git."""
        if self.history_index > 0:
            self.history_index -= 1
            section = self.history[self.history_index]
            self.select_section_without_history(section)
            self.update_navigation_buttons()

    def go_forward(self):
        """İleri git."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            section = self.history[self.history_index]
            self.select_section_without_history(section)
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Geri/İleri butonlarının aktiflik durumunu günceller."""
        self.back_btn.configure(state="normal" if self.history_index > 0 else "disabled")
        self.forward_btn.configure(state="normal" if self.history_index < len(self.history) - 1 else "disabled")

    def on_search(self, event):
        """Arama kutusu işleyicisi."""
        query = self.search_entry.get().lower()
        self._animate_search_results(query=query, show_all=not query)

    # --- Animations ---

    def start_fade_in_animation(self):
        """Pencere açılış fade-in animasyonu."""
        if self.fade_alpha < 1.0:
            self.fade_alpha += 0.1
            self.attributes("-alpha", self.fade_alpha)
            self.after(30, self.start_fade_in_animation)
        else:
            self.fade_alpha = 1.0
            self.attributes("-alpha", 1.0)

    def animate_content_fade_in(self):
        """İçerik yukarı kayma ve belirme animasyonu."""
        if self.content_offset > 0:
            self.content_offset -= 3
            # Bu metod text widget'ı kaydırmaz, sadece logic olarak offset azaltır. 
            # Ancak orijinal kodda yview_moveto(0) çağrılıyordu her adımda.
            # Orijinal efektin korunması için burada farklı bir işlem yapmıyoruz
            # çünkü textbox içeriği zaten statik duruyor.
            # Orijinal kodda bu sadece bir zamanlayıcı gibi çalışıyordu.
            self.after(20, self.animate_content_fade_in)

    def _animate_title_slide(self):
        """Başlık kayma animasyonu."""
        if self.title_slide_offset < 0:
            self.title_slide_offset += 2
            self.content_title.grid(row=0, column=0, sticky="w", 
                                   pady=(max(0, self.title_slide_offset), 15),
                                   padx=(max(0, -self.title_slide_offset), 0))
            self.after(20, self._animate_title_slide)
        else:
            self.content_title.grid(row=0, column=0, sticky="w", pady=(0, 15), padx=0)

    def animate_logo_pulse(self):
        """Logo nabız animasyonu."""
        if not self.winfo_exists():
            return
        
        self.logo_pulse_size += self.logo_pulse_direction
        if self.logo_pulse_size >= 36:
            self.logo_pulse_direction = -1
        elif self.logo_pulse_size <= 32:
            self.logo_pulse_direction = 1
        
        try:
            self.logo_label.configure(font=("Segoe UI", self.logo_pulse_size))
        except Exception:
            pass
        
        self.after(100, self.animate_logo_pulse)

    def _animate_search_results(self, query=None, show_all=False):
        """Arama sonuçlarını filtreler."""
        for name, btn in self.buttons.items():
            if show_all or (query and query in name.lower()):
                if not btn.winfo_ismapped():
                    btn.pack(fill="x", padx=8, pady=3)
            else:
                if btn.winfo_ismapped():
                    btn.pack_forget()

    def animate_button_selection(self, button, is_selected):
        """Buton seçili/seçili değil durumu için renk geçişi."""
        if is_selected:
            button.configure(fg_color=("gray85", "#404040"), font=("Segoe UI", 12, "bold"))
        else:
            button.configure(fg_color="transparent", font=("Segoe UI", 12))

    def _add_button_hover_animation(self, button):
        button.bind("<Enter>", lambda e: button.configure(cursor="hand2"), add="+")
        button.bind("<Leave>", lambda e: button.configure(cursor=""), add="+")

    def create_hover_effect(self, widget):
        widget.bind("<Enter>", lambda e: widget.configure(cursor="hand2"))
        widget.bind("<Leave>", lambda e: widget.configure(cursor=""))

    def _add_search_focus_animation(self):
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.configure(border_width=2))
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.configure(border_width=1))


class HelpSystem:
    """Yardım penceresinin tekil (singleton benzeri) yönetimini sağlar."""
    def __init__(self, master_window):
        self.master = master_window
        self.help_window = None

    def open_help(self, section="Hızlı Başlangıç"):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self.master, self.master, start_section=section)
        else:
            self.help_window.lift()
            self.help_window.focus()
            
            # Bölüm ara ve seç
            section_found = False
            for sec_name in self.help_window.sections.keys():
                if section in sec_name:
                    self.help_window.select_section(sec_name)
                    section_found = True
                    break
            
            if not section_found:
                self.help_window.select_section("🚀 Hızlı Başlangıç")
    
    def start_tutorial(self):
        """Tutorial Mode başlatıcı."""
        from text_editor.ui.tutorial_mode import TutorialSystem
        
        if not hasattr(self.master, 'tutorial_system'):
            self.master.tutorial_system = TutorialSystem(self.master)
        
        self.master.tutorial_system.start_tutorial()
