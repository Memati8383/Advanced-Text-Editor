
import json
import os
from typing import Dict, Optional

class ShortcutManager:
    """
    Klavye kısayollarını yöneten sınıf.
    Kısayolları dosyadan yükler, kaydeder ve varsayılan değerleri tutar.
    """
    
    # Varsayılan kısayollar
    DEFAULT_SHORTCUTS = {
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
        "toggle_zen_mode": "<Control-k>", # + Z logic handled elsewhere usually but bind needs key
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
        
        # Zoom (Not configurable via standard key bind usually, but good to track)
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
    
    # Kategori ve Etiket eşleşmeleri (UI için)
    SHORTCUT_METADATA = {
        "new_tab": {"category": "Dosya İşlemleri", "label": "Yeni Sekme"},
        "open_file": {"category": "Dosya İşlemleri", "label": "Dosya Aç"},
        "open_folder": {"category": "Dosya İşlemleri", "label": "Klasör Aç"},
        "save_file": {"category": "Dosya İşlemleri", "label": "Kaydet"},
        "save_as": {"category": "Dosya İşlemleri", "label": "Farklı Kaydet"},
        "close_tab": {"category": "Dosya İşlemleri", "label": "Sekmeyi Kapat"},
        "quit": {"category": "Dosya İşlemleri", "label": "Çıkış"},
        
        "undo": {"category": "Düzenleme", "label": "Geri Al"},
        "redo": {"category": "Düzenleme", "label": "Yinele"},
        "cut": {"category": "Düzenleme", "label": "Kes"},
        "copy": {"category": "Düzenleme", "label": "Kopyala"},
        "paste": {"category": "Düzenleme", "label": "Yapıştır"},
        "select_all": {"category": "Düzenleme", "label": "Tümünü Seç"},
        "find": {"category": "Düzenleme", "label": "Bul"},
        "replace": {"category": "Düzenleme", "label": "Değiştir"},
        "goto_line": {"category": "Düzenleme", "label": "Satıra Git"},
        
        "toggle_fullscreen": {"category": "Görünüm", "label": "Tam Ekran"},
        "toggle_zen_mode": {"category": "Görünüm", "label": "Zen Modu"},
        "toggle_line_numbers": {"category": "Görünüm", "label": "Satır Numaraları"},
        "toggle_word_wrap": {"category": "Görünüm", "label": "Kelime Kaydırma"},
        "toggle_minimap": {"category": "Görünüm", "label": "Minimap"},
        "toggle_status_bar": {"category": "Görünüm", "label": "Durum Çubuğu"},
        "toggle_file_explorer": {"category": "Görünüm", "label": "Dosya Gezgini"},
        "toggle_terminal": {"category": "Görünüm", "label": "Terminal"},
        "preview_markdown": {"category": "Görünüm", "label": "Markdown Önizleme"},
        
        "next_tab": {"category": "Gezinme", "label": "Sonraki Sekme"},
        "prev_tab": {"category": "Gezinme", "label": "Önceki Sekme"},
        "zoom_in": {"category": "Görünüm", "label": "Yakınlaştır"},
        "zoom_out": {"category": "Görünüm", "label": "Uzaklaştır"},
        "zoom_reset": {"category": "Görünüm", "label": "Zoom Sıfırla"},
        
        "duplicate_line": {"category": "Düzenleme", "label": "Satır Çoğalt"},
        "move_line_up": {"category": "Düzenleme", "label": "Yukarı Taşı"},
        "move_line_down": {"category": "Düzenleme", "label": "Aşağı Taşı"},
        "delete_line": {"category": "Düzenleme", "label": "Satır Sil"},
        "join_lines": {"category": "Düzenleme", "label": "Satır Birleştir"},
        
        "copy_path": {"category": "Dosya İşlemleri", "label": "Yol Kopyala"},
        "copy_relative_path": {"category": "Dosya İşlemleri", "label": "Göreli Yol Kopyala"}
    }
    
    # Singleton benzeri kullanım için
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.config_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        self.config_file = os.path.join(self.config_dir, "keybindings.json")
        self.load_shortcuts()
        
    def load_shortcuts(self):
        """Kısayolları dosyadan yükler."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.shortcuts.update(saved)
            except Exception as e:
                print(f"Kısayollar yüklenemedi: {e}")
                
    def save_shortcuts(self):
        """Kısayolları dosyaya kaydeder."""
        os.makedirs(self.config_dir, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            print(f"Kısayollar kaydedilemedi: {e}")
            
    def get(self, action_id: str) -> str:
        """Aksiyon ID'sine göre kısayolu döndürür."""
        return self.shortcuts.get(action_id, "")
        
    def set(self, action_id: str, sequence: str):
        """Kısayolu günceller ve kaydeder."""
        if action_id in self.shortcuts:
            self.shortcuts[action_id] = sequence
            self.save_shortcuts()
            
    def reset_to_defaults(self):
        """Varsayılanlara döndürür."""
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.save_shortcuts()
        
    def get_display_string(self, sequence: str) -> str:
        """Tkinter sequence string'ini kullanıcı dostu formata çevirir (örn: <Control-n> -> Ctrl+N)."""
        s = sequence.replace("<", "").replace(">", "")
        parts = s.split("-")
        
        formatted_parts = []
        for part in parts:
            if part.lower() == "control":
                formatted_parts.append("Ctrl")
            elif part.lower() == "shift":
                formatted_parts.append("Shift")
            elif part.lower() == "alt":
                formatted_parts.append("Alt")
            else:
                formatted_parts.append(part.upper())
                
        return "+".join(formatted_parts)

