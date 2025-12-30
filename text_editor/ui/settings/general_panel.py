"""
Genel Ayarlar Paneli

Uygulama adı, dil ve yazı tipi ayarları.
Optimize edilmiş ve localizable yapı.

Özellikler:
    - Uygulama adı değiştirme
    - Dil seçimi (anlık UI yenileme)
    - Font ailesi seçimi
    - Font boyutu kontrolü
"""
from __future__ import annotations

import tkinter as tk
import customtkinter as ctk
from tkinter import font as tkfont
from typing import List, Final

from text_editor.ui.settings.base_panel import BaseSettingsPanel, PanelConstants, ValidationRule


class GeneralPanelConstants:
    """Panel sabitleri."""
    MIN_FONT_SIZE: Final[int] = 8
    MAX_FONT_SIZE: Final[int] = 32
    AVAILABLE_LANGUAGES: Final[List[str]] = [
        "Türkçe", 
        "English", 
        "Español", 
        "Deutsch", 
        "Azerbaycan Türkçesi"
    ]


class GeneralSettingsPanel(BaseSettingsPanel):
    """
    Genel ayarlar için panel.
    
    Temel uygulama yapılandırmasını içerir.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini oluşturur."""
        
        # ── Uygulama Grubu ──
        app_title = self._get_localized("sections.application", "🏠 Uygulama")
        app_desc = self._get_localized("sections.application_desc", "Temel uygulama ayarları")
        self._add_section_header(app_title, app_desc)
        
        # Uygulama Adı - Validation ile
        self.add_entry(
            "app_name",
            validation=ValidationRule(
                min_length=1,
                max_length=50,
                error_message="Uygulama adı 1-50 karakter olmalı"
            )
        )
        
        # Dil Seçimi
        self._add_language_selector()
        
        # ── Yazı Tipi Grubu ──
        font_title = self._get_localized("sections.font", "✏️ Yazı Tipi")
        font_desc = self._get_localized("sections.font_desc", "Editör yazı tipi ayarları")
        self._add_section_header(font_title, font_desc)
        
        # Font Ailesi
        font_families = self._get_monospace_fonts()
        self.add_combo("font_family", font_families)
        
        # Font Boyutu
        self._add_font_size_stepper()
        
        # ── Bilgi Kartı ──
        tip_title = self._get_localized("tips.font_tip_title", "Yazı Tipi Önerisi")
        tip_content = self._get_localized(
            "tips.font_tip_content",
            "Kod yazımı için monospace (eşit genişlikli) fontları tercih edin:\n"
            "• Consolas, Fira Code, JetBrains Mono\n"
            "• Source Code Pro, Cascadia Code"
        )
        self.add_info_card("💡", tip_title, tip_content)

    def _add_language_selector(self) -> None:
        """Dil seçici ekler (özel callback ile)."""
        label, desc = self._get_setting_info("language")
        container = self._create_row_frame(label, desc)
        
        current_lang = self.current_settings.get("language", "Türkçe")
        lang_var = tk.StringVar(value=current_lang)
        
        def on_lang_change(choice: str) -> None:
            self.update_setting("language", choice)
            self.lang_manager.load_language(choice)
            
            # UI'ı yenile
            if hasattr(self.settings_dialog, '_reload_ui'):
                self.settings_dialog._reload_ui()
        
        combo = ctk.CTkComboBox(
            container, 
            values=GeneralPanelConstants.AVAILABLE_LANGUAGES,
            variable=lang_var,
            width=220, 
            command=on_lang_change,
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            button_color=("gray80", "gray30"),
            button_hover_color=("gray70", "gray40"),
            dropdown_hover_color=("gray85", "gray25")
        )
        combo.pack(side="right")
        
        self._widget_cache["language"] = combo

    def _add_font_size_stepper(self) -> None:
        """Font boyutu stepper kontrolü ekler."""
        label, desc = self._get_setting_info("font_size")
        container = self._create_row_frame(label, desc)
        
        current_size = self.current_settings.get("font_size", 14)
        font_size_var = tk.IntVar(value=current_size)
        
        def change_font_size(delta: int) -> None:
            new_val = font_size_var.get() + delta
            if GeneralPanelConstants.MIN_FONT_SIZE <= new_val <= GeneralPanelConstants.MAX_FONT_SIZE:
                font_size_var.set(new_val)
                self.update_setting("font_size", new_val)
        
        stepper_frame = ctk.CTkFrame(container, fg_color="transparent")
        stepper_frame.pack(side="right")
        
        # - Butonu
        ctk.CTkButton(
            stepper_frame, 
            text="−", 
            width=36, 
            height=36,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=18, weight="bold"),
            command=lambda: change_font_size(-1)
        ).pack(side="left")
        
        # Değer Label
        value_label = ctk.CTkLabel(
            stepper_frame, 
            textvariable=font_size_var, 
            width=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("gray90", "gray25"),
            corner_radius=6
        )
        value_label.pack(side="left", padx=10)
        
        # + Butonu
        ctk.CTkButton(
            stepper_frame, 
            text="+", 
            width=36, 
            height=36,
            corner_radius=8,
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=18, weight="bold"),
            command=lambda: change_font_size(1)
        ).pack(side="left")
        
        # pt etiketi
        ctk.CTkLabel(
            stepper_frame,
            text="pt",
            font=ctk.CTkFont(size=12),
            text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK)
        ).pack(side="left", padx=(8, 0))
        
        self._widget_cache["font_size"] = font_size_var

    def _get_monospace_fonts(self) -> List[str]:
        """
        Sistemdeki monospace fontları öncelikli olarak listeler.
        
        Returns:
            List[str]: Sıralı font listesi
        """
        all_fonts = list(tkfont.families())
        
        # Öncelikli monospace fontlar
        preferred = [
            "Consolas", "Fira Code", "JetBrains Mono", "Source Code Pro",
            "Cascadia Code", "Cascadia Mono", "Monaco", "Menlo",
            "Courier New", "DejaVu Sans Mono", "Ubuntu Mono",
            "Roboto Mono", "Inconsolata", "Hack"
        ]
        
        # Öncelikli fontları başa al
        available_preferred = [f for f in preferred if f in all_fonts]
        other_fonts = sorted([f for f in all_fonts if f not in preferred])
        
        return available_preferred + other_fonts
