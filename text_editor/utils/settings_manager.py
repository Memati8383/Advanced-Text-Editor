import json
import os
from typing import Dict, Any, Optional

class SettingsManager:
    """
    Uygulama ayarlarını yöneten, kaydeden ve yükleyen sınıf.
    Singleton tasarım desenini kullanır.
    """
    _instance: Optional['SettingsManager'] = None
    
    DEFAULT_SETTINGS = {
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
        "error_reporting": True,
        "recent_files": []
    }
    
    def __init__(self):
        if SettingsManager._instance is not None:
            raise Exception("SettingsManager is a singleton class!")
        
        self.config_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
        
    @classmethod
    def get_instance(cls) -> 'SettingsManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_settings(self) -> Dict[str, Any]:
        """Ayarları dosyadan yükler, yoksa varsayılanları kullanır."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Mevcut ayarlara ekle (yeni eklenen default ayarlar kaybolmasın)
                    temp_settings = self.DEFAULT_SETTINGS.copy()
                    temp_settings.update(loaded)
                    self.settings = temp_settings
            except Exception as e:
                print(f"SettingsManager: Ayarlar yüklenemedi: {e}")
        return self.settings

    def save_settings(self) -> bool:
        """Mevcut ayarları dosyaya kaydeder."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"SettingsManager: Ayarlar kaydedilemedi: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Belirli bir ayar değerini döndürür."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Bir ayarı günceller ve isteğe bağlı olarak kaydeder."""
        self.settings[key] = value
        if save:
            self.save_settings()

    def update_multiple(self, new_settings: Dict[str, Any], save: bool = True) -> None:
        """Birden fazla ayarı aynı anda günceller."""
        self.settings.update(new_settings)
        if save:
            self.save_settings()

    def reset_to_defaults(self) -> None:
        """Ayarları varsayılan değerlerine döndürür."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()

    # Son kullanılan dosyalar için maksimum limit
    MAX_RECENT_FILES = 15

    def _normalize_path(self, file_path: str) -> str:
        """Dosya yolunu normalleştirir (tutarlılık için)."""
        if not file_path:
            return ""
        # Normalize: backslash/forward slash tutarlılığı ve case sensitivity
        return os.path.normcase(os.path.normpath(os.path.abspath(file_path)))

    def add_recent_file(self, file_path: str) -> None:
        """Son kullanılan dosyalara bir dosya ekler."""
        if not file_path:
            return
        
        # Dosya var mı kontrol et
        if not os.path.exists(file_path):
            return
            
        # Yolu normalleştir
        normalized_path = self._normalize_path(file_path)
        
        recent = self.get("recent_files", [])
        if not isinstance(recent, list):
            recent = []
        
        # Normalize edilmiş yollarla karşılaştır ve varsa çıkar
        recent = [p for p in recent if self._normalize_path(p) != normalized_path]
            
        # Başa ekle (orijinal formatta)
        recent.insert(0, file_path)
        
        # Limit uygula
        recent = recent[:self.MAX_RECENT_FILES]
        
        self.set("recent_files", recent)

    def remove_recent_file(self, file_path: str) -> None:
        """Belirli bir dosyayı son kullanılanlardan çıkarır."""
        if not file_path:
            return
            
        normalized_path = self._normalize_path(file_path)
        recent = self.get("recent_files", [])
        
        if not isinstance(recent, list):
            return
            
        # Normalize edilmiş karşılaştırma ile sil
        new_recent = [p for p in recent if self._normalize_path(p) != normalized_path]
        
        if len(new_recent) != len(recent):
            self.set("recent_files", new_recent)

    def get_recent_files(self) -> list:
        """Var olan son kullanılan dosyaları döndürür."""
        recent = self.get("recent_files", [])
        if not isinstance(recent, list):
            return []
        
        # Sadece var olan dosyaları filtrele
        valid_files = [p for p in recent if os.path.exists(p)]
        
        # Eğer geçersiz dosyalar temizlendiyse, kaydet
        if len(valid_files) != len(recent):
            self.set("recent_files", valid_files)
        
        return valid_files

    def clear_recent_files(self) -> None:
        """Tüm son kullanılan dosyaları temizler."""
        self.set("recent_files", [])
