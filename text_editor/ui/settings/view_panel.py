"""
Görünüm Ayarları Paneli

Arayüz görünürlük ve düzen ayarları.
Optimize edilmiş ve localizable yapı.

Özellikler:
    - Panel görünürlük ayarları
    - Başlangıç ayarları
    - Opaklık ve boyut ayarları
    - Bilgi kartları
    - Animasyon ayarları
    - Tab bar görünümü
"""
from __future__ import annotations

from text_editor.ui.settings.base_panel import BaseSettingsPanel


class ViewSettingsPanel(BaseSettingsPanel):
    """
    Görünüm ayarları için panel.
    
    Arayüz panellerinin görünürlüğünü ve düzenini kontrol eder.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini oluşturur."""
        
        # ── Paneller Grubu ──
        panels_title = self._get_localized("sections.panels", "📋 Paneller")
        panels_desc = self._get_localized("sections.panels_desc", "Arayüz panellerinin görünürlüğü")
        self._add_section_header(panels_title, panels_desc)
        
        self.add_switch("show_status_bar")
        self.add_switch("show_file_explorer")
        self.add_switch("show_terminal")
        
        # Ek paneller (varsa)
        if "show_outline" in self.current_settings:
            self.add_switch("show_outline")
        
        if "show_breadcrumbs" in self.current_settings:
            self.add_switch("show_breadcrumbs")
        
        # ── Tab Bar Görünümü (varsa) ──
        if "tab_bar_position" in self.current_settings or "show_tab_icons" in self.current_settings:
            tab_title = self._get_localized("sections.tab_bar", "📑 Sekme Çubuğu")
            tab_desc = self._get_localized("sections.tab_bar_desc", "Sekme çubuğu görünüm ayarları")
            self._add_section_header(tab_title, tab_desc)
            
            if "tab_bar_position" in self.current_settings:
                tab_positions = ["top", "bottom"]
                self.add_segmented_control("tab_bar_position", tab_positions)
            
            if "show_tab_icons" in self.current_settings:
                self.add_switch("show_tab_icons")
            
            if "tab_close_button" in self.current_settings:
                self.add_switch("tab_close_button")
        
        # ── Düzen Grubu ──
        layout_title = self._get_localized("sections.layout", "📐 Düzen")
        layout_desc = self._get_localized("sections.layout_desc", "Pencere ve panel boyutları")
        self._add_section_header(layout_title, layout_desc)
        
        # Pencere opaklığı (varsa)
        if "window_opacity" in self.current_settings:
            self.add_slider("window_opacity", 50, 100, steps=10, unit="%")
        
        # Kenar çubuğu genişliği (varsa)
        if "sidebar_width" in self.current_settings:
            self.add_slider("sidebar_width", 180, 400, steps=22, unit="px")
        
        # Panel konumu (varsa)
        if "sidebar_position" in self.current_settings:
            positions = [
                {"value": "left", "label": "⬅️ Sol"},
                {"value": "right", "label": "➡️ Sağ"}
            ]
            self.add_radio_group("sidebar_position", positions)
        
        # ── Animasyon Ayarları (varsa) ──
        if "enable_animations" in self.current_settings or "animation_speed" in self.current_settings:
            anim_title = self._get_localized("sections.animations", "✨ Animasyonlar")
            anim_desc = self._get_localized("sections.animations_desc", "Arayüz animasyon ayarları")
            self._add_section_header(anim_title, anim_desc)
            
            if "enable_animations" in self.current_settings:
                self.add_switch("enable_animations")
            
            if "animation_speed" in self.current_settings:
                speeds = ["slow", "normal", "fast"]
                self.add_segmented_control("animation_speed", speeds)
            
            if "smooth_scrolling" in self.current_settings:
                self.add_switch("smooth_scrolling")
        
        # ── Başlangıç Ayarları Grubu ──
        startup_title = self._get_localized("sections.startup", "🚀 Başlangıç")
        startup_desc = self._get_localized("sections.startup_desc", "Uygulama açılış ayarları")
        self._add_section_header(startup_title, startup_desc)
        
        self.add_switch("start_fullscreen")
        
        if "restore_last_session" in self.current_settings:
            self.add_switch("restore_last_session")
        
        if "show_welcome_page" in self.current_settings:
            self.add_switch("show_welcome_page")
        
        # ── Erişilebilirlik Ayarları (varsa) ──
        if "high_contrast" in self.current_settings or "reduce_motion" in self.current_settings:
            access_title = self._get_localized("sections.accessibility", "♿ Erişilebilirlik")
            access_desc = self._get_localized("sections.accessibility_desc", "Erişilebilirlik tercihleri")
            self._add_section_header(access_title, access_desc)
            
            if "high_contrast" in self.current_settings:
                self.add_switch("high_contrast")
            
            if "reduce_motion" in self.current_settings:
                self.add_switch("reduce_motion")
            
            if "ui_scale" in self.current_settings:
                self.add_slider("ui_scale", 80, 150, steps=7, unit="%")
        
        # ── Bilgi Kartı ──
        tip_title = self._get_localized("tips.shortcut_tip_title", "İpucu")
        tip_content = self._get_localized(
            "tips.view_shortcuts",
            "Panel görünürlüğünü kısayollarla da kontrol edebilirsiniz:\n"
            "• Ctrl+B: Dosya Gezgini\n"
            "• Ctrl+`: Terminal\n"
            "• Ctrl+M: Minimap"
        )
        self.add_info_card("💡", tip_title, tip_content)
