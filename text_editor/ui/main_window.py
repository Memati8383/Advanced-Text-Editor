import customtkinter as ctk
from text_editor.config import APP_NAME
from text_editor.ui.tab_manager import TabManager
from text_editor.ui.status_bar import StatusBar
from text_editor.ui.file_explorer import FileExplorer
import tkinter as tk
import os
import json
import re
from text_editor.utils.shortcut_manager import ShortcutManager
from text_editor.utils.settings_manager import SettingsManager

from text_editor.ui.menu_bar import MenuBar
from text_editor.ui.drop_zone import DragDropManager
from tkinterdnd2 import TkinterDnD, DND_FILES

class MainWindow(ctk.CTk, TkinterDnD.DnDWrapper):
    """
    Uygulamanın ana penceresi. 
    Tüm üst düzey bileşenleri (Menü, Dosya Gezgini, Sekmeler, Durum Çubuğu) barındırır
    ve aralarındaki koordinasyonu sağlar.
    """
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Dil yöneticisini başlat
        from text_editor.utils.language_manager import LanguageManager
        self.lang = LanguageManager.get_instance()
        
        # Ayarlar yöneticisini başlat
        self.settings_manager = SettingsManager.get_instance()
        self.settings = self.settings_manager.settings
        
        # Kayıtlı dili uygula
        saved_lang = self.settings_manager.get("language", "Türkçe")
        self.lang.load_language(saved_lang)
        
        # Görünüm durumları
        self._status_bar_visible = self.settings_manager.get("show_status_bar", True)
        self._file_explorer_visible = self.settings_manager.get("show_file_explorer", True)
        self._menu_visible = True
        self._zen_mode = False
        self._terminal_visible = self.settings_manager.get("show_terminal", False)
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
        self.file_explorer = FileExplorer(self, open_file_callback=self.open_file_from_explorer)

        # 2. Düzeni Oluştur
        # Menü Çubuğu (Satır 0)
        self.menu_bar = MenuBar(self)
        self.menu_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        # Dosya Gezgini (Satır 1, Sütun 0)
        self.file_explorer.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(10, 0))
        
        # Sekme Yöneticisi (Satır 1, Sütun 1)
        self.tab_manager.grid(row=1, column=1, sticky="nsew", padx=10, pady=(10, 0))

        # Durum Çubuğu (Satır 3, tümünü kapsayan)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Ağırlıkları güncelle
        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=1)
        
        # Yardım Sistemini Başlat
        from text_editor.ui.help_system import HelpSystem
        self.help_system = HelpSystem(self)
        
        # Kısayolları ve olayları ayarla
        self._setup_global_events()
        
        # Başlangıç temasını uygula
        saved_theme = self.settings_manager.get("theme", "Dark")
        self.after(100, lambda: self.apply_theme(saved_theme))

        # Tam ekran başlat (ayar varsa)
        if self.settings_manager.get("start_fullscreen", False):
            self.after(200, lambda: self.attributes("-fullscreen", True))

        # Sürükle Bırak Yöneticisi
        self._setup_drag_drop()

    def _setup_drag_drop(self):
        """Gelişmiş sürükle-bırak sistemini yapılandırır."""
        # DragDropManager oluştur
        self.drag_drop_manager = DragDropManager(
            self,
            on_file_open=self._handle_file_drop,
            on_folder_open=self._handle_folder_drop
        )
        
        # TkinterDnD2 event'lerini bağla
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)
        # Not: TkinterDnD2'de DragEnter/DragLeave event'leri için farklı syntax'lar deneniyor
        # Bazı Windows sistemlerinde bu event'ler çalışmayabiliyor
        try:
            # Önce standart syntax dene
            self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        except Exception:
            pass
        
        # Alternatif event adlarını da dene
        try:
            self.dnd_bind('<DragEnter>', self._on_drag_enter)
            self.dnd_bind('<DragLeave>', self._on_drag_leave)
        except Exception:
            pass
        
        # DropEnter/DropLeave event'lerini de dene (bazı versiyonlarda bu isimler kullanılıyor)
        try:
            self.dnd_bind('<<DropEnter>>', self._on_drag_enter)
            self.dnd_bind('<<DropLeave>>', self._on_drag_leave)
        except Exception:
            pass
    
    def _on_drag_enter(self, event):
        """Dosya sürüklenip pencereye girdiğinde çağrılır."""
        self.drag_drop_manager.on_drag_enter(event)
        return event.action
    
    def _on_drag_leave(self, event):
        """Dosya sürüklenip pencereden çıktığında çağrılır."""
        self.drag_drop_manager.on_drag_leave(event)
        return event.action
    
    def _on_drop(self, event):
        """Dosya bırakıldığında çağrılır."""
        return self.drag_drop_manager.on_drop(event)
    
    def _handle_file_drop(self, file_path: str):
        """Sürükle-bırak ile gelen dosyayı açar."""
        self.tab_manager.open_file(path=file_path)
    
    def _handle_folder_drop(self, folder_path: str):
        """Sürükle-bırak ile gelen klasörü açar."""
        self.open_folder_path(folder_path)

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
            self.open_folder_path(folder_path)

    def open_folder_path(self, folder_path):
        """Verilen klasör yolunu açar."""
        if folder_path:
            self.file_explorer.set_root_path(folder_path)
            self.title(f"{APP_NAME} - {os.path.basename(folder_path)}")

    def _setup_global_events(self):
        """Uygulama genelindeki olayları ve kısayolları bağlar."""
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
        
        # Kopyalama Kısayolları
        self.bind("<Control-Shift-C>", lambda e: self.tab_manager.copy_path())
        self.bind("<Control-Alt-c>", lambda e: self.tab_manager.copy_relative_path())
        
        # Ayarlar kısayolu
        self.bind("<Control-comma>", lambda e: self.open_settings())

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

    # change_theme and apply_theme below

    def change_theme(self, theme_name):
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name):
        from text_editor.theme_config import get_theme
        theme = get_theme(theme_name)
        
        # Mevcut tema adını kaydet (terminal için)
        self._current_theme_name = theme_name
        
        # Temel görünüm modunu ayarla (Açık/Koyu)
        ctk.set_appearance_mode(theme["type"])
        
        # Pencere başlığını güncelle
        theme_msg = self.lang.get("menu.theme")  # "Tema" veya "Theme"
        theme_msg = theme_msg.replace("🎨", "").strip()
        self.title(f"🪐 {APP_NAME} - {theme_name} {theme_msg}")
        
        # 1. Menü Çubuğu
        self.menu_bar.apply_theme(theme)

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
        
        # 7. Sürükle-Bırak Overlay (varsa)
        if hasattr(self, 'drag_drop_manager'):
            self.drag_drop_manager.update_theme(theme)
        
        # 8. Ana pencere arka planı
        self.configure(fg_color=theme.get("bg", "#1e1e1e"))

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    # === Görünüm Ayarları ===
    
    # show_view_menu removed (managed by MenuBar)
    
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
            # Tüm panelleri gizle
            self.menu_bar.grid_remove()
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
            # Menüyü geri getir
            self.menu_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
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
                
                # Menüyü güncelle (MenuBar kendi dilini günceller)
                if hasattr(self, 'menu_bar') and self.menu_bar:
                    self.menu_bar.update_language()
                
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
            self.settings_manager.update_multiple(new_settings)
            
            # Durum mesajı
            if self._status_bar_visible:
                msg = "✅ Settings applied" if self.lang.current_lang == "en" else "✅ Ayarlar uygulandı"
                self.status_bar.set_message(msg, "success")
        
        # Ayarlar penceresini aç
        from text_editor.ui.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self, self.settings, apply_settings)
