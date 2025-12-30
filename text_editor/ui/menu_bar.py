import customtkinter as ctk
import tkinter as tk
from text_editor.config import APP_NAME
from text_editor.ui.modern_menu import ModernMenuBar
from text_editor.utils.shortcut_manager import ShortcutManager
from text_editor.theme_config import get_available_themes
from text_editor.utils.settings_manager import SettingsManager
try:
    from text_editor.utils.file_icons import FileIcons
except ImportError:
    FileIcons = None
import os

class MenuBar(ctk.CTkFrame):
    """
    Uygulamanın ana menü çubuğunu yöneten bileşen.
    MainWindow'dan menü mantığını ayırmak için oluşturuldu.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, height=45, corner_radius=0, border_width=0, **kwargs)
        self.master = master
        self.lang = master.lang
        self.shortcut_manager = ShortcutManager.get_instance()
        
        # ModernDropdown yöneticisi
        self.modern_menu_helper = None
        
        self.menu_buttons = []
        self._setup_ui()
        
    def _setup_ui(self):
        # Logo/Başlık
        self.logo_label = ctk.CTkLabel(
            self,
            text=f"🪐 {APP_NAME}",
            font=("Segoe UI", 14, "bold"),
            text_color=("gray20", "#00d4ff")
        )
        self.logo_label.pack(side="left", padx=(15, 30))

        # Menü Butonları
        self.add_menu_btn("menu.file", self.show_file_menu, "📁")
        self.add_menu_btn("menu.edit", self.show_edit_menu, "✏️")
        self.add_menu_btn("menu.view", self.show_view_menu, "👁️")
        self.add_menu_btn("menu.theme", self.show_theme_menu, "🎨")
        
        # Tutorial butonu
        self.tutorial_btn = ctk.CTkButton(
            self,
            text=f"🎓 {self.lang.get('menu.tutorial')}",
            width=90,
            height=40,
            corner_radius=6,
            fg_color=("#00d4ff", "#0096c7"),
            hover_color=("#00b8e6", "#007ea7"),
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            border_width=0,
            command=self.master.start_tutorial if hasattr(self.master, 'start_tutorial') else None
        )
        self.tutorial_btn.pack(side="left", padx=3, pady=2)
        self.menu_buttons.append(self.tutorial_btn)
        
        # Ayarlar butonu
        self.settings_btn = ctk.CTkButton(
            self,
            text=f"⚙️ {self.lang.get('menu.settings')}",
            width=90,
            height=40,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            border_width=0,
            command=self.master.open_settings if hasattr(self.master, 'open_settings') else None
        )
        self.settings_btn.pack(side="left", padx=3, pady=2)
        self.menu_buttons.append(self.settings_btn)
        
        # Yardım butonu
        self.add_menu_btn("menu.help", lambda: self.master.help_system.open_help("Hızlı Başlangıç"), "❓", pass_widget=False)
        
        # Versiyon bilgisi
        self.version_label = ctk.CTkLabel(
            self,
            text="v1.0",
            font=("Segoe UI", 9),
            text_color=("gray50", "gray60")
        )
        self.version_label.pack(side="right", padx=15)

    def add_menu_btn(self, text_key, command, icon="", pass_widget=True):
        text = self.lang.get(text_key)
        display_text = f"{icon} {text}" if icon else text
        btn = ctk.CTkButton(
            self, 
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

    def apply_theme(self, theme):
        """Temayı menü çubuğuna ve dropdown yardımcıya uygular."""
        self.configure(
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
            
        # ModernDropdownHelper'ı oluştur veya güncelle
        if not self.modern_menu_helper:
            self.modern_menu_helper = ModernMenuBar(self.master, theme)
        else:
            self.modern_menu_helper.theme = theme

    # === Menü Gösterme Fonksiyonları ===

    def show_file_menu(self, button):
        if not self.modern_menu_helper: return
        
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        tm = self.master.tab_manager
        
        menu_items = [
            {"icon": "📄", "label": self.lang.get("menu.items.new_tab"), "shortcut": fmt(shortcuts.get("new_tab")), "command": tm.add_new_tab},
            {"icon": "📂", "label": self.lang.get("menu.items.open_file"), "shortcut": fmt(shortcuts.get("open_file")), "command": tm.open_file},
            {"icon": "📁", "label": self.lang.get("menu.items.open_folder"), "shortcut": fmt(shortcuts.get("open_folder")), "command": self.master.open_folder},
            {"separator": True},
        ]

        # Son Kullanılanlar Bölümü
        settings = SettingsManager.get_instance()
        recent_files = settings.get_recent_files()  # Otomatik olarak var olmayan dosyaları filtreler
        
        def _shorten_path(path: str, max_len: int = 45) -> str:
            """Uzun dosya yollarını akıllıca kısaltır."""
            if len(path) <= max_len:
                return path
            
            # Drive + klasör + dosya formatı: C:\...\parent\file.txt
            parts = path.replace('/', '\\').split('\\')
            filename = parts[-1]
            
            if len(parts) <= 2:
                return path  # Çok kısa yol
            
            # Drive veya root
            drive = parts[0]
            parent = parts[-2] if len(parts) > 2 else ""
            
            # Kısaltılmış format oluştur
            if parent:
                shortened = f"{drive}\\...\\{parent}\\{filename}"
            else:
                shortened = f"{drive}\\...\\{filename}"
            
            # Hâlâ çok uzunsa sadece dosya adını göster
            if len(shortened) > max_len:
                return f"...\\{filename}" if len(filename) < max_len else filename[:max_len-3] + "..."
            
            return shortened
        
        if recent_files:
            menu_items.append({
                "icon": "🕒", 
                "label": self.lang.get('menu.items.recent_files'), 
                "is_header": True, 
                "enabled": False,
                "on_delete": settings.clear_recent_files,
                "delete_icon": "🧹",
                "delete_hover": ("#404040", "#505050")
            })
            for file_path in recent_files:
                filename = os.path.basename(file_path)
                icon = FileIcons.get_icon(filename) if FileIcons else "📝"
                short_label = _shorten_path(file_path)
                
                menu_items.append({
                    "icon": icon, 
                    "label": short_label,
                    "tooltip": file_path,  # Hover'da tam yolu göster
                    "command": lambda p=file_path: tm.open_file(p),
                    "on_delete": lambda p=file_path: settings.remove_recent_file(p)
                })
            menu_items.append({"separator": True})

        menu_items.extend([
            {"icon": "💾", "label": self.lang.get("menu.items.save"), "shortcut": fmt(shortcuts.get("save_file")), "command": tm.save_current_file},
            {"icon": "📝", "label": self.lang.get("menu.items.save_as"), "shortcut": fmt(shortcuts.get("save_as")), "command": tm.save_current_file_as},
            {"separator": True},
            {"icon": "🔍", "label": self.lang.get("menu.items.find_replace"), "shortcut": fmt(shortcuts.get("find")), "command": tm.show_find_replace},
            {"icon": "🎯", "label": self.lang.get("menu.items.goto_line"), "shortcut": fmt(shortcuts.get("goto_line")), "command": tm.show_goto_line},
            {"separator": True},
            {"icon": "🚪", "label": self.lang.get("menu.items.exit"), "shortcut": fmt(shortcuts.get("quit")), "command": self.master.quit}
        ])
        
        self.modern_menu_helper.show_dropdown(button, menu_items)

    def show_edit_menu(self, button):
        if not self.modern_menu_helper: return
        
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        tm = self.master.tab_manager
        focus = self.master.focus_get()
        
        menu_items = [
            {"icon": "↶", "label": self.lang.get("menu.items.undo"), "shortcut": fmt(shortcuts.get("undo")), "command": lambda: focus.event_generate("<<Undo>>") if focus else None},
            {"icon": "↷", "label": self.lang.get("menu.items.redo"), "shortcut": fmt(shortcuts.get("redo")), "command": lambda: focus.event_generate("<<Redo>>") if focus else None},
            {"separator": True},
            {"icon": "✂️", "label": self.lang.get("menu.items.cut"), "shortcut": fmt(shortcuts.get("cut")), "command": lambda: focus.event_generate("<<Cut>>") if focus else None},
            {"icon": "📋", "label": self.lang.get("menu.items.copy"), "shortcut": fmt(shortcuts.get("copy")), "command": lambda: focus.event_generate("<<Copy>>") if focus else None},
            {"icon": "📌", "label": self.lang.get("menu.items.paste"), "shortcut": fmt(shortcuts.get("paste")), "command": lambda: focus.event_generate("<<Paste>>") if focus else None},
            {"separator": True},
            {"icon": "📑", "label": self.lang.get("menu.items.duplicate_line"), "shortcut": fmt(shortcuts.get("duplicate_line")), "command": tm.duplicate_line},
            {"icon": "⬆️", "label": self.lang.get("menu.items.move_up"), "shortcut": fmt(shortcuts.get("move_line_up")), "command": tm.move_line_up},
            {"icon": "⬇️", "label": self.lang.get("menu.items.move_down"), "shortcut": fmt(shortcuts.get("move_line_down")), "command": tm.move_line_down},
            {"icon": "🗑️", "label": self.lang.get("menu.items.delete_line"), "shortcut": fmt(shortcuts.get("delete_line")), "command": tm.delete_line},
            {"icon": "🔗", "label": self.lang.get("menu.items.join_lines"), "shortcut": fmt(shortcuts.get("join_lines")), "command": tm.join_lines},
            {"separator": True},
            {"icon": "📋", "label": self.lang.get("menu.items.copy_path"), "shortcut": fmt(shortcuts.get("copy_path")), "command": tm.copy_path},
            {"icon": "📂", "label": self.lang.get("menu.items.relative_path"), "shortcut": fmt(shortcuts.get("copy_relative_path")), "command": tm.copy_relative_path}
        ]
        self.modern_menu_helper.show_dropdown(button, menu_items)

    def show_view_menu(self, button):
        if not self.modern_menu_helper: return
        
        view_states = self.master.tab_manager.get_view_states()
        shortcuts = self.shortcut_manager
        fmt = shortcuts.get_display_string
        
        def get_toggle_icon(is_on): return "✅" if is_on else "⬜"
        
        menu_items = [
            {"icon": get_toggle_icon(view_states.get("line_numbers", True)), "label": self.lang.get("menu.items.line_numbers"), "shortcut": fmt(shortcuts.get("toggle_line_numbers")), "command": self.master.toggle_line_numbers_with_feedback},
            {"icon": get_toggle_icon(view_states.get("word_wrap", False)), "label": self.lang.get("menu.items.word_wrap"), "shortcut": fmt(shortcuts.get("toggle_word_wrap")), "command": self.master.toggle_word_wrap_with_feedback},
            {"icon": get_toggle_icon(view_states.get("minimap", True)), "label": self.lang.get("menu.items.minimap"), "shortcut": fmt(shortcuts.get("toggle_minimap")), "command": self.master.toggle_minimap_with_feedback},
            {"separator": True},
            {"icon": get_toggle_icon(self.master._status_bar_visible), "label": self.lang.get("menu.items.status_bar"), "shortcut": fmt(shortcuts.get("toggle_status_bar")), "command": self.master.toggle_status_bar},
            {"icon": get_toggle_icon(self.master._file_explorer_visible), "label": self.lang.get("menu.items.file_explorer"), "shortcut": fmt(shortcuts.get("toggle_file_explorer")), "command": self.master.toggle_file_explorer},
            {"icon": get_toggle_icon(self.master._terminal_visible), "label": self.lang.get("menu.items.terminal"), "shortcut": fmt(shortcuts.get("toggle_terminal")), "command": self.master.toggle_terminal},
            {"icon": get_toggle_icon(self.master._markdown_preview_visible), "label": self.lang.get("menu.items.markdown_preview"), "shortcut": fmt(shortcuts.get("preview_markdown")), "command": self.master.toggle_markdown_preview},
            {"separator": True},
            {"icon": "🧘", "label": self.lang.get("menu.items.zen_mode"), "shortcut": fmt(shortcuts.get("toggle_zen_mode")), "command": self.master.toggle_zen_mode},
            {"icon": "📺", "label": self.lang.get("menu.items.fullscreen"), "shortcut": fmt(shortcuts.get("toggle_fullscreen")), "command": self.master.toggle_fullscreen}
        ]
        self.modern_menu_helper.show_dropdown(button, menu_items)

    def show_theme_menu(self, button):
        if not self.modern_menu_helper: return
        
        theme_icons = {
            "Dark": "🌑", "Light": "☀️", "Dracula": "🧛", "Solarized Light": "🌅",
            "Monokai": "🔥", "Nord": "❄️", "Gruvbox": "🍂", "One Dark Pro": "⚫",
            "GitHub Dark": "🐙", "Synthwave 84": "🌃", "Solarized Dark": "🌘",
            "Night Owl": "🦉", "Tokyo Night": "🗼", "Cobalt2": "🔵",
            "Material Palenight": "👾", "Ayu Dark": "🦈", "Shades of Purple": "💜"
        }
        
        menu_items = []
        for theme_name in get_available_themes():
            icon = theme_icons.get(theme_name, "🎨")
            menu_items.append({
                "icon": icon,
                "label": theme_name,
                "command": lambda t=theme_name: self.master.apply_theme(t)
            })
        
        self.modern_menu_helper.show_dropdown(button, menu_items)
    
    def update_language(self):
        """
        Dil değiştiğinde menü butonlarını yeniden oluşturur.
        Tüm mevcut butonları temizler ve yeni dilde oluşturur.
        """
        # Mevcut butonları temizle
        for widget in self.winfo_children():
            widget.destroy()
        
        self.menu_buttons.clear()
        
        # UI'yi yeniden oluştur
        self._setup_ui()
        
        # Temayı yeniden uygula (eğer varsa)
        if hasattr(self.master, '_current_theme_name'):
            from text_editor.theme_config import get_theme
            theme = get_theme(self.master._current_theme_name)
            self.apply_theme(theme)

