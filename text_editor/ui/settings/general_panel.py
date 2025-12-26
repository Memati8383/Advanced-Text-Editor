import tkinter as tk
import customtkinter as ctk
from tkinter import font as tkfont
from text_editor.ui.settings.base_panel import BaseSettingsPanel

class GeneralSettingsPanel(BaseSettingsPanel):
    def _setup_content(self):
        # Uygulama Adı
        self.add_entry("app_name")
        
        # Dil Seçimi
        self._add_language_selector()

        # Yazı Tipi
        font_families = list(tkfont.families())
        font_families.sort()
        self.add_combo("font_family", font_families)
        
        # Yazı Boyutu
        self._add_font_size_selector()

    def _add_language_selector(self):
        label, desc = self._get_setting_info("language")
        container = self._create_row_frame(label, desc)
        
        lang_var = tk.StringVar(value=self.current_settings.get("language", "Türkçe"))
        
        def on_lang_change(choice):
            self.update_setting("language", choice)
            self.lang_manager.load_language(choice)
            # SettingsDialog'u yeniden yüklemeyi tetiklemek için bir sinyal gerekebilir
            # veya SettingsDialog bu callback'i inject eder.
            if hasattr(self.settings_dialog, '_reload_ui'):
                self.settings_dialog._reload_ui()
            
        ctk.CTkComboBox(
            container, values=["Türkçe", "English", "Español", "Deutsch", "Azerbaycan Türkçesi"], variable=lang_var,
            width=200, command=on_lang_change
        ).pack(side="right")

    def _add_font_size_selector(self):
        label, desc = self._get_setting_info("font_size")
        container = self._create_row_frame(label, desc)
        
        font_size_var = tk.IntVar(value=self.current_settings.get("font_size", 14))
        
        def change_font(delta):
            new_val = font_size_var.get() + delta
            if 8 <= new_val <= 32:
                font_size_var.set(new_val)
                self.update_setting("font_size", new_val)
                
        ctk.CTkButton(container, text="+", width=30, command=lambda: change_font(1)).pack(side="right", padx=(5, 0))
        ctk.CTkLabel(container, textvariable=font_size_var, width=30, font=ctk.CTkFont(weight="bold")).pack(side="right")
        ctk.CTkButton(container, text="-", width=30, command=lambda: change_font(-1)).pack(side="right")
