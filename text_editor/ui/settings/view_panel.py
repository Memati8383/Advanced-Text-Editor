"""
Görünüm Ayarları Paneli
Arayüz görünürlük ve düzen ayarları.
"""

import customtkinter as ctk
from text_editor.ui.settings.base_panel import BaseSettingsPanel


class ViewSettingsPanel(BaseSettingsPanel):
    """Görünüm ayarları için panel."""
    
    def _setup_content(self):
        """Panel içeriğini oluşturur."""
        
        # ── Paneller Grubu ──
        self._add_section_header("📋 Paneller", "Arayüz panellerinin görünürlüğü")
        
        self.add_switch("show_status_bar")
        self.add_switch("show_file_explorer")
        self.add_switch("show_terminal")
        
        # ── Başlangıç Ayarları Grubu ──
        self._add_section_header("🚀 Başlangıç", "Uygulama açılış ayarları")
        
        self.add_switch("start_fullscreen")
        
        # ── Bilgi Kartı ──
        self.add_info_card(
            "💡",
            "İpucu",
            "Panel görünürlüğünü kısayollarla da kontrol edebilirsiniz:\n"
            "• Ctrl+B: Dosya Gezgini\n"
            "• Ctrl+`: Terminal\n"
            "• Ctrl+M: Minimap"
        )
