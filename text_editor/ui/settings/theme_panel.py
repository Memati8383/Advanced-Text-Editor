"""
Theme Settings Panel (Tema Ayarları Paneli)

Kullanıcının uygulama temasını seçmesini ve önizlemesini sağlar.
Clean Code prensiplerine uygun olarak optimize edilmiştir.
Özellikler:
    - Anlık UI tepkisi (Optimistic UI)
    - Debounce edilmiş tema uygulama işlemi (Performans)
    - Tip güvenli ve modüler kod yapısı
"""
from __future__ import annotations

import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Final, Optional, Union, Tuple

from text_editor.ui.settings.base_panel import BaseSettingsPanel
from text_editor.theme_config import get_available_themes, get_theme

class ThemePanelConstants:
    """Panel ile ilgili sabitler."""
    GRID_COLUMNS: Final[int] = 3
    CARD_CORNER_RADIUS: Final[int] = 12
    PREVIEW_HEIGHT: Final[int] = 90
    BORDER_WIDTH_SELECTED: Final[int] = 3
    BORDER_WIDTH_NORMAL: Final[int] = 1
    APPLY_DEBOUNCE_MS: Final[int] = 300
    
    # Varsayılan Renkler
    BORDER_DARK: Final[str] = "gray40"
    BORDER_LIGHT: Final[str] = "gray60"
    DEFAULT_ACCENT: Final[str] = "#0098ff"

class ThemeSettingsPanel(BaseSettingsPanel):
    """
    Tema seçim ve önizleme paneli.
    """
    
    def _setup_content(self) -> None:
        """Panel içeriğini ve durumunu başlatır."""
        # State Initialization
        self._card_widgets: Dict[str, Dict[str, Any]] = {}
        self._theme_apply_job: Optional[str] = None
        
        current_theme = self.current_settings.get("theme", "Dark")
        self._current_theme_name: str = current_theme
        
        self.theme_var = tk.StringVar(value=current_theme)
        
        # UI Oluşturma
        self._create_header()
        self._create_theme_grid()

    def _create_header(self) -> None:
        """Başlık ve açıklama alanını oluşturur."""
        label, desc = self._get_setting_info("theme_select")
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15), padx=10)
        
        ctk.CTkLabel(
            header, 
            text=label, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header, 
            text=desc, 
            font=ctk.CTkFont(size=12), 
            text_color="gray60", 
            anchor="w"
        ).pack(anchor="w")

    def _create_theme_grid(self) -> None:
        """Tema kartlarının bulunduğu ızgarayı oluşturur."""
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10)
        
        # Kolon ağırlıkları
        for i in range(ThemePanelConstants.GRID_COLUMNS):
            grid.grid_columnconfigure(i, weight=1)
        
        themes = get_available_themes()
        for i, theme_name in enumerate(themes):
            self._create_theme_card(grid, theme_name, i)

    def _create_theme_card(self, parent: ctk.CTkFrame, theme_name: str, index: int) -> None:
        """
        Tek bir tema kartı oluşturur.
        
        Args:
            parent: Ebeveyn frame
            theme_name: Tema adı
            index: Grid pozisyonu için indeks
        """
        theme_data = get_theme(theme_name)
        is_selected = (theme_name == self._current_theme_name)
        
        border_color = self._get_border_color(theme_data, is_selected)
        border_width = ThemePanelConstants.BORDER_WIDTH_SELECTED if is_selected else ThemePanelConstants.BORDER_WIDTH_NORMAL
        
        # Kart Frame
        card = ctk.CTkFrame(
            parent, 
            fg_color=theme_data.get("bg", "#2b2b2b"), 
            corner_radius=ThemePanelConstants.CARD_CORNER_RADIUS,
            border_width=border_width,
            border_color=border_color,
            cursor="hand2"
        )
        
        # Grid Yerleşimi
        row = index // ThemePanelConstants.GRID_COLUMNS
        col = index % ThemePanelConstants.GRID_COLUMNS
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Tıklama Event'i
        self._bind_click_event(card, theme_name)
        
        # İçerik
        self._create_card_preview(card, theme_data, theme_name)
        check_icon = self._create_card_footer(card, theme_data, theme_name, is_selected)
        
        # Widget referanslarını sakla
        self._card_widgets[theme_name] = {
            "card": card,
            "check_icon": check_icon
        }

    def _create_card_preview(self, parent: ctk.CTkFrame, data: Dict[str, Any], theme_name: str) -> None:
        """Kart üzerindeki kod önizleme alanını oluşturur."""
        preview = ctk.CTkFrame(
            parent, 
            fg_color="transparent", 
            height=ThemePanelConstants.PREVIEW_HEIGHT
        )
        preview.pack(fill="x", padx=10, pady=10)
        preview.pack_propagate(False)
        self._bind_click_event(preview, theme_name)
        
        code_view = ctk.CTkFrame(
            preview, 
            fg_color=data.get("editor_bg", "#1e1e1e"), 
            corner_radius=6
        )
        code_view.pack(fill="both", expand=True)
        self._bind_click_event(code_view, theme_name)
        
        # Kod Örnekleri
        def_text = f"def {theme_name.lower()}():"
        self._create_code_line(code_view, def_text, data.get("fg", "white"), (8, 0), theme_name)
        self._create_code_line(code_view, '    return "UI"', data.get("string", "#f1fa8c"), (2, 8), theme_name)

    def _create_code_line(
        self, 
        parent: ctk.CTkFrame, 
        text: str, 
        color: str, 
        pady: Tuple[int, int],
        theme_name: str
    ) -> None:
        """Tek bir kod satırı oluşturur."""
        label = ctk.CTkLabel(
            parent, 
            text=text, 
            text_color=color,
            font=("Consolas", 10), 
            anchor="w"
        )
        label.pack(padx=8, pady=pady, fill="x")
        self._bind_click_event(label, theme_name)

    def _create_card_footer(
        self, 
        parent: ctk.CTkFrame, 
        data: Dict[str, Any], 
        theme_name: str, 
        is_selected: bool
    ) -> ctk.CTkLabel:
        """Kartın alt kısmını (isim ve ikon) oluşturur."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=(0, 12))
        self._bind_click_event(footer, theme_name)
        
        # Tema Adı
        name_label = ctk.CTkLabel(
            footer, 
            text=theme_name, 
            font=ctk.CTkFont(weight="bold"), 
            text_color=data.get("fg", "white")
        )
        name_label.pack(side="left")
        self._bind_click_event(name_label, theme_name)
        
        # Onay İkonu
        icon_text = "✅" if is_selected else ""
        icon_color = data.get("accent_color", ThemePanelConstants.DEFAULT_ACCENT)
        
        icon_label = ctk.CTkLabel(
            footer, 
            text=icon_text, 
            text_color=icon_color
        )
        icon_label.pack(side="right")
        self._bind_click_event(icon_label, theme_name)
        
        return icon_label

    def _bind_click_event(self, widget: ctk.CTkBaseClass, theme_name: str) -> None:
        """Widget'a tıklama event'i bağlar."""
        widget.bind("<Button-1>", lambda e: self._on_theme_clicked(theme_name))

    def _get_border_color(self, theme_data: Dict[str, Any], is_selected: bool) -> str:
        """Kart kenarlık rengini belirler."""
        if is_selected:
            return theme_data.get("accent_color", ThemePanelConstants.DEFAULT_ACCENT)
        
        theme_type = theme_data.get("type", "Dark")
        return ThemePanelConstants.BORDER_DARK if theme_type == "Dark" else ThemePanelConstants.BORDER_LIGHT

    def _on_theme_clicked(self, theme_name: str) -> None:
        """Tema seçildiğinde çalışır (Optimistic UI & Debounce)."""
        if self._current_theme_name == theme_name:
            return
            
        # 1. UI Güncelle (Hemen - Optimistic UI)
        self._update_cards_visuals(self._current_theme_name, theme_name)
        self._current_theme_name = theme_name
        self.theme_var.set(theme_name)
        
        # 2. Ayarı Kaydet
        self.update_setting("theme", theme_name)
        
        # 3. Temayı Uygula (Gecikmeli - Performans)
        if hasattr(self, '_theme_apply_job') and self._theme_apply_job:
            self.after_cancel(self._theme_apply_job)
            
        # Zaten SettingsDialog içinde değişiklik badge'i güncelleniyor, 
        # asıl ağır işlem olan tema uygulamasını geciktiriyoruz.
        self._theme_apply_job = self.after(
            ThemePanelConstants.APPLY_DEBOUNCE_MS, 
            lambda: self._apply_theme_to_app(theme_name)
        )

    def _update_cards_visuals(self, old_theme: str, new_theme: str) -> None:
        """Sadece etkilenen kartların görünümünü günceller."""
        # Eski kartı pasif yap
        if old_theme in self._card_widgets:
            widgets = self._card_widgets[old_theme]
            theme_data = get_theme(old_theme)
            
            widgets["card"].configure(
                border_width=ThemePanelConstants.BORDER_WIDTH_NORMAL, 
                border_color=self._get_border_color(theme_data, False)
            )
            widgets["check_icon"].configure(text="")
            
        # Yeni kartı aktif yap
        if new_theme in self._card_widgets:
            widgets = self._card_widgets[new_theme]
            theme_data = get_theme(new_theme)
            accent = theme_data.get("accent_color", ThemePanelConstants.DEFAULT_ACCENT)
            
            widgets["card"].configure(
                border_width=ThemePanelConstants.BORDER_WIDTH_SELECTED, 
                border_color=accent
            )
            widgets["check_icon"].configure(text="✅", text_color=accent)

    def _apply_theme_to_app(self, theme_name: str) -> None:
        """Temayı tüm uygulamaya uygular."""
        if hasattr(self.settings_dialog.parent, 'apply_theme'):
             self.settings_dialog.parent.apply_theme(theme_name)
