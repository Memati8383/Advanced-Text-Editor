"""
Terminal Paneli

Memati Editör için gelişmiş entegre terminal bileşeni.
PowerShell/CMD/Bash desteği, ANSI renkleri, tema entegrasyonu,
shell seçici, hızlı komutlar ve modern arayüz sağlar.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import subprocess
import threading
import queue
import os
import sys
import re
import signal

from text_editor.ui.context_menu import ModernTerminalContextMenu


class TerminalPanel(ctk.CTkFrame):
    """
    Gelişmiş entegre terminal paneli.
    
    Özellikler:
    - PowerShell, CMD ve Bash desteği
    - Shell seçici dropdown
    - Hızlı komut butonları
    - Font boyutu ayarı
    - Komut geçmişi
    - Çalışan komutu durdurma
    - Sağ tık menüsü
    - ANSI renk desteği
    - Tema entegrasyonu
    """
    
    # Desteklenen shell'ler
    SHELLS = {
        "powershell": {
            "name": "PowerShell",
            "icon": "⚡",
            "cmd": ["powershell", "-NoProfile", "-Command"],
            "color": "#012456"
        },
        "cmd": {
            "name": "CMD",
            "icon": "📟",
            "cmd": ["cmd", "/c"],
            "color": "#0c0c0c"
        },
        "bash": {
            "name": "Bash",
            "icon": "🐚",
            "cmd": ["bash", "-c"],
            "color": "#300a24"
        }
    }
    
    # Hızlı komutlar
    QUICK_COMMANDS = [
        {"icon": "🐍", "label": "Python", "cmd": "python", "tooltip": "Python çalıştır"},
        {"icon": "📦", "label": "pip", "cmd": "pip install ", "tooltip": "pip install"},
        {"icon": "📂", "label": "Aç", "cmd": "explorer .", "tooltip": "Klasörü aç"},
        {"icon": "📋", "label": "Liste", "cmd": "dir" if sys.platform == "win32" else "ls -la", "tooltip": "Dosyaları listele"},
        {"icon": "🔍", "label": "Git", "cmd": "git status", "tooltip": "Git durumu"},
        {"icon": "🌐", "label": "Node", "cmd": "node --version", "tooltip": "Node.js sürümü"},
    ]
    
    def __init__(self, master, theme=None, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        
        # Tema ayarları
        self.theme = theme or {}
        self._bg_color = self.theme.get("terminal_bg", "#1e1e1e")
        self._fg_color = self.theme.get("terminal_fg", "#cccccc")
        self._selection_color = self.theme.get("terminal_selection", "#264f78")
        self._accent_color = self.theme.get("accent", "#007acc")
        
        # Terminal durumu
        self.process = None
        self.current_process = None
        self.output_queue = queue.Queue()
        self.command_history = []
        self.history_index = -1
        self.is_running = False
        self.is_command_running = False
        
        # Mevcut shell
        self.current_shell = "powershell" if sys.platform == "win32" else "bash"
        
        # Font boyutu
        self.font_size = 11
        
        # Mevcut çalışma dizini
        self.current_dir = os.getcwd()
        
        # Tab tamamlama için
        self.tab_completions = []
        self.tab_index = 0
        
        # UI oluştur
        self._create_ui()
        
        # Terminal başlat
        self._start_terminal()
    
    def _create_ui(self):
        """Terminal arayüzünü oluştur"""
        # Grid yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Başlık çubuğu
        self.grid_rowconfigure(1, weight=0)  # Araç çubuğu
        self.grid_rowconfigure(2, weight=1)  # Terminal çıktısı
        self.grid_rowconfigure(3, weight=0)  # Giriş alanı
        
        # ═══════════════════════════════════════════════════════════════
        # BAŞLIK ÇUBUĞU
        # ═══════════════════════════════════════════════════════════════
        self.header_frame = ctk.CTkFrame(
            self, 
            height=36, 
            corner_radius=0, 
            fg_color=self._bg_color,
            border_width=0
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(2, weight=1)
        
        # Terminal başlık
        shell_info = self.SHELLS[self.current_shell]
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=f"{shell_info['icon']} {shell_info['name']}",
            font=("Segoe UI", 12, "bold"),
            text_color=self._fg_color
        )
        self.title_label.grid(row=0, column=0, padx=12, pady=8, sticky="w")
        
        # Shell seçici
        shell_options = [f"{s['icon']} {s['name']}" for s in self.SHELLS.values()]
        self.shell_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=shell_options,
            width=120,
            height=26,
            font=("Segoe UI", 10),
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            dropdown_fg_color="#2d2d2d",
            dropdown_hover_color="#404040",
            command=self._change_shell
        )
        self.shell_selector.set(f"{shell_info['icon']} {shell_info['name']}")
        self.shell_selector.grid(row=0, column=1, padx=5, pady=6, sticky="w")
        
        # Durum göstergesi (çalışan komut için)
        self.status_indicator = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=("Segoe UI", 10),
            text_color="#888888"
        )
        self.status_indicator.grid(row=0, column=2, padx=10, pady=6, sticky="w")
        
        # Sağ taraf butonları
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=3, padx=5, pady=4, sticky="e")
        
        # Font küçült
        self.font_down_btn = ctk.CTkButton(
            btn_frame, text="A-", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#3c3c3c", text_color=self._fg_color,
            font=("Segoe UI", 10), command=self._decrease_font
        )
        self.font_down_btn.pack(side="left", padx=1)
        
        # Font büyült
        self.font_up_btn = ctk.CTkButton(
            btn_frame, text="A+", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#3c3c3c", text_color=self._fg_color,
            font=("Segoe UI", 10), command=self._increase_font
        )
        self.font_up_btn.pack(side="left", padx=1)
        
        # Ayırıcı
        sep = ctk.CTkLabel(btn_frame, text="│", text_color="#555555", font=("Segoe UI", 12))
        sep.pack(side="left", padx=4)
        
        # Yeniden başlat
        self.restart_btn = ctk.CTkButton(
            btn_frame, text="🔄", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#3c3c3c", text_color=self._fg_color,
            font=("Segoe UI", 11), command=self._restart_terminal
        )
        self.restart_btn.pack(side="left", padx=1)
        
        # Durdur butonu
        self.stop_btn = ctk.CTkButton(
            btn_frame, text="⏹", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#ff4444", text_color="#888888",
            font=("Segoe UI", 11), command=self._stop_command,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=1)
        
        # Temizle
        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑️", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#3c3c3c", text_color=self._fg_color,
            font=("Segoe UI", 10), command=self._clear_output
        )
        self.clear_btn.pack(side="left", padx=1)
        
        # Kapat
        self.close_btn = ctk.CTkButton(
            btn_frame, text="✕", width=28, height=24,
            corner_radius=4, fg_color="transparent",
            hover_color="#e81123", text_color=self._fg_color,
            font=("Segoe UI", 11), command=self._close_terminal
        )
        self.close_btn.pack(side="left", padx=1)
        
        # ═══════════════════════════════════════════════════════════════
        # HIZLI KOMUTLAR ARAÇ ÇUBUĞU
        # ═══════════════════════════════════════════════════════════════
        self.toolbar_frame = ctk.CTkFrame(
            self, 
            height=32, 
            corner_radius=0, 
            fg_color="#252526",
            border_width=0
        )
        self.toolbar_frame.grid(row=1, column=0, sticky="ew")
        
        # Hızlı komut butonları
        for qc in self.QUICK_COMMANDS:
            btn = ctk.CTkButton(
                self.toolbar_frame,
                text=f"{qc['icon']} {qc['label']}",
                width=65,
                height=24,
                corner_radius=4,
                fg_color="transparent",
                hover_color="#3c3c3c",
                text_color="#aaaaaa",
                font=("Segoe UI", 9),
                command=lambda c=qc['cmd']: self._quick_command(c)
            )
            btn.pack(side="left", padx=2, pady=4)
        
        # Ayırıcı ve dizin göstergesi
        dir_sep = ctk.CTkLabel(
            self.toolbar_frame, 
            text="│", 
            text_color="#444444",
            font=("Segoe UI", 12)
        )
        dir_sep.pack(side="left", padx=8)
        
        self.dir_label = ctk.CTkLabel(
            self.toolbar_frame,
            text=f"📂 {self._shorten_path(self.current_dir)}",
            font=("Segoe UI", 9),
            text_color="#888888"
        )
        self.dir_label.pack(side="left", padx=5, pady=4)
        
        # ═══════════════════════════════════════════════════════════════
        # TERMİNAL ÇIKTI ALANI
        # ═══════════════════════════════════════════════════════════════
        self.output_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self._bg_color)
        self.output_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)
        
        # Sabit genişlikli (Monospace) yazı tipi
        self.terminal_font = tkfont.Font(family="Cascadia Code", size=self.font_size)
        # Yedek yazı tipi
        try:
            self.terminal_font.actual()
        except:
            self.terminal_font = tkfont.Font(family="Consolas", size=self.font_size)
        
        # Metin bileşeni
        self.output_text = tk.Text(
            self.output_frame,
            wrap="word",
            font=self.terminal_font,
            bg=self._bg_color,
            fg=self._fg_color,
            insertbackground=self._fg_color,
            selectbackground=self._selection_color,
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
            cursor="arrow",
            spacing1=2,
            spacing3=2
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        # Kaydırma çubuğu
        self.scrollbar = ctk.CTkScrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        
        # ANSI renk etiketleri
        self._setup_ansi_tags()
        
        # Sağ tık menüsü
        self._create_context_menu()
        self.output_text.bind("<Button-3>", self._show_context_menu)
        
        # ═══════════════════════════════════════════════════════════════
        # GİRİŞ ALANI
        # ═══════════════════════════════════════════════════════════════
        self.input_frame = ctk.CTkFrame(
            self, 
            height=40, 
            corner_radius=0, 
            fg_color="#252526",
            border_width=0
        )
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        # Prompt göstergesi
        shell_info = self.SHELLS[self.current_shell]
        self.prompt_label = ctk.CTkLabel(
            self.input_frame,
            text=f"{shell_info['icon']} ❯",
            font=("Cascadia Code", 12, "bold"),
            text_color="#00d084",
            width=45
        )
        self.prompt_label.grid(row=0, column=0, padx=(12, 5), pady=8)
        
        # Komut girişi
        self.command_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Komut girin... (Tab ile tamamla, ↑↓ geçmiş)",
            font=("Cascadia Code", 11),
            fg_color="#1e1e1e",
            text_color=self._fg_color,
            border_width=1,
            border_color="#3c3c3c",
            corner_radius=6,
            height=32
        )
        self.command_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=6)
        
        # Çalıştır butonu
        self.run_btn = ctk.CTkButton(
            self.input_frame,
            text="▶",
            width=36,
            height=32,
            corner_radius=6,
            fg_color="#0e639c",
            hover_color="#1177bb",
            text_color="white",
            font=("Segoe UI", 12),
            command=self._execute_command
        )
        self.run_btn.grid(row=0, column=2, padx=(0, 10), pady=6)
        
        # Klavye bağlamaları
        self.command_entry.bind("<Return>", self._execute_command)
        self.command_entry.bind("<Up>", self._history_up)
        self.command_entry.bind("<Down>", self._history_down)
        self.command_entry.bind("<Escape>", self._clear_input)
        self.command_entry.bind("<Tab>", self._tab_complete)
        self.command_entry.bind("<Control-c>", self._copy_selection)
        self.command_entry.bind("<Control-v>", self._paste_clipboard)
        
        # Çıktı alanına tıklama -> giriş alanına odaklan
        self.output_text.bind("<Button-1>", lambda e: self.command_entry.focus_set())
    
    def _setup_ansi_tags(self):
        """ANSI renk etiketlerini ayarla"""
        # Temel ANSI renkleri
        ansi_colors = {
            "30": "#000000",  # Siyah
            "31": "#cc0000",  # Kırmızı
            "32": "#00cc00",  # Yeşil
            "33": "#cccc00",  # Sarı
            "34": "#0000cc",  # Mavi
            "35": "#cc00cc",  # Magenta
            "36": "#00cccc",  # Cyan
            "37": "#cccccc",  # Beyaz
            "90": "#666666",  # Parlak siyah
            "91": "#ff0000",  # Parlak kırmızı
            "92": "#00ff00",  # Parlak yeşil
            "93": "#ffff00",  # Parlak sarı
            "94": "#0000ff",  # Parlak mavi
            "95": "#ff00ff",  # Parlak magenta
            "96": "#00ffff",  # Parlak cyan
            "97": "#ffffff",  # Parlak beyaz
        }
        
        for code, color in ansi_colors.items():
            self.output_text.tag_configure(f"ansi_{code}", foreground=color)
        
        # Özel etiketler
        self.output_text.tag_configure("bold", font=("Cascadia Code", self.font_size, "bold"))
        self.output_text.tag_configure("error", foreground="#ff6b6b")
        self.output_text.tag_configure("success", foreground="#69ff94")
        self.output_text.tag_configure("info", foreground="#61afef")
        self.output_text.tag_configure("warning", foreground="#e5c07b")
        self.output_text.tag_configure("prompt", foreground="#00d084", font=("Cascadia Code", self.font_size, "bold"))
        self.output_text.tag_configure("command", foreground="#88c0d0")
        self.output_text.tag_configure("path", foreground="#d8a657")
        self.output_text.tag_configure("timestamp", foreground="#5c6370")
    
    def _create_context_menu(self):
        """Sağ tık menüsü için tema bilgilerini hazırla"""
        # Yeni modern context menu sistemi kullanılıyor
        # Eskiden tk.Menu kullanılıyordu, artık _show_context_menu içinde 
        # ModernTerminalContextMenu oluşturuluyor
        self._context_menu_window = None
    
    def _show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        # Önceki menü varsa kapat
        if self._context_menu_window:
            try:
                self._context_menu_window.close()
            except:
                pass
        
        # Tema hazırla
        menu_theme = {
            "bg": self._bg_color,
            "bg_hover": self.theme.get("menu_hover", "#2a2d2e"),
            "bg_active": self._accent_color,
            "border": "#454545",
            "text": self._fg_color,
            "text_hover": "#ffffff",
            "shortcut": "#858585",
            "separator": "#404040",
            "icon": self._accent_color,
            "accent": self._accent_color,
            "shadow": "#000000"
        }
        
        # Modern context menu oluştur
        self._context_menu_window = ModernTerminalContextMenu.create(
            master=self.winfo_toplevel(),
            x=event.x_root,
            y=event.y_root,
            theme=menu_theme,
            on_copy=self._copy_to_clipboard,
            on_paste=self._paste_from_clipboard,
            on_select_all=self._select_all_output,
            on_clear=self._clear_output,
            on_open_folder=lambda: self._quick_command("explorer ."),
            on_save_output=self._save_output
        )
    
    def _copy_to_clipboard(self):
        """Seçili metni panoya kopyala"""
        try:
            selected = self.output_text.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass
    
    def _paste_from_clipboard(self):
        """Panodan yapıştır"""
        try:
            text = self.clipboard_get()
            self.command_entry.insert("insert", text)
        except tk.TclError:
            pass
    
    def _select_all_output(self):
        """Tüm çıktıyı seç"""
        self.output_text.configure(state="normal")
        self.output_text.tag_add("sel", "1.0", "end")
        self.output_text.configure(state="disabled")
    
    def _save_output(self):
        """Çıktıyı dosyaya kaydet"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Metin Dosyası", "*.txt"), ("Log Dosyası", "*.log")],
            title="Terminal Çıktısını Kaydet"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.output_text.get("1.0", "end-1c"))
                self._append_output(f"✅ Çıktı kaydedildi: {file_path}\n\n", "success")
            except Exception as e:
                self._append_output(f"❌ Kayıt hatası: {str(e)}\n\n", "error")
    
    def _change_shell(self, selection):
        """Shell'i değiştir"""
        # Seçimden shell anahtarını bul
        for key, shell in self.SHELLS.items():
            if shell['name'] in selection:
                self.current_shell = key
                shell_info = shell
                break
        
        # UI'ı güncelle
        self.title_label.configure(text=f"{shell_info['icon']} {shell_info['name']}")
        self.prompt_label.configure(text=f"{shell_info['icon']} ❯")
        
        # Bilgi mesajı
        self._append_output(f"\n🔄 Shell değiştirildi: {shell_info['name']}\n\n", "info")
    
    def _quick_command(self, cmd):
        """Hızlı komutu çalıştır veya giriş alanına ekle"""
        if cmd.endswith(" "):
            # pip install gibi - giriş alanına ekle
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, cmd)
            self.command_entry.focus_set()
        else:
            # Doğrudan çalıştır
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, cmd)
            self._execute_command()
    
    def _shorten_path(self, path, max_length=40):
        """Uzun yolu kısalt"""
        if len(path) <= max_length:
            return path
        
        parts = path.replace("\\", "/").split("/")
        if len(parts) <= 2:
            return path
        
        # Başı ve sonu göster
        return f"{parts[0]}/.../{parts[-1]}"
    
    def _tab_complete(self, event=None):
        """Tab ile dosya/dizin tamamlama"""
        current_text = self.command_entry.get()
        
        # Son kelimeyi al
        words = current_text.split()
        if not words:
            return "break"
        
        last_word = words[-1]
        prefix = " ".join(words[:-1]) + " " if len(words) > 1 else ""
        
        # Dizin tamamlama
        try:
            search_dir = os.path.dirname(last_word) or self.current_dir
            search_prefix = os.path.basename(last_word).lower()
            
            if not os.path.isabs(search_dir):
                search_dir = os.path.join(self.current_dir, search_dir)
            
            if os.path.isdir(search_dir):
                matches = []
                for item in os.listdir(search_dir):
                    if item.lower().startswith(search_prefix):
                        full_path = os.path.join(os.path.dirname(last_word) or "", item)
                        if os.path.isdir(os.path.join(search_dir, item)):
                            full_path += os.sep
                        matches.append(full_path)
                
                if len(matches) == 1:
                    # Tek eşleşme - tamamla
                    self.command_entry.delete(0, "end")
                    self.command_entry.insert(0, prefix + matches[0])
                elif len(matches) > 1:
                    # Çoklu eşleşme - listele
                    self._append_output("\n" + "  ".join(matches) + "\n\n", "info")
        except Exception:
            pass
        
        return "break"
    
    def _copy_selection(self, event=None):
        """Seçimi kopyala"""
        try:
            selected = self.command_entry.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass
        return "break"
    
    def _paste_clipboard(self, event=None):
        """Panodan yapıştır"""
        try:
            text = self.clipboard_get()
            self.command_entry.insert("insert", text)
        except tk.TclError:
            pass
        return "break"
    
    def _increase_font(self):
        """Font boyutunu artır"""
        if self.font_size < 20:
            self.font_size += 1
            self._update_font_size()
    
    def _decrease_font(self):
        """Font boyutunu küçült"""
        if self.font_size > 8:
            self.font_size -= 1
            self._update_font_size()
    
    def _update_font_size(self):
        """Font boyutunu güncelle"""
        self.terminal_font.configure(size=self.font_size)
        self.output_text.configure(font=self.terminal_font)
        self._setup_ansi_tags()  # Tag'leri yeniden yapılandır
    
    def _stop_command(self):
        """Çalışan komutu durdur"""
        if self.current_process:
            try:
                if sys.platform == "win32":
                    self.current_process.terminate()
                else:
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                self._append_output("\n⏹ Komut durduruldu\n\n", "warning")
            except Exception as e:
                self._append_output(f"\n❌ Durdurma hatası: {str(e)}\n\n", "error")
            finally:
                self.is_command_running = False
                self._update_status("")
    
    def _restart_terminal(self):
        """Terminali yeniden başlat"""
        self._clear_output()
        self.command_history = []
        self.history_index = -1
        self._append_output(f"🔄 Terminal yeniden başlatıldı\n", "info")
        self._append_output(f"📂 Dizin: {self.current_dir}\n\n", "path")
    
    def _update_status(self, text):
        """Durum göstergesini güncelle"""
        self.status_indicator.configure(text=text)
        if text:
            self.stop_btn.configure(state="normal", text_color="#ff6b6b")
        else:
            self.stop_btn.configure(state="disabled", text_color="#888888")
    
    def _start_terminal(self):
        """Terminal sürecini başlat"""
        self.is_running = True
        
        # Hoşgeldin mesajı
        shell_info = self.SHELLS[self.current_shell]
        self._append_output(f"🪐 Memati Terminal - {shell_info['name']}\n", "bold")
        self._append_output(f"📂 Dizin: {self.current_dir}\n", "path")
        self._append_output("💡 Komut girmek için aşağıdaki alana yazın ve Enter'a basın.\n", "info")
        self._append_output("❓ Yardım için 'help' yazın.\n\n", "info")
        
        # Çıktı okuma thread'ini başlat
        self._process_output()
    
    def _execute_command(self, event=None):
        """Komutu çalıştır"""
        command = self.command_entry.get().strip()
        
        if not command:
            return
        
        # Geçmişe ekle
        if command and (not self.command_history or self.command_history[-1] != command):
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Girişi temizle
        self.command_entry.delete(0, "end")
        
        # Komutu çıktıya yaz
        shell_info = self.SHELLS[self.current_shell]
        self._append_output(f"{shell_info['icon']} ❯ ", "prompt")
        self._append_output(f"{command}\n", "command")
        
        # Özel komutları kontrol et
        if command.lower() in ["exit", "quit"]:
            self._close_terminal()
            return
        
        if command.lower() == "clear" or command.lower() == "cls":
            self._clear_output()
            return
        
        if command.lower() == "help":
            self._show_help()
            return
        
        # cd komutu için özel işlem
        if command.lower().startswith("cd "):
            new_dir = command[3:].strip()
            self._change_directory(new_dir)
            return
        
        if command.lower() == "cd":
            self._append_output(f"{self.current_dir}\n\n")
            return
        
        # Komutu arka planda çalıştır
        threading.Thread(target=self._run_command, args=(command,), daemon=True).start()
    
    def _show_help(self):
        """Yardım mesajı göster"""
        help_text = """
╭────────────────────────────────────────────╮
│  🪐 MEMATI TERMINAL YARDIM                 │
╰────────────────────────────────────────────╯

📋 TEMEL KOMUTLAR
  cls / clear    →  Ekranı temizle
  cd <dizin>     →  Dizin değiştir
  exit / quit    →  Terminali kapat
  help           →  Bu yardımı göster

⌨️ KLAVYE KISAYOLLARI
  ↑ / ↓          →  Komut geçmişi
  Tab            →  Otomatik tamamla
  Escape         →  Girişi temizle
  Ctrl+C         →  Komutu durdur

🔧 ÖZELLİKLER
  • Shell seçici (PowerShell, CMD, Bash)
  • Hızlı komut butonları
  • Font boyutu ayarı (A+ / A-)
  • Sağ tık menüsü
  • Çıktıyı kaydetme

"""
        self._append_output(help_text, "info")
    
    def _run_command(self, command):
        """Komutu subprocess ile çalıştır"""
        try:
            self.is_command_running = True
            self.after(0, lambda: self._update_status("⏳ Çalışıyor..."))
            
            # Shell belirle
            shell_info = self.SHELLS[self.current_shell]
            shell_cmd = shell_info['cmd'] + [command]
            
            # Subprocess başlat
            self.current_process = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.current_dir,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            
            # Çıktıyı oku
            stdout, stderr = self.current_process.communicate(timeout=60)
            
            # Çıktıları göster
            if stdout:
                self._append_output_threadsafe(self._strip_ansi(stdout))
            if stderr:
                self._append_output_threadsafe(stderr, "error")
            
            # Boş satır ekle
            self._append_output_threadsafe("\n")
            
        except subprocess.TimeoutExpired:
            if self.current_process:
                self.current_process.kill()
            self._append_output_threadsafe("⚠️ Komut zaman aşımına uğradı (60s)!\n\n", "error")
        except FileNotFoundError:
            self._append_output_threadsafe(f"❌ Komut bulunamadı: {command.split()[0]}\n\n", "error")
        except Exception as e:
            self._append_output_threadsafe(f"❌ Hata: {str(e)}\n\n", "error")
        finally:
            self.is_command_running = False
            self.current_process = None
            self.after(0, lambda: self._update_status(""))
    
    def _change_directory(self, new_dir):
        """Dizin değiştir"""
        try:
            # ~ işareti için home dizini
            if new_dir.startswith("~"):
                new_dir = os.path.expanduser(new_dir)
            
            # Göreli veya mutlak yol
            if not os.path.isabs(new_dir):
                new_dir = os.path.join(self.current_dir, new_dir)
            
            # Normalize et
            new_dir = os.path.normpath(new_dir)
            
            if os.path.isdir(new_dir):
                self.current_dir = new_dir
                self._append_output(f"📂 {self.current_dir}\n\n", "path")
                # Dizin etiketini güncelle
                self.dir_label.configure(text=f"📂 {self._shorten_path(self.current_dir)}")
            else:
                self._append_output(f"❌ Dizin bulunamadı: {new_dir}\n\n", "error")
        
        except Exception as e:
            self._append_output(f"❌ Hata: {str(e)}\n\n", "error")
    
    def _strip_ansi(self, text):
        """ANSI escape kodlarını kaldır"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _append_output(self, text, tag=None):
        """Çıktı alanına metin ekle"""
        self.output_text.configure(state="normal")
        if tag:
            self.output_text.insert("end", text, tag)
        else:
            self.output_text.insert("end", text)
        self.output_text.configure(state="disabled")
        self.output_text.see("end")
    
    def _append_output_threadsafe(self, text, tag=None):
        """Thread-safe çıktı ekleme"""
        self.after(0, lambda: self._append_output(text, tag))
    
    def _process_output(self):
        """Çıktı kuyruğunu işle"""
        try:
            while not self.output_queue.empty():
                text, tag = self.output_queue.get_nowait()
                self._append_output(text, tag)
        except queue.Empty:
            pass
        
        if self.is_running:
            self.after(100, self._process_output)
    
    def _history_up(self, event=None):
        """Geçmişte yukarı git"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"
    
    def _history_down(self, event=None):
        """Geçmişte aşağı git"""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, "end")
        return "break"
    
    def _clear_input(self, event=None):
        """Giriş alanını temizle"""
        self.command_entry.delete(0, "end")
        return "break"
    
    def _clear_output(self):
        """Çıktı alanını temizle"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        shell_info = self.SHELLS[self.current_shell]
        self._append_output(f"🪐 Memati Terminal - {shell_info['name']}\n", "bold")
        self._append_output(f"📂 Dizin: {self.current_dir}\n\n", "path")
    
    def _close_terminal(self):
        """Terminali kapat"""
        self.is_running = False
        if self.process:
            self.process.terminate()
        if self.current_process:
            self.current_process.terminate()
        
        # Ana pencereye terminal kapatma sinyali gönder
        if hasattr(self.master, "toggle_terminal"):
            self.master.toggle_terminal()
    
    def update_theme(self, theme):
        """Tema değişikliğinde renkleri güncelle"""
        self.theme = theme
        self._bg_color = theme.get("terminal_bg", theme.get("editor_bg", "#1e1e1e"))
        self._fg_color = theme.get("terminal_fg", theme.get("editor_fg", "#cccccc"))
        self._selection_color = theme.get("terminal_selection", "#264f78")
        
        # Ana frame
        self.configure(fg_color=self._bg_color)
        
        # Header
        self.header_frame.configure(fg_color=self._bg_color)
        self.title_label.configure(text_color=self._fg_color)
        self.font_down_btn.configure(text_color=self._fg_color)
        self.font_up_btn.configure(text_color=self._fg_color)
        self.restart_btn.configure(text_color=self._fg_color)
        self.clear_btn.configure(text_color=self._fg_color)
        self.close_btn.configure(text_color=self._fg_color)
        
        # Toolbar
        toolbar_bg = theme.get("tab_bg", "#252526")
        self.toolbar_frame.configure(fg_color=toolbar_bg)
        
        # Output
        self.output_frame.configure(fg_color=self._bg_color)
        self.output_text.configure(
            bg=self._bg_color,
            fg=self._fg_color,
            insertbackground=self._fg_color,
            selectbackground=self._selection_color
        )
        
        # Input
        self.input_frame.configure(fg_color=toolbar_bg)
        self.command_entry.configure(
            fg_color=self._bg_color,
            text_color=self._fg_color,
            border_color=theme.get("border", "#3c3c3c")
        )
    
    def set_working_directory(self, path):
        """Çalışma dizinini ayarla"""
        if os.path.isdir(path):
            self.current_dir = path
            self._append_output(f"📂 Dizin değişti: {self.current_dir}\n\n", "path")
            self.dir_label.configure(text=f"📂 {self._shorten_path(self.current_dir)}")
        elif os.path.isfile(path):
            self.current_dir = os.path.dirname(path)
            self._append_output(f"📂 Dizin değişti: {self.current_dir}\n\n", "path")
            self.dir_label.configure(text=f"📂 {self._shorten_path(self.current_dir)}")
    
    def focus_input(self):
        """Giriş alanına odaklan"""
        self.command_entry.focus_set()
    
    def destroy(self):
        """Widget'ı yok et"""
        self.is_running = False
        if self.process:
            self.process.terminate()
        if self.current_process:
            self.current_process.terminate()
        super().destroy()
