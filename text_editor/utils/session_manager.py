import json
import os
from typing import List, Dict, Any, Optional

class SessionManager:
    """
    Uygulama oturumlarını (açık dosyalar, en son aktif sekme vb.) yöneten sınıf.
    Uygulama kapandığında mevcut durumu kaydeder ve açıldığında geri yükler.
    """
    _instance: Optional['SessionManager'] = None
    
    def __init__(self):
        if SessionManager._instance is not None:
            raise Exception("SessionManager is a singleton class!")
        
        self.config_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        self.session_file = os.path.join(self.config_dir, "session.json")
        self.last_session: Dict[str, Any] = {}
        self.load_session()
        
    @classmethod
    def get_instance(cls) -> 'SessionManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_session(self) -> Dict[str, Any]:
        """En son oturum verilerini dosyadan yükler."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    self.last_session = json.load(f)
            except Exception as e:
                print(f"SessionManager: Oturum yüklenemedi: {e}")
        return self.last_session

    def save_session(self, open_files: List[str], active_tab: Optional[str] = None) -> bool:
        """Mevcut oturum verilerini dosyaya kaydeder."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            data = {
                "open_files": open_files,
                "active_tab": active_tab,
                "timestamp": os.path.getmtime(self.session_file) if os.path.exists(self.session_file) else 0
            }
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"SessionManager: Oturum kaydedilemedi: {e}")
            return False

    def get_last_files(self) -> List[str]:
        """En son açık olan dosyaların listesini döndürür."""
        return self.last_session.get("open_files", [])

    def get_last_active_tab(self) -> Optional[str]:
        """En son aktif olan sekmenin adını döndürür."""
        return self.last_session.get("active_tab")
