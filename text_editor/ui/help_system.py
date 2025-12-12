import customtkinter as ctk
import tkinter as tk
import platform
import sys
from text_editor.config import APP_NAME
from text_editor.ui.help_content import HelpContentProvider
from text_editor.utils.language_manager import LanguageManager

class HelpSidebar(ctk.CTkScrollableFrame):
    """
    Yardım penceresinin sol tarafındaki menü ve arama çubuğunu yönetir.
    """
    def __init__(self, master, app_instance, sections, on_selection_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        self.sections = sections
        self.on_select = on_selection_callback
        self.buttons = {}
        self.lang_manager = LanguageManager.get_instance()
        
        self._setup_ui()
        
    def _setup_ui(self):
        self._create_logo()
        self._create_tutorial_button()
        self._create_search_box()
        self._create_buttons()
        
    def _create_logo(self):
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(logo_frame, text="🪐", font=("Segoe UI", 32)).pack()
        header_text = self.lang_manager.get("help.header", "Yardım Merkezi")
        ctk.CTkLabel(logo_frame, text=header_text, font=("Segoe UI", 14, "bold")).pack()

    def _create_tutorial_button(self):
        btn_text = self.lang_manager.get("help.start_tutorial", "🎓 İnteraktif Öğreticiyi Başlat")
        btn = ctk.CTkButton(
            self,
            text=btn_text,
            height=45,
            corner_radius=10,
            fg_color=("#00d4ff", "#0096c7"),
            hover_color=("#00b8e6", "#007ea7"),
            font=("Segoe UI", 13, "bold"),
            command=self._start_tutorial
        )
        btn.pack(fill="x", padx=10, pady=(10, 5))

    def _create_search_box(self):
        placeholder = self.lang_manager.get("help.search_placeholder", "🔍 Ara...")
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=35,
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Focus animation
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.configure(border_width=2))
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.configure(border_width=1))

    def _create_buttons(self):
        for key in self.sections.keys():
            display_text = self.lang_manager.get(f"help.sections.{key}", key)
            btn = ctk.CTkButton(
                self, 
                text=display_text, 
                anchor="w", 
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray35"),
                height=40,
                corner_radius=8,
                font=("Segoe UI", 12),
                command=lambda k=key: self.on_select(k) # Trigger parent callback with internal key
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.buttons[key] = btn # Store by internal key
            self._add_hover_effect(btn)

    def _add_hover_effect(self, btn):
        btn.bind("<Enter>", lambda e: btn.configure(cursor="hand2"))
        btn.bind("<Leave>", lambda e: btn.configure(cursor=""))

    def _on_search(self, event):
        query = self.search_entry.get().lower()
        for key, btn in self.buttons.items():
            display_text = btn.cget("text").lower()
            match = not query or query in display_text or query in key.lower()
            if match:
                if not btn.winfo_ismapped():
                    btn.pack(fill="x", padx=8, pady=3)
            else:
                if btn.winfo_ismapped():
                    btn.pack_forget()

    def update_selection_visuals(self, selected_key):
        """Seçili butonun görsel durumunu günceller."""
        for key, btn in self.buttons.items():
            if key == selected_key:
                btn.configure(fg_color=("gray85", "#404040"), font=("Segoe UI", 12, "bold"))
            else:
                btn.configure(fg_color="transparent", font=("Segoe UI", 12))

    def _start_tutorial(self):
        """Tutorial modunu başlatır."""
        from text_editor.ui.tutorial_mode import TutorialSystem
        if not hasattr(self.app, 'tutorial_system'):
            self.app.tutorial_system = TutorialSystem(self.app)
        self.app.tutorial_system.start_tutorial()


class HelpContentDisplay(ctk.CTkFrame):
    """
    Yardım penceresinin sağ tarafındaki içerik görüntüleme alanını yönetir.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = None
        self.text_area = None
        self._setup_ui()

    def _setup_ui(self):
        self.title_label = ctk.CTkLabel(
            self, 
            text="", 
            font=("Segoe UI", 24, "bold"), 
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.text_area = ctk.CTkTextbox(
            self, 
            wrap="word", 
            font=("Segoe UI", 13),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.text_area.grid(row=1, column=0, sticky="nsew")

    def show_content(self, title, content):
        """İçeriği görüntüler ve stillendirir."""
        self.title_label.configure(text=title)
        
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)
        
        self._apply_markdown_styling()
        
        self.text_area.configure(state="disabled")
        self.text_area.yview_moveto(0)
        
        # Basit bir fade-in efekti için animasyon metodunu tetikle (opsiyonel)
        # Buradaki animasyon mantığını basit tutuyoruz.

    def _apply_markdown_styling(self):
        """Metne görsel stiller uygular."""
        # Tag tanımları
        tb = self.text_area._textbox
        tb.tag_config("h1", font=("Segoe UI", 22, "bold"), foreground="#3a7ebf")
        tb.tag_config("h2", font=("Segoe UI", 16, "bold"), foreground="#61afef")
        tb.tag_config("bold", font=("Segoe UI", 13, "bold"))
        tb.tag_config("box", font=("Consolas", 12), foreground="#e5c07b")
        tb.tag_config("code", font=("Consolas", 12), background="#2c313a", foreground="#abb2bf")
        
        content = self.text_area.get("1.0", "end")
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_idx = i + 1
            if line.startswith("# "):
                self.text_area.tag_add("h1", f"{line_idx}.0", f"{line_idx}.end")
            elif line.startswith("## ") or "NASIL KULLANILIR?" in line:
                self.text_area.tag_add("h2", f"{line_idx}.0", f"{line_idx}.end")
            
            if any( c in line for c in ["┌", "└", "│", "─"]):
                self.text_area.tag_add("box", f"{line_idx}.0", f"{line_idx}.end")
                
            if line.strip().startswith("•") or line.strip().startswith("🔸"):
                self.text_area.tag_add("bold", f"{line_idx}.0", f"{line_idx}.2")

            if (line.startswith("    ") or line.startswith("\t")) and not line.strip().startswith("•"):
                self.text_area.tag_add("code", f"{line_idx}.0", f"{line_idx}.end")


class HelpWindow(ctk.CTkToplevel):
    """
    Ana yardım penceresi.
    Bileşenleri (Sidebar, ContentDisplay) ve navigasyon mantığını yönetir.
    """
    def __init__(self, master, app_instance, start_section="quick_start"):
        super().__init__(master)
        self.app = app_instance
        self.lang_manager = LanguageManager.get_instance()
        
        self.sections = self._get_sections()
        self.history = []
        self.history_index = -1
        
        self._setup_window()
        self._setup_layout()
        
        # Başlangıç
        self._select_initial_section(start_section)
        self.after(50, self._fade_in)

    def _get_sections(self):
        return {
            "quick_start": HelpContentProvider.get_quick_start,
            "shortcuts": HelpContentProvider.get_shortcuts,
            "multi_cursor": HelpContentProvider.get_multi_cursor_guide,
            "theme_guide": HelpContentProvider.get_theme_guide,
            "file_formats": HelpContentProvider.get_supported_formats,
            "markdown_guide": HelpContentProvider.get_markdown_guide,
            "tips": HelpContentProvider.get_tips_and_tricks,
            "faq": HelpContentProvider.get_faq,
            "performance": lambda: HelpContentProvider.get_performance_report(self.app),
            "image_viewer": HelpContentProvider.get_image_viewer_guide,
            "goto_line": HelpContentProvider.get_goto_line_guide,
            "report_bug": HelpContentProvider.get_report_bug,
            "about": HelpContentProvider.get_about
        }

    def _setup_window(self):
        title_text = self.lang_manager.get("help.title", f"🪐 {APP_NAME} - Yardım Merkezi").format(app_name=APP_NAME)
        self.title(title_text)
        self.geometry("1000x700")
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)
        self.lift()
        self.focus()

    def _setup_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_toolbar()
        
        # Sidebar
        self.sidebar = HelpSidebar(
            self, 
            app_instance=self.app, 
            sections=self.sections, 
            on_selection_callback=self.select_section,
            corner_radius=0,
            fg_color=("gray92", "#2b2b2b"),
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 1))
        
        # Content
        self.content_display = HelpContentDisplay(self)
        self.content_display.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def _create_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color=("gray95", "#2b2b2b"))
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.back_btn = self._create_nav_button(toolbar, self.lang_manager.get("help.buttons.back", "◀ Geri"), self.go_back)
        self.back_btn.pack(side="left", padx=(10, 5), pady=7)
        
        self.forward_btn = self._create_nav_button(toolbar, self.lang_manager.get("help.buttons.forward", "İleri ▶"), self.go_forward)
        self.forward_btn.pack(side="left", padx=5, pady=7)
        
        ctk.CTkLabel(toolbar, text="|", text_color=("gray60", "gray50")).pack(side="left", padx=10)
        
        home_text = self.lang_manager.get("help.buttons.home", "🏠 Ana Sayfa")
        home_btn = self._create_nav_button(toolbar, home_text, lambda: self.select_section("quick_start"), width=100)
        home_btn.pack(side="left", padx=5, pady=7)
        
        self._update_nav_buttons_state()

    def _create_nav_button(self, parent, text, command, width=80):
        btn = ctk.CTkButton(
            parent, text=text, width=width, height=32, corner_radius=6, command=command
        )
        return btn

    def select_section(self, key):
        """Bölüm seçme mantığı (Geçmiş kaydı tutar)."""
        # Aynı sayfa kontrolü
        if self.history_index != -1 and self.history and self.history[self.history_index] == key:
             return

        # Geçmişi güncelle (eğer geçmişin ortasındaysak ileri kısmını sil)
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        self.history.append(key)
        self.history_index = len(self.history) - 1
        
        self._load_section_content(key)

    def _load_section_content(self, key):
        """İçeriği yükler (Geçmişe eklemeden)."""
        if key not in self.sections:
            return

        # UI Güncelle
        self.sidebar.update_selection_visuals(key)
        
        # İçeriği Getir (Provider metodunu çalıştır)
        content_func = self.sections[key]
        content = content_func() # Burası hala ContentProvider'daki hardcoded metinleri döndürüyor. Düzeltilmeli.
        
        # Başlık da çevrilmeli
        display_title = self.lang_manager.get(f"help.sections.{key}", key)
        
        # Göster
        self.content_display.show_content(display_title, content)
        
        # Navigasyon butonlarını güncelle
        self._update_nav_buttons_state()

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            key = self.history[self.history_index]
            self._load_section_content(key)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            key = self.history[self.history_index]
            self._load_section_content(key)

    def _update_nav_buttons_state(self):
        self.back_btn.configure(state="normal" if self.history_index > 0 else "disabled")
        self.forward_btn.configure(state="normal" if self.history_index < len(self.history) - 1 else "disabled")

    def _select_initial_section(self, start_section):
        # start_section "Hızlı Başlangıç" gibi eski bir değer olabilir veya "quick_start"
        # Mapping yapmaya çalış
        target = "quick_start"
        
        # Eğer direkt key ise
        if start_section in self.sections:
             target = start_section
        else:
            # Belki Türkçe isimdir, tersine arama yapamayız kolayca ama basit bir kontrol:
            pass # Varsayılan quick_start
             
        self.select_section(target)

    def _fade_in(self):
        """Pencere açılış animasyonu."""
        current_alpha = self.attributes("-alpha")
        if current_alpha < 1.0:
            new_alpha = current_alpha + 0.1
            self.attributes("-alpha", new_alpha)
            self.after(30, self._fade_in)
        else:
            self.attributes("-alpha", 1.0)


class HelpSystem:
    """Singleton yönetim sınıfı."""
    def __init__(self, master_window):
        self.master = master_window
        self.help_window = None

    def open_help(self, section="Hızlı Başlangıç"):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self.master, self.master, start_section=section)
        else:
            self.help_window.lift()
            self.help_window.focus()
            
            # Bölüm ara
            found = False
            for sec_name in self.help_window.sections.keys():
                if section in sec_name:
                    self.help_window.select_section(sec_name)
                    found = True
                    break
            if not found:
                self.help_window.select_section("🚀 Hızlı Başlangıç")
            
    def start_tutorial(self):
        """Tutorial Mode başlatıcı."""
        from text_editor.ui.tutorial_mode import TutorialSystem
        if not hasattr(self.master, 'tutorial_system'):
            self.master.tutorial_system = TutorialSystem(self.master)
        self.master.tutorial_system.start_tutorial()
