"""
Terminal Ayarları Paneli
Entegre terminal yapılandırması.
"""

import os
import customtkinter as ctk
from text_editor.ui.settings.base_panel import BaseSettingsPanel


class TerminalSettingsPanel(BaseSettingsPanel):
    """Terminal ayarları için panel."""
    
    def _setup_content(self):
        """Panel içeriğini oluşturur."""
        
        # ── Kabuk Ayarları Grubu ──
        self._add_section_header("🐚 Kabuk", "Terminal kabuk (shell) ayarları")
        
        # İşletim sistemine göre kabuk listesi
        if os.name == "nt":
            shells = ["PowerShell", "Command Prompt", "Git Bash", "WSL"]
        else:
            shells = ["Bash", "Zsh", "Fish", "Sh"]
        
        self.add_combo("terminal_type", shells)
        
        # ── Görünüm Ayarları Grubu ──
        self._add_section_header("🎨 Görünüm", "Terminal görünüm ayarları")
        
        self.add_slider("terminal_font_size", 8, 24, steps=16)
        
        # ── Performans Ayarları Grubu ──
        self._add_section_header("⚡ Performans", "Terminal performans ayarları")
        
        self.add_slider("terminal_history", 100, 5000, steps=49)
        
        # ── Bilgi Kartı ──
        self.add_info_card(
            "⌨️",
            "Terminal Kısayolları",
            "• Ctrl+`: Terminal aç/kapat\n"
            "• Ctrl+Shift+C: Terminalde kopyala\n"
            "• Ctrl+Shift+V: Terminalde yapıştır\n"
            "• Yukarı/Aşağı Ok: Komut geçmişi"
        )
