import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=35, corner_radius=8, **kwargs)
        
        # Grid yapılandırması - 4 sütunlu modern layout
        self.grid_columnconfigure(0, weight=0)  # İkonlar
        self.grid_columnconfigure(1, weight=1)  # Mesaj
        self.grid_columnconfigure(2, weight=0)  # Dosya bilgisi
        self.grid_columnconfigure(3, weight=0)  # İmleç bilgisi
        
        # Sol taraf: Durum ikonu ve mesaj
        self.status_icon = ctk.CTkLabel(
            self, 
            text="●", 
            font=("Segoe UI", 16, "bold"), 
            text_color="#00ff88",
            width=20
        )
        self.status_icon.grid(row=0, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.message_label = ctk.CTkLabel(
            self, 
            text="✨ Hazır", 
            anchor="w",
            font=("Segoe UI", 11)
        )
        self.message_label.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Orta: Dosya bilgisi
        self.file_info_label = ctk.CTkLabel(
            self,
            text="📄 Python | UTF-8",
            anchor="center",
            font=("Segoe UI", 10)
        )
        self.file_info_label.grid(row=0, column=2, sticky="e", padx=10, pady=5)
        
        # Sağ: İmleç konumu ve satır bilgisi
        self.cursor_info = ctk.CTkLabel(
            self, 
            text="⌖ Ln 1, Col 1 | 0 satır",
            anchor="e",
            font=("Segoe UI", 10, "bold")
        )
        self.cursor_info.grid(row=0, column=3, sticky="e", padx=(10, 15), pady=5)
        
        # Hover efekti için
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        self._default_height = 35
        self._hover_height = 38

    def _on_hover(self, event):
        """Durum çubuğu üzerine gelindiğinde hafif animasyon"""
        self.configure(height=self._hover_height)
    
    def _on_leave(self, event):
        """Durum çubuğundan ayrılındığında normal boyuta dön"""
        self.configure(height=self._default_height)

    def set_message(self, message, status="ready"):
        """
        Mesajı ve durum ikonunu günceller.
        status: 'ready', 'working', 'error', 'success'
        """
        status_icons = {
            "ready": ("●", "#00ff88"),
            "working": ("◐", "#ffaa00"),
            "error": ("✕", "#ff4444"),
            "success": ("✓", "#00ff88"),
            "info": ("ℹ", "#4488ff")
        }
        
        icon, color = status_icons.get(status, ("●", "#00ff88"))
        self.status_icon.configure(text=icon, text_color=color)
        self.message_label.configure(text=f"✨ {message}")

    def set_file_info(self, file_type="Metin", encoding="UTF-8", lines=0):
        """Dosya bilgisini günceller"""
        from text_editor.utils.file_icons import FileIcons
        
        # Dosya türü için ikon al (eğer bir dosya adı girilmişse)
        # Aksi halde file_type string'inden ikon bulmaya çalış
        icon = "📄"  # Varsayılan
        
        # Dosya türü map'i - geriye dönük uyumluluk
        type_icons = {
            "Python": "🐍",
            "JavaScript": "📜",
            "TypeScript": "🔷",
            "HTML": "🌐",
            "CSS": "🎨",
            "JSON": "📋",
            "Markdown": "📝",
            "XML": "📰",
            "SQL": "🗄️",
            "Java": "☕",
            "C++": "⚙️",
            "C": "©️",
            "C#": "#️⃣",
            "PHP": "🐘",
            "Ruby": "💎",
            "Go": "🦫",
            "Rust": "🦀",
            "Swift": "🕊️",
            "Kotlin": "🅺",
            "Shell Script": "🐚",
            "Batch File": "⚡",
            "PowerShell": "💠",
            "React JSX": "⚛️",
            "React TSX": "⚛️",
            "Vue": "💚",
            "Svelte": "🔥",
            "YAML": "📄",
            "TOML": "⚙️",
            "Config": "🔧",
            "Environment": "🌍",
            "Metin": "📄",
            "Text": "📄",
            "File": "📄"
        }
        
        icon = type_icons.get(file_type, "📄")
        
        self.file_info_label.configure(text=f"{icon} {file_type} | {encoding}")

    def set_cursor_info(self, line, col, total_lines=0):
        """İmleç konumunu günceller"""
        self.cursor_info.configure(text=f"⌖ Ln {line}, Col {col} | {total_lines} satır")

    def set_info(self, info):
        """Genel bilgi güncellemesi (geriye dönük uyumluluk için)"""
        if "|" in info:
            parts = info.split("|")
            if len(parts) >= 2:
                cursor_part = parts[0].strip()
                encoding_part = parts[1].strip() if len(parts) > 1 else "UTF-8"
                
                # "Ln 1, Col 1" formatını parse et
                if "Ln" in cursor_part and "Col" in cursor_part:
                    try:
                        ln_col = cursor_part.replace("Ln", "").replace("Col", "").split(",")
                        line = ln_col[0].strip()
                        col = ln_col[1].strip()
                        self.set_cursor_info(line, col)
                    except:
                        pass
