"""
Gelişmiş Ayarlar Paneli
Performans ve sistem ayarları.
"""

import tkinter as tk
import customtkinter as ctk
from text_editor.ui.settings.base_panel import BaseSettingsPanel


class AdvancedSettingsPanel(BaseSettingsPanel):
    """Gelişmiş ayarlar için panel."""
    
    def _setup_content(self):
        """Panel içeriğini oluşturur."""
        
        # ── Performans Grubu ──
        self._add_section_header("⚡ Performans", "Performans optimizasyon ayarları")
        
        self.add_switch("performance_mode")
        
        # ── Yedekleme Grubu ──
        self._add_section_header("💾 Yedekleme", "Otomatik yedekleme ayarları")
        
        self.add_switch("auto_backup")
        
        # Max dosya boyutu - Özel Entry
        self._add_max_file_size()
        
        # ── Hata Ayıklama Grubu ──
        self._add_section_header("🐛 Hata Ayıklama", "Hata raporlama ve günlük ayarları")
        
        self.add_switch("error_reporting")
        
        # Log seviyesi
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.add_combo("log_level", log_levels, width=150)
        
        # ── Veri Yönetimi Grubu ──
        self._add_section_header("📦 Veri Yönetimi", "Ayar dışa/içe aktarma")
        
        # İçe/Dışa Aktarma Butonları
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Dışa Aktar
        ctk.CTkButton(
            button_frame, 
            text=self.lang_manager.get("buttons.export"), 
            command=self.settings_dialog.export_settings,
            height=42, 
            corner_radius=10,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1f618d"),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", pady=(0, 8))
        
        # İçe Aktar
        ctk.CTkButton(
            button_frame, 
            text=self.lang_manager.get("buttons.import"), 
            command=self.settings_dialog.import_settings,
            height=42, 
            corner_radius=10, 
            fg_color=("gray75", "gray30"), 
            hover_color=("gray65", "gray40"),
            text_color=("gray20", "gray85"),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x")
        
        # ── Uyarı Kartı ──
        self.add_info_card(
            "⚠️",
            "Dikkat",
            "Performans modu etkinleştirildiğinde bazı görsel efektler "
            "(animasyonlar, gölgeler vb.) devre dışı bırakılır. "
            "Bu, düşük donanımlı sistemlerde daha akıcı bir deneyim sağlar."
        )
    
    def _add_max_file_size(self):
        """Maksimum dosya boyutu ayarı."""
        label, desc = self._get_setting_info("max_file_size")
        container = self._create_row_frame(label, desc)
        
        # MB etiketi
        ctk.CTkLabel(
            container, 
            text="MB", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray50", "gray55")
        ).pack(side="right", padx=(8, 0))
        
        # Değer girişi
        size_var = tk.IntVar(value=self.current_settings.get("max_file_size", 10))
        
        entry = ctk.CTkEntry(
            container, 
            textvariable=size_var, 
            width=80,
            justify="center",
            border_width=2,
            border_color=("gray75", "gray35"),
            fg_color=("white", "gray22"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        entry.pack(side="right")
        entry.bind("<FocusOut>", lambda e: self.update_setting("max_file_size", size_var.get()))
        entry.bind("<Return>", lambda e: self.update_setting("max_file_size", size_var.get()))
