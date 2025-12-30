"""
Gelişmiş Ayarlar Paneli

Performans, yedekleme ve sistem ayarları.
Optimize edilmiş ve localizable yapı.

Özellikler:
    - Performans modu
    - Yedekleme ayarları
    - Hata raporlama
    - Ayar dışa/içe aktarma
    - Log seviyeleri
"""
from __future__ import annotations

import tkinter as tk
import customtkinter as ctk
from typing import Final

from text_editor.ui.settings.base_panel import BaseSettingsPanel, PanelConstants, ValidationRule


class AdvancedPanelConstants:
    """Panel sabitleri."""
    LOG_LEVELS: Final[list] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    MIN_FILE_SIZE_MB: Final[int] = 1
    MAX_FILE_SIZE_MB: Final[int] = 100
    MIN_CACHE_SIZE_MB: Final[int] = 10
    MAX_CACHE_SIZE_MB: Final[int] = 500


class AdvancedSettingsPanel(BaseSettingsPanel):
    """
    Gelişmiş ayarlar için panel.
    
    Performans, yedekleme ve sistem seviyesi ayarları içerir.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini oluşturur."""
        
        # ── Performans Grubu ──
        perf_title = self._get_localized("sections.performance", "⚡ Performans")
        perf_desc = self._get_localized("sections.performance_desc", "Performans optimizasyon ayarları")
        self._add_section_header(perf_title, perf_desc)
        
        self.add_switch("performance_mode")
        
        # Cache boyutu (varsa)
        if "cache_size" in self.current_settings:
            self.add_slider(
                "cache_size", 
                AdvancedPanelConstants.MIN_CACHE_SIZE_MB, 
                AdvancedPanelConstants.MAX_CACHE_SIZE_MB, 
                steps=49,
                unit="MB"
            )
        
        # ── Yedekleme Grubu ──
        backup_title = self._get_localized("sections.backup", "💾 Yedekleme")
        backup_desc = self._get_localized("sections.backup_desc", "Otomatik yedekleme ayarları")
        self._add_section_header(backup_title, backup_desc)
        
        self.add_switch("auto_backup")
        self._add_max_file_size()
        
        # ── Hata Ayıklama Grubu ──
        debug_title = self._get_localized("sections.debugging", "🐛 Hata Ayıklama")
        debug_desc = self._get_localized("sections.debugging_desc", "Hata raporlama ve günlük ayarları")
        self._add_section_header(debug_title, debug_desc)
        
        self.add_switch("error_reporting")
        
        # Log seviyesi
        if "log_level" in self.current_settings:
            self.add_segmented_control("log_level", AdvancedPanelConstants.LOG_LEVELS)
        
        # ── Veri Yönetimi Grubu ──
        data_title = self._get_localized("sections.data_management", "📦 Veri Yönetimi")
        data_desc = self._get_localized("sections.data_management_desc", "Ayar dışa/içe aktarma")
        self._add_section_header(data_title, data_desc)
        
        # İçe/Dışa Aktarma Butonları
        self._create_export_import_buttons()
        
        # ── Uyarı Kartı ──
        warning_title = self._get_localized("warnings.performance_mode_title", "Dikkat")
        warning_content = self._get_localized(
            "warnings.performance_mode_content",
            "Performans modu etkinleştirildiğinde bazı görsel efektler "
            "(animasyonlar, gölgeler vb.) devre dışı bırakılır. "
            "Bu, düşük donanımlı sistemlerde daha akıcı bir deneyim sağlar."
        )
        self.add_info_card("⚠️", warning_title, warning_content, card_type="warning")
    
    def _add_max_file_size(self) -> None:
        """Maksimum dosya boyutu ayarını özel widget ile ekler."""
        label, desc = self._get_setting_info("max_file_size")
        container = self._create_row_frame(label, desc)
        
        # Değer container
        value_frame = ctk.CTkFrame(container, fg_color="transparent")
        value_frame.pack(side="right")
        
        # Entry
        size_var = tk.IntVar(value=self.current_settings.get("max_file_size", 10))
        
        entry = ctk.CTkEntry(
            value_frame, 
            textvariable=size_var, 
            width=80,
            justify="center",
            border_width=2,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            fg_color=("white", "gray22"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        entry.pack(side="left")
        
        # MB etiketi
        ctk.CTkLabel(
            value_frame, 
            text="MB", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK)
        ).pack(side="left", padx=(8, 0))
        
        def on_change(event=None):
            try:
                value = size_var.get()
                # Sınır kontrolü
                if AdvancedPanelConstants.MIN_FILE_SIZE_MB <= value <= AdvancedPanelConstants.MAX_FILE_SIZE_MB:
                    self.update_setting("max_file_size", value)
                    entry.configure(border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK))
                else:
                    entry.configure(border_color=("#e74c3c", "#e74c3c"))
            except tk.TclError:
                entry.configure(border_color=("#e74c3c", "#e74c3c"))
        
        entry.bind("<FocusOut>", on_change)
        entry.bind("<Return>", on_change)
        
        self._widget_cache["max_file_size"] = entry

    def _create_export_import_buttons(self) -> None:
        """Dışa/İçe aktarma butonlarını oluşturur."""
        export_text = self._get_localized("buttons.export", "📤 Dışa Aktar")
        import_text = self._get_localized("buttons.import", "📥 İçe Aktar")
        
        self.add_button_row([
            {
                "text": export_text,
                "command": self.settings_dialog.export_settings,
                "style": "primary"
            },
            {
                "text": import_text,
                "command": self.settings_dialog.import_settings,
                "style": "default"
            }
        ])
