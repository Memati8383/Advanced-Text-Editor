import json
import os
from typing import Dict, Any, Optional

class LanguageManager:
    """
    Çoklu dil desteğini yöneten sınıf.
    Dil dosyalarını yükler ve çevirileri sağlar.
    Singleton tasarım desenini kullanır.
    """
    _instance: Optional['LanguageManager'] = None
    
    # Dil isimlerini kodlarla eşleştir
    LANGUAGE_MAPPING = {
        "Türkçe": "tr",
        "English": "en",
        "Español": "es",
        "Deutsch": "de",
        "Azerbaycan Türkçesi": "az"
    }
    
    def __init__(self):
        if LanguageManager._instance is not None:
            raise Exception("LanguageManager is a singleton class!")
        self._current_language = "tr" # Varsayılan dil
        self._translations: Dict[str, Any] = {}
        self._locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
        self.load_language(self._current_language)
        
    @staticmethod
    def get_instance() -> 'LanguageManager':
        if LanguageManager._instance is None:
            LanguageManager._instance = LanguageManager()
        return LanguageManager._instance

    def load_language(self, lang_code: str) -> None:
        """Belirtilen dildeki çeviri dosyasını yükler."""
        # Eğer tam isim verilmişse koda çevir
        lang_code = self.LANGUAGE_MAPPING.get(lang_code, lang_code)
        
        file_path = os.path.join(self._locales_dir, f"{lang_code}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self._translations = json.load(f)
                self._current_language = lang_code
        except Exception as e:
            print(f"LanguageManager: Dil dosyası yüklenemedi ({file_path}): {e}")
            # Hata durumunda, eğer zaten yüklü bir dil yoksa TR'yi dene
            if not self._translations and lang_code != "tr":
                self.load_language("tr")

    def get(self, key_path: str, default: Any = "") -> Any:
        """
        Nokta ile ayrılmış anahtar yolunu kullanarak çeviriyi döndürür.
        Örn: get("buttons.save")
        """
        if not key_path:
            return default
            
        keys = key_path.split(".")
        value = self._translations
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default if default else key_path

    @property
    def current_lang(self) -> str:
        return self._current_language
