import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
from typing import Dict, Any, Callable, Tuple, List

class BaseSettingsPanel(ctk.CTkFrame):
    """
    Tüm ayar panelleri için temel sınıf.
    Ortak yardımcı metodları ve UI oluşturma araçlarını içerir.
    """
    
    def __init__(self, master, settings_dialog, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.settings_dialog = settings_dialog
        self.lang_manager = settings_dialog.lang_manager
        self.current_settings = settings_dialog.current_settings
        
        self._setup_content()

    def _setup_content(self):
        """Panel içeriğini oluşturmak için alt sınıflar tarafından override edilmeli."""
        pass

    def update_setting(self, key: str, value: Any):
        """Ayarı günceller ve SettingsDialog'a bildirir."""
        self.settings_dialog.update_setting(key, value)

    def _get_setting_info(self, key: str) -> Tuple[str, str]:
        """Dil yöneticisinden ayar etiketini ve açıklamasını alır."""
        return self.settings_dialog._get_setting_info(key)

    def _create_row_frame(self, label_text: str, description: str = "") -> ctk.CTkFrame:
        """Standart bir ayar satırı çerçevesi oluşturur."""
        row = ctk.CTkFrame(self, fg_color=("gray95", "gray20"), corner_radius=10)
        row.pack(fill="x", pady=6, padx=10)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=14)
        
        ctk.CTkLabel(
            left, text=label_text, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            anchor="w"
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                left, text=description, font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray55"), anchor="w", 
                wraplength=400, justify="left"
            ).pack(anchor="w", pady=(3, 0))
            
        right = ctk.CTkFrame(row, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=16, pady=14)
        
        return right
    
    def _add_section_header(self, title: str, description: str = ""):
        """Bölüm başlığı ekler."""
        # Üst boşluk (ilk bölüm hariç)
        if len(self.winfo_children()) > 0:
            ctk.CTkFrame(self, height=16, fg_color="transparent").pack(fill="x")
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(8, 4))
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                header_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray55")
            ).pack(anchor="w", pady=(2, 0))
        
        # İnce ayırıcı
        ctk.CTkFrame(
            self,
            height=1,
            fg_color=("gray80", "gray30")
        ).pack(fill="x", padx=10, pady=(6, 8))

    def add_switch(self, key: str):
        """Boolean ayar için switch ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        var = tk.BooleanVar(value=self.current_settings.get(key, False))
        
        switch = ctk.CTkSwitch(
            container, text="", variable=var,
            command=lambda: self.update_setting(key, var.get()),
            progress_color=("#2ecc71", "#27ae60"),
            button_color=("gray70", "gray40"),
            button_hover_color=("gray60", "gray50")
        )
        switch.pack(side="right")

    def add_combo(self, key: str, values: List[str], width: int = 200, is_int: bool = False):
        """Seçenek listesi için ComboBox ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key)
        var = tk.StringVar(value=str(current_val))
        
        def callback(choice):
            val = int(choice) if is_int else choice
            self.update_setting(key, val)

        combo = ctk.CTkComboBox(
            container, values=[str(v) for v in values], variable=var,
            width=width, command=callback,
            border_width=2,
            border_color=("gray75", "gray35"),
            button_color=("gray80", "gray30"),
            button_hover_color=("gray70", "gray40"),
            dropdown_hover_color=("gray85", "gray25")
        )
        combo.pack(side="right")

    def add_slider(self, key: str, from_: int, to: int, steps: int = None, show_value: bool = True):
        """Sayısal değerler için Slider ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, from_)
        var = tk.IntVar(value=current_val)
        
        if show_value:
            value_label = ctk.CTkLabel(
                container, textvariable=var, width=50,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=("gray90", "gray25"),
                corner_radius=6
            )
            value_label.pack(side="right", padx=(10, 0))

        if steps is None:
            steps = to - from_ 

        slider = ctk.CTkSlider(
            container, from_=from_, to=to, number_of_steps=steps,
            variable=var, width=160,
            command=lambda val: self.update_setting(key, int(val)),
            progress_color=("#3498db", "#2980b9"),
            button_color=("#3498db", "#2980b9"),
            button_hover_color=("#2980b9", "#1f618d")
        )
        slider.pack(side="right")

    def add_entry(self, key: str, placeholder: str = "", width: int = 200, readonly: bool = False):
        """Metin girişi ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        entry = ctk.CTkEntry(
            container, width=width, placeholder_text=placeholder,
            border_width=2,
            border_color=("gray75", "gray35"),
            fg_color=("white", "gray22")
        )
        entry.insert(0, str(self.current_settings.get(key, "")))
        
        if readonly:
            entry.configure(state="readonly")
        else:
            entry.bind("<FocusOut>", lambda e: self.update_setting(key, entry.get()))
            entry.bind("<Return>", lambda e: self.update_setting(key, entry.get()))
            
        entry.pack(side="right")
    
    def add_color_picker(self, key: str):
        """Renk seçici ekler."""
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_color = self.current_settings.get(key, "#0098ff")
        
        # Renk önizleme kutusu
        color_frame = ctk.CTkFrame(
            container, 
            width=80, height=32, 
            corner_radius=8,
            fg_color=current_color,
            border_width=2,
            border_color=("gray70", "gray40")
        )
        color_frame.pack(side="right")
        color_frame.pack_propagate(False)
        
        # Hex kodu etiketi
        hex_label = ctk.CTkLabel(
            color_frame,
            text=current_color.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white"
        )
        hex_label.pack(expand=True)
        
        def pick_color():
            result = colorchooser.askcolor(
                color=current_color,
                title=label,
                parent=self.winfo_toplevel()
            )
            if result[1]:
                new_color = result[1]
                color_frame.configure(fg_color=new_color)
                hex_label.configure(text=new_color.upper())
                self.update_setting(key, new_color)
        
        # Tıklama olayı
        color_frame.bind("<Button-1>", lambda e: pick_color())
        hex_label.bind("<Button-1>", lambda e: pick_color())
        
        # Cursor değiştir
        color_frame.configure(cursor="hand2")
    
    def add_info_card(self, icon: str, title: str, description: str):
        """Bilgi kartı ekler (ayar olmadan sadece bilgi gösterir)."""
        card = ctk.CTkFrame(
            self, 
            fg_color=("gray92", "gray22"),
            corner_radius=10,
            border_width=1,
            border_color=("gray85", "gray28")
        )
        card.pack(fill="x", pady=8, padx=10)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        
        # İkon ve başlık satırı
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Açıklama
        ctk.CTkLabel(
            inner,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray55"),
            wraplength=500,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

