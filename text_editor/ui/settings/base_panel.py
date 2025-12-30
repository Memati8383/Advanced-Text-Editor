"""
Base Settings Panel

Tüm ayar panelleri için temel sınıf.
Ortak yardımcı metodları, UI oluşturma araçlarını ve 
gelişmiş özellikler içerir.

Özellikler:
    - Tip güvenli yapı
    - Input validation
    - Tooltip desteği
    - Animasyonlar
    - Segmented control
    - Number stepper
"""
from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
from typing import Dict, Any, Callable, Tuple, List, Optional, Final, Union
from dataclasses import dataclass
import re


# =============================================================================
# Sabitler
# =============================================================================

class PanelConstants:
    """Panel UI sabitleri."""
    # Spacing
    ROW_PADDING_Y: Final[int] = 6
    ROW_PADDING_X: Final[int] = 10
    ROW_CORNER_RADIUS: Final[int] = 10
    INNER_PADDING: Final[int] = 14
    SECTION_SPACING: Final[int] = 16
    
    # Colors
    ROW_BG_LIGHT: Final[str] = "gray95"
    ROW_BG_DARK: Final[str] = "gray20"
    BORDER_LIGHT: Final[str] = "gray75"
    BORDER_DARK: Final[str] = "gray35"
    TEXT_MUTED_LIGHT: Final[str] = "gray50"
    TEXT_MUTED_DARK: Final[str] = "gray55"
    
    # Switch Colors
    SWITCH_ACTIVE: Final[Tuple[str, str]] = ("#2ecc71", "#27ae60")
    
    # Slider Colors  
    SLIDER_PROGRESS: Final[Tuple[str, str]] = ("#3498db", "#2980b9")
    SLIDER_BUTTON: Final[Tuple[str, str]] = ("#3498db", "#2980b9")
    SLIDER_BUTTON_HOVER: Final[Tuple[str, str]] = ("#2980b9", "#1f618d")
    
    # Fonts
    LABEL_FONT_SIZE: Final[int] = 14
    DESC_FONT_SIZE: Final[int] = 11
    HEADER_FONT_SIZE: Final[int] = 15
    VALUE_FONT_SIZE: Final[int] = 13
    
    # Animation
    FADE_DURATION_MS: Final[int] = 150
    HOVER_SCALE: Final[float] = 1.02


@dataclass(frozen=True)
class ValidationRule:
    """Input doğrulama kuralı."""
    pattern: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    error_message: str = "Geçersiz değer"


# =============================================================================
# Ana Sınıf
# =============================================================================

class BaseSettingsPanel(ctk.CTkFrame):
    """
    Tüm ayar panelleri için temel sınıf.
    
    Ortak yardımcı metodları ve UI oluşturma araçlarını içerir.
    Clean Code prensiplerine uygun olarak yapılandırılmıştır.
    """
    
    def __init__(
        self, 
        master: ctk.CTkFrame, 
        settings_dialog: Any, 
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Referanslar
        self.settings_dialog = settings_dialog
        self.lang_manager = settings_dialog.lang_manager
        self.current_settings = settings_dialog.current_settings
        
        # Widget cache (performans için)
        self._widget_cache: Dict[str, Any] = {}
        
        # Validation errors
        self._validation_errors: Dict[str, str] = {}
        
        self._setup_content()

    def _setup_content(self) -> None:
        """Panel içeriğini oluşturmak için alt sınıflar tarafından override edilmeli."""
        pass

    # =========================================================================
    # Core Methods
    # =========================================================================

    def update_setting(self, key: str, value: Any) -> None:
        """
        Ayarı günceller ve SettingsDialog'a bildirir.
        
        Args:
            key: Ayar anahtarı
            value: Yeni değer
        """
        self.settings_dialog.update_setting(key, value)

    def _get_setting_info(self, key: str) -> Tuple[str, str]:
        """
        Dil yöneticisinden ayar etiketini ve açıklamasını alır.
        
        Args:
            key: Ayar anahtarı
            
        Returns:
            Tuple[str, str]: (label, description)
        """
        return self.settings_dialog._get_setting_info(key)

    def _get_localized(self, key: str, default: str = "") -> str:
        """
        Çeviri al.
        
        Args:
            key: Çeviri anahtarı
            default: Varsayılan değer
            
        Returns:
            str: Çevrilmiş metin
        """
        return self.lang_manager.get(key, default)

    # =========================================================================
    # Layout Helpers
    # =========================================================================

    def _create_row_frame(
        self, 
        label_text: str, 
        description: str = "",
        tooltip: Optional[str] = None
    ) -> ctk.CTkFrame:
        """
        Standart bir ayar satırı çerçevesi oluşturur.
        
        Args:
            label_text: Etiket metni
            description: Açıklama metni
            tooltip: İsteğe bağlı tooltip
            
        Returns:
            CTkFrame: Sağ taraftaki container (widget'ları eklemek için)
        """
        row = ctk.CTkFrame(
            self, 
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK), 
            corner_radius=PanelConstants.ROW_CORNER_RADIUS
        )
        row.pack(fill="x", pady=PanelConstants.ROW_PADDING_Y, padx=PanelConstants.ROW_PADDING_X)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        
        # Sol taraf - Etiket ve açıklama
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=PanelConstants.INNER_PADDING)
        
        label = ctk.CTkLabel(
            left, 
            text=label_text, 
            font=ctk.CTkFont(size=PanelConstants.LABEL_FONT_SIZE, weight="bold"), 
            anchor="w"
        )
        label.pack(anchor="w")
        
        # Tooltip ekle
        if tooltip:
            self._add_tooltip(label, tooltip)
        
        if description:
            ctk.CTkLabel(
                left, 
                text=description, 
                font=ctk.CTkFont(size=PanelConstants.DESC_FONT_SIZE),
                text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK), 
                anchor="w", 
                wraplength=400, 
                justify="left"
            ).pack(anchor="w", pady=(3, 0))
            
        # Sağ taraf - Widget container
        right = ctk.CTkFrame(row, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=16, pady=PanelConstants.INNER_PADDING)
        
        return right
    
    def _add_section_header(
        self, 
        title: str, 
        description: str = "",
        icon: Optional[str] = None
    ) -> None:
        """
        Bölüm başlığı ekler.
        
        Args:
            title: Başlık metni
            description: Açıklama metni
            icon: İsteğe bağlı ikon (emoji)
        """
        # Üst boşluk (ilk bölüm hariç)
        if len(self.winfo_children()) > 0:
            spacer = ctk.CTkFrame(self, height=PanelConstants.SECTION_SPACING, fg_color="transparent")
            spacer.pack(fill="x")
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=(8, 4))
        
        # İkon varsa ekle
        display_title = f"{icon} {title}" if icon else title
        
        ctk.CTkLabel(
            header_frame,
            text=display_title,
            font=ctk.CTkFont(size=PanelConstants.HEADER_FONT_SIZE, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                header_frame,
                text=description,
                font=ctk.CTkFont(size=PanelConstants.DESC_FONT_SIZE),
                text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK)
            ).pack(anchor="w", pady=(2, 0))
        
        # İnce ayırıcı - gradient efekti
        separator = ctk.CTkFrame(
            self,
            height=1,
            fg_color=("gray80", "gray30")
        )
        separator.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=(6, 8))

    # =========================================================================
    # Input Widgets
    # =========================================================================

    def add_switch(
        self, 
        key: str,
        on_change: Optional[Callable[[bool], None]] = None
    ) -> ctk.CTkSwitch:
        """
        Boolean ayar için switch ekler.
        
        Args:
            key: Ayar anahtarı
            on_change: Değişiklik callback'i
            
        Returns:
            CTkSwitch: Oluşturulan switch widget'ı
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        var = tk.BooleanVar(value=self.current_settings.get(key, False))
        
        def on_toggle():
            value = var.get()
            self.update_setting(key, value)
            if on_change:
                on_change(value)
        
        switch = ctk.CTkSwitch(
            container, 
            text="", 
            variable=var,
            command=on_toggle,
            progress_color=PanelConstants.SWITCH_ACTIVE,
            button_color=("gray70", "gray40"),
            button_hover_color=("gray60", "gray50")
        )
        switch.pack(side="right")
        
        # Cache'le
        self._widget_cache[key] = switch
        
        return switch

    def add_combo(
        self, 
        key: str, 
        values: List[str], 
        width: int = 200, 
        is_int: bool = False,
        on_change: Optional[Callable[[Any], None]] = None
    ) -> ctk.CTkComboBox:
        """
        Seçenek listesi için ComboBox ekler.
        
        Args:
            key: Ayar anahtarı
            values: Seçenek listesi
            width: Widget genişliği
            is_int: Integer dönüşümü yapılsın mı
            on_change: Değişiklik callback'i
            
        Returns:
            CTkComboBox: Oluşturulan combo widget'ı
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key)
        var = tk.StringVar(value=str(current_val))
        
        def callback(choice: str):
            val = int(choice) if is_int else choice
            self.update_setting(key, val)
            if on_change:
                on_change(val)

        combo = ctk.CTkComboBox(
            container, 
            values=[str(v) for v in values], 
            variable=var,
            width=width, 
            command=callback,
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            button_color=("gray80", "gray30"),
            button_hover_color=("gray70", "gray40"),
            dropdown_hover_color=("gray85", "gray25")
        )
        combo.pack(side="right")
        
        self._widget_cache[key] = combo
        
        return combo

    def add_slider(
        self, 
        key: str, 
        from_: int, 
        to: int, 
        steps: Optional[int] = None, 
        show_value: bool = True,
        unit: str = "",
        on_change: Optional[Callable[[int], None]] = None
    ) -> ctk.CTkSlider:
        """
        Sayısal değerler için Slider ekler.
        
        Args:
            key: Ayar anahtarı
            from_: Minimum değer
            to: Maximum değer
            steps: Adım sayısı
            show_value: Değer etiketi gösterilsin mi
            unit: Birim etiketi (örn: "px", "ms")
            on_change: Değişiklik callback'i
            
        Returns:
            CTkSlider: Oluşturulan slider widget'ı
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, from_)
        var = tk.IntVar(value=current_val)
        
        def on_slide(val: float):
            int_val = int(val)
            var.set(int_val)
            self.update_setting(key, int_val)
            if on_change:
                on_change(int_val)
        
        if show_value:
            # Değer gösterge frame
            value_frame = ctk.CTkFrame(container, fg_color="transparent")
            value_frame.pack(side="right", padx=(10, 0))
            
            value_label = ctk.CTkLabel(
                value_frame, 
                textvariable=var, 
                width=40,
                font=ctk.CTkFont(size=PanelConstants.VALUE_FONT_SIZE, weight="bold"),
                fg_color=("gray90", "gray25"),
                corner_radius=6
            )
            value_label.pack(side="left")
            
            if unit:
                ctk.CTkLabel(
                    value_frame,
                    text=unit,
                    font=ctk.CTkFont(size=11),
                    text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK)
                ).pack(side="left", padx=(4, 0))

        if steps is None:
            steps = to - from_ 

        slider = ctk.CTkSlider(
            container, 
            from_=from_, 
            to=to, 
            number_of_steps=steps,
            variable=var, 
            width=160,
            command=on_slide,
            progress_color=PanelConstants.SLIDER_PROGRESS,
            button_color=PanelConstants.SLIDER_BUTTON,
            button_hover_color=PanelConstants.SLIDER_BUTTON_HOVER
        )
        slider.pack(side="right")
        
        self._widget_cache[key] = slider
        
        return slider

    def add_entry(
        self, 
        key: str, 
        placeholder: str = "", 
        width: int = 200, 
        readonly: bool = False,
        validation: Optional[ValidationRule] = None,
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkEntry:
        """
        Metin girişi ekler.
        
        Args:
            key: Ayar anahtarı
            placeholder: Placeholder metni
            width: Widget genişliği
            readonly: Salt okunur mu
            validation: Doğrulama kuralı
            on_change: Değişiklik callback'i
            
        Returns:
            CTkEntry: Oluşturulan entry widget'ı
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        # Entry container (validation feedback için)
        entry_container = ctk.CTkFrame(container, fg_color="transparent")
        entry_container.pack(side="right")
        
        entry = ctk.CTkEntry(
            entry_container, 
            width=width, 
            placeholder_text=placeholder,
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            fg_color=("white", "gray22")
        )
        entry.insert(0, str(self.current_settings.get(key, "")))
        entry.pack(side="left")
        
        # Validation error label (başlangıçta gizli)
        error_label = ctk.CTkLabel(
            entry_container,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#e74c3c",
            width=0
        )
        
        if readonly:
            entry.configure(state="readonly")
        else:
            def on_value_change(event=None):
                value = entry.get()
                
                # Validation
                if validation:
                    is_valid, error = self._validate_input(value, validation)
                    if not is_valid:
                        entry.configure(border_color=("#e74c3c", "#e74c3c"))
                        error_label.configure(text=error)
                        error_label.pack(side="left", padx=(4, 0))
                        self._validation_errors[key] = error
                        return
                    else:
                        entry.configure(border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK))
                        error_label.pack_forget()
                        self._validation_errors.pop(key, None)
                
                self.update_setting(key, value)
                if on_change:
                    on_change(value)
            
            entry.bind("<FocusOut>", on_value_change)
            entry.bind("<Return>", on_value_change)
        
        self._widget_cache[key] = entry
        
        return entry

    def add_number_stepper(
        self, 
        key: str,
        min_val: int = 0,
        max_val: int = 100,
        step: int = 1,
        width: int = 50
    ) -> ctk.CTkFrame:
        """
        Sayı artırma/azaltma kontrolü ekler (+ / - butonları ile).
        
        Args:
            key: Ayar anahtarı
            min_val: Minimum değer
            max_val: Maximum değer
            step: Artış miktarı
            width: Değer label genişliği
            
        Returns:
            CTkFrame: Stepper container
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, min_val)
        var = tk.IntVar(value=current_val)
        
        def change_value(delta: int):
            new_val = var.get() + delta
            if min_val <= new_val <= max_val:
                var.set(new_val)
                self.update_setting(key, new_val)
        
        stepper_frame = ctk.CTkFrame(container, fg_color="transparent")
        stepper_frame.pack(side="right")
        
        # - Butonu
        ctk.CTkButton(
            stepper_frame, 
            text="−", 
            width=32, 
            height=32,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: change_value(-step)
        ).pack(side="left")
        
        # Değer Label
        ctk.CTkLabel(
            stepper_frame, 
            textvariable=var, 
            width=width,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=8)
        
        # + Butonu
        ctk.CTkButton(
            stepper_frame, 
            text="+", 
            width=32, 
            height=32,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda: change_value(step)
        ).pack(side="left")
        
        self._widget_cache[key] = var
        
        return stepper_frame

    def add_segmented_control(
        self, 
        key: str, 
        values: List[str],
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkSegmentedButton:
        """
        Segmented button kontrolü ekler.
        
        Args:
            key: Ayar anahtarı
            values: Seçenek listesi
            on_change: Değişiklik callback'i
            
        Returns:
            CTkSegmentedButton: Oluşturulan widget
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = str(self.current_settings.get(key, values[0]))
        
        def callback(value: str):
            self.update_setting(key, value)
            if on_change:
                on_change(value)
        
        segmented = ctk.CTkSegmentedButton(
            container,
            values=values,
            command=callback,
            selected_color=("#3498db", "#2980b9"),
            selected_hover_color=("#2980b9", "#1f618d"),
            unselected_color=("gray85", "gray28"),
            unselected_hover_color=("gray75", "gray35")
        )
        segmented.set(current_val)
        segmented.pack(side="right")
        
        self._widget_cache[key] = segmented
        
        return segmented

    def add_color_picker(
        self, 
        key: str,
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkFrame:
        """
        Renk seçici ekler.
        
        Args:
            key: Ayar anahtarı
            on_change: Değişiklik callback'i
            
        Returns:
            CTkFrame: Renk önizleme frame'i
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_color = self.current_settings.get(key, "#0098ff")
        
        # Renk önizleme kutusu
        color_frame = ctk.CTkFrame(
            container, 
            width=80, 
            height=32, 
            corner_radius=8,
            fg_color=current_color,
            border_width=2,
            border_color=("gray70", "gray40"),
            cursor="hand2"
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
                if on_change:
                    on_change(new_color)
        
        # Tıklama olayları
        color_frame.bind("<Button-1>", lambda e: pick_color())
        hex_label.bind("<Button-1>", lambda e: pick_color())
        
        self._widget_cache[key] = color_frame
        
        return color_frame

    # =========================================================================
    # Information Widgets
    # =========================================================================

    def add_info_card(
        self, 
        icon: str, 
        title: str, 
        description: str,
        card_type: str = "info"
    ) -> ctk.CTkFrame:
        """
        Bilgi kartı ekler.
        
        Args:
            icon: Kart ikonu
            title: Kart başlığı
            description: Kart açıklaması
            card_type: Kart tipi ("info", "warning", "success", "error")
            
        Returns:
            CTkFrame: Oluşturulan kart
        """
        # Kart tipine göre renkler
        type_colors = {
            "info": (("gray92", "gray22"), ("gray85", "gray28")),
            "warning": (("#fff3cd", "#3d3200"), ("#ffc107", "#735c00")),
            "success": (("#d1e7dd", "#0f3d1f"), ("#198754", "#0d6f3f")),
            "error": (("#f8d7da", "#3d0f11"), ("#dc3545", "#a71d2a"))
        }
        
        colors = type_colors.get(card_type, type_colors["info"])
        
        card = ctk.CTkFrame(
            self, 
            fg_color=colors[0],
            corner_radius=10,
            border_width=1,
            border_color=colors[1]
        )
        card.pack(fill="x", pady=8, padx=PanelConstants.ROW_PADDING_X)
        
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
            text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK),
            wraplength=500,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))
        
        return card

    def add_button_row(
        self,
        buttons: List[Dict[str, Any]]
    ) -> ctk.CTkFrame:
        """
        Buton satırı ekler.
        
        Args:
            buttons: Buton tanım listesi
                     [{"text": str, "command": Callable, "style": str, ...}, ...]
            
        Returns:
            CTkFrame: Buton container
        """
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=10)
        
        for btn_config in buttons:
            text = btn_config.get("text", "Button")
            command = btn_config.get("command", lambda: None)
            style = btn_config.get("style", "default")
            width = btn_config.get("width", None)
            
            # Stil bazlı renkler
            style_configs = {
                "default": {
                    "fg_color": ("gray75", "gray30"),
                    "hover_color": ("gray65", "gray40"),
                    "text_color": ("gray20", "gray85")
                },
                "primary": {
                    "fg_color": ("#3498db", "#2980b9"),
                    "hover_color": ("#2980b9", "#1f618d"),
                    "text_color": "white"
                },
                "success": {
                    "fg_color": ("#2ecc71", "#27ae60"),
                    "hover_color": ("#27ae60", "#1e8449"),
                    "text_color": "white"
                },
                "danger": {
                    "fg_color": ("#e74c3c", "#c0392b"),
                    "hover_color": ("#c0392b", "#a93226"),
                    "text_color": "white"
                },
                "ghost": {
                    "fg_color": "transparent",
                    "hover_color": ("gray90", "gray25"),
                    "text_color": ("gray45", "gray55"),
                    "border_width": 1,
                    "border_color": ("gray70", "gray40")
                }
            }
            
            config = style_configs.get(style, style_configs["default"])
            
            btn_kwargs = {
                "text": text,
                "command": command,
                "height": 42,
                "corner_radius": 10,
                "font": ctk.CTkFont(size=13, weight="bold"),
                **config
            }
            
            if width:
                btn_kwargs["width"] = width
            
            btn = ctk.CTkButton(button_frame, **btn_kwargs)
            btn.pack(fill="x", pady=(0, 8))
        
        return button_frame

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_input(
        self, 
        value: str, 
        rule: ValidationRule
    ) -> Tuple[bool, str]:
        """
        Input değerini doğrular.
        
        Args:
            value: Doğrulanacak değer
            rule: Doğrulama kuralı
            
        Returns:
            Tuple[bool, str]: (geçerli mi, hata mesajı)
        """
        # Pattern kontrolü
        if rule.pattern:
            if not re.match(rule.pattern, value):
                return False, rule.error_message
        
        # Uzunluk kontrolleri
        if rule.min_length is not None and len(value) < rule.min_length:
            return False, f"En az {rule.min_length} karakter gerekli"
        
        if rule.max_length is not None and len(value) > rule.max_length:
            return False, f"En fazla {rule.max_length} karakter olabilir"
        
        # Sayısal kontroller
        try:
            if rule.min_value is not None or rule.max_value is not None:
                num_value = float(value)
                
                if rule.min_value is not None and num_value < rule.min_value:
                    return False, f"En az {rule.min_value} olmalı"
                
                if rule.max_value is not None and num_value > rule.max_value:
                    return False, f"En fazla {rule.max_value} olabilir"
        except ValueError:
            if rule.min_value is not None or rule.max_value is not None:
                return False, "Geçerli bir sayı giriniz"
        
        return True, ""

    def has_validation_errors(self) -> bool:
        """Validation hatası var mı kontrol eder."""
        return len(self._validation_errors) > 0

    # =========================================================================
    # Tooltip
    # =========================================================================

    def _add_tooltip(
        self, 
        widget: ctk.CTkBaseClass, 
        text: str,
        delay_ms: int = 500,
        position: str = "bottom"  # "top", "bottom", "left", "right"
    ) -> None:
        """
        Widget'a gelişmiş tooltip ekler.
        
        Args:
            widget: Hedef widget
            text: Tooltip metni
            delay_ms: Görünme gecikmesi (ms)
            position: Tooltip konumu
        """
        tooltip_window = None
        schedule_id = None
        
        def calculate_position():
            """Tooltip konumunu hesaplar."""
            x = widget.winfo_rootx()
            y = widget.winfo_rooty()
            w = widget.winfo_width()
            h = widget.winfo_height()
            
            if position == "bottom":
                return x + w // 2, y + h + 8
            elif position == "top":
                return x + w // 2, y - 8
            elif position == "left":
                return x - 8, y + h // 2
            else:  # right
                return x + w + 8, y + h // 2
        
        def show_tooltip():
            nonlocal tooltip_window
            if tooltip_window:
                return
            
            px, py = calculate_position()
            
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_attributes("-topmost", True)
            
            # İlk başta görünmez (fade-in için)
            tooltip_window.attributes("-alpha", 0.0)
            
            # Tooltip container
            container = tk.Frame(
                tooltip_window,
                background="#1a1a1a",
                bd=1,
                relief="solid"
            )
            container.pack()
            
            # Tooltip label
            label = tk.Label(
                container,
                text=text,
                background="#1a1a1a",
                foreground="#f0f0f0",
                font=("Segoe UI", 10),
                padx=10,
                pady=6,
                wraplength=300,
                justify="left"
            )
            label.pack()
            
            # Konum ayarı (metin genişliğine göre merkezle)
            tooltip_window.update_idletasks()
            tw = tooltip_window.winfo_width()
            th = tooltip_window.winfo_height()
            
            if position in ("bottom", "top"):
                final_x = px - tw // 2
                final_y = py if position == "bottom" else py - th
            else:
                final_x = px if position == "right" else px - tw
                final_y = py - th // 2
            
            tooltip_window.wm_geometry(f"+{final_x}+{final_y}")
            
            # Fade-in animasyonu
            def fade_in(alpha=0.0):
                if tooltip_window and alpha < 1.0:
                    alpha += 0.15
                    tooltip_window.attributes("-alpha", min(alpha, 1.0))
                    tooltip_window.after(20, lambda: fade_in(alpha))
            
            fade_in()
        
        def schedule_tooltip(event):
            nonlocal schedule_id
            if schedule_id:
                widget.after_cancel(schedule_id)
            schedule_id = widget.after(delay_ms, show_tooltip)
        
        def hide_tooltip(event):
            nonlocal tooltip_window, schedule_id
            
            if schedule_id:
                widget.after_cancel(schedule_id)
                schedule_id = None
            
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", schedule_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        widget.bind("<Button-1>", hide_tooltip)  # Tıklamada da kapat

    # =========================================================================
    # Widget Access
    # =========================================================================

    def get_widget(self, key: str) -> Optional[Any]:
        """
        Cache'lenmiş widget'ı döndürür.
        
        Args:
            key: Widget anahtarı
            
        Returns:
            Widget veya None
        """
        return self._widget_cache.get(key)

    # =========================================================================
    # Gelişmiş Widgets
    # =========================================================================

    def add_radio_group(
        self, 
        key: str, 
        options: List[Dict[str, str]],
        orientation: str = "horizontal",
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkFrame:
        """
        Radio button grubu ekler.
        
        Args:
            key: Ayar anahtarı
            options: [{"value": str, "label": str}, ...] formatında seçenekler
            orientation: "horizontal" veya "vertical"
            on_change: Değişiklik callback'i
            
        Returns:
            CTkFrame: Radio group container
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = str(self.current_settings.get(key, options[0]["value"] if options else ""))
        var = tk.StringVar(value=current_val)
        
        def on_select():
            value = var.get()
            self.update_setting(key, value)
            if on_change:
                on_change(value)
        
        radio_frame = ctk.CTkFrame(container, fg_color="transparent")
        radio_frame.pack(side="right")
        
        pack_side = "left" if orientation == "horizontal" else "top"
        
        for option in options:
            rb = ctk.CTkRadioButton(
                radio_frame,
                text=option.get("label", option["value"]),
                variable=var,
                value=option["value"],
                command=on_select,
                font=ctk.CTkFont(size=12),
                radiobutton_width=18,
                radiobutton_height=18,
                border_width_checked=5,
                fg_color=PanelConstants.SWITCH_ACTIVE,
                hover_color=("#27ae60", "#1e8449")
            )
            rb.pack(side=pack_side, padx=(8, 0) if pack_side == "left" else 0, pady=2)
        
        self._widget_cache[key] = var
        
        return radio_frame

    def add_file_picker(
        self,
        key: str,
        file_types: Optional[List[Tuple[str, str]]] = None,
        mode: str = "file",  # "file", "directory", "save"
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkFrame:
        """
        Dosya/klasör seçici ekler.
        
        Args:
            key: Ayar anahtarı
            file_types: [("Python Files", "*.py"), ...] formatında dosya türleri
            mode: "file", "directory" veya "save"
            on_change: Değişiklik callback'i
            
        Returns:
            CTkFrame: File picker container
        """
        from tkinter import filedialog
        
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, "")
        
        picker_frame = ctk.CTkFrame(container, fg_color="transparent")
        picker_frame.pack(side="right")
        
        # Path entry
        path_entry = ctk.CTkEntry(
            picker_frame,
            width=200,
            placeholder_text="Seçilmedi...",
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            fg_color=("white", "gray22")
        )
        path_entry.insert(0, current_val)
        path_entry.pack(side="left", padx=(0, 8))
        
        def browse():
            if mode == "file":
                result = filedialog.askopenfilename(
                    parent=self.winfo_toplevel(),
                    filetypes=file_types or [("All Files", "*.*")]
                )
            elif mode == "directory":
                result = filedialog.askdirectory(
                    parent=self.winfo_toplevel()
                )
            else:  # save
                result = filedialog.asksaveasfilename(
                    parent=self.winfo_toplevel(),
                    filetypes=file_types or [("All Files", "*.*")]
                )
            
            if result:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, result)
                self.update_setting(key, result)
                if on_change:
                    on_change(result)
        
        browse_btn = ctk.CTkButton(
            picker_frame,
            text="📂",
            width=36,
            height=32,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=14),
            command=browse
        )
        browse_btn.pack(side="left")
        
        self._widget_cache[key] = path_entry
        
        return picker_frame

    def add_text_area(
        self,
        key: str,
        height: int = 100,
        placeholder: str = "",
        on_change: Optional[Callable[[str], None]] = None
    ) -> ctk.CTkTextbox:
        """
        Çok satırlı metin alanı ekler.
        
        Args:
            key: Ayar anahtarı
            height: Yükseklik (piksel)
            placeholder: Placeholder metin
            on_change: Değişiklik callback'i
            
        Returns:
            CTkTextbox: Text area widget'ı
        """
        label, desc = self._get_setting_info(key)
        
        # Full-width text area için özel layout
        text_frame = ctk.CTkFrame(
            self,
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK),
            corner_radius=PanelConstants.ROW_CORNER_RADIUS
        )
        text_frame.pack(fill="x", pady=PanelConstants.ROW_PADDING_Y, padx=PanelConstants.ROW_PADDING_X)
        
        # Header
        header = ctk.CTkFrame(text_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 8))
        
        ctk.CTkLabel(
            header,
            text=label,
            font=ctk.CTkFont(size=PanelConstants.LABEL_FONT_SIZE, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        if desc:
            ctk.CTkLabel(
                header,
                text=desc,
                font=ctk.CTkFont(size=PanelConstants.DESC_FONT_SIZE),
                text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK),
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))
        
        # Textbox
        current_val = self.current_settings.get(key, "")
        
        textbox = ctk.CTkTextbox(
            text_frame,
            height=height,
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            fg_color=("white", "gray22"),
            font=ctk.CTkFont(size=12)
        )
        textbox.pack(fill="x", padx=16, pady=(0, 14))
        textbox.insert("1.0", current_val)
        
        def on_text_change(event=None):
            value = textbox.get("1.0", tk.END).strip()
            self.update_setting(key, value)
            if on_change:
                on_change(value)
        
        textbox.bind("<FocusOut>", on_text_change)
        
        self._widget_cache[key] = textbox
        
        return textbox

    def add_accordion_section(
        self,
        title: str,
        description: str = "",
        expanded: bool = False,
        icon: str = ""
    ) -> Tuple[ctk.CTkFrame, Callable[[], None]]:
        """
        Açılır/kapanır section ekler.
        
        Args:
            title: Section başlığı
            description: Section açıklaması
            expanded: Başlangıçta açık mı
            icon: İsteğe bağlı ikon
            
        Returns:
            Tuple[CTkFrame, Callable]: (content_frame, toggle_function)
        """
        is_expanded = tk.BooleanVar(value=expanded)
        
        # Ana container
        accordion = ctk.CTkFrame(
            self,
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK),
            corner_radius=PanelConstants.ROW_CORNER_RADIUS
        )
        accordion.pack(fill="x", pady=PanelConstants.ROW_PADDING_Y, padx=PanelConstants.ROW_PADDING_X)
        
        # Header (tıklanabilir)
        header = ctk.CTkFrame(accordion, fg_color="transparent", cursor="hand2")
        header.pack(fill="x", padx=16, pady=12)
        
        # Toggle ikonu
        toggle_icon = ctk.CTkLabel(
            header,
            text="▶" if not expanded else "▼",
            font=ctk.CTkFont(size=12),
            width=20
        )
        toggle_icon.pack(side="left")
        
        # Başlık ve açıklama
        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        display_title = f"{icon} {title}" if icon else title
        ctk.CTkLabel(
            text_frame,
            text=display_title,
            font=ctk.CTkFont(size=PanelConstants.LABEL_FONT_SIZE, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                text_frame,
                text=description,
                font=ctk.CTkFont(size=PanelConstants.DESC_FONT_SIZE),
                text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK),
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))
        
        # İçerik alanı
        content = ctk.CTkFrame(accordion, fg_color="transparent")
        if expanded:
            content.pack(fill="x", padx=16, pady=(0, 12))
        
        def toggle():
            if is_expanded.get():
                content.pack_forget()
                toggle_icon.configure(text="▶")
            else:
                content.pack(fill="x", padx=16, pady=(0, 12))
                toggle_icon.configure(text="▼")
            is_expanded.set(not is_expanded.get())
        
        # Tıklama olayları
        for widget in [header, toggle_icon, text_frame]:
            widget.bind("<Button-1>", lambda e: toggle())
        
        return content, toggle

    def add_chips(
        self,
        key: str,
        options: List[str],
        multi_select: bool = True,
        on_change: Optional[Callable[[List[str]], None]] = None
    ) -> ctk.CTkFrame:
        """
        Chip (etiket) seçici ekler.
        
        Args:
            key: Ayar anahtarı
            options: Seçenek listesi
            multi_select: Çoklu seçim izni
            on_change: Değişiklik callback'i
            
        Returns:
            CTkFrame: Chips container
        """
        label, desc = self._get_setting_info(key)
        container = self._create_row_frame(label, desc)
        
        current_val = self.current_settings.get(key, [])
        if isinstance(current_val, str):
            current_val = [current_val] if current_val else []
        
        selected = set(current_val)
        chip_buttons = {}
        
        chips_frame = ctk.CTkFrame(container, fg_color="transparent")
        chips_frame.pack(side="right")
        
        def update_chip_style(chip: ctk.CTkButton, is_selected: bool):
            if is_selected:
                chip.configure(
                    fg_color=("#3498db", "#2980b9"),
                    text_color="white",
                    border_color=("#2980b9", "#1f618d")
                )
            else:
                chip.configure(
                    fg_color=("transparent", "transparent"),
                    text_color=("gray40", "gray60"),
                    border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK)
                )
        
        def on_chip_click(option: str):
            if multi_select:
                if option in selected:
                    selected.discard(option)
                else:
                    selected.add(option)
            else:
                selected.clear()
                selected.add(option)
            
            # Tüm chip'leri güncelle
            for opt, chip in chip_buttons.items():
                update_chip_style(chip, opt in selected)
            
            # Ayarı kaydet
            value = list(selected)
            self.update_setting(key, value)
            if on_change:
                on_change(value)
        
        for option in options:
            chip = ctk.CTkButton(
                chips_frame,
                text=option,
                height=28,
                corner_radius=14,
                border_width=1,
                font=ctk.CTkFont(size=11),
                command=lambda o=option: on_chip_click(o)
            )
            chip.pack(side="left", padx=3)
            update_chip_style(chip, option in selected)
            chip_buttons[option] = chip
        
        self._widget_cache[key] = chip_buttons
        
        return chips_frame

    def add_badge(
        self,
        text: str,
        badge_type: str = "default"
    ) -> ctk.CTkLabel:
        """
        Bilgi rozeti ekler.
        
        Args:
            text: Rozet metni
            badge_type: "default", "new", "beta", "pro", "deprecated"
            
        Returns:
            CTkLabel: Badge widget
        """
        type_styles = {
            "default": (("gray85", "gray28"), ("gray40", "gray60")),
            "new": (("#e8f5e9", "#1b3d1b"), ("#2e7d32", "#66bb6a")),
            "beta": (("#fff3e0", "#3d2500"), ("#f57c00", "#ffb74d")),
            "pro": (("#fce4ec", "#3d0a1a"), ("#c2185b", "#f06292")),
            "deprecated": (("#fafafa", "#1a1a1a"), ("#757575", "#9e9e9e"))
        }
        
        bg_color, text_color = type_styles.get(badge_type, type_styles["default"])
        
        badge = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=bg_color,
            text_color=text_color,
            corner_radius=10,
            padx=10,
            pady=3
        )
        badge.pack(anchor="w", padx=PanelConstants.ROW_PADDING_X, pady=4)
        
        return badge

    def add_key_value_editor(
        self,
        key: str,
        on_change: Optional[Callable[[Dict[str, str]], None]] = None
    ) -> ctk.CTkFrame:
        """
        Anahtar-değer çifti düzenleyici ekler.
        
        Args:
            key: Ayar anahtarı
            on_change: Değişiklik callback'i
            
        Returns:
            CTkFrame: Editor container
        """
        label, desc = self._get_setting_info(key)
        
        editor_frame = ctk.CTkFrame(
            self,
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK),
            corner_radius=PanelConstants.ROW_CORNER_RADIUS
        )
        editor_frame.pack(fill="x", pady=PanelConstants.ROW_PADDING_Y, padx=PanelConstants.ROW_PADDING_X)
        
        # Header
        header = ctk.CTkFrame(editor_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 8))
        
        ctk.CTkLabel(
            header,
            text=label,
            font=ctk.CTkFont(size=PanelConstants.LABEL_FONT_SIZE, weight="bold"),
            anchor="w"
        ).pack(side="left")
        
        current_data: Dict[str, str] = self.current_settings.get(key, {})
        entries: List[Tuple[ctk.CTkEntry, ctk.CTkEntry]] = []
        rows_container = ctk.CTkFrame(editor_frame, fg_color="transparent")
        rows_container.pack(fill="x", padx=16, pady=(0, 8))
        
        def save_data():
            data = {}
            for k_entry, v_entry in entries:
                k = k_entry.get().strip()
                v = v_entry.get().strip()
                if k:
                    data[k] = v
            self.update_setting(key, data)
            if on_change:
                on_change(data)
        
        def add_row(k: str = "", v: str = ""):
            row = ctk.CTkFrame(rows_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            k_entry = ctk.CTkEntry(
                row,
                placeholder_text="Anahtar",
                width=150,
                border_width=1,
                border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK)
            )
            k_entry.insert(0, k)
            k_entry.pack(side="left", padx=(0, 8))
            k_entry.bind("<FocusOut>", lambda e: save_data())
            
            v_entry = ctk.CTkEntry(
                row,
                placeholder_text="Değer",
                width=200,
                border_width=1,
                border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK)
            )
            v_entry.insert(0, v)
            v_entry.pack(side="left", padx=(0, 8))
            v_entry.bind("<FocusOut>", lambda e: save_data())
            
            entries.append((k_entry, v_entry))
            
            def remove_row():
                entries.remove((k_entry, v_entry))
                row.destroy()
                save_data()
            
            ctk.CTkButton(
                row,
                text="✕",
                width=28,
                height=28,
                corner_radius=6,
                fg_color=("gray90", "gray25"),
                hover_color=("#e74c3c", "#c0392b"),
                text_color=("gray50", "gray60"),
                font=ctk.CTkFont(size=12),
                command=remove_row
            ).pack(side="left")
        
        # Mevcut verileri yükle
        for k, v in current_data.items():
            add_row(k, v)
        
        # Ekle butonu
        add_btn = ctk.CTkButton(
            editor_frame,
            text="+ Yeni Ekle",
            height=32,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray40", "gray60"),
            font=ctk.CTkFont(size=12),
            command=lambda: add_row()
        )
        add_btn.pack(anchor="w", padx=16, pady=(0, 14))
        
        self._widget_cache[key] = entries
        
        return editor_frame

