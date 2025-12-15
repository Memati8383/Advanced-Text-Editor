import customtkinter as ctk
from typing import Dict, Any, Optional, Tuple
from text_editor.utils.file_icons import FileIcons

class StatusBar(ctk.CTkFrame):
    """
    Uygulama Durum Çubuğu bileşeni.
    
    Şunları görüntüler:
    - Durum mesajları ve ikonlar (Sol taraf)
    - İmleç konumu (Satır/Sütun)
    - Dosya kodlaması
    - Dosya türü bilgisi (Sağ taraf)
    """

    # Düzen sabitleri
    HEIGHT = 32
    FONT_MAIN = ("Segoe UI", 12)
    FONT_ICON = ("Segoe UI", 14)
    FONT_INFO = ("Segoe UI", 11)
    
    # Durum Stilleri: anahtar -> (ikon_karakteri, varsayılan_renk_hex)
    STATUS_STYLES = {
        "ready":   ("●", "#00ff88"),  # Yeşil
        "working": ("◐", "#00acc1"),  # Camgöbeği
        "error":   ("✕", "#ff5252"),  # Kırmızı
        "success": ("✓", "#00ff88"),  # Yeşil
        "warning": ("⚠", "#ffa726"),  # Turuncu
        "info":    ("ℹ", "#448aff")   # Mavi
    }

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, height=self.HEIGHT, corner_radius=0, **kwargs)
        
        from text_editor.utils.language_manager import LanguageManager
        self.lang = LanguageManager.get_instance()
        
        self.type_to_icon: Dict[str, str] = {}
        self._init_type_mapping()
        
        self._setup_layout()
        self._setup_left_panel()
        self._setup_right_panel()
        
        # Başlangıç durumu
        self.set_message(self.lang.get("status_messages.ready", "Hazır"))

    def _setup_layout(self):
        """Ana ızgara (grid) düzenini yapılandırır."""
        # Sütun 0: Mesaj (genişler), Sütun 1: Bilgi (sabit)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def _setup_left_panel(self):
        """Sola hizalanmış durum mesajı bölümünü oluşturur."""
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=2)
        
        # Durum İkonu
        self.status_icon = ctk.CTkLabel(
            self.left_frame, 
            text="●", 
            font=self.FONT_ICON, 
            text_color="#00ff88",
            width=20
        )
        self.status_icon.pack(side="left", padx=(0, 5))
        
        # Durum Mesajı
        self.message_label = ctk.CTkLabel(
            self.left_frame, 
            text="Hazır", 
            font=self.FONT_MAIN, 
            text_color="#cccccc",
            anchor="w"
        )
        self.message_label.pack(side="left", fill="x", expand=True)

    def _setup_right_panel(self):
        """Sağa hizalanmış bilgi bölümünü oluşturur."""
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="e", padx=5, pady=2)
        
        # İmleç Bilgisi
        self.cursor_info = self._create_info_item(self.right_frame, "Ln 1, Col 1")
        self._create_separator(self.right_frame)
        
        # Kodlama
        self.encoding_label = self._create_info_item(self.right_frame, "UTF-8")
        self._create_separator(self.right_frame)
        
        # Dosya Türü
        self.file_info_label = self._create_info_item(self.right_frame, "📄 Metin")
        
        # Harici sınıflar tarafından ihtiyaç duyulursa geriye dönük uyumluluk sarmalayıcısı
        self.info_label = self.cursor_info 

    def _create_info_item(self, parent: Any, text: str, width: Optional[int] = None) -> ctk.CTkLabel:
        """Durum çubuğunda standart bir bilgi etiketi oluşturmak için yardımcı."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=8)
        
        lbl = ctk.CTkLabel(
            frame, 
            text=text, 
            font=self.FONT_INFO,
            text_color="#bfbfbf"
        )
        if width:
            lbl.configure(width=width)
        lbl.pack()
        return lbl

    def _create_separator(self, parent: Any):
        """Dikey ayırıcı çizgi oluşturmak için yardımcı."""
        lbl = ctk.CTkLabel(
            parent, 
            text="|", 
            font=("Arial", 10), 
            text_color="#444444"
        )
        lbl.pack(side="left", padx=2)

    def _init_type_mapping(self):
        """
        FileIcons sınıfından 'Tür Açıklaması' -> 'İkon' önbelleği oluşturur.
        Bu, sadece okunabilir tür metni bilindiğinde ikonları bulmayı sağlar.
        """
        self.type_to_icon = {}
        for data in FileIcons.ICONS.values():
            if "type" in data and "icon" in data:
                self.type_to_icon[data["type"]] = data["icon"]
        
        # Manuel düzeltmeler ve varsayılanlar
        self.type_to_icon.update({
            "Text": "📄",
            "Metin": "📄",
            "File": "📄",
            "Python": "🐍",
        })

    def set_message(self, message: str, status: str = "ready"):
        """
        Durum mesajını ve ikonunu günceller.
        
        Args:
            message: Gösterilecek metin.
            status: Şunlardan biri: 'ready', 'working', 'error', 'success', 'warning', 'info'.
        """
        icon, color = self.STATUS_STYLES.get(status, ("●", "#cccccc"))
        self.status_icon.configure(text=icon, text_color=color)
        self.message_label.configure(text=message)

    def set_cursor_info(self, line: int, col: int, total_lines: int = 0):
        """İmleç konumu göstergesini günceller."""
        ln_text = self.lang.get("status_bar.ln", "Ln")
        col_text = self.lang.get("status_bar.col", "Col")
        self.cursor_info.configure(text=f"{ln_text} {line}, {col_text} {col}")

    def set_file_info(self, file_type: str = "Metin", encoding: str = "UTF-8", lines: int = 0):
        """Dosya türü ve kodlama bilgisini günceller."""
        icon = self.type_to_icon.get(file_type, "📄")
        self.file_info_label.configure(text=f"{icon} {file_type}")
        self.encoding_label.configure(text=encoding)

    def set_info(self, info: str):
        """
        Geriye dönük uyumluluk için eski yöntem.
        String formatını ayrıştırır: 'Ln 1, Col 1 | UTF-8'
        """
        if "|" in info:
            try:
                parts = info.split("|")
                # İmleci Ayrıştır
                cursor_part = parts[0].strip()
                if "Ln" in cursor_part and "Col" in cursor_part:
                    clean = cursor_part.replace("Ln", "").replace("Col", "")
                    if "," in clean:
                        l, c = clean.split(",")
                        self.set_cursor_info(int(l.strip()), int(c.strip()))
                
                # Kodlamayı Ayrıştır
                if len(parts) > 1:
                    encoding_part = parts[1].strip()
                    self.encoding_label.configure(text=encoding_part)
            except Exception:
                pass

    def update_theme(self, theme: Dict[str, Any]):
        """
        Verilen tema sözlüğüne göre bileşen renklerini günceller.
        
        Args:
            theme: Renk tanımlarını içeren sözlük.
        """
        status_fg = theme.get("status_fg", "#bfbfbf")
        
        self.configure(
            fg_color=theme.get("status_bg", "#333333"),
            border_color=theme.get("accent_color", "#444444"),
            border_width=1
        )
        
        # Metin renklerini güncelle
        self.message_label.configure(text_color=status_fg)
        self.file_info_label.configure(text_color=status_fg)
        self.cursor_info.configure(text_color=status_fg)
        self.encoding_label.configure(text_color=status_fg)

