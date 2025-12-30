"""
Klavye Kısayolları Paneli

Kullanıcının klavye kısayollarını özelleştirmesini sağlar.
Optimize edilmiş ve localizable yapı.

Özellikler:
    - Kısayol gruplandırma
    - Canlı kısayol atama
    - Varsayılana döndürme
    - Çakışma kontrolü
"""
from __future__ import annotations

import customtkinter as ctk
from typing import Dict, List, Tuple, Optional, Final, Any

from text_editor.ui.settings.base_panel import BaseSettingsPanel, PanelConstants
from text_editor.utils.shortcut_manager import ShortcutManager


class ShortcutsPanelConstants:
    """Panel sabitleri."""
    SHORTCUT_BUTTON_WIDTH: Final[int] = 140
    SHORTCUT_BUTTON_HEIGHT: Final[int] = 32
    DIALOG_WIDTH: Final[int] = 440
    DIALOG_HEIGHT: Final[int] = 280
    KEY_DISPLAY_FONT: Final[Tuple[str, int, str]] = ("Consolas", 12, "bold")
    KEY_RECORDING_FONT: Final[Tuple[str, int, str]] = ("Consolas", 24, "bold")


class ShortcutsSettingsPanel(BaseSettingsPanel):
    """
    Klavye kısayolları ayarları için panel.
    
    Tüm kısayolları kategorize ederek gösterir ve
    özelleştirme imkanı sunar.
    """
    
    def _setup_content(self) -> None:
        """Klavye kısayolları panelini oluşturur."""
        manager = ShortcutManager.get_instance()
        shortcuts = manager.shortcuts
        
        # Arama alanı
        self._create_search_box()
        
        # Kısayolları kategorilere göre grupla
        grouped = self._group_shortcuts(shortcuts, manager)
        
        # Her kategori için bölüm oluştur
        for category, items in grouped.items():
            self._create_category_section(category, items)
        
        # Buton satırı
        self._create_action_buttons()

    def _group_shortcuts(
        self, 
        shortcuts: Dict[str, str], 
        manager: ShortcutManager
    ) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Kısayolları kategorilere göre gruplar.
        
        Args:
            shortcuts: Kısayol sözlüğü
            manager: ShortcutManager instance
            
        Returns:
            Dict[str, List[Tuple]]: Kategorize edilmiş kısayollar
        """
        grouped: Dict[str, List[Tuple[str, str, str]]] = {}
        
        for action_id, sequence in shortcuts.items():
            meta = manager.get_localized_metadata(action_id)
            category = meta["category"]
            label = meta["label"]
            
            if category not in grouped:
                grouped[category] = []
            grouped[category].append((action_id, label, sequence))
        
        return grouped

    def _create_category_section(
        self, 
        category: str, 
        items: List[Tuple[str, str, str]]
    ) -> None:
        """
        Bir kategori bölümü oluşturur.
        
        Args:
            category: Kategori adı
            items: (action_id, label, sequence) tuple listesi
        """
        # Kategori başlığı
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=(16, 6))
        
        ctk.CTkLabel(
            header_frame, 
            text=category, 
            font=ctk.CTkFont(size=PanelConstants.HEADER_FONT_SIZE, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w")
        
        # Ayırıcı
        ctk.CTkFrame(
            self, 
            height=1, 
            fg_color=("gray80", "gray30")
        ).pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=(0, 8))
        
        # Kısayol satırları
        for action_id, label, sequence in items:
            self._create_shortcut_row(action_id, label, sequence)

    def _create_shortcut_row(
        self, 
        action_id: str, 
        label: str, 
        sequence: str
    ) -> None:
        """
        Tek bir kısayol satırı oluşturur.
        
        Args:
            action_id: Aksiyon kimliği
            label: Görünen etiket
            sequence: Mevcut kısayol dizisi
        """
        manager = ShortcutManager.get_instance()
        
        # Satır frame - arka plan ile
        frame = ctk.CTkFrame(
            self, 
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK),
            corner_radius=8
        )
        frame.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=3)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        
        # Sol taraf - Etiket
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.grid(row=0, column=0, sticky="nsew", padx=(14, 10), pady=10)
        
        ctk.CTkLabel(
            label_frame, 
            text=label, 
            font=ctk.CTkFont(size=13),
            text_color=("gray15", "gray85"),
            anchor="w"
        ).pack(side="left")
        
        # Sağ taraf container
        right_frame = ctk.CTkFrame(frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=8)
        
        # Kısayol butonu
        display = manager.get_display_string(sequence) or self._get_localized("status.none", "Yok")
        
        btn = ctk.CTkButton(
            right_frame, 
            text=display, 
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=("gray88", "gray18"),
            text_color=("gray15", "gray90"),
            width=ShortcutsPanelConstants.SHORTCUT_BUTTON_WIDTH, 
            height=ShortcutsPanelConstants.SHORTCUT_BUTTON_HEIGHT, 
            border_width=1, 
            border_color=("gray70", "gray40"),
            hover_color=("gray80", "gray28"),
            corner_radius=6,
            command=lambda aid=action_id: self._start_shortcut_recording(aid)
        )
        btn.pack(side="left")
        
        # Temizle butonu
        clear_btn = ctk.CTkButton(
            right_frame,
            text="✕",
            width=30,
            height=ShortcutsPanelConstants.SHORTCUT_BUTTON_HEIGHT,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("#fee2e2", "#5c0000"),
            text_color=("gray50", "gray55"),
            border_width=1,
            border_color=("gray75", "gray40"),
            font=ctk.CTkFont(size=11),
            command=lambda aid=action_id: self._clear_shortcut(aid)
        )
        clear_btn.pack(side="left", padx=(6, 0))
        
        # Widget cache'e ekle (güncelleme için)
        self._widget_cache[f"shortcut_{action_id}"] = btn
        self._widget_cache[f"shortcut_row_{action_id}"] = frame

    def _create_search_box(self) -> None:
        """Arama alanı oluşturur."""
        import tkinter as tk
        
        search_frame = ctk.CTkFrame(
            self,
            fg_color=(PanelConstants.ROW_BG_LIGHT, PanelConstants.ROW_BG_DARK),
            corner_radius=PanelConstants.ROW_CORNER_RADIUS
        )
        search_frame.pack(fill="x", pady=(8, 12), padx=PanelConstants.ROW_PADDING_X)
        
        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        
        # Arama ikonu
        ctk.CTkLabel(
            inner,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color=("gray50", "gray55")
        ).pack(side="left", padx=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            inner,
            textvariable=search_var,
            placeholder_text=self._get_localized("placeholders.search_shortcuts", "Kısayol ara..."),
            height=34,
            border_width=1,
            border_color=(PanelConstants.BORDER_LIGHT, PanelConstants.BORDER_DARK),
            fg_color=("white", "gray22"),
            font=ctk.CTkFont(size=13)
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Temizle butonu (arama varken görünür)
        clear_search_btn = ctk.CTkButton(
            inner,
            text="✕",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=("gray85", "gray30"),
            text_color=("gray50", "gray55"),
            font=ctk.CTkFont(size=12),
            command=lambda: search_var.set("")
        )
        
        def on_search(*args):
            query = search_var.get().lower()
            
            # Temizle butonunu göster/gizle
            if query:
                clear_search_btn.pack(side="left", padx=(8, 0))
            else:
                clear_search_btn.pack_forget()
            
            for key, widget in self._widget_cache.items():
                if key.startswith("shortcut_row_"):
                    action_id = key.replace("shortcut_row_", "")
                    manager = ShortcutManager.get_instance()
                    meta = manager.get_localized_metadata(action_id)
                    label = meta.get("label", "").lower()
                    
                    if query in label or query in action_id.lower() or not query:
                        widget.pack(fill="x", padx=PanelConstants.ROW_PADDING_X, pady=3)
                    else:
                        widget.pack_forget()
        
        search_var.trace_add("write", on_search)
        self._widget_cache["search_entry"] = search_entry

    def _create_action_buttons(self) -> None:
        """Aksiyon butonlarını oluşturur."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", pady=20, padx=PanelConstants.ROW_PADDING_X)
        
        # Sıfırlama Butonu
        reset_text = self._get_localized("buttons.reset_shortcuts", "Kısayolları Sıfırla")
        
        ctk.CTkButton(
            button_frame, 
            text=reset_text, 
            fg_color="transparent",
            border_width=1, 
            border_color="#dc3545", 
            text_color="#dc3545",
            hover_color=("#fee2e2", "#5c0000"), 
            width=180,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._reset_shortcuts
        ).pack(side="right")
        
        # Bilgi metni
        ctk.CTkLabel(
            button_frame,
            text=self._get_localized("hints.click_to_change", "Değiştirmek için kısayola tıklayın"),
            font=ctk.CTkFont(size=11),
            text_color=(PanelConstants.TEXT_MUTED_LIGHT, PanelConstants.TEXT_MUTED_DARK)
        ).pack(side="left")

    def _clear_shortcut(self, action_id: str) -> None:
        """Kısayolu temizler."""
        manager = ShortcutManager.get_instance()
        manager.set(action_id, "")
        
        # UI'ı güncelle
        btn = self._widget_cache.get(f"shortcut_{action_id}")
        if btn:
            btn.configure(text=self._get_localized("status.none", "Yok"))

    def _start_shortcut_recording(self, action_id: str) -> None:
        """
        Kısayol atama diyaloğunu açar.
        
        Args:
            action_id: Ayarlanacak aksiyonun kimliği
        """
        manager = ShortcutManager.get_instance()
        current_seq = manager.get(action_id)
        
        # Diyalog oluştur
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title(self._get_localized("dialogs.assign_shortcut", "Kısayol Ata"))
        dialog.geometry(
            f"{ShortcutsPanelConstants.DIALOG_WIDTH}x{ShortcutsPanelConstants.DIALOG_HEIGHT}"
        )
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Ortalama
        self._center_dialog(dialog)
        
        # İçerik
        self._create_dialog_content(dialog, manager, action_id, current_seq)

    def _center_dialog(self, dialog: ctk.CTkToplevel) -> None:
        """Diyaloğu ana pencereye göre ortalar."""
        dialog.update_idletasks()
        
        try:
            parent = self.winfo_toplevel()
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (ShortcutsPanelConstants.DIALOG_WIDTH // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (ShortcutsPanelConstants.DIALOG_HEIGHT // 2)
        except Exception:
            x, y = 100, 100
            
        dialog.geometry(f"+{x}+{y}")

    def _create_dialog_content(
        self, 
        dialog: ctk.CTkToplevel, 
        manager: ShortcutManager,
        action_id: str,
        current_seq: str
    ) -> None:
        """
        Diyalog içeriğini oluşturur.
        
        Args:
            dialog: Diyalog penceresi
            manager: ShortcutManager instance
            action_id: Aksiyon kimliği
            current_seq: Mevcut kısayol
        """
        # Başlık
        ctk.CTkLabel(
            dialog, 
            text=self._get_localized("dialogs.press_new_shortcut", "Yeni Kısayol Tuşlayın"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(24, 8))
        
        # İpucu
        ctk.CTkLabel(
            dialog, 
            text=self._get_localized("dialogs.press_escape", "İptal için ESC"), 
            text_color="gray"
        ).pack()
        
        # Kısayol gösterge alanı
        display_lbl = ctk.CTkLabel(
            dialog, 
            text=manager.get_display_string(current_seq),
            font=ShortcutsPanelConstants.KEY_RECORDING_FONT,
            width=220, 
            height=60,
            fg_color=("gray90", "gray20"), 
            corner_radius=10
        )
        display_lbl.pack(pady=24)
        
        # Durum değişkenleri
        recorded_sequence = {"value": None}
        
        # Buton frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=24, pady=(0, 20))
        
        # Kaydet butonu (başlangıçta disabled)
        save_btn = ctk.CTkButton(
            button_frame, 
            text=self._get_localized("buttons.save", "Kaydet"), 
            state="disabled",
            width=120,
            height=38,
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#1e8449"),
            font=ctk.CTkFont(weight="bold")
        )
        save_btn.pack(side="left", expand=True, padx=8)
        
        # İptal butonu
        ctk.CTkButton(
            button_frame, 
            text=self._get_localized("buttons.cancel", "İptal"),
            command=dialog.destroy,
            width=120,
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray40"),
            text_color=("gray30", "gray70"),
            hover_color=("gray90", "gray25")
        ).pack(side="right", expand=True, padx=8)
        
        def on_key(event) -> None:
            """Tuş basımını işler."""
            # Modifier'ları topla
            keys = []
            if event.state & 0x4:
                keys.append("Control")
            if event.state & 0x20000 or event.state & 0x20:
                keys.append("Alt")
            if event.state & 0x1:
                keys.append("Shift")
            
            # Ana tuşu ekle
            if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
                if event.keysym == "Escape":
                    dialog.destroy()
                    return
                keys.append(event.keysym)
            
            # Sadece modifier varsa bekle
            if not keys or (len(keys) == 1 and keys[0] in ("Control", "Alt", "Shift")):
                display_lbl.configure(text=" + ".join(keys) + " ...")
                return
            
            # Sequence oluştur
            parts = [k for k in ["Control", "Alt", "Shift"] if k in keys]
            if keys[-1] not in parts:
                parts.append(keys[-1])
            
            sequence = f"<{'-'.join(parts)}>"
            display_lbl.configure(text=manager.get_display_string(sequence))
            
            # Kaydet butonunu aktif et
            recorded_sequence["value"] = sequence
            save_btn.configure(
                state="normal",
                command=lambda: self._apply_shortcut(action_id, sequence, dialog)
            )
        
        dialog.bind("<Key>", on_key)
        dialog.focus_set()

    def _apply_shortcut(
        self, 
        action_id: str, 
        sequence: str, 
        dialog: ctk.CTkToplevel
    ) -> None:
        """
        Kısayolu uygular ve paneli yeniler.
        
        Args:
            action_id: Aksiyon kimliği
            sequence: Yeni kısayol
            dialog: Diyalog penceresi
        """
        manager = ShortcutManager.get_instance()
        
        # Çakışma kontrolü
        existing = manager.find_action_by_shortcut(sequence) if hasattr(manager, 'find_action_by_shortcut') else None
        if existing and existing != action_id:
            # Çakışma uyarısı göster
            self._show_conflict_warning(dialog, existing, action_id, sequence, manager)
            return
        
        manager.set(action_id, sequence)
        dialog.destroy()
        
        # UI'ı güncelle (tam yenileme yerine)
        btn = self._widget_cache.get(f"shortcut_{action_id}")
        if btn:
            btn.configure(text=manager.get_display_string(sequence))

    def _show_conflict_warning(
        self,
        parent: ctk.CTkToplevel,
        existing_action: str,
        new_action: str,
        sequence: str,
        manager: ShortcutManager
    ) -> None:
        """Çakışma uyarısı gösterir."""
        existing_meta = manager.get_localized_metadata(existing_action)
        existing_label = existing_meta.get("label", existing_action)
        
        # Uyarı mesajı
        warning_frame = ctk.CTkFrame(
            parent,
            fg_color=("#fff3cd", "#3d3200"),
            corner_radius=8
        )
        warning_frame.place(relx=0.5, rely=0.85, anchor="center")
        
        ctk.CTkLabel(
            warning_frame,
            text=f"⚠️ Bu kısayol '{existing_label}' için kullanılıyor!",
            font=ctk.CTkFont(size=11),
            text_color=("#856404", "#ffc107"),
            padx=12,
            pady=6
        ).pack()
        
        # 2 saniye sonra uyarıyı kaldır
        parent.after(2000, warning_frame.destroy)

    def _reset_shortcuts(self) -> None:
        """Tüm kısayolları varsayılana döndürür."""
        ShortcutManager.get_instance().reset_to_defaults()
        self.settings_dialog.show_category("Klavye Kısayolları")
