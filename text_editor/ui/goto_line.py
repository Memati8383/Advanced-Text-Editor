import customtkinter as ctk
from typing import Any, Optional

class GoToLineDialog(ctk.CTkToplevel):
    """
    Editörde belirli bir satıra gitmek için kullanıcı arayüzü penceresi.
    """
    
    # Pencere Yapılandırması için Sabitler
    WINDOW_SIZE = "380x200"
    WINDOW_TITLE = "Satıra Git"
    
    def __init__(self, parent: Any, editor: Any):
        """
        GoToLineDialog'u başlatır.

        Args:
            parent: Bu iletişim kutusuyla ilişkili ana widget.
            editor: Üzerinde işlem yapılacak metin alanını içeren editör örneği.
        """
        super().__init__(parent)
        
        self.editor = editor
        self._total_lines = self._get_total_lines()
        
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        
        self.focus_force()
        self.entry.focus_set()

    def _get_total_lines(self) -> int:
        """Editördeki toplam satır sayısını hesaplar."""
        try:
            # "end-1c", Tkinter'ın eklediği sondaki yeni satır karakterini hariç tutar
            index = self.editor.text_area.index("end-1c")
            return int(index.split('.')[0])
        except (ValueError, AttributeError):
            return 1

    def _setup_window(self) -> None:
        """Pencere özelliklerini ve geometrisini yapılandırır."""
        self.title(self.WINDOW_TITLE)
        self.geometry(self.WINDOW_SIZE)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(self.master)
        self.grab_set()
        self._center_window()

    def _center_window(self) -> None:
        """Pencereyi ekranda ortalar."""
        self.update_idletasks()
        
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x_pos = (screen_width // 2) - (window_width // 2)
        y_pos = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f'{window_width}x{window_height}+{x_pos}+{y_pos}')

    def _create_widgets(self) -> None:
        """Arayüz elemanlarını oluşturur ve düzenler."""
        # Ana Konteyner
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık Etiketi
        self.lbl_instruction = ctk.CTkLabel(
            self.main_frame, 
            text=f"Satır Numarası Girin (1 - {self._total_lines}):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_instruction.pack(pady=(0, 10), anchor="w")
        
        # Giriş Alanı
        self.entry = ctk.CTkEntry(
            self.main_frame,
            width=200,
            height=35,
            placeholder_text="Örn: 42"
        )
        self.entry.pack(fill="x", pady=(0, 5))
        
        # Hata Bildirim Etiketi
        self.lbl_error = ctk.CTkLabel(
            self.main_frame,
            text="",
            text_color=("#ff5555", "#ff6b6b"),
            font=ctk.CTkFont(size=12),
            height=20,
            anchor="w"
        )
        self.lbl_error.pack(pady=(0, 10), fill="x", anchor="w")

        # Buton Konteyneri
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=(10, 0))
        
        self._create_actions()

    def _create_actions(self) -> None:
        """İşlem butonlarını oluşturur (İptal, Git)."""
        # İptal Butonu
        self.btn_cancel = ctk.CTkButton(
            self.btn_frame,
            text="İptal",
            command=self.destroy,
            width=100,
            height=35,
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray40"),
            text_color=("gray10", "gray90"),
            hover_color=("gray90", "gray30")
        )
        self.btn_cancel.pack(side="right", padx=(10, 0))

        # İşlem Butonu
        self.btn_go = ctk.CTkButton(
            self.btn_frame, 
            text="Git", 
            command=self.on_submit, 
            width=100,
            height=35
        )
        self.btn_go.pack(side="right")

    def _setup_bindings(self) -> None:
        """Klavye olaylarını bağlar."""
        self.bind("<Escape>", lambda e: self.destroy())
        self.entry.bind("<Return>", self.on_submit)

    def on_submit(self, event=None) -> None:
        """Gönderim mantığını işler."""
        input_value = self.entry.get().strip()
        
        if not self._validate_input(input_value):
            return

        line_num = int(input_value)
        self._navigate_to_line(line_num)

    def _validate_input(self, value: str) -> bool:
        """
        Kullanıcı girişini doğrular.
        
        Args:
            value: Kullanıcıdan gelen metin girişi.
            
        Returns:
            Geçerliyse True, değilse False (ve hata mesajı ayarlar).
        """
        if not value:
            self._show_error("⚠️ Lütfen bir sayı girin.")
            return False

        if not value.isdigit():
            self._show_error("⚠️ Geçersiz giriş. Sadece sayı girin.")
            return False
            
        line_num = int(value)
        if not (1 <= line_num <= self._total_lines):
            self._show_error(f"⚠️ 1 ile {self._total_lines} arasında olmalı.")
            return False
            
        return True

    def _navigate_to_line(self, line_num: int) -> None:
        """
        Editör üzerinde gezinme mantığını gerçekleştirir.
        
        Args:
            line_num: Hedef satır numarası (1 tabanlı).
        """
        try:
            # İmleci taşı ve kaydır
            target_index = f"{line_num}.0"
            self.editor.text_area.mark_set("insert", target_index)
            self.editor.text_area.see(target_index)
            
            # Satırı vurgula
            next_line_index = f"{line_num + 1}.0"
            self.editor.text_area.tag_remove("sel", "1.0", "end")
            self.editor.text_area.tag_add("sel", target_index, next_line_index)
            
            # Odağı editöre geri ver
            self.editor.text_area.focus_force()
            
            self.destroy()
        except Exception as e:
            self._show_error(f"⚠️ Hata: {str(e)}")

    def _show_error(self, message: str) -> None:
        """Kullanıcıya bir hata mesajı görüntüler."""
        self.lbl_error.configure(text=message)
