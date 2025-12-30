"""
Terminal Ayarları Paneli

Entegre terminal yapılandırması.
Optimize edilmiş ve localizable yapı.

Özellikler:
    - Kabuk seçimi (OS'a göre)
    - Görünüm ayarları
    - Performans ayarları
    - Cursor ayarları
    - Font ailesi ve boyutu
"""
from __future__ import annotations

import os
from tkinter import font as tkfont
from text_editor.ui.settings.base_panel import BaseSettingsPanel


class TerminalSettingsPanel(BaseSettingsPanel):
    """
    Terminal ayarları için panel.
    
    Entegre terminalin tüm yapılandırma seçeneklerini sunar.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini oluşturur."""
        
        # ── Kabuk Ayarları Grubu ──
        shell_title = self._get_localized("sections.shell", "🐚 Kabuk")
        shell_desc = self._get_localized("sections.shell_desc", "Terminal kabuk (shell) ayarları")
        self._add_section_header(shell_title, shell_desc)
        
        # İşletim sistemine göre kabuk listesi
        shells = self._get_available_shells()
        self.add_combo("terminal_type", shells)
        
        # Başlangıç dizini (varsa)
        if "terminal_start_directory" in self.current_settings:
            self.add_file_picker(
                "terminal_start_directory",
                mode="directory"
            )
        
        # ── Görünüm Ayarları Grubu ──
        appearance_title = self._get_localized("sections.terminal_appearance", "🎨 Görünüm")
        appearance_desc = self._get_localized("sections.terminal_appearance_desc", "Terminal görünüm ayarları")
        self._add_section_header(appearance_title, appearance_desc)
        
        # Font ailesi
        if "terminal_font_family" in self.current_settings:
            monospace_fonts = self._get_monospace_fonts()
            self.add_combo("terminal_font_family", monospace_fonts)
        
        self.add_slider("terminal_font_size", 8, 24, steps=16, unit="pt")
        
        # ── Cursor Ayarları Grubu ──
        cursor_title = self._get_localized("sections.terminal_cursor", "▌ Cursor")
        cursor_desc = self._get_localized("sections.terminal_cursor_desc", "İmleç görünüm ayarları")
        self._add_section_header(cursor_title, cursor_desc)
        
        # Cursor stili (varsa)
        if "terminal_cursor_style" in self.current_settings:
            cursor_styles = [
                {"value": "block", "label": "█ Blok"},
                {"value": "underline", "label": "_ Alt Çizgi"},
                {"value": "bar", "label": "| Çubuk"}
            ]
            self.add_radio_group("terminal_cursor_style", cursor_styles)
        
        # Cursor yanıp sönme (varsa)
        if "terminal_cursor_blink" in self.current_settings:
            self.add_switch("terminal_cursor_blink")
        
        # ── Performans Ayarları Grubu ──
        performance_title = self._get_localized("sections.terminal_performance", "⚡ Performans")
        performance_desc = self._get_localized("sections.terminal_performance_desc", "Terminal performans ayarları")
        self._add_section_header(performance_title, performance_desc)
        
        self.add_slider("terminal_history", 100, 5000, steps=49)
        
        # Scrollback buffer (varsa)
        if "terminal_scrollback" in self.current_settings:
            self.add_slider("terminal_scrollback", 1000, 50000, steps=49, unit="satır")
        
        # ── Ses Ayarları Grubu (varsa) ──
        if "terminal_bell" in self.current_settings or "terminal_bell_style" in self.current_settings:
            sound_title = self._get_localized("sections.terminal_sound", "🔔 Ses")
            sound_desc = self._get_localized("sections.terminal_sound_desc", "Terminal ses ayarları")
            self._add_section_header(sound_title, sound_desc)
            
            if "terminal_bell" in self.current_settings:
                self.add_switch("terminal_bell")
            
            if "terminal_bell_style" in self.current_settings:
                bell_styles = ["sound", "visual", "both", "none"]
                self.add_segmented_control("terminal_bell_style", bell_styles)
        
        # ── Entegrasyon Ayarları Grubu (varsa) ──
        if "terminal_copy_on_select" in self.current_settings or "terminal_right_click_paste" in self.current_settings:
            integration_title = self._get_localized("sections.terminal_integration", "🔗 Entegrasyon")
            integration_desc = self._get_localized("sections.terminal_integration_desc", "Pano ve kısayol entegrasyonları")
            self._add_section_header(integration_title, integration_desc)
            
            if "terminal_copy_on_select" in self.current_settings:
                self.add_switch("terminal_copy_on_select")
            
            if "terminal_right_click_paste" in self.current_settings:
                self.add_switch("terminal_right_click_paste")
        
        # ── Bilgi Kartı ──
        tips_title = self._get_localized("tips.terminal_shortcuts_title", "Terminal Kısayolları")
        tips_content = self._get_localized(
            "tips.terminal_shortcuts",
            "• Ctrl+`: Terminal aç/kapat\n"
            "• Ctrl+Shift+C: Terminalde kopyala\n"
            "• Ctrl+Shift+V: Terminalde yapıştır\n"
            "• Yukarı/Aşağı Ok: Komut geçmişi"
        )
        self.add_info_card("⌨️", tips_title, tips_content)

    def _get_available_shells(self) -> list:
        """
        İşletim sistemine göre mevcut kabukları döndürür.
        
        Returns:
            list: Kullanılabilir kabuk listesi
        """
        if os.name == "nt":
            # Windows
            return ["PowerShell", "Command Prompt", "Git Bash", "WSL"]
        else:
            # Unix-like (Linux, macOS)
            return ["Bash", "Zsh", "Fish", "Sh"]

    def _get_monospace_fonts(self) -> list:
        """
        Sistemdeki monospace fontları listeler.
        
        Returns:
            list: Monospace font listesi
        """
        try:
            all_fonts = list(tkfont.families())
            preferred = [
                "Consolas", "Fira Code", "JetBrains Mono", "Cascadia Code",
                "Cascadia Mono", "Source Code Pro", "Menlo", "Monaco",
                "Courier New", "DejaVu Sans Mono", "Ubuntu Mono",
                "Roboto Mono", "Inconsolata", "Hack"
            ]
            available_preferred = [f for f in preferred if f in all_fonts]
            return available_preferred if available_preferred else ["Consolas", "Courier New"]
        except Exception:
            return ["Consolas", "Courier New"]
