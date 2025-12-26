import json
import os
from typing import Dict, Optional, Any, ClassVar
from text_editor.utils.language_manager import LanguageManager

class ShortcutManager:
    """
    Klavye kısayollarını yöneten sınıf.
    Kısayolları dosyadan yükler, kaydeder ve varsayılan değerleri tutar.
    Singleton tasarım desenini kullanır.
    """
    
    # Varsayılan kısayollar
    DEFAULT_SHORTCUTS: ClassVar[Dict[str, str]] = {
        # Dosya İşlemleri
        "new_tab": "<Control-n>",
        "open_file": "<Control-o>",
        "open_folder": "<Control-Shift-O>",
        "save_file": "<Control-s>",
        "save_as": "<Control-Shift-S>",
        "close_tab": "<Control-w>",
        "quit": "<Alt-F4>",
        
        # Düzenleme
        "undo": "<Control-z>",
        "redo": "<Control-y>",
        "cut": "<Control-x>",
        "copy": "<Control-c>",
        "paste": "<Control-v>",
        "select_all": "<Control-a>",
        "find": "<Control-f>",
        "replace": "<Control-h>",
        "goto_line": "<Control-g>",
        
        # Görünüm
        "toggle_fullscreen": "<F11>",
        "toggle_zen_mode": "<Control-k>",
        "toggle_line_numbers": "<Control-Shift-L>",
        "toggle_word_wrap": "<Alt-z>",
        "toggle_minimap": "<Control-m>",
        "toggle_status_bar": "<Control-Shift-M>",
        "toggle_file_explorer": "<Control-b>",
        "toggle_terminal": "<Control-grave>",
        "preview_markdown": "<Control-Shift-V>",
        
        # Gezinme
        "next_tab": "<Control-Tab>",
        "prev_tab": "<Control-Shift-Tab>",
        
        # Zoom
        "zoom_in": "<Control-plus>",
        "zoom_out": "<Control-minus>",
        "zoom_reset": "<Control-0>",
        
        # Gelişmiş Düzenleme
        "duplicate_line": "<Control-Shift-D>",
        "move_line_up": "<Alt-Up>",
        "move_line_down": "<Alt-Down>",
        "delete_line": "<Control-Shift-K>",
        "join_lines": "<Control-J>",
        
        # Yollar
        "copy_path": "<Control-Shift-C>",
        "copy_relative_path": "<Control-Alt-c>"
    }
    
    # Kategori ve Etiket anahtarları (Localization için JSON keys)
    SHORTCUT_METADATA: ClassVar[Dict[str, Dict[str, str]]] = {
        "new_tab": {"category": "categories.file", "label": "shortcuts.new_tab"},
        "open_file": {"category": "categories.file", "label": "shortcuts.open_file"},
        "open_folder": {"category": "categories.file", "label": "shortcuts.open_folder"},
        "save_file": {"category": "categories.file", "label": "shortcuts.save_file"},
        "save_as": {"category": "categories.file", "label": "shortcuts.save_as"},
        "close_tab": {"category": "categories.file", "label": "shortcuts.close_tab"},
        "quit": {"category": "categories.file", "label": "shortcuts.quit"},
        
        "undo": {"category": "categories.edit", "label": "shortcuts.undo"},
        "redo": {"category": "categories.edit", "label": "shortcuts.redo"},
        "cut": {"category": "categories.edit", "label": "shortcuts.cut"},
        "copy": {"category": "categories.edit", "label": "shortcuts.copy"},
        "paste": {"category": "categories.edit", "label": "shortcuts.paste"},
        "select_all": {"category": "categories.edit", "label": "shortcuts.select_all"},
        "find": {"category": "categories.edit", "label": "shortcuts.find"},
        "replace": {"category": "categories.edit", "label": "shortcuts.replace"},
        "goto_line": {"category": "categories.edit", "label": "shortcuts.goto_line"},
        
        "toggle_fullscreen": {"category": "categories.view", "label": "shortcuts.toggle_fullscreen"},
        "toggle_zen_mode": {"category": "categories.view", "label": "shortcuts.toggle_zen_mode"},
        "toggle_line_numbers": {"category": "categories.view", "label": "shortcuts.toggle_line_numbers"},
        "toggle_word_wrap": {"category": "categories.view", "label": "shortcuts.toggle_word_wrap"},
        "toggle_minimap": {"category": "categories.view", "label": "shortcuts.toggle_minimap"},
        "toggle_status_bar": {"category": "categories.view", "label": "shortcuts.toggle_status_bar"},
        "toggle_file_explorer": {"category": "categories.view", "label": "shortcuts.toggle_file_explorer"},
        "toggle_terminal": {"category": "categories.view", "label": "shortcuts.toggle_terminal"},
        "preview_markdown": {"category": "categories.view", "label": "shortcuts.preview_markdown"},
        
        "next_tab": {"category": "categories.navigation", "label": "shortcuts.next_tab"},
        "prev_tab": {"category": "categories.navigation", "label": "shortcuts.prev_tab"},
        "zoom_in": {"category": "categories.view", "label": "shortcuts.zoom_in"},
        "zoom_out": {"category": "categories.view", "label": "shortcuts.zoom_out"},
        "zoom_reset": {"category": "categories.view", "label": "shortcuts.zoom_reset"},
        
        "duplicate_line": {"category": "categories.edit", "label": "shortcuts.duplicate_line"},
        "move_line_up": {"category": "categories.edit", "label": "shortcuts.move_line_up"},
        "move_line_down": {"category": "categories.edit", "label": "shortcuts.move_line_down"},
        "delete_line": {"category": "categories.edit", "label": "shortcuts.delete_line"},
        "join_lines": {"category": "categories.edit", "label": "shortcuts.join_lines"},
        
        "copy_path": {"category": "categories.file", "label": "shortcuts.copy_path"},
        "copy_relative_path": {"category": "categories.file", "label": "shortcuts.copy_relative_path"}
    }
    
    _instance: Optional['ShortcutManager'] = None
    
    @classmethod
    def get_instance(cls) -> 'ShortcutManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.config_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        self.config_file = os.path.join(self.config_dir, "keybindings.json")
        self.lang_manager = LanguageManager.get_instance()
        self.load_shortcuts()
        
    def load_shortcuts(self) -> None:
        """Kısayolları kullanıcı yapılandırma dosyasından yükler."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.shortcuts.update(saved)
            except Exception as e:
                print(f"ShortcutManager: Kısayollar yüklenemedi: {e}")
                
    def save_shortcuts(self) -> None:
        """Mevcut kısayolları kullanıcı yapılandırma dosyasına kaydeder."""
        os.makedirs(self.config_dir, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            print(f"ShortcutManager: Kısayollar kaydedilemedi: {e}")
            
    def get(self, action_id: str) -> str:
        """Aksiyon ID'sine göre atanan kısayol dizisini döndürür."""
        return self.shortcuts.get(action_id, "")
        
    def set(self, action_id: str, sequence: str) -> None:
        """Belirli bir aksiyon için kısayol atar ve kaydeder."""
        if action_id in self.shortcuts:
            self.shortcuts[action_id] = sequence
            self.save_shortcuts()
            
    def reset_to_defaults(self) -> None:
        """Tüm kısayolları varsayılan değerlerine döndürür."""
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.save_shortcuts()
        
    def get_display_string(self, sequence: str) -> str:
        """Tkinter dizi formatını kullanıcı dostu bir dizeye dönüştürür (örn: <Control-n> -> Ctrl+N)."""
        s = sequence.replace("<", "").replace(">", "")
        parts = s.split("-")
        
        formatted_parts = []
        for part in parts:
            p_lower = part.lower()
            if p_lower == "control":
                formatted_parts.append("Ctrl")
            elif p_lower == "shift":
                formatted_parts.append("Shift")
            elif p_lower == "alt":
                formatted_parts.append("Alt")
            elif p_lower == "grave":
                formatted_parts.append("`")
            elif p_lower == "plus":
                formatted_parts.append("+")
            elif p_lower == "minus":
                formatted_parts.append("-")
            else:
                formatted_parts.append(part.upper())
                
        return "+".join(formatted_parts)

    def get_localized_metadata(self, action_id: str) -> Dict[str, str]:
        """Kısayol için yerelleştirilmiş kategori ve etiket bilgilerini döndürür."""
        meta = self.SHORTCUT_METADATA.get(action_id, {})
        if not meta:
            return {"category": "Unknown", "label": action_id}
            
        return {
            "category": self.lang_manager.get(meta["category"], meta["category"]),
            "label": self.lang_manager.get(meta["label"], meta["label"])
        }
