"""
Editör Ayarları Paneli

Kod düzenleme deneyimini özelleştirmek için gelişmiş ayarlar.
BaseSettingsPanel'den kalıtım alarak optimize edilmiştir.

Özellikler:
    - Görünüm ayarları
    - Düzenleme davranışları
    - Otomatik kayıt
    - Otomatik tamamlama
    - Kod katlama
"""
from __future__ import annotations

from text_editor.ui.settings.base_panel import BaseSettingsPanel


class EditorSettingsPanel(BaseSettingsPanel):
    """
    Editör ayarları için panel.
    
    Kod düzenleme deneyimini özelleştiren tüm ayarları içerir.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini oluşturur."""
        
        # ── Görünüm Grubu ──
        view_title = self._get_localized("sections.editor_view", "👁️ Görünüm")
        view_desc = self._get_localized("sections.editor_view_desc", "Editör görünüm ayarları")
        self._add_section_header(view_title, view_desc)
        
        self.add_switch("show_line_numbers")
        self.add_switch("show_minimap")
        self.add_switch("highlight_current_line")
        self.add_switch("show_whitespace")
        
        # Indent guides (varsa)
        if "show_indent_guides" in self.current_settings:
            self.add_switch("show_indent_guides")
        
        # ── Düzenleme Grubu ──
        edit_title = self._get_localized("sections.editing", "✏️ Düzenleme")
        edit_desc = self._get_localized("sections.editing_desc", "Metin düzenleme davranışları")
        self._add_section_header(edit_title, edit_desc)
        
        self.add_switch("word_wrap")
        self.add_switch("auto_indent")
        self.add_segmented_control("tab_size", ["2", "4", "8"])
        self.add_switch("bracket_matching")
        self.add_switch("syntax_highlighting")
        
        # Akıllı özellikler (varsa)
        if "smart_quotes" in self.current_settings:
            self.add_switch("smart_quotes")
        
        if "auto_close_brackets" in self.current_settings:
            self.add_switch("auto_close_brackets")
        
        # ── Otomatik Tamamlama Grubu ──
        autocomplete_title = self._get_localized("sections.autocomplete", "🔮 Otomatik Tamamlama")
        autocomplete_desc = self._get_localized("sections.autocomplete_desc", "Kod tamamlama ayarları")
        self._add_section_header(autocomplete_title, autocomplete_desc)
        
        if "enable_autocomplete" in self.current_settings:
            self.add_switch("enable_autocomplete")
        else:
            # Varsayılan olarak göster
            self.add_switch("autocomplete_enabled")
        
        if "autocomplete_delay" in self.current_settings:
            self.add_slider("autocomplete_delay", 0, 1000, steps=10, unit="ms")
        
        if "suggest_on_trigger_characters" in self.current_settings:
            self.add_switch("suggest_on_trigger_characters")
        
        # ── Kod Katlama Grubu (varsa) ──
        if "enable_code_folding" in self.current_settings or "fold_regions_by_default" in self.current_settings:
            folding_title = self._get_localized("sections.code_folding", "📑 Kod Katlama")
            folding_desc = self._get_localized("sections.code_folding_desc", "Kod bölümlerini katlama ayarları")
            self._add_section_header(folding_title, folding_desc)
            
            if "enable_code_folding" in self.current_settings:
                self.add_switch("enable_code_folding")
            
            if "fold_imports" in self.current_settings:
                self.add_switch("fold_imports")
        
        # ── Otomatik Kayıt Grubu ──
        save_title = self._get_localized("sections.auto_save", "💾 Otomatik Kayıt")
        save_desc = self._get_localized("sections.auto_save_desc", "Kaydetme ve yedekleme ayarları")
        self._add_section_header(save_title, save_desc)
        
        self.add_switch("auto_save")
        self.add_slider("auto_save_interval", 10, 120, steps=11, unit="sn")
        
        if "format_on_save" in self.current_settings:
            self.add_switch("format_on_save")
        
        if "trim_trailing_whitespace" in self.current_settings:
            self.add_switch("trim_trailing_whitespace")
        
        # ── Bilgi Kartı ──
        tip_title = self._get_localized("tips.editor_tip_title", "Verimlilik İpucu")
        tip_content = self._get_localized(
            "tips.editor_tip_content",
            "Kod yazarken verimliliği artırmak için:\n"
            "• Ctrl+D: Satırı çoğalt\n"
            "• Ctrl+/: Satırı yorum yap\n"
            "• Alt+↑↓: Satırı taşı\n"
            "• Ctrl+Shift+K: Satırı sil"
        )
        self.add_info_card("⚡", tip_title, tip_content)
