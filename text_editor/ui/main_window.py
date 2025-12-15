import customtkinter as ctk
from text_editor.config import APP_NAME
from text_editor.ui.tab_manager import TabManager
from text_editor.ui.status_bar import StatusBar
from text_editor.ui.file_explorer import FileExplorer
import tkinter as tk
import os
import re
import json
from text_editor.utils.shortcut_manager import ShortcutManager

class MainWindow(ctk.CTk):
    """
    Uygulamanın ana penceresi. 
    Tüm üst düzey bileşenleri (Menü, Dosya Gezgini, Sekmeler, Durum Çubuğu) barındırır
    ve aralarındaki koordinasyonu sağlar.
    """
    def __init__(self):
        super().__init__()
        
        # Dil yöneticisini başlat
        from text_editor.utils.language_manager import LanguageManager
        self.lang = LanguageManager.get_instance()
        
        # Ayarları yükle
        self.settings = self.load_settings()
        
        # Kayıtlı dili uygula
        saved_lang = self.settings.get("language", "Türkçe")
        self.lang.load_language(saved_lang)
        
        # Modern menü bar (tema uygulandıktan sonra güncellenecek)
        self.modern_menu = None
        
        # Görünüm durumları
        self._status_bar_visible = self.settings.get("show_status_bar", True)
        self._file_explorer_visible = self.settings.get("show_file_explorer", True)
        self._menu_visible = True
        self._zen_mode = False
        self._terminal_visible = self.settings.get("show_terminal", False)
        self.terminal_panel = None  # Terminal paneli referansı
        self._markdown_preview_visible = False  # Markdown preview başlangıçta kapalı
        self.markdown_preview = None  # Markdown preview referansı

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Menü
        self.grid_rowconfigure(1, weight=1)  # Sekmeler (ana içerik)
        self.grid_rowconfigure(2, weight=0)  # Terminal (başlangıçta gizli)
        self.grid_rowconfigure(3, weight=0)  # Durum çubuğu

        # 1. Bileşenleri Başlat
        self.status_bar = StatusBar(self) # Önce durum çubuğunu başlat
        self.tab_manager = TabManager(self)
        
        # Dosya Gezgini
        # Önemli: open yöntemini sarmalamak için bir lambda iletin veya open_file'ın bağımsız değişkenleri işlediğinden emin olun
        self.file_explorer = FileExplorer(self, open_file_callback=self.open_file_from_explorer)

        # 2. Düzeni Oluştur
        # Menü Çubuğu (Satır 0)
        self.create_custom_menu()
        
        # Dosya Gezgini (Satır 1, Sütun 0)
        self.file_explorer.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(10, 0))
        
        # Sekme Yöneticisi (Satır 1, Sütun 1)
        self.tab_manager.grid(row=1, column=1, sticky="nsew", padx=10, pady=(10, 0))

        # Durum Çubuğu (Satır 3, tümünü kapsayan)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Ağırlıkları güncelle (Sütun 0: Kenar Çubuğu, Sütun 1: Ana)
        self.grid_columnconfigure(0, weight=0, minsize=200) # Kenar çubuğu başlangıçta sabit genişlikte mi? yoksa yeniden boyutlandırılabilir mi
        self.grid_columnconfigure(1, weight=1)

    def open_file_from_explorer(self, file_path):
        """
        Dosya gezgininden (FileExplorer) gelen dosya açma isteğini karşılar.
        İsteği TabManager'a yönlendirerek dosyayı yeni veya mevcut sekmede açar.
        """
        # Belirli bir yolu açmak için yardımcı
        # TabManager içinde bir yöntem göstermemiz veya mantığı yeniden kullanmamız gerekiyor
        # İdeal olarak TabManager'daki open_file isteğe bağlı bir yol kabul etmelidir
        self.tab_manager.open_file(path=file_path)

    def open_folder(self):
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.file_explorer.set_root_path(folder_path)
            self.title(f"{APP_NAME} - {os.path.basename(folder_path)}")

    def create_custom_menu(self):
        """
        Özel başlık çubuğu/menü çubuğunu ve uygulama menülerini oluşturur.
        Ayrıca klavye kısayollarını (Ctrl+N, Ctrl+S vb.) tanımlar.
        Modern, estetik bir tasarıma sahip.
        """
        # Menü çubuğu için çerçeve - daha yüksek ve stilize
        self.menu_frame = ctk.CTkFrame(
            self, 
            height=45, 
            corner_radius=0, 
            fg_color=("white", "#2b2b2b"),
            border_width=0
        )
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        # Menü düğmeleri için liste
        self.menu_buttons = []
        
        # Menü düğmeleri oluşturmak için yardımcı
        def add_menu_btn(text_key, command, icon="", pass_widget=False):
            text = self.lang.get(text_key)
            display_text = f"{icon} {text}" if icon else text
            btn = ctk.CTkButton(
                self.menu_frame, 
                text=display_text,
                width=80, 
                height=40,
                corner_radius=6,
                fg_color="transparent", 
                hover_color=("gray75", "gray25"),
                font=("Segoe UI", 12, "bold"),
                anchor="center",
                border_width=0
            )
            if pass_widget:
                btn.configure(command=lambda: command(btn))
            else:
                btn.configure(command=command)
                
            btn.pack(side="left", padx=3, pady=2)
            self.menu_buttons.append(btn)
            return btn

        # Logo/Başlık
        logo_label = ctk.CTkLabel(
            self.menu_frame,
            text="🪐 Memati Editör",
            font=("Segoe UI", 14, "bold"),
            text_color=("gray20", "#00d4ff")
        )
        logo_label.pack(side="left", padx=(15, 30))

        # Menü Butonları
        add_menu_btn("menu.file", self.show_file_menu, "📁", pass_widget=True)
        add_menu_btn("menu.edit", self.show_edit_menu, "✏️", pass_widget=True)
        add_menu_btn("menu.view", self.show_view_menu, "👁️", pass_widget=True)
        add_menu_btn("menu.theme", self.show_theme_menu, "🎨", pass_widget=True)
        
        # Tutorial butonu - özel stil
        tutorial_btn = ctk.CTkButton(
            self.menu_frame,
            text=f"🎓 {self.lang.get('menu.tutorial')}",
            width=90,
            height=40,
            corner_radius=6,
            fg_color=("#00d4ff", "#0096c7"),
            hover_color=("#00b8e6", "#007ea7"),
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            border_width=0,
            command=self.start_tutorial
        )
        tutorial_btn.pack(side="left", padx=3, pady=2)
        self.menu_buttons.append(tutorial_btn)
        
        # Ayarlar butonu - özel stil
        settings_btn = ctk.CTkButton(
            self.menu_frame,
            text=f"⚙️ {self.lang.get('menu.settings')}",
            width=90,
            height=40,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            border_width=0,
            command=self.open_settings
        )
        settings_btn.pack(side="left", padx=3, pady=2)
        self.menu_buttons.append(settings_btn)
        
        add_menu_btn("menu.help", lambda: self.help_system.open_help("Hızlı Başlangıç"), "❓", pass_widget=False)
        
        # Sağ tarafta versiyon bilgisi
        version_label = ctk.CTkLabel(
            self.menu_frame,
            text="v1.0",
            font=("Segoe UI", 9),
            text_color=("gray50", "gray60")
        )
        version_label.pack(side="right", padx=15)
        
        # Yardım Sistemini Başlat
        from text_editor.ui.help_system import HelpSystem
        self.help_system = HelpSystem(self)

        # Klavye Kısayolları (ShortcutManager üzerinden)
        self.shortcut_manager = ShortcutManager.get_instance()
        shortcuts = self.shortcut_manager
        
        # Dosya İşlemleri
        self.bind(shortcuts.get("new_tab"), lambda e: self.tab_manager.add_new_tab())
        self.bind(shortcuts.get("open_file"), lambda e: self.tab_manager.open_file())
        self.bind(shortcuts.get("open_folder"), lambda e: self.open_folder())
        self.bind(shortcuts.get("save_file"), lambda e: self.tab_manager.save_current_file())
        self.bind(shortcuts.get("save_as"), lambda e: self.tab_manager.save_current_file_as())
        self.bind(shortcuts.get("find"), lambda e: self.tab_manager.show_find_replace())
        self.bind(shortcuts.get("goto_line"), lambda e: self.tab_manager.show_goto_line())
        
        # Görünüm
        self.bind(shortcuts.get("toggle_fullscreen"), self.toggle_fullscreen)
        self.bind(shortcuts.get("toggle_file_explorer"), lambda e: self.toggle_file_explorer())
        self.bind(shortcuts.get("toggle_minimap"), lambda e: self.tab_manager.toggle_minimap())
        self.bind(shortcuts.get("toggle_status_bar"), lambda e: self.toggle_status_bar())
        self.bind(shortcuts.get("toggle_line_numbers"), lambda e: self.tab_manager.toggle_line_numbers())
        self.bind(shortcuts.get("toggle_word_wrap"), lambda e: self.tab_manager.toggle_word_wrap())
        self.bind(shortcuts.get("toggle_terminal"), lambda e: self.toggle_terminal())
        self.bind(shortcuts.get("preview_markdown"), lambda e: self.toggle_markdown_preview())
        
        # Zen Mode
        self.bind(shortcuts.get("toggle_zen_mode"), self.toggle_zen_mode)
        
        # Kopyalama Kısayolları (Henüz manager'da yoksa ekleyelim veya varsayılan bırakalım)
        self.bind("<Control-Shift-C>", lambda e: self.tab_manager.copy_path())
        self.bind("<Control-Alt-c>", lambda e: self.tab_manager.copy_relative_path())
        
        # Ayarlar kısayolu
        self.bind("<Control-comma>", lambda e: self.open_settings())
        
        # Başlangıç temasını uygula
        saved_theme = self.settings.get("theme", "Dark")
        self.after(100, lambda: self.apply_theme(saved_theme))

    def create_zen_exit_button(self):
        """Zen modu çıkış butonunu oluşturur."""
        self.zen_exit_btn = ctk.CTkButton(
            self,
            text=self.lang.get("menu.items.zen_exit"),
            command=self.toggle_zen_mode,
            width=140,
            height=32,
            corner_radius=16,
            fg_color=("gray80", "gray20"),
            hover_color=("gray70", "gray30"),
            font=("Segoe UI", 12, "bold")
        )
        # Sağ üst köşeye yerleştir
        self.zen_exit_btn.place(relx=0.98, rely=0.02, anchor="ne")

    def show_file_menu(self, button):
        """Dosya menüsünü gösterir - modern, stilize dropdown"""
        if not self.modern_menu:
            return
        
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        
        menu_items = [
            {
                "icon": "📄",
                "label": self.lang.get("menu.items.new_tab"),
                "shortcut": fmt(shortcuts.get("new_tab")),
                "command": self.tab_manager.add_new_tab
            },
            {
                "icon": "📂",
                "label": self.lang.get("menu.items.open_file"),
                "shortcut": fmt(shortcuts.get("open_file")),
                "command": self.tab_manager.open_file
            },
            {
                "icon": "📁",
                "label": self.lang.get("menu.items.open_folder"),
                "shortcut": fmt(shortcuts.get("open_folder")),
                "command": self.open_folder
            },
            {"separator": True},
            {
                "icon": "💾",
                "label": self.lang.get("menu.items.save"),
                "shortcut": fmt(shortcuts.get("save_file")),
                "command": self.tab_manager.save_current_file
            },
            {
                "icon": "📝",
                "label": self.lang.get("menu.items.save_as"),
                "shortcut": fmt(shortcuts.get("save_as")),
                "command": self.tab_manager.save_current_file_as
            },
            {"separator": True},
            {
                "icon": "🔍",
                "label": self.lang.get("menu.items.find_replace"),
                "shortcut": fmt(shortcuts.get("find")),
                "command": self.tab_manager.show_find_replace
            },
            {
                "icon": "🎯",
                "label": self.lang.get("menu.items.goto_line"),
                "shortcut": fmt(shortcuts.get("goto_line")),
                "command": self.tab_manager.show_goto_line
            },
            {"separator": True},
            {
                "icon": "🚪",
                "label": self.lang.get("menu.items.exit"),
                "shortcut": fmt(shortcuts.get("quit")),
                "command": self.quit
            }
        ]
        
        self.modern_menu.show_dropdown(button, menu_items)

    def show_edit_menu(self, button):
        """Düzenle menüsünü gösterir - modern, stilize dropdown"""
        if not self.modern_menu:
            return
        
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        
        menu_items = [
            {
                "icon": "↶",
                "label": self.lang.get("menu.items.undo"),
                "shortcut": fmt(shortcuts.get("undo")),
                "command": lambda: self.focus_get().event_generate("<<Undo>>") if self.focus_get() else None
            },
            {
                "icon": "↷",
                "label": self.lang.get("menu.items.redo"),
                "shortcut": fmt(shortcuts.get("redo")),
                "command": lambda: self.focus_get().event_generate("<<Redo>>") if self.focus_get() else None
            },
            {"separator": True},
            {
                "icon": "✂️",
                "label": self.lang.get("menu.items.cut"),
                "shortcut": fmt(shortcuts.get("cut")),
                "command": lambda: self.focus_get().event_generate("<<Cut>>") if self.focus_get() else None
            },
            {
                "icon": "📋",
                "label": self.lang.get("menu.items.copy"),
                "shortcut": fmt(shortcuts.get("copy")),
                "command": lambda: self.focus_get().event_generate("<<Copy>>") if self.focus_get() else None
            },
            {
                "icon": "📌",
                "label": self.lang.get("menu.items.paste"),
                "shortcut": fmt(shortcuts.get("paste")),
                "command": lambda: self.focus_get().event_generate("<<Paste>>") if self.focus_get() else None
            },
            {"separator": True},
            {
                "icon": "📑",
                "label": self.lang.get("menu.items.duplicate_line"),
                "shortcut": fmt(shortcuts.get("duplicate_line")),
                "command": self.tab_manager.duplicate_line
            },
            {
                "icon": "⬆️",
                "label": self.lang.get("menu.items.move_up"),
                "shortcut": fmt(shortcuts.get("move_line_up")),
                "command": self.tab_manager.move_line_up
            },
            {
                "icon": "⬇️",
                "label": self.lang.get("menu.items.move_down"),
                "shortcut": fmt(shortcuts.get("move_line_down")),
                "command": self.tab_manager.move_line_down
            },
            {
                "icon": "🗑️",
                "label": self.lang.get("menu.items.delete_line"),
                "shortcut": fmt(shortcuts.get("delete_line")),
                "command": self.tab_manager.delete_line
            },
            {
                "icon": "🔗",
                "label": self.lang.get("menu.items.join_lines"),
                "shortcut": fmt(shortcuts.get("join_lines")),
                "command": self.tab_manager.join_lines
            },
            {"separator": True},
            {
                "icon": "🔍",
                "label": self.lang.get("menu.items.find_replace"),
                "shortcut": fmt(shortcuts.get("find")),
                "command": self.tab_manager.show_find_replace
            },
            {
                "icon": "🎯",
                "label": self.lang.get("menu.items.goto_line"),
                "shortcut": fmt(shortcuts.get("goto_line")),
                "command": self.tab_manager.show_goto_line
            },
            {"separator": True},
            {
                "icon": "📋",
                "label": self.lang.get("menu.items.copy_path"),
                "shortcut": fmt(shortcuts.get("copy_path")),
                "command": self.tab_manager.copy_path
            },
            {
                "icon": "📂",
                "label": self.lang.get("menu.items.relative_path"),
                "shortcut": fmt(shortcuts.get("copy_relative_path")),
                "command": self.tab_manager.copy_relative_path
            }
        ]
        
        self.modern_menu.show_dropdown(button, menu_items)

    def popup_menu(self, menu, button):
        """Eski tkinter menü sistemi için geriye dönük uyumluluk"""
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def show_theme_menu(self, button):
        """Tema menüsünü gösterir - modern, ikonlu dropdown"""
        if not self.modern_menu:
            return
        
        from text_editor.theme_config import get_available_themes
        
        # Temalar için ikonlar
        theme_icons = {
            "Dark": "🌑",
            "Light": "☀️",
            "Dracula": "🧛",
            "Solarized Light": "🌅",
            "Monokai": "🔥",
            "Nord": "❄️",
            "Gruvbox": "🍂",
            "One Dark Pro": "⚫",
            "GitHub Dark": "🐙",
            "Synthwave 84": "🌃",
            "Solarized Dark": "🌘",
            "Night Owl": "🦉",
            "Tokyo Night": "🗼",
            "Cobalt2": "🔵",
            "Material Palenight": "👾",
            "Ayu Dark": "🦈",
            "Shades of Purple": "💜"
        }
        
        menu_items = []
        for theme_name in get_available_themes():
            icon = theme_icons.get(theme_name, "🎨")
            menu_items.append({
                "icon": icon,
                "label": theme_name,
                "command": lambda t=theme_name: self.change_theme(t)
            })
        
        self.modern_menu.show_dropdown(button, menu_items)

    def change_theme(self, theme_name):
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name):
        from text_editor.theme_config import get_theme
        from text_editor.ui.modern_menu import ModernMenuBar
        theme = get_theme(theme_name)
        
        # Mevcut tema adını kaydet (terminal için)
        self._current_theme_name = theme_name
        
        # Modern menü bar'ı ilk kez oluştur veya tema bilgisini güncelle
        if not self.modern_menu:
            self.modern_menu = ModernMenuBar(self, theme)
        else:
            self.modern_menu.theme = theme
        
        # Temel görünüm modunu ayarla (Açık/Koyu)
        ctk.set_appearance_mode(theme["type"])
        
        # Pencere başlığını güncelle
        # Pencere başlığını güncelle
        theme_msg = self.lang.get("menu.theme")  # "Tema" veya "Theme"
        # İkonu temizleyelim
        theme_msg = theme_msg.replace("🎨", "").strip()
        self.title(f"🪐 {APP_NAME} - {theme_name} {theme_msg}")
        
        # 1. Menü Çubuğu - Gradient efekti için border ekle
        self.menu_frame.configure(
            fg_color=theme["menu_bg"],
            border_color=theme.get("accent_color", theme["status_bg"]),
            border_width=2
        )
        for btn in self.menu_buttons:
            btn.configure(
                text_color=theme["menu_fg"], 
                hover_color=theme["menu_hover"],
                border_color=theme.get("accent_color", "transparent")
            )

        # 2. Durum Çubuğu - Yeni yapıya göre
        self.status_bar.configure(
            fg_color=theme["status_bg"],
            border_color=theme.get("accent_color", theme["editor_bg"]),
            border_width=1
        )
        
        # Durum çubuğu etiketlerini güncelle
        if hasattr(self.status_bar, 'message_label'):
            self.status_bar.message_label.configure(text_color=theme["status_fg"])
        if hasattr(self.status_bar, 'file_info_label'):
            self.status_bar.file_info_label.configure(text_color=theme["status_fg"])
        if hasattr(self.status_bar, 'cursor_info'):
            self.status_bar.cursor_info.configure(text_color=theme["status_fg"])
        if hasattr(self.status_bar, 'encoding_label'):
            self.status_bar.encoding_label.configure(text_color=theme["status_fg"])
        
        # Eski info_label varsa (geriye dönük uyumluluk)
        if hasattr(self.status_bar, 'info_label'):
            self.status_bar.info_label.configure(text_color=theme["status_fg"])

        # 3. Sekme Yöneticisi ve Editörler
        self.tab_manager.apply_theme(theme)
            
        # 4. Dosya Gezgini
        self.file_explorer.update_theme(theme)
        self.file_explorer.configure(fg_color=theme["tab_bg"])
        
        # 5. Terminal (varsa)
        if self.terminal_panel:
            self.terminal_panel.update_theme(theme)
        
        # 6. Markdown Preview (varsa)
        if self.markdown_preview:
            self.markdown_preview.update_theme(theme)
        
        # 7. Ana pencere arka planı
        self.configure(fg_color=theme.get("bg", "#1e1e1e"))

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    # === Görünüm Ayarları ===
    
    def show_view_menu(self, button):
        """Görünüm menüsünü gösterir - toggle seçenekleri ile"""
        if not self.modern_menu:
            return
        
        # Mevcut durumları al
        view_states = self.tab_manager.get_view_states()
        
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        
        def get_toggle_icon(is_on):
            return "✅" if is_on else "⬜"
        
        menu_items = [
            {
                "icon": get_toggle_icon(view_states.get("line_numbers", True)),
                "label": self.lang.get("menu.items.line_numbers"),
                "shortcut": fmt(shortcuts.get("toggle_line_numbers")),
                "command": self.toggle_line_numbers_with_feedback
            },
            {
                "icon": get_toggle_icon(view_states.get("word_wrap", False)),
                "label": self.lang.get("menu.items.word_wrap"),
                "shortcut": fmt(shortcuts.get("toggle_word_wrap")),
                "command": self.toggle_word_wrap_with_feedback
            },
            {
                "icon": get_toggle_icon(view_states.get("minimap", True)),
                "label": self.lang.get("menu.items.minimap"),
                "shortcut": fmt(shortcuts.get("toggle_minimap")),
                "command": self.toggle_minimap_with_feedback
            },
            {"separator": True},
            {
                "icon": get_toggle_icon(self._status_bar_visible),
                "label": self.lang.get("menu.items.status_bar"),
                "shortcut": fmt(shortcuts.get("toggle_status_bar")),
                "command": self.toggle_status_bar
            },
            {
                "icon": get_toggle_icon(self._file_explorer_visible),
                "label": self.lang.get("menu.items.file_explorer"),
                "shortcut": fmt(shortcuts.get("toggle_file_explorer")),
                "command": self.toggle_file_explorer
            },
            {
                "icon": get_toggle_icon(self._terminal_visible),
                "label": self.lang.get("menu.items.terminal"),
                "shortcut": fmt(shortcuts.get("toggle_terminal")),
                "command": self.toggle_terminal
            },
            {
                "icon": get_toggle_icon(self._markdown_preview_visible),
                "label": self.lang.get("menu.items.markdown_preview"),
                "shortcut": fmt(shortcuts.get("preview_markdown")),
                "command": self.toggle_markdown_preview
            },
            {"separator": True},
            {
                "icon": "🧘",
                "label": self.lang.get("menu.items.zen_mode"),
                "shortcut": fmt(shortcuts.get("toggle_zen_mode")),
                "command": self.toggle_zen_mode
            },
            {
                "icon": "📺",
                "label": self.lang.get("menu.items.fullscreen"),
                "shortcut": fmt(shortcuts.get("toggle_fullscreen")),
                "command": self.toggle_fullscreen
            }
        ]
        
        self.modern_menu.show_dropdown(button, menu_items)
    
    def toggle_line_numbers_with_feedback(self):
        """Satır numaralarını toggle eder ve durum mesajı gösterir."""
        is_visible = self.tab_manager.toggle_line_numbers()
        msg = self.lang.get("status_messages.line_numbers_on") if is_visible else self.lang.get("status_messages.line_numbers_off")
        self.status_bar.set_message(msg, "info")
    
    def toggle_word_wrap_with_feedback(self):
        """Word wrap'ı toggle eder ve durum mesajı gösterir."""
        is_enabled = self.tab_manager.toggle_word_wrap()
        msg = self.lang.get("status_messages.word_wrap_on") if is_enabled else self.lang.get("status_messages.word_wrap_off")
        self.status_bar.set_message(msg, "info")
    
    def toggle_minimap_with_feedback(self):
        """Minimap'i toggle eder ve durum mesajı gösterir."""
        is_visible = self.tab_manager.toggle_minimap()
        msg = self.lang.get("status_messages.minimap_on") if is_visible else self.lang.get("status_messages.minimap_off")
        self.status_bar.set_message(msg, "info")
    
    def toggle_status_bar(self, event=None):
        """Durum çubuğunu gösterir/gizler."""
        self._status_bar_visible = not self._status_bar_visible
        
        if self._status_bar_visible:
            self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        else:
            self.status_bar.grid_remove()
        
        return self._status_bar_visible
    
    def toggle_file_explorer(self, event=None):
        """Dosya gezginini gösterir/gizler."""
        self._file_explorer_visible = not self._file_explorer_visible
        
        if self._file_explorer_visible:
            self.file_explorer.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(10, 0))
            self.grid_columnconfigure(0, weight=0, minsize=200)
        else:
            self.file_explorer.grid_remove()
            self.grid_columnconfigure(0, weight=0, minsize=0)
        
        # Durum mesajı (status bar görünürse)
        if self._status_bar_visible:
            msg = self.lang.get("status_messages.explorer_on") if self._file_explorer_visible else self.lang.get("status_messages.explorer_off")
            self.status_bar.set_message(msg, "info")
        
        return self._file_explorer_visible
    
    def _zen_mode_check(self, event=None):
        """Zen mode için ikinci tuş (Z) bekler."""
        # Ctrl+K basıldığında bir sonraki tuşu bekle
        def wait_for_z(e):
            if e.keysym.lower() == 'z':
                self.toggle_zen_mode()
            # Bağlamayı kaldır
            self.unbind("<Key>")
        
        # Geçici olarak bir sonraki tuşu bekle
        self.bind("<Key>", wait_for_z)
        # 1 saniye sonra iptal et
        self.after(1000, lambda: self.unbind("<Key>"))
    
    def toggle_zen_mode(self, event=None):
        """
        Zen Mode: Sadece editörü göster, tüm panelleri gizle.
        Tekrar çağrıldığında eski duruma geri dön.
        """
        self._zen_mode = not self._zen_mode
        
        if self._zen_mode:
            # Zen Mode'a gir - önceki durumları kaydet
            self._pre_zen_status_bar = self._status_bar_visible
            self._pre_zen_file_explorer = self._file_explorer_visible
            self._pre_zen_menu = self._menu_visible
            self._pre_zen_line_numbers = self.tab_manager.get_view_states().get("line_numbers", True)
            self._pre_zen_minimap = self.tab_manager.get_view_states().get("minimap", True)
            
            # Tüm panelleri gizle
            self.menu_frame.grid_remove()
            self.status_bar.grid_remove()
            self.file_explorer.grid_remove()
            self.grid_columnconfigure(0, weight=0, minsize=0)
            
            # Editör ayarları
            for editor in self.tab_manager.editors.values():
                editor.toggle_line_numbers(False)
                editor.toggle_minimap(False)
            
            # Tam ekran yap
            self.attributes("-fullscreen", True)
            
            # Çıkış butonunu göster
            self.create_zen_exit_button()
            
            self._status_bar_visible = False
            self._file_explorer_visible = False
            self._menu_visible = False
            
        else:
            # Zen Mode'dan çık - önceki durumları geri yükle
            self.attributes("-fullscreen", False)
            
            # Çıkış butonunu kaldır
            if hasattr(self, 'zen_exit_btn'):
                self.zen_exit_btn.destroy()
            
            # Menüyü geri getir
            self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
            self._menu_visible = True
            
            # Önceki durumları geri yükle
            if getattr(self, '_pre_zen_status_bar', True):
                self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
                self._status_bar_visible = True
            
            if getattr(self, '_pre_zen_file_explorer', True):
                self.file_explorer.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(10, 0))
                self.grid_columnconfigure(0, weight=0, minsize=200)
                self._file_explorer_visible = True
            
            # Editör ayarlarını geri yükle
            for editor in self.tab_manager.editors.values():
                editor.toggle_line_numbers(getattr(self, '_pre_zen_line_numbers', True))
                editor.toggle_minimap(getattr(self, '_pre_zen_minimap', True))
        
        return self._zen_mode
    
    def toggle_terminal(self, event=None):
        """
        Terminal panelini gösterir/gizler.
        Ctrl+` kısayolu ile çağrılır.
        """
        self._terminal_visible = not self._terminal_visible
        
        if self._terminal_visible:
            # Terminal panelini oluştur (eğer yoksa)
            if not self.terminal_panel:
                # Mevcut temayı al
                from text_editor.theme_config import get_theme
                from text_editor.ui.terminal import TerminalPanel
                current_theme = getattr(self, '_current_theme_name', 'Dark')
                theme = get_theme(current_theme)
                
                self.terminal_panel = TerminalPanel(self, theme=theme)
                
                # Çalışma dizinini ayarla (açık dosyanın dizini veya proje dizini)
                if hasattr(self.file_explorer, 'root_path') and self.file_explorer.root_path:
                    self.terminal_panel.set_working_directory(self.file_explorer.root_path)
            
            # Terminal panelini göster
            self.terminal_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5, 0))
            self.grid_rowconfigure(2, weight=0, minsize=200)  # Terminal yüksekliği
            
            # Odaklan
            self.terminal_panel.focus_input()
            
            # Durum mesajı
            if self._status_bar_visible:
                self.status_bar.set_message(self.lang.get("status_messages.terminal_opened"), "success")
        else:
            # Terminal panelini gizle
            if self.terminal_panel:
                self.terminal_panel.grid_remove()
            self.grid_rowconfigure(2, weight=0, minsize=0)
            
            # Durum mesajı
            if self._status_bar_visible:
                self.status_bar.set_message(self.lang.get("status_messages.terminal_closed"), "info")
        
        return self._terminal_visible
    
    def toggle_markdown_preview(self, event=None):
        """
        Markdown önizleme panelini gösterir/gizler.
        Ctrl+Shift+V kısayolu ile çağrılır.
        Sadece .md dosyaları için aktif olmalı.
        """
        # Mevcut editörü al
        editor = self.tab_manager.get_current_editor()
        if not editor:
            if self._status_bar_visible:
                self.status_bar.set_message(self.lang.get("status_messages.file_needed"), "warning")
            return
        
        # Markdown dosyası mı kontrol et
        file_path = getattr(editor, 'file_path', None)
        is_markdown = False
        if file_path:
            is_markdown = file_path.lower().endswith(('.md', '.markdown', '.mdown', '.mkd'))
        else:
            # Dosya yolu yoksa içeriğe bak
            content = editor.text_area.get("1.0", "100.0")
            # Markdown belirtileri var mı kontrol et
            is_markdown = bool(re.search(r'^#+\s|^[\-\*]\s|^>\s|```', content, re.MULTILINE))
        
        self._markdown_preview_visible = not self._markdown_preview_visible
        
        if self._markdown_preview_visible:
            # Önizleme panelini oluştur (eğer yoksa)
            if not self.markdown_preview:
                from text_editor.ui.markdown_preview import MarkdownPreview
                # Mevcut temayı al
                from text_editor.theme_config import get_theme
                current_theme = getattr(self, '_current_theme_name', 'Dark')
                theme = get_theme(current_theme)
                
                self.markdown_preview = MarkdownPreview(self, editor=editor, theme=theme)
            else:
                # Editörü güncelle
                self.markdown_preview.set_editor(editor)
            
            # Layout'u düzenle - sağ tarafta göster
            # Mevcut grid yapısını değiştirmemek için, tab_manager'ın yanına koyalım
            self.grid_columnconfigure(2, weight=1)  # Preview için yeni sütun
            self.markdown_preview.grid(row=1, column=2, sticky="nsew", padx=(5, 10), pady=(10, 0))
            
            # Editörü bağla
            self.markdown_preview.set_editor(editor)
            
            # Durum mesajı
            # Durum mesajı
            if self._status_bar_visible:
                self.status_bar.set_message(self.lang.get("status_messages.preview_opened"), "success")
        else:
            # Önizleme panelini gizle
            self.close_markdown_preview()
        
        return self._markdown_preview_visible
    
    def close_markdown_preview(self):
        """Markdown önizleme panelini kapatır."""
        self._markdown_preview_visible = False
        
        if self.markdown_preview:
            self.markdown_preview.grid_remove()
        
        # Sütun ağırlığını sıfırla
        self.grid_columnconfigure(2, weight=0, minsize=0)
        
        # Durum mesajı
        # Durum mesajı
        if self._status_bar_visible:
            self.status_bar.set_message(self.lang.get("status_messages.preview_closed"), "info")
    
    def start_tutorial(self):
        """Tutorial Mode'u başlatır"""
        from text_editor.ui.tutorial_mode import TutorialSystem
        
        if not hasattr(self, 'tutorial_system'):
            self.tutorial_system = TutorialSystem(self)
        
        self.tutorial_system.start_tutorial()
    
    def open_settings(self):
        """Ayarlar penceresini açar."""
        def apply_settings(new_settings):
            """Ayarları uygular."""
            # Eski dili kaydet
            old_lang = self.settings.get("language", "Türkçe")

            self.settings = new_settings
            
            # Tema değişmişse uygula
            if "theme" in new_settings:
                self.apply_theme(new_settings["theme"])
            
            # Yazı tipi değişmişse
            if "font_family" in new_settings or "font_size" in new_settings:
                font_family = new_settings.get("font_family", "Consolas")
                font_size = new_settings.get("font_size", 14)
                # Tüm editörlere uygula
                for editor in self.tab_manager.editors.values():
                    editor.text_area.configure(font=(font_family, font_size))
            
            # Görünüm ayarları
            if "show_status_bar" in new_settings:
                if new_settings["show_status_bar"] != self._status_bar_visible:
                    self.toggle_status_bar()
            
            if "show_file_explorer" in new_settings:
                if new_settings["show_file_explorer"] != self._file_explorer_visible:
                    self.toggle_file_explorer()
            
            if "show_terminal" in new_settings:
                if new_settings["show_terminal"] != self._terminal_visible:
                    self.toggle_terminal()
            
            # Editör ayarları
            if "show_line_numbers" in new_settings:
                for editor in self.tab_manager.editors.values():
                    editor.toggle_line_numbers(new_settings["show_line_numbers"])
            
            if "word_wrap" in new_settings:
                for editor in self.tab_manager.editors.values():
                    editor.toggle_word_wrap(new_settings["word_wrap"])
            
            if "show_minimap" in new_settings:
                for editor in self.tab_manager.editors.values():
                    editor.toggle_minimap(new_settings["show_minimap"])
            
            # Dil değişmişse
            new_lang = new_settings.get("language", "Türkçe")
            if new_lang != old_lang:
                # Dil dosyasını yükle (LanguageManager otomatik dönüştürür)
                self.lang.load_language(new_lang)
                
                # Menüyü yeniden oluştur
                for widget in self.menu_frame.winfo_children():
                    widget.destroy()
                self.menu_buttons.clear()
                self.create_custom_menu()
                
                # Dosya Gezgini başlığını güncelle
                if hasattr(self, 'file_explorer') and self.file_explorer:
                    self.file_explorer.update_language()
                
                # Sekme isimlerini güncelle
                if hasattr(self, 'tab_manager') and self.tab_manager:
                    self.tab_manager.update_language()
                    
                # Pencere başlığını güncelle
                current_tab = self.tab_manager.get_current_tab_name() or self.lang.get("menu.items.new_tab", "Yeni Dosya")
                app_name = new_settings.get("app_name", "Memati Editör")
                self.title(f"{app_name} - {current_tab}")

                # Tema border'larını tekrar uygula
                current_theme_name = new_settings.get("theme", getattr(self, '_current_theme_name', 'Dark'))
                self.apply_theme(current_theme_name)
                
                # Durum mesajını güncelle
                welcome_msg = self.lang.get("status_messages.ready", "Hazır")
                self.status_bar.set_message(welcome_msg)

            # Ayarları kaydet
            self.save_settings()
            
            # Durum mesajı
            if self._status_bar_visible:
                msg = "✅ Settings applied" if self.lang.current_lang == "en" else "✅ Ayarlar uygulandı"
                self.status_bar.set_message(msg, "success")
        
        # Ayarlar penceresini aç
        from text_editor.ui.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self, self.settings, apply_settings)
    
    def load_settings(self):
        """Ayarları dosyadan yükler."""
        settings_file = os.path.join(
            os.path.expanduser("~"),
            ".memati_editor",
            "settings.json"
        )
        
        # Varsayılan ayarlar
        default_settings = {
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
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Varsayılan ayarları güncelle
                    default_settings.update(loaded_settings)
            except Exception as e:
                print(f"Ayarlar yüklenemedi: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Ayarları dosyaya kaydeder."""
        settings_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, "settings.json")
        
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilemedi: {e}")
