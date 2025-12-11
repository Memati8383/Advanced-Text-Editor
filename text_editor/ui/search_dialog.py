import customtkinter as ctk
import tkinter as tk
from typing import Optional

# Sabitler
FONT_MAIN = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 11)
PADDING_STD = 10
PADDING_SMALL = 5
WINDOW_SIZE = "480x320"

class SearchDialog(ctk.CTkToplevel):
    """
    Metin editörü için gelişmiş Bul ve Değiştir iletişim penceresi.
    Clean Code prensiplerine göre yapılandırılmıştır.
    """
    
    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager
        
        self._init_window()
        self._init_variables()
        self._setup_ui()
        self._bind_events()
        
    def _init_window(self):
        """Pencere özelliklerini başlatır."""
        self.title("Bul ve Değiştir")
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.after(10, self._center_window)

    def _init_variables(self):
        """Arama durumu değişkenlerini başlatır."""
        self.search_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.match_case_var = tk.BooleanVar(value=False)
        self.whole_word_var = tk.BooleanVar(value=False)

    def _center_window(self):
        """Pencereyi ekranın ortasına konumlandırır."""
        try:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            
            self.geometry(f'+{x}+{y}')
        except Exception:
            pass

    def _setup_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        self._create_search_input()
        self._create_replace_input()
        self._create_options()
        self._create_buttons()
        self._create_status_bar()

    def _create_search_input(self):
        """Arama girişi alanını oluşturur."""
        ctk.CTkLabel(
            self.main_frame, 
            text="Aranan:", 
            font=FONT_MAIN
        ).grid(row=0, column=0, padx=(0, PADDING_STD), pady=PADDING_STD, sticky="w")
        
        self.find_entry = ctk.CTkEntry(
            self.main_frame, 
            textvariable=self.search_var, 
            width=300
        )
        self.find_entry.grid(row=0, column=1, padx=0, pady=PADDING_STD, sticky="ew")

    def _create_replace_input(self):
        """Değiştirme girişi alanını oluşturur."""
        ctk.CTkLabel(
            self.main_frame, 
            text="Yeni Değer:", 
            font=FONT_MAIN
        ).grid(row=1, column=0, padx=(0, PADDING_STD), pady=PADDING_STD, sticky="w")
        
        self.replace_entry = ctk.CTkEntry(
            self.main_frame, 
            textvariable=self.replace_var, 
            width=300
        )
        self.replace_entry.grid(row=1, column=1, padx=0, pady=PADDING_STD, sticky="ew")

    def _create_options(self):
        """Arama seçeneklerini (checkbox) oluşturur."""
        options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, columnspan=2, pady=PADDING_STD, sticky="w")
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Büyük/Küçük Harf Duyarlı", 
            variable=self.match_case_var, 
            font=FONT_SMALL
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkCheckBox(
            options_frame, 
            text="Tam Sözcük", 
            variable=self.whole_word_var, 
            font=FONT_SMALL
        ).pack(side="left")

    def _create_buttons(self):
        """Aksiyon butonlarını oluşturur."""
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        
        btn_config = {"height": 32, "font": FONT_MAIN}
        
        self.find_btn = ctk.CTkButton(
            btn_frame, 
            text="Sonrakini Bul", 
            command=self.find_next, 
            **btn_config
        )
        self.find_btn.pack(side="left", expand=True, fill="x", padx=(0, PADDING_SMALL))
        
        self.replace_btn = ctk.CTkButton(
            btn_frame, 
            text="Değiştir", 
            command=self.replace_one, 
            fg_color="transparent", 
            border_width=1, 
            **btn_config
        )
        self.replace_btn.pack(side="left", expand=True, fill="x", padx=PADDING_SMALL)
        
        self.replace_all_btn = ctk.CTkButton(
            btn_frame, 
            text="Tümünü Değiştir", 
            command=self.replace_all, 
            fg_color="transparent", 
            border_width=1, 
            **btn_config
        )
        self.replace_all_btn.pack(side="left", expand=True, fill="x", padx=(PADDING_SMALL, 0))

    def _create_status_bar(self):
        """Durum bilgi çubuğunu oluşturur."""
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="", 
            text_color="gray", 
            font=FONT_SMALL
        )
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(PADDING_STD, 0), sticky="w")

    def _bind_events(self):
        """Klavye kısayollarını tanımlar."""
        self.bind("<Return>", lambda e: self.find_next())
        self.bind("<Escape>", lambda e: self.destroy())
        self.find_entry.focus_set()

    def _get_active_text_widget(self) -> Optional[tk.Text]:
        """Aktif editörün metin bileşenini döndürür."""
        editor = self.tab_manager.get_current_editor()
        return editor.text_area if editor else None

    def _update_status(self, message: str, is_error: bool = False):
        """Durum çubuğunda mesaj gösterir."""
        color = "#ff5555" if is_error else "gray"
        self.status_label.configure(text=message, text_color=color)

    def _is_whole_word_match(self, text_widget: tk.Text, start_pos: str, end_pos: str) -> bool:
        """Belirtilen aralığın tam sözcük olup olmadığını kontrol eder."""
        if not self.whole_word_var.get():
            return True
            
        char_before = text_widget.get(f"{start_pos}-1c", start_pos) if start_pos != "1.0" else " "
        char_after = text_widget.get(end_pos, f"{end_pos}+1c")
        
        # Karakterlerin alfanümerik olup olmadığını kontrol et
        is_word_start = not char_before.isalnum() and char_before != "_"
        is_word_end = not char_after.isalnum() and char_after != "_"
        
        return is_word_start and is_word_end

    def find_next(self) -> bool:
        """Sıradaki eşleşmeyi bulur ve seçer."""
        text_widget = self._get_active_text_widget()
        if not text_widget:
            return False
            
        search_str = self.search_var.get()
        if not search_str:
            self._update_status("Lütfen aranacak metni girin.", True)
            return False

        start_pos = text_widget.index("insert")
        nocase = not self.match_case_var.get()
        
        # İlk arama (imleçten sona kadar)
        pos = text_widget.search(search_str, start_pos, stopindex="end", nocase=nocase)
        
        # Bulunamadıysa baştan ara (döngüsel)
        if not pos:
            pos = text_widget.search(search_str, "1.0", stopindex=start_pos, nocase=nocase)
            if pos:
                self._update_status("Baştan devam ediliyor.")

        if not pos:
            self._update_status(f"'{search_str}' bulunamadı.", True)
            return False

        # Bulunan pozisyonu işle
        return self._process_found_match(text_widget, pos, search_str)

    def _process_found_match(self, text_widget: tk.Text, pos: str, search_str: str) -> bool:
        """Bulunan eşleşmeyi doğrular ve seçer."""
        length = len(search_str)
        end_pos = f"{pos}+{length}c"
        
        # Tam sözcük kontrolü
        if not self._is_whole_word_match(text_widget, pos, end_pos):
            # Eşleşme geçerli değilse, bir sonraki karakterden aramaya devam et
            text_widget.mark_set("insert", f"{pos}+1c")
            return self.find_next()

        # Eşleşmeyi seç
        text_widget.tag_remove("sel", "1.0", "end")
        text_widget.tag_add("sel", pos, end_pos)
        text_widget.mark_set("insert", end_pos)
        text_widget.see(pos)
        self._update_status(f"'{search_str}' bulundu.")
        return True

    def replace_one(self):
        """Seçili metni değiştirir ve sonrakini bulur."""
        text_widget = self._get_active_text_widget()
        if not text_widget: return
        
        try:
            # Seçim kontrolü
            sel_start = text_widget.index("sel.first")
            sel_end = text_widget.index("sel.last")
            selected_text = text_widget.get(sel_start, sel_end)
            
            search_str = self.search_var.get()
            match_case = self.match_case_var.get()
            
            # Eşleşme kontrolü
            is_match = (selected_text == search_str) if match_case else (selected_text.lower() == search_str.lower())
            
            if is_match:
                text_widget.delete(sel_start, sel_end)
                text_widget.insert(sel_start, self.replace_var.get())
                self._update_status("Değiştirildi.")
            
            self.find_next()
            
        except tk.TclError:
            self.find_next()

    def replace_all(self):
        """Tüm eşleşmeleri değiştirir."""
        text_widget = self._get_active_text_widget()
        if not text_widget: return
        
        search_str = self.search_var.get()
        if not search_str: return
        
        replace_str = self.replace_var.get()
        nocase = not self.match_case_var.get()
        
        count = 0
        current_pos = "1.0"
        
        while True:
            # Arama yap
            pos = text_widget.search(search_str, current_pos, stopindex="end", nocase=nocase)
            if not pos:
                break
                
            end_pos = f"{pos}+{len(search_str)}c"
            
            if self._is_whole_word_match(text_widget, pos, end_pos):
                text_widget.delete(pos, end_pos)
                text_widget.insert(pos, replace_str)
                count += 1
                current_pos = f"{pos}+{len(replace_str)}c"
            else:
                current_pos = f"{pos}+1c"
            
        self._update_status(f"Toplam {count} değişiklik yapıldı.")
