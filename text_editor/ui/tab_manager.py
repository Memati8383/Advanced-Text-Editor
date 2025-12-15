import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List, Dict, Any, Callable

import customtkinter as ctk

from text_editor.ui.editor import CodeEditor
from text_editor.utils.file_monitor import FileMonitor
from text_editor.theme_config import DARK_THEME
from text_editor.ui.context_menu import ModernContextMenu 
try:
    from text_editor.utils.file_icons import FileIcons
except ImportError:
    FileIcons = None

# Günlüğe kaydetmeyi yapılandır
logger = logging.getLogger(__name__)

# Sabitler
AUTO_SAVE_INTERVAL_MS = 30000  # 30 seconds
DEFAULT_FONT = ("Segoe UI", 13)
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp'}
KNOWN_TAB_PREFIXES = ["Adsız", "Untitled"]

class TabManager(ctk.CTkFrame):
    """
    Birden fazla sekmeyi ve kod editörünü yönetir.
    Scrollable (kaydırılabilir) sekme çubuğu ile çok sayıda sekmeyi destekler.
    Her sekme bağımsız bir CodeEditor örneği içerir.
    Dosya açma, kaydetme, otomatik kaydetme ve dosya izleme işlemlerini yönetir.
    """

    def __init__(self, master, status_callback: Callable[[str, str], None] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.status_callback = status_callback
        
        from text_editor.utils.language_manager import LanguageManager
        self.lang = LanguageManager.get_instance()
        
        # Grid yapılandırması
        self.grid_rowconfigure(0, weight=0) # Sekme çubuğu (sabit yükseklik)
        self.grid_rowconfigure(1, weight=1) # İçerik alanı (esnek)
        self.grid_columnconfigure(0, weight=1)

        self._init_state()
        self._setup_ui()

        # İlk sekmeyi oluştur
        self.add_new_tab()
        
        self._start_services()

    def _init_state(self):
        """Dahili durum değişkenlerini başlatır."""
        self.editors: Dict[str, CodeEditor] = {}
        self.current_theme = DARK_THEME
        self.context_menu_window = None
        
        # Özel sekme yönetimi için yapılar
        self._tab_buttons: Dict[str, ctk.CTkButton] = {}
        self._tab_frames: Dict[str, ctk.CTkFrame] = {}
        self._current_name: Optional[str] = None
        
        # Tema renkleri (Varsayılan - Dark Theme benzeri)
        self.style_config = {
            "tab_bg": "transparent",
            "tab_hover": "#2d2d2d",
            "tab_selected": "#1e1e1e",
            "tab_text": "#d4d4d4",
            "bar_bg": "transparent",
            "accent_color": "#007acc"
        }

    def _setup_ui(self):
        """UI bileşenlerini ve stillerini yapılandırır."""
        # Kendisi şeffaf olabilir veya arka plan rengi alabilir
        self.configure(fg_color="transparent")

        # 1. Kaydırılabilir Sekme Çubuğu
        self._tab_bar = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            height=32, # Buton yüksekliğine uygun
            fg_color=self.style_config["bar_bg"],
            corner_radius=0
        )
        self._tab_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))
        
        # 2. İçerik Alanı
        self._content_area = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self._content_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._content_area.grid_rowconfigure(0, weight=1)
        self._content_area.grid_columnconfigure(0, weight=1)

    def _start_services(self):
        """Arka plan hizmetlerini başlatır (Dosya izleyici, Otomatik kaydetme)."""
        self.file_monitor = FileMonitor(self.on_file_changed)
        self.after(AUTO_SAVE_INTERVAL_MS, self.auto_save_loop)

    # === CTkTabview Uyumluluk Yöntemleri ===

    def add(self, name: str):
        """Yeni bir sekme (buton ve çerçeve) ekler."""
        if name in self._tab_frames:
            return  # Zaten varsa işlem yapma

        # 1. İçerik Çerçevesi
        frame = ctk.CTkFrame(self._content_area, corner_radius=0, fg_color="transparent")
        self._tab_frames[name] = frame
        
        # 2. Sekme Butonu
        btn = ctk.CTkButton(
            self._tab_bar,
            text=name,
            font=DEFAULT_FONT,
            width=120, # Genişlik, yazıya göre değişebilir aslında ama sabit iyidir
            height=30,
            corner_radius=6,
            fg_color=self.style_config["tab_bg"],
            hover_color=self.style_config["tab_hover"],
            text_color=self.style_config["tab_text"],
            command=lambda n=name: self.set(n)
        )
        btn.pack(side="left", padx=2, pady=2)
        self._tab_buttons[name] = btn
        
        return name

    def _get_tab_order(self) -> List[str]:
        """Sekmelerin görsel sırasını döndürür."""
        return list(self._tab_buttons.keys())

    def delete(self, name: str):
        """Sekmeyi, butonunu ve içeriğini siler."""
        if name not in self._tab_frames:
            return

        # İçeriği temizle
        self._tab_frames[name].destroy()
        del self._tab_frames[name]

        # Butonu temizle
        self._tab_buttons[name].destroy()
        del self._tab_buttons[name]

        # Editörü temizle (TabManager maintainerı olarak)
        if name in self.editors:
            del self.editors[name]

        # Eğer silinen aktif sekme ise, başka birine geç
        if self._current_name == name:
            self._current_name = None
            if self._tab_frames:
                # Son eklenen veya ilk sekmeye geç
                new_tab = list(self._tab_frames.keys())[-1]
                self.set(new_tab)
            else:
                # Hiç sekme kalmadıysa yeni oluştur
                self.add_new_tab()

    def set(self, name: str):
        """Aktif sekmeyi değiştirir."""
        if name not in self._tab_frames:
            return

        # Eski sekmeyi gizle
        if self._current_name and self._current_name in self._tab_frames:
            self._tab_frames[self._current_name].grid_forget()
            # Eski butonu pasif renge döndür
            if self._current_name in self._tab_buttons:
                self._tab_buttons[self._current_name].configure(
                    fg_color=self.style_config["tab_bg"],
                    border_width=0
                )

        # Yeni sekmeyi göster
        self._current_name = name
        self._tab_frames[name].grid(row=0, column=0, sticky="nsew")
        
        # Yeni butonu aktif renge döndür
        if name in self._tab_buttons:
            self._tab_buttons[name].configure(
                fg_color=self.style_config["tab_selected"],
                border_width=2,
                border_color=self.style_config.get("accent_color", "#007acc")
            )

    def get(self) -> str:
        """Aktif sekmenin adını döndürür."""
        return self._current_name

    def tab(self, name: str) -> ctk.CTkFrame:
        """Sekmenin içerik çerçevesini döndürür."""
        return self._tab_frames[name]

    # === Yardımcı Yöntemler ===

    def _update_status(self, message: str, status_type: str = "info", timeout: int = 0):
        """
        Durum çubuğunu güvenli bir şekilde günceller.
        """
        if self.status_callback:
            try:
                self.status_callback(message, status_type)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
        else:
            try:
                main_window = self.winfo_toplevel()
                if hasattr(main_window, 'status_bar') and main_window.status_bar:
                    main_window.status_bar.set_message(message, status_type)
            except Exception as e:
                logger.debug(f"Status update fallback failed: {e}")

        if timeout > 0:
            self.after(timeout, lambda: self._update_status("Hazır", "ready"))

    def get_current_tab_name(self) -> str:
        """Aktif sekmenin adını (ID) döndürür."""
        return self.get()

    def get_current_editor(self) -> Optional[CodeEditor]:
        """Aktif kod editörü örneğini döndürür."""
        name = self.get_current_tab_name()
        return self.editors.get(name)

    def get_display_name(self, tab_name: str) -> str:
        """Sekmenin görüntülenen adını (yerelleştirilmiş) döndürür."""
        if tab_name not in self.editors:
            return tab_name
            
        editor = self.editors[tab_name]
        if editor.file_path:
            return os.path.basename(editor.file_path)
            
        # Kaydedilmemiş dosya: "Adsız-X" veya "Untitled-X" formatını kontrol et
        if "-" in tab_name:
            prefix, suffix = tab_name.rsplit("-", 1)
            
            # Eğer prefix bilinenlerden biriyse, o anki dilin karşılığına çevir
            if prefix in KNOWN_TAB_PREFIXES:
                current_prefix = self.lang.get("untitled_tab", "Adsız")
                return f"{current_prefix}-{suffix}"
                
        return tab_name

    def _copy_to_clipboard(self, text: str, success_message: str):
        """Metni panoya kopyalar."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self._update_status(success_message, "success")

    def _update_tab_visuals(self, tab_name: str):
        """
        Sekme düğmesi metnini günceller (İkon + İsim + Değişiklik İşaretçisi).
        """
        if tab_name not in self.editors:
            return

        editor = self.editors[tab_name]
        
        # Görünen Adı Belirle
        display_name = self.get_display_name(tab_name)
        
        if editor.file_path:
            icon = FileIcons.get_icon(display_name) if FileIcons else "📄"
        else:
            icon = "📝"

        # Değişiklik Göstergesi
        dirty_marker = " •" if editor.content_modified else ""
        
        # Metni ayarla
        final_text = f"{icon} {display_name}{dirty_marker}"
        
        # Buton metnini güncelle
        if tab_name in self._tab_buttons:
            self._tab_buttons[tab_name].configure(text=final_text)

    # === Çekirdek Mantık ===

    def auto_save_loop(self):
        """Periyodik otomatik kaydetme döngüsü."""
        for name, editor in self.editors.items():
            if editor.file_path and editor.content_modified:
                try:
                    current_path = editor.file_path
                    editor.save_file()
                    filename = os.path.basename(current_path)
                    self._update_status(f"Otomatik kaydedildi: {filename}", "success", 2000)
                    self._update_tab_visuals(name)
                except Exception as e:
                    logger.error(f"Auto-save failed for {name}: {e}")
        
        self.after(AUTO_SAVE_INTERVAL_MS, self.auto_save_loop)

    def add_new_tab(self, name: str = None) -> str:
        """Yeni sekme oluşturur ve editörü başlatır."""
        if name is None:
            # En küçük numarayı bul
            prefix = self.lang.get("untitled_tab", "Adsız")
            
            used_numbers = set()
            for existing_name in self.editors:
                if "-" in existing_name:
                    parts = existing_name.rsplit("-", 1)
                    if len(parts) == 2 and parts[0] in KNOWN_TAB_PREFIXES:
                        try:
                            used_numbers.add(int(parts[1]))
                        except ValueError:
                            pass
            
            new_number = 1
            while new_number in used_numbers:
                new_number += 1
                
            name = f"{prefix}-{new_number}"
        
        name = self._ensure_unique_name(name)

        # Sekme ekle (Custom Implementation)
        self.add(name)
        
        # Editör oluştur
        self._create_editor_in_tab(name)
        
        # Olayları bağla
        self._bind_tab_events(name)

        # Görseli güncelle
        self._update_tab_visuals(name)
        
        # Sekmeyi aktif yap
        self.set(name)
        
        return name

    def _ensure_unique_name(self, name: str) -> str:
        """Sekme adının dahili sözlükte benzersiz olduğundan emin olur."""
        original_name = name
        counter = 1
        while name in self.editors:
            name = f"{original_name} ({counter})"
            counter += 1
        return name

    def _bind_tab_events(self, tab_name: str):
        """Fare olaylarını sekme butonuna bağlar."""
        if tab_name in self._tab_buttons:
            btn = self._tab_buttons[tab_name]
            
            # Sağ tık - Bağlam Menüsü
            btn.bind("<Button-3>", lambda e, n=tab_name: self.show_context_menu(e, n))
            
            # Orta tık - Sekmeyi Kapat
            btn.bind("<Button-2>", lambda e, n=tab_name: self.check_and_close_tab(n)) 

    def _create_editor_in_tab(self, tab_name: str):
        """Sekme içinde CodeEditor oluşturur."""
        tab_frame = self.tab(tab_name)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        editor = CodeEditor(tab_frame)
        if self.current_theme:
            editor.apply_theme(self.current_theme)
        
        editor.grid(row=0, column=0, sticky="nsew")
        self.editors[tab_name] = editor

        editor.text_area.bind("<KeyRelease>", lambda e: self._on_editor_content_changed(tab_name), add="+")
        editor.text_area.bind("<<Change>>", lambda e: self._on_editor_content_changed(tab_name), add="+")

    def _on_editor_content_changed(self, tab_name: str):
        """Editör içeriği değiştiğinde çağrılır."""
        self._update_tab_visuals(tab_name)

    def show_context_menu(self, event, tab_name: str):
        """Bir sekme için modern bağlam menüsünü gösterir."""
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()

        if self.context_menu_window:
            self.context_menu_window.close()
            self.context_menu_window = None

        commands = [
            (lang.get("context_menu.close", "Kapat"), lambda: self.check_and_close_tab(tab_name)),
            (lang.get("context_menu.close_others", "Diğerlerini Kapat"), lambda: self.close_others(tab_name)),
            (lang.get("context_menu.close_right", "Sağdakileri Kapat"), lambda: self.close_right(tab_name)),
            "-",
            (f"📋 {lang.get('menu.items.copy_path', 'Dosya Yolunu Kopyala')}", lambda: self.copy_path(tab_name)),
            (f"📋 {lang.get('context_menu.copy_filename', 'Dosya Adını Kopyala')}", lambda: self.copy_filename(tab_name))
        ]

        menu_theme = None
        if self.current_theme:
            border_color = self.current_theme.get("accent_color", "#454545")
            if "border" in self.current_theme:
                border_color = self.current_theme["border"]

            menu_theme = {
                "bg": self.current_theme.get("menu_bg", "#2b2b2b"),
                "border": border_color,
                "hover": self.current_theme.get("menu_hover", "#094771"),
                "text": self.current_theme.get("menu_fg", "#cccccc"),
                "separator": border_color
            }
        
        self.context_menu_window = ModernContextMenu(
            self.winfo_toplevel(),
            commands,
            event.x_root,
            event.y_root,
            theme=menu_theme
        )

    # === Sekme Kapatma Mantığı ===

    def check_and_close_tab(self, name: str):
        """Sekmeyi kapatmadan önce kaydedilmemiş değişiklikleri kontrol eder."""
        if name not in self.editors:
            # Editör yoksa direkt sil (örn. bozuk durum)
            self.close_tab(name)
            return

        editor = self.editors[name]
        if editor.content_modified:
            display_name = self.get_display_name(name)
            response = messagebox.askyesnocancel(
                "Kaydedilmemiş Değişiklikler",
                f"'{display_name}' dosyasında kaydedilmemiş değişiklikler var.\nKapatmadan önce kaydetmek ister misiniz?"
            )
            
            if response is None: 
                return
            elif response is True: 
                if editor.file_path:
                    editor.save_file()
                else:
                    self.set(name)
                    self.save_current_file_as()
                    if editor.content_modified:
                        return

        self.close_tab(name)

    def close_tab(self, name: str):
        """Sekmeyi kapatır ve kaynakları temizler."""
        if name in self.editors:
            del self.editors[name]
        
        # UI'dan sil
        self.delete(name)

    def close_current_tab(self):
        """Mevcut aktif sekmeyi kapatır."""
        name = self.get_current_tab_name()
        if name:
            self.check_and_close_tab(name)

    def close_others(self, keeper_name: str):
        """Belirtilen sekme dışındaki tüm sekmeleri kapatır."""
        for tab in list(self.editors.keys()):
            if tab != keeper_name:
                self.check_and_close_tab(tab)

    def close_right(self, boundary_name: str):
        """Belirtilen sekmenin sağındaki tüm sekmeleri kapatır."""
        ordered_tabs = self._get_tab_order()
        start_closing = False
        
        for tab in ordered_tabs:
            if start_closing:
                self.check_and_close_tab(tab)
            if tab == boundary_name:
                start_closing = True

    # === Pano İşlemleri ===

    def copy_path(self, name: str = None) -> bool:
        editor = self.editors.get(name or self.get_current_tab_name())
        if editor and editor.file_path:
            self._copy_to_clipboard(editor.file_path, "Dosya yolu kopyalandı")
            return True
        self._update_status("Dosya kaydedilmemiş", "warning")
        return False

    def copy_relative_path(self, name: str = None) -> bool:
        editor = self.editors.get(name or self.get_current_tab_name())
        if not (editor and editor.file_path):
            self._update_status("Dosya kaydedilmemiş", "warning")
            return False

        try:
            main_window = self.winfo_toplevel()
            root_path = getattr(main_window.file_explorer, 'root_path', None) if hasattr(main_window, 'file_explorer') else None
            base_path = root_path or os.getcwd()
            relative_path = os.path.relpath(editor.file_path, base_path)
            self._copy_to_clipboard(relative_path, "Göreli yol kopyalandı")
            return True
        except Exception:
            return self.copy_path(name)

    def copy_filename(self, name: str = None) -> bool:
        editor = self.editors.get(name or self.get_current_tab_name())
        if editor and editor.file_path:
            filename = os.path.basename(editor.file_path)
            self._copy_to_clipboard(filename, "Dosya adı kopyalandı")
            return True
        self._update_status("Dosya kaydedilmemiş", "warning")
        return False

    # === Dosya İşlemleri ===

    def open_file(self, path: str = None):
        file_path = path or filedialog.askopenfilename()
        if not file_path:
            return

        for name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(file_path):
                self.set(name)
                return

        if self._should_use_current_tab():
            current_name = self.get_current_tab_name()
            self._load_file_into_tab(current_name, file_path)
        else:
            self._load_file_into_new_tab(file_path)

    def _should_use_current_tab(self) -> bool:
        current_name = self.get_current_tab_name()
        current_editor = self.get_current_editor()
        return (NEW_TAB_PREFIX in current_name and 
                current_editor and 
                not current_editor.content_modified and 
                len(current_editor.text_area.get("1.0", "end-1c")) == 0)

    def _load_file_into_tab(self, tab_name: str, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        is_image = ext in IMAGE_EXTENSIONS
        current_view = self.editors[tab_name]
        
        if is_image:
            from text_editor.ui.image_viewer import ImageViewer
            if not isinstance(current_view, ImageViewer):
                self._replace_tab_content(tab_name, ImageViewer)
        elif not is_image and not isinstance(current_view, CodeEditor):
            self._replace_tab_content(tab_name, CodeEditor)
            
        editor = self.editors[tab_name]
        editor.load_file(file_path)
        editor.file_path = file_path
        editor.set_lexer_from_file(file_path)
        self.file_monitor.add_file(file_path)
        self._update_tab_visuals(tab_name)

    def _replace_tab_content(self, tab_name: str, view_class):
        if tab_name in self.editors:
            self.editors[tab_name].destroy()
            
        tab_frame = self.tab(tab_name)
        new_view = view_class(tab_frame)
        
        if self.current_theme:
            new_view.apply_theme(self.current_theme)
            
        new_view.grid(row=0, column=0, sticky="nsew")
        self.editors[tab_name] = new_view
        
        if isinstance(new_view, CodeEditor):
            new_view.text_area.bind("<KeyRelease>", lambda e: self._on_editor_content_changed(tab_name), add="+")
            new_view.text_area.bind("<<Change>>", lambda e: self._on_editor_content_changed(tab_name), add="+")

    def _load_file_into_new_tab(self, file_path: str):
        filename = os.path.basename(file_path)
        tab_name = self.add_new_tab(filename)
        self._load_file_into_tab(tab_name, file_path)

    def save_current_file(self):
        editor = self.get_current_editor()
        if not editor:
            return

        if editor.file_path:
            editor.save_file()
            self._update_tab_visuals(self.get_current_tab_name())
            self._update_status(f"Kaydedildi: {os.path.basename(editor.file_path)}", "success", 2000)
        else:
            self.save_current_file_as()

    def save_current_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file_path:
            return

        old_path = editor.file_path
        editor.file_path = file_path
        
        if editor.save_file():
            editor.set_lexer_from_file(file_path)
            
            if old_path:
                self.file_monitor.remove_file(old_path)
            self.file_monitor.add_file(file_path)
            
            current_tab_name = self.get_current_tab_name()
            self._update_tab_visuals(current_tab_name)
            self._update_status(f"Farklı kaydedildi: {os.path.basename(file_path)}", "success")

    def on_file_changed(self, path: str):
        self.after(0, lambda: self.handle_file_change(path))

    def handle_file_change(self, path: str):
        if not os.path.exists(path):
            return

        for name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(path):
                try:
                    current_mtime = os.path.getmtime(path)
                    if hasattr(editor, 'last_mtime') and abs(current_mtime - editor.last_mtime) < 2.0:
                        return
                except OSError:
                    pass

                display_name = os.path.basename(editor.file_path)
                if messagebox.askyesno("Dosya Değişti", f"'{display_name}' dosyası harici olarak değiştirildi.\nYeniden yüklemek ister misiniz?"):
                    editor.load_file(path)
                    self._update_tab_visuals(name)
                break

    # === Görünüm ve Tema ===

    def apply_theme(self, theme: Dict[str, Any]):
        """TabManager ve tüm editörlere temayı uygular."""
        self.current_theme = theme
        
        # Tema renklerini güncelle
        self.style_config["tab_bg"] = "transparent"
        self.style_config["tab_selected"] = theme.get("tab_selected", "#1e1e1e")
        self.style_config["tab_hover"] = theme.get("tab_hover", "#2d2d2d")
        self.style_config["tab_text"] = theme.get("fg", "#d4d4d4")
        self.style_config["bar_bg"] = theme.get("tab_bg", "transparent")
        self.style_config["accent_color"] = theme.get("accent_color", "#007acc")

        self.configure(fg_color="transparent")
        
        if hasattr(self, "_tab_bar"):
            self._tab_bar.configure(fg_color=self.style_config["bar_bg"])
        
        # Mevcut butonları güncelle
        for name, btn in self._tab_buttons.items():
            is_active = (name == self._current_name)
            
            if is_active:
                btn.configure(
                    text_color=self.style_config["tab_text"],
                    hover_color=self.style_config["tab_selected"],
                    fg_color=self.style_config["tab_selected"],
                    border_width=2,
                    border_color=self.style_config["accent_color"]
                )
            else:
                btn.configure(
                    text_color=self.style_config["tab_text"],
                    hover_color=self.style_config["tab_hover"],
                    fg_color=self.style_config["tab_bg"],
                    border_width=0
                )
        
        # Editörleri güncelle
        for editor in self.editors.values():
            editor.apply_theme(theme)

    # === Görünüm Eylemleri (Editör Ayarları) ===

    def _toggle_editor_feature(self, feature_method_name: str) -> Optional[bool]:
        current_editor = self.get_current_editor()
        if not current_editor:
            return None
            
        method = getattr(current_editor, feature_method_name)
        new_state = method()
        
        for editor in self.editors.values():
            getattr(editor, feature_method_name)(new_state)
            
        return new_state

    def toggle_line_numbers(self): return self._toggle_editor_feature('toggle_line_numbers')
    def toggle_minimap(self): return self._toggle_editor_feature('toggle_minimap')
    def toggle_word_wrap(self): return self._toggle_editor_feature('toggle_word_wrap')

    def get_view_states(self) -> Dict[str, Any]:
        editor = self.get_current_editor()
        if editor:
            return editor.get_view_states()
        return {"line_numbers": True, "minimap": True, "word_wrap": False}

    # === Editör Proxy Yöntemleri ===

    def _proxy_editor_action(self, action_name: str):
        editor = self.get_current_editor()
        if editor and hasattr(editor, action_name):
            getattr(editor, action_name)()

    def duplicate_line(self): self._proxy_editor_action('duplicate_line')
    def move_line_up(self): self._proxy_editor_action('move_line_up')
    def move_line_down(self): self._proxy_editor_action('move_line_down')
    def delete_line(self): self._proxy_editor_action('delete_line')
    def join_lines(self): self._proxy_editor_action('join_lines')

    def show_goto_line(self):
        editor = self.get_current_editor()
        if editor:
            from text_editor.ui.goto_line import GoToLineDialog
            GoToLineDialog(self, editor)

    def show_find_replace(self):
        from text_editor.ui.search_dialog import SearchDialog
        SearchDialog(self)

    def update_language(self):
        """Bütün sekmelerin isimlerini o anki dile göre günceller."""
        for name in list(self.editors.keys()):
            self._update_tab_visuals(name)
