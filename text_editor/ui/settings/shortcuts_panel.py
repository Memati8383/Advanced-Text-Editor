import customtkinter as ctk
from text_editor.ui.settings.base_panel import BaseSettingsPanel
from text_editor.utils.shortcut_manager import ShortcutManager

class ShortcutsSettingsPanel(BaseSettingsPanel):
    def _setup_content(self):
        """Klavye kısayolları paneli."""
        manager = ShortcutManager.get_instance()
        shortcuts = manager.shortcuts
        
        grouped = {}
        for aid, seq in shortcuts.items():
            meta = manager.get_localized_metadata(aid)
            cat = meta["category"]
            if cat not in grouped: grouped[cat] = []
            grouped[cat].append((aid, meta["label"], seq))
            
        for cat, items in grouped.items():
            ctk.CTkLabel(self, text=cat, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(15, 5))
            ctk.CTkFrame(self, height=1, fg_color=("gray70", "gray30")).pack(fill="x", pady=(0, 10))
            
            for aid, lbl, seq in items:
                frame = ctk.CTkFrame(self, fg_color="transparent")
                frame.pack(fill="x", pady=3)
                
                ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=12)).pack(side="left")
                
                display = manager.get_display_string(seq) or self.lang_manager.get("status.none", "None")
                ctk.CTkButton(
                    frame, text=display, font=("Consolas", 12, "bold"),
                    fg_color=("gray90", "gray15"), text_color=("gray10", "gray90"),
                    width=120, height=28, border_width=1, border_color=("gray70", "gray40"),
                    command=lambda i=aid: self.start_shortcut_recording(i)
                ).pack(side="right")
                
        # Sıfırlama Butonu
        ctk.CTkButton(
            self, text=self.lang_manager.get("buttons.reset_shortcuts"), fg_color="transparent",
            border_width=1, border_color="#dc3545", text_color="#dc3545",
            hover_color=("#fee2e2", "#5c0000"), width=160,
            command=self._reset_shortcuts
        ).pack(pady=30, anchor="e")

    def start_shortcut_recording(self, action_id):
        """Kısayol atama diyaloğu."""
        manager = ShortcutManager.get_instance()
        current_seq = manager.get(action_id)
        
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("Kısayol Ata")
        dialog.geometry("400x250")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Ortalama
        dialog.update_idletasks()
        try:
             # Ana pencereye göre ortala
            parent = self.winfo_toplevel()
            x = parent.winfo_x() + (parent.winfo_width()//2) - 200
            y = parent.winfo_y() + (parent.winfo_height()//2) - 125
        except:
            x = 100
            y = 100
            
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="Yeni Kısayol Tuşlayın", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="İptal için ESC", text_color="gray").pack()
        
        display_lbl = ctk.CTkLabel(
            dialog, text=manager.get_display_string(current_seq),
            font=("Courier New", 24, "bold"), width=200, height=50,
            fg_color=("gray90", "gray20"), corner_radius=8
        )
        display_lbl.pack(pady=20)
        
        # Kaydet Butonunu tanımla (başlangıçta disabled)
        save_btn = ctk.CTkButton(dialog, text="Kaydet", state="disabled", width=100)
        
        def on_key(event):
            # Modifier kontrolü
            keys = []
            if event.state & 0x4: keys.append("Control")
            if event.state & 0x20000 or event.state & 0x20: keys.append("Alt")
            if event.state & 0x1: keys.append("Shift")
            
            if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
                if event.keysym == "Escape": 
                    dialog.destroy()
                    return
                keys.append(event.keysym)
            
            if not keys or (len(keys) == 1 and keys[0] in ("Control", "Alt", "Shift")):
                display_lbl.configure(text=" + ".join(keys) + " ...")
                return

            # Sequence oluştur
            parts = [k for k in ["Control", "Alt", "Shift"] if k in keys]
            if keys[-1] not in parts: parts.append(keys[-1])
            
            sequence = f"<{'-'.join(parts)}>"
            display_lbl.configure(text=manager.get_display_string(sequence))
            
            # Kaydet Butonunu Aktif Et ve komutunu güncelle
            save_btn.configure(state="normal", command=lambda: self._apply_shortcut_change(action_id, sequence, dialog))

        save_btn.pack(side="left", padx=20, expand=True)
        ctk.CTkButton(dialog, text="İptal", command=dialog.destroy, 
                      fg_color="transparent", border_width=1, width=100).pack(side="right", padx=20, expand=True)
        
        dialog.bind("<Key>", on_key)
        dialog.focus_set()

    def _apply_shortcut_change(self, action_id, sequence, dialog):
        ShortcutManager.get_instance().set(action_id, sequence)
        dialog.destroy()
        # Paneli yenile
        self.settings_dialog.show_category("Klavye Kısayolları")

    def _reset_shortcuts(self):
        ShortcutManager.get_instance().reset_to_defaults()
        self.settings_dialog.show_category("Klavye Kısayolları")
