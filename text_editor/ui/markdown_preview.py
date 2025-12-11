"""
Gelişmiş Markdown Önizleme Paneli

Memati Editör için canlı markdown önizleme bileşeni.
Clean Code mimarisine uygun olarak refactor edilmiştir.
"""

import customtkinter as ctk
import tkinter as tk
import re

from .markdown.styler import MarkdownStyler
from .markdown.renderer import MarkdownRenderer
from .markdown.exporter import MarkdownExporter

class MarkdownPreview(ctk.CTkFrame):
    """
    Gelişmiş Markdown dosya önizleme paneli.
    Modüler yapı: Styler, Renderer ve Exporter olarak ayrılmıştır.
    """
    
    def __init__(self, master, editor=None, theme=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.editor = editor
        self.theme = theme or {}
        self._update_job = None
        self._sync_scroll_enabled = True
        self._zoom_level = 100
        self._base_font_size = 12
        
        # UI Elementleri
        self._create_ui()
        
        # Alt bileşenler
        self.styler = MarkdownStyler(self.preview_text, self.theme)
        self.renderer = MarkdownRenderer(self.preview_text, self.styler)
        self.exporter = MarkdownExporter(editor, self.styler)
        
        # İlk stil ayarları
        self._apply_zoom()
        
        self._create_context_menu()
        
        # Arama değişkenleri
        self._search_matches = []
        self._current_match_index = -1
        
        if editor:
            self.set_editor(editor)
            
    def _create_ui(self):
        """Önizleme arayüzünü oluşturur."""
        self.configure(corner_radius=8)
        
        # === Başlık çubuğu ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Sol taraf - Başlık
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side="left", fill="y")
        
        title_label = ctk.CTkLabel(
            left_header,
            text="📄 Markdown Önizleme",
            font=("Segoe UI", 13, "bold"),
            # Renkler styler'dan alınacak, şimdilik varsayılan veya theme'den
            text_color=self.theme.get("accent_color", "#569cd6")
        )
        title_label.pack(side="left")
        
        self.sync_indicator = ctk.CTkLabel(
            left_header, text="🔗", font=("Segoe UI", 11)
        )
        self.sync_indicator.pack(side="left", padx=(10, 0))
        
        # Orta - Kontrol paneli
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.pack(side="left", padx=20)
        
        # Zoom kontrolü
        self._create_zoom_controls(control_frame)
        
        # Senkron scroll butonu
        self.sync_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Senkron",
            width=80, height=25, corner_radius=5,
            command=self._toggle_sync_scroll
        )
        self.sync_btn.pack(side="left", padx=10)
        
        # Sağ taraf - Butonlar
        right_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header.pack(side="right")
        
        self._create_action_buttons(right_header)
        
        # === İstatistik çubuğu ===
        self._create_stats_bar()
        
        # Ayırıcı
        self.separator = ctk.CTkFrame(self, height=1)
        self.separator.pack(fill="x", padx=10, pady=5)
        
        # === Önizleme alanı ===
        self.preview_frame = ctk.CTkFrame(self, corner_radius=0)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap="word",
            font=("Segoe UI", self._base_font_size),
            relief="flat",
            padx=15, pady=10,
            cursor="arrow",
            state="disabled",
            borderwidth=0,
            highlightthickness=0
        )
        
        self.scrollbar = ctk.CTkScrollbar(self.preview_frame, command=self._on_scroll)
        self.scrollbar.pack(side="right", fill="y")
        self.preview_text.configure(yscrollcommand=self._on_preview_scroll)
        self.preview_text.pack(fill="both", expand=True)
        
        # Bindings
        self.preview_text.bind("<MouseWheel>", self._on_mousewheel)
        self.preview_text.bind("<Button-4>", self._on_mousewheel)
        self.preview_text.bind("<Button-5>", self._on_mousewheel)
        self.preview_text.bind("<Button-3>", self._show_context_menu)
        
        # Kısayollar
        self.bind("<Control-p>", lambda e: self._print_preview())
        self.bind("<Control-e>", lambda e: self.export_as_html())
        self.bind("<Control-f>", lambda e: self.search_entry.focus())

    def _create_zoom_controls(self, parent):
        zoom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        zoom_frame.pack(side="left")
        
        ctk.CTkButton(
            zoom_frame, text="➖", width=25, height=25, corner_radius=5,
            fg_color="transparent", command=self._zoom_out
        ).pack(side="left", padx=2)
        
        self.zoom_label = ctk.CTkLabel(zoom_frame, text="100%", width=45, font=("Segoe UI", 10))
        self.zoom_label.pack(side="left", padx=2)
        
        ctk.CTkButton(
            zoom_frame, text="➕", width=25, height=25, corner_radius=5,
            fg_color="transparent", command=self._zoom_in
        ).pack(side="left", padx=2)

    def _create_action_buttons(self, parent):
        buttons = [
            ("📑", self._show_toc),
            ("🔄", self.refresh),
            ("✕", self._close),
            ("📤", self.export_as_html),
            ("🌐", self._open_in_browser),
            ("🖨️", self._print_preview),
            ("📄", self._export_as_pdf)
        ]
        
        for text, cmd in buttons:
            color = "#c42b1c" if text == "✕" else "transparent"
            hover = "#c42b1c" if text == "✕" else None # Default hover handled by theme usually
            
            btn = ctk.CTkButton(
                parent, text=text, width=30, height=25, corner_radius=5,
                fg_color="transparent", hover_color=hover,
                command=cmd
            )
            btn.pack(side="left", padx=2)

    def _create_stats_bar(self):
        self.stats_frame = ctk.CTkFrame(self, height=28, corner_radius=5)
        self.stats_frame.pack(fill="x", padx=10, pady=(5, 2))
        self.stats_frame.pack_propagate(False)
        
        self.word_count_label = ctk.CTkLabel(self.stats_frame, text="📝 0 kelime", font=("Segoe UI", 10))
        self.word_count_label.pack(side="left", padx=10)
        
        self.char_count_label = ctk.CTkLabel(self.stats_frame, text="🔤 0 karakter", font=("Segoe UI", 10))
        self.char_count_label.pack(side="left", padx=10)
        
        self.reading_time_label = ctk.CTkLabel(self.stats_frame, text="⏱️ ~0 dk okuma", font=("Segoe UI", 10))
        self.reading_time_label.pack(side="left", padx=10)
        
        # Arama
        search_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="🔍 Ara...", width=120, height=22,
            font=("Segoe UI", 10), border_width=1
        )
        self.search_entry.pack(side="left", padx=2)
        self.search_entry.bind("<Return>", self._search_next)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        ctk.CTkButton(
            search_frame, text="◀", width=22, height=22, fg_color="transparent",
            command=self._search_prev
        ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            search_frame, text="▶", width=22, height=22, fg_color="transparent",
            command=self._search_next
        ).pack(side="left", padx=1)
        
        self.search_count_label = ctk.CTkLabel(search_frame, text="", font=("Segoe UI", 9), width=50)
        self.search_count_label.pack(side="left", padx=2)

    def update_theme(self, theme):
        """Tema renklerini günceller."""
        self.theme = theme
        
        # Styler'ı güncelle
        self.styler.update_theme(theme)
        
        # UI Elementlerini güncelle
        colors = self.styler.colors
        self.configure(fg_color=colors["bg"])
        self.preview_frame.configure(fg_color=colors["bg"])
        self.stats_frame.configure(fg_color=colors["code_bg"])
        self.separator.configure(fg_color=colors["hr"])
        self.search_entry.configure(fg_color=colors["bg"], text_color=colors["fg"], border_color=colors["hr"])
        
        # Text widget
        self.preview_text.configure(
            bg=colors["bg"], fg=colors["fg"],
            selectbackground=colors["h1"],
            insertbackground=colors["fg"]
        )
        
        # Etiketler
        for lbl in [self.word_count_label, self.char_count_label, self.reading_time_label, self.zoom_label]:
            lbl.configure(text_color=colors["fg"])
            
        self.sync_indicator.configure(text_color=colors["h2"])
        self.start_sync_state_update() # Buton renklerini güncelle
        
        # Yeniden oluştur
        self._apply_zoom()
        self.refresh()

    def start_sync_state_update(self):
        colors = self.styler.colors
        if self._sync_scroll_enabled:
            self.sync_indicator.configure(text="🔗", text_color=colors["h2"])
            self.sync_btn.configure(fg_color=colors["code_bg"])
        else:
            self.sync_indicator.configure(text="🔓", text_color="#808080")
            self.sync_btn.configure(fg_color="transparent")

    def refresh(self):
        """Markdown içeriğini yeniden render eder."""
        if not self.editor:
            return
            
        try:
            content = self.editor.text_area.get("1.0", "end-1c")
            scroll_pos = self.preview_text.yview()
            
            # File path güncelle
            if hasattr(self.editor, 'file_path'):
                self.renderer.file_path = self.editor.file_path
            
            self.renderer.render(content)
            
            # İstatistikleri güncelle (Renderer hesapladı)
            self._update_stats(content)
            
            self.preview_text.yview_moveto(scroll_pos[0])
            
            # Arama varsa tekrar uygula
            if self.search_entry.get().strip():
                self._perform_search(self.search_entry.get().strip())
                
        except Exception as e:
            print(f"Render Error: {e}")

    def _update_stats(self, text):
        stats = self.renderer.task_stats
        # Kelime/Karakter
        words = len(text.split())
        chars = len(text)
        reading_time = max(1, round(words / 200))
        
        self.word_count_label.configure(text=f"📝 {words:,} kelime")
        self.char_count_label.configure(text=f"🔤 {chars:,} karakter")
        self.reading_time_label.configure(text=f"⏱️ ~{reading_time} dk okuma")
        
    def set_editor(self, editor):
        """Bağlı editörü ayarlar."""
        # Eskileri çöz (Unbind)
        if self.editor and hasattr(self.editor, 'text_area'):
            try:
                self.editor.text_area.unbind("<<Modified>>")
                self.editor.text_area.unbind("<KeyRelease>")
            except: pass
            
        self.editor = editor
        self.exporter.editor = editor
        
        if editor:
            editor.text_area.bind("<<Modified>>", self._on_editor_change)
            editor.text_area.bind("<KeyRelease>", self._on_editor_change)
            editor.text_area.bind("<MouseWheel>", self._on_editor_scroll)
            # Gerekirse Linux bağlamaları
            self.refresh()
            self.update_theme(self.theme) # Temayı başlangıçta uygula

    def _on_editor_change(self, event=None):
        if self._update_job:
            self.after_cancel(self._update_job)
        self._update_job = self.after(300, self.refresh)

    def _on_editor_scroll(self, event=None):
        if not self._sync_scroll_enabled or not self.editor: return
        try:
            first_visible = self.editor.text_area.index("@0,0")
            line_num = int(first_visible.split(".")[0])
            total_lines = int(self.editor.text_area.index("end-1c").split(".")[0])
            if total_lines > 1:
                fraction = line_num / total_lines
                self.preview_text.yview_moveto(fraction)
        except: pass

    def _on_preview_scroll(self, first, last):
        self.scrollbar.set(first, last)
        
    def _on_scroll(self, *args):
        self.preview_text.yview(*args)
        
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.preview_text.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.preview_text.yview_scroll(3, "units")

    def _zoom_in(self):
        if self._zoom_level < 200:
            self._zoom_level += 10
            self._apply_zoom()
            
    def _zoom_out(self):
        if self._zoom_level > 50:
            self._zoom_level -= 10
            self._apply_zoom()
            
    def _apply_zoom(self):
        self.zoom_label.configure(text=f"{self._zoom_level}%")
        self.styler.setup_tags(self._base_font_size, self._zoom_level)
        self.refresh()

    def _toggle_sync_scroll(self):
        self._sync_scroll_enabled = not self._sync_scroll_enabled
        self.start_sync_state_update()

    def _show_toc(self):
        """İçindekiler tablosunu gösterir."""
        if not self.editor: return
        content = self.editor.text_area.get("1.0", "end-1c")
        lines = content.split("\n")
        toc = []
        for i, line in enumerate(lines):
            if line.startswith("#"):
                level = len(re.match(r'^#+', line).group())
                text = line[level:].strip()
                toc.append((level, text, i + 1))
        
        if not toc: return
        
        toc_window = ctk.CTkToplevel(self)
        toc_window.title("📑 İçindekiler")
        toc_window.geometry("300x400")
        toc_window.transient(self)
        toc_window.configure(fg_color=self.styler.colors.get("bg", "#1e1e1e"))
        
        ctk.CTkLabel(toc_window, text="📑 İçindekiler", font=("Segoe UI", 14, "bold"),
                     text_color=self.styler.colors.get("h1", "#fff")).pack(pady=10)
        
        toc_frame = ctk.CTkScrollableFrame(toc_window, fg_color="transparent")
        toc_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for level, text, line_num in toc:
            indent = "  " * (level - 1)
            btn = ctk.CTkButton(
                toc_frame,
                text=f"{indent}{'▸ ' if level > 1 else '📌 '}{text}",
                anchor="w", fg_color="transparent",
                hover_color=self.styler.colors.get("code_bg", "#333"),
                text_color=self.styler.colors.get(f"h{level}", "#fff"),
                command=lambda ln=line_num, w=toc_window: self._goto_line(ln, w)
            )
            btn.pack(fill="x", pady=2)

    def _goto_line(self, line_num, window):
        if self.editor:
            self.editor.text_area.see(f"{line_num}.0")
            self.editor.text_area.mark_set("insert", f"{line_num}.0")
        if window: window.destroy()

    def _close(self):
        try:
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'close_markdown_preview'):
                main_window.close_markdown_preview()
            else:
                self.grid_remove()
        except: self.grid_remove()

    def export_as_html(self):
        self.exporter.export_as_html(self.winfo_toplevel())
        
    def _print_preview(self):
        self.exporter.print_preview()
        
    def _export_as_pdf(self):
        # HTML için dışa aktarıcıyı kullanır ve sonra kullanıcıyı yönlendiririz
        path = self.exporter.export_as_html(self.winfo_toplevel())
        if path and hasattr(self.winfo_toplevel(), "status_bar"):
             self.winfo_toplevel().status_bar.set_message("PDF için: HTML dosyasını tarayıcıda açıp Yazdır > PDF olarak kaydet yapın.", "info")

    def _open_in_browser(self):
        self.exporter.open_in_browser()

    # Aratma Logic
    def _on_search_change(self, event=None):
        query = self.search_entry.get().strip()
        if len(query) < 2:
            self._clear_search_highlights()
            self.search_count_label.configure(text="")
            return
        self._perform_search(query)
        
    def _perform_search(self, query):
        self._clear_search_highlights()
        self._search_matches = []
        self._current_match_index = -1
        
        if not query: return
        
        self.preview_text.tag_configure("search_highlight", background="#ffff00", foreground="#000000")
        self.preview_text.tag_configure("search_current", background="#ff9500", foreground="#000000")
        
        start = "1.0"
        while True:
            pos = self.preview_text.search(query, start, stopindex="end", nocase=True)
            if not pos: break
            end = f"{pos}+{len(query)}c"
            self._search_matches.append((pos, end))
            self.preview_text.tag_add("search_highlight", pos, end)
            start = end
            
        count = len(self._search_matches)
        if count > 0:
            self._current_match_index = 0
            self._highlight_current_match()
            self.search_count_label.configure(text=f"1/{count}")
        else:
            self.search_count_label.configure(text="0 sonuç")

    def _search_next(self, event=None):
        if not self._search_matches: return
        self._current_match_index = (self._current_match_index + 1) % len(self._search_matches)
        self._highlight_current_match()
        
    def _search_prev(self, event=None):
        if not self._search_matches: return
        self._current_match_index = (self._current_match_index - 1) % len(self._search_matches)
        self._highlight_current_match()
        
    def _highlight_current_match(self):
        if not self._search_matches: return
        self.preview_text.tag_remove("search_current", "1.0", "end")
        pos, end = self._search_matches[self._current_match_index]
        self.preview_text.tag_add("search_current", pos, end)
        self.preview_text.see(pos)
        self.search_count_label.configure(text=f"{self._current_match_index + 1}/{len(self._search_matches)}")
        
    def _clear_search_highlights(self):
        try:
            self.preview_text.tag_remove("search_highlight", "1.0", "end")
            self.preview_text.tag_remove("search_current", "1.0", "end")
        except: pass

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        # Renkleri styler'dan al
        colors = self.styler.colors
        # Not: Eğer renkler henüz yüklenmediyse varsayılanları kullanır, 
        # update_theme metodunda burası güncellenmeli mi? 
        # Tkinter menu konfigürasyonu dinamik olarak yapılmalı.
        # Basitçe şimdilik statik bırakalım veya lazily oluşturalım.
        # En iyisi show anında configure etmek.
        
        self.context_menu.add_command(label="📋 Kopyala", command=self._copy_selection)
        self.context_menu.add_command(label="✅ Tümünü Seç", command=self._select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📤 HTML Olarak Kaydet", command=self.export_as_html)
        self.context_menu.add_command(label="🖨️ Yazdır", command=self._print_preview)
        
    def _show_context_menu(self, event):
        # Renkleri güncelle
        colors = self.styler.colors
        self.context_menu.configure(
            bg=colors.get("menu_bg", "#2b2b2b"),
            fg=colors.get("menu_fg", "#d4d4d4"),
            activebackground=colors.get("menu_hover", "#3c3c3c"),
            activeforeground=colors.get("menu_fg", "#ffffff")
        )
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_selection(self):
        try:
            text = self.preview_text.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(text)
        except: pass
        
    def _select_all(self):
        self.preview_text.tag_add("sel", "1.0", "end")
