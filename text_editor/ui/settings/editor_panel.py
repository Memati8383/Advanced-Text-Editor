"""
Editör Ayarları Paneli
Kod düzenleme deneyimini özelleştirmek için ayarlar.
"""

import customtkinter as ctk
from text_editor.ui.settings.base_panel import BaseSettingsPanel


class EditorSettingsPanel(BaseSettingsPanel):
    """Editör ayarları için panel."""
    
    def _setup_content(self):
        """Panel içeriğini oluşturur."""
        
        # ── Görünüm Grubu ──
        self._add_section_header("👁️ Görünüm", "Editör görünüm ayarları")
        
        self.add_switch("show_line_numbers")
        self.add_switch("show_minimap")
        self.add_switch("highlight_current_line")
        self.add_switch("show_whitespace")
        
        # ── Düzenleme Grubu ──
        self._add_section_header("✏️ Düzenleme", "Metin düzenleme davranışları")
        
        self.add_switch("word_wrap")
        self.add_switch("auto_indent")
        self.add_combo("tab_size", ["2", "4", "8"], width=120, is_int=True)
        self.add_switch("bracket_matching")
        self.add_switch("syntax_highlighting")
        
        # ── Otomatik Kayıt Grubu ──
        self._add_section_header("💾 Otomatik Kayıt", "Kaydetme ve yedekleme ayarları")
        
        self.add_switch("auto_save")
        self.add_slider("auto_save_interval", 10, 120, steps=11)
    
    def _add_section_header(self, title: str, description: str = ""):
        """Bölüm başlığı ekler."""
        # Üst boşluk (ilk bölüm hariç)
        if len(self.winfo_children()) > 0:
            ctk.CTkFrame(self, height=16, fg_color="transparent").pack(fill="x")
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(8, 4))
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w")
        
        if description:
            ctk.CTkLabel(
                header_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray55")
            ).pack(anchor="w", pady=(2, 0))
        
        # İnce ayırıcı
        ctk.CTkFrame(
            self,
            height=1,
            fg_color=("gray80", "gray30")
        ).pack(fill="x", padx=10, pady=(6, 8))
