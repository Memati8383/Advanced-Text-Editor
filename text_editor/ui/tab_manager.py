import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List, Dict, Any, Callable

import customtkinter as ctk

from text_editor.ui.editor import CodeEditor
from text_editor.utils.file_monitor import FileMonitor
from text_editor.theme_config import DARK_THEME
try:
    from text_editor.utils.file_icons import FileIcons
except ImportError:
    FileIcons = None

# Günlüğe kaydetmeyi yapılandır
logger = logging.getLogger(__name__)

# Sabitler
AUTO_SAVE_INTERVAL_MS = 30000  # 30 seconds
NEW_TAB_PREFIX = "Adsız"
DEFAULT_FONT = ("Segoe UI", 13)

class TabManager(ctk.CTkTabview):
    """
    Birden fazla sekmeyi ve kod editörünü yönetir.
    Her sekme bağımsız bir CodeEditor örneği içerir.
    Dosya açma, kaydetme, otomatik kaydetme ve dosya izleme işlemlerini yönetir.
    """

    def __init__(self, master, status_callback: Callable[[str, str], None] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.status_callback = status_callback
        self._init_state()
        
        # Create first tab
        self.add_new_tab()
        
        self._setup_ui()
        self._start_services()

    def _init_state(self):
        """Dahili durum değişkenlerini başlatır."""
        self.editors: Dict[str, CodeEditor] = {}
        self.current_theme = DARK_THEME
        self.untitled_count = 0

    def _setup_ui(self):
        """UI bileşenlerini ve stillerini yapılandırır."""
        self.configure(
            corner_radius=8,
            fg_color="transparent",
            segmented_button_fg_color="#181818",
            segmented_button_selected_color="#1e1e1e",
            segmented_button_selected_hover_color="#252526",
            segmented_button_unselected_color="#181818",
            segmented_button_unselected_hover_color="#2d2d2d",
            text_color="#d4d4d4"
        )
        self._segmented_button.configure(font=DEFAULT_FONT)

    def _start_services(self):
        """Arka plan hizmetlerini başlatır (Dosya izleyici, Otomatik kaydetme)."""
        self.file_monitor = FileMonitor(self.on_file_changed)
        self.after(AUTO_SAVE_INTERVAL_MS, self.auto_save_loop)

    # === Yardımcı Yöntemler ===

    def _update_status(self, message: str, status_type: str = "info", timeout: int = 0):
        """
        Durum çubuğunu geri çağırma veya geri dönüş (fallback) kullanarak güvenli bir şekilde günceller.
        """
        if self.status_callback:
            try:
                self.status_callback(message, status_type)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
        else:
            # Geri çekilme (Gevşek bağlantı girişimi)
            try:
                main_window = self.winfo_toplevel()
                if hasattr(main_window, 'status_bar') and main_window.status_bar:
                    main_window.status_bar.set_message(message, status_type)
            except Exception as e:
                logger.debug(f"Status update fallback failed: {e}")

        if timeout > 0:
            self.after(timeout, lambda: self._update_status("Hazır", "ready"))

    def _get_tab_order(self) -> List[str]:
        """Sekmelerin görsel sırasını döndürür."""
        try:
            return self._segmented_button._value_list
        except AttributeError:
            return list(self.editors.keys())

    def get_current_tab_name(self) -> str:
        """Aktif sekmenin adını (ID) döndürür."""
        return self.get()

    def get_current_editor(self) -> Optional[CodeEditor]:
        """Aktif kod editörü örneğini döndürür."""
        name = self.get_current_tab_name()
        return self.editors.get(name)

    def _copy_to_clipboard(self, text: str, success_message: str):
        """Metni panoya kopyalar ve kullanıcıyı bilgilendirir."""
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
        if editor.file_path:
            display_name = os.path.basename(editor.file_path)
            icon = FileIcons.get_icon(display_name) if FileIcons else "📄"
        else:
            display_name = tab_name # Dahili isme geri dön (örn. Adsız-1)
            icon = "📝"

        # Değişiklik Göstergesi
        dirty_marker = " * " if editor.content_modified else " "
        
        # Metni ayarla: "🐍 script.py *"
        final_text = f"{icon} {display_name}{dirty_marker}"
        
        # Buton metnini doğrudan güncelle
        try:
            if hasattr(self, "_segmented_button") and tab_name in self._segmented_button._buttons_dict:
                self._segmented_button._buttons_dict[tab_name].configure(text=final_text)
        except Exception as e:
            logger.error(f"Failed to update tab visuals: {e}")

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
            self.untitled_count += 1
            name = f"{NEW_TAB_PREFIX}-{self.untitled_count}"
        
        # Benzersiz dahili isim/ID sağla
        name = self._ensure_unique_name(name)

        # Sekme ekle
        self.add(name)
        self.set(name)
        
        # Editör oluştur
        self._create_editor_in_tab(name)
        
        # Olayları bağla
        self._bind_tab_events(name)
        
        # İlk görsel güncelleme
        self._update_tab_visuals(name)
        
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
        if hasattr(self, "_segmented_button") and tab_name in self._segmented_button._buttons_dict:
            btn = self._segmented_button._buttons_dict[tab_name]
            
            # Sağ tık - Bağlam Menüsü
            btn.bind("<Button-3>", lambda e, n=tab_name: self.show_context_menu(e, n))
            
            # Orta tık - Sekmeyi Kapat
            btn.bind("<Button-2>", lambda e, n=tab_name: self.check_and_close_tab(n)) 
            # Not: Button-2 genellikle Windows'ta orta tıklamadır, bazı Linux yapılandırmalarında Button-3 olabilir.
            # Kapsam için Button-2 ekleniyor.

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

        # "Kirli" (değiştirilmiş) durumunu güncellemek için değişiklikleri dinle
        # Bir proxy geri çağrısı ile metin widget'ının olaylarına bağlanıyoruz
        # CodeEditor zaten <<Change>> olayını bağladığından, mantığımızı ekleyebilir veya KeyRelease olayına bağlayabiliriz
        editor.text_area.bind("<KeyRelease>", lambda e: self._on_editor_content_changed(tab_name), add="+")
        
        # Ayrıca editör mantığı tarafından yayınlanıyorsa özel <<Change>> olayına da bağlan
        editor.text_area.bind("<<Change>>", lambda e: self._on_editor_content_changed(tab_name), add="+")

    def _on_editor_content_changed(self, tab_name: str):
        """Editör içeriği değiştiğinde çağrılır."""
        self._update_tab_visuals(tab_name)

    def show_context_menu(self, event, tab_name: str):
        """Bir sekme için bağlam menüsünü gösterir."""
        menu = tk.Menu(self, tearoff=0)
        
        # Kapatma
        menu.add_command(label=f"Kapat", command=lambda: self.check_and_close_tab(tab_name))
        menu.add_command(label="Diğerlerini Kapat", command=lambda: self.close_others(tab_name))
        menu.add_command(label="Sağdakileri Kapat", command=lambda: self.close_right(tab_name))
        menu.add_separator()
        
        # Kopyalama
        menu.add_command(label="📋 Dosya Yolunu Kopyala", command=lambda: self.copy_path(tab_name))
        menu.add_command(label="📋 Dosya Adını Kopyala", command=lambda: self.copy_filename(tab_name))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # === Sekme Kapatma Mantığı ===

    def check_and_close_tab(self, name: str):
        """
        Sekmeyi kapatmadan önce kaydedilmemiş değişiklikleri kontrol eder.
        """
        if name not in self.editors:
            return

        editor = self.editors[name]
        if editor.content_modified:
            display_name = os.path.basename(editor.file_path) if editor.file_path else name
            response = messagebox.askyesnocancel(
                "Kaydedilmemiş Değişiklikler",
                f"'{display_name}' dosyasında kaydedilmemiş değişiklikler var.\nKapatmadan önce kaydetmek ister misiniz?"
            )
            
            if response is None: # İptal
                return
            elif response is True: # Evet
                if editor.file_path:
                    editor.save_file()
                else:
                    self.set(name) # Farklı kaydetmek için odaklan
                    self.save_current_file_as()
                    # Kaydetmenin başarılı olup olmadığını kontrol et (dosya yolu ayarlandı ve değiştirilmedi)
                    if editor.content_modified: # Kullanıcı kaydetme iletişim kutusunu iptal etti
                        return

        # Kapatmaya devam et
        self.close_tab(name)

    def close_tab(self, name: str):
        """Sekmeyi kapatır ve kaynakları temizler."""
        self.delete(name)
        if name in self.editors:
            del self.editors[name]
        
        # Eğer hiç sekme kalmadıysa, yeni bir tane oluştur
        if not self.editors:
            self.add_new_tab()

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
        """Tam dosya yolunu kopyalar."""
        editor = self.editors.get(name or self.get_current_tab_name())
        if editor and editor.file_path:
            self._copy_to_clipboard(editor.file_path, "Dosya yolu kopyalandı")
            return True
        self._update_status("Dosya kaydedilmemiş", "warning")
        return False

    def copy_relative_path(self, name: str = None) -> bool:
        """Dosya yolunu proje köküne göre kopyalar."""
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
        """Sadece dosya adını kopyalar."""
        editor = self.editors.get(name or self.get_current_tab_name())
        if editor and editor.file_path:
            filename = os.path.basename(editor.file_path)
            self._copy_to_clipboard(filename, "Dosya adı kopyalandı")
            return True
        self._update_status("Dosya kaydedilmemiş", "warning")
        return False

    # === Dosya İşlemleri ===

    def open_file(self, path: str = None):
        """Bir dosya açar. Zaten açıksa odaklanır. Değilse yeni sekmede açar."""
        file_path = path or filedialog.askopenfilename()
        if not file_path:
            return

        # Zaten açık mı kontrol et
        for name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(file_path):
                self.set(name)
                return

        # Boş ve isimsiz ise mevcut olanı yeniden kullan
        if self._should_use_current_tab():
            # Sadece mevcut olanın içine yükle
            current_name = self.get_current_tab_name()
            self._load_file_into_tab(current_name, file_path)
        else:
            # Yeni sekme mantığını aç
            self._load_file_into_new_tab(file_path)

    def _should_use_current_tab(self) -> bool:
        """Mevcut sekmenin yeni bir dosya için kullanılıp kullanılamayacağını belirler."""
        current_name = self.get_current_tab_name()
        current_editor = self.get_current_editor()
        
        # ID kontrolü (isimsiz) + içerik kontrolü
        return (NEW_TAB_PREFIX in current_name and 
                current_editor and 
                not current_editor.content_modified and 
                len(current_editor.text_area.get("1.0", "end-1c")) == 0)

    def _load_file_into_tab(self, tab_name: str, file_path: str):
        """Bir dosyayı mevcut bir sekmeye/editöre yükler."""
        editor = self.editors[tab_name]
        editor.load_file(file_path)
        editor.file_path = file_path
        editor.set_lexer_from_file(file_path)
        
        self.file_monitor.add_file(file_path)
        self._update_tab_visuals(tab_name)

    def _load_file_into_new_tab(self, file_path: str):
        """Yeni bir sekme oluşturur ve dosyayı yükler."""
        # İlk ID için temel olarak dosya adını kullan, ancak benzersiz olduğundan emin ol
        filename = os.path.basename(file_path)
        tab_name = self.add_new_tab(filename)
        self._load_file_into_tab(tab_name, file_path)

    def save_current_file(self):
        """Mevcut dosyayı kaydeder."""
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
        """
        Farklı Kaydet iletişim kutusu. Sekmeyi yok etmeden (geri alma geçmişini/durumunu koruyarak)
        editör yolunu ve sekme başlığını günceller.
        """
        editor = self.get_current_editor()
        if not editor:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file_path:
            return

        # Yeni yola kaydet
        old_path = editor.file_path
        editor.file_path = file_path
        
        if editor.save_file():
            # Editör durumunu güncelle
            editor.set_lexer_from_file(file_path)
            
            # Dosya izleyiciyi değiştir
            if old_path:
                self.file_monitor.remove_file(old_path)
            self.file_monitor.add_file(file_path)
            
            # Görselleri güncelle (Başlık, İkon)
            current_tab_name = self.get_current_tab_name()
            self._update_tab_visuals(current_tab_name)
            
            self._update_status(f"Farklı kaydedildi: {os.path.basename(file_path)}", "success")

    def on_file_changed(self, path: str):
        """Harici dosya değişiklikleri için geri çağrı."""
        self.after(0, lambda: self.handle_file_change(path))

    def handle_file_change(self, path: str):
        """Harici dosya değişikliklerini işler."""
        if not os.path.exists(path):
            return

        for name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(path):
                # Kendi kaydettiğimiz değişiklik mi?
                try:
                    current_mtime = os.path.getmtime(path)
                    # Eğer son kaydettiğimiz zaman ile şimdiki zaman kaba taslak aynıysa (fark < 2sn), yoksay
                    if hasattr(editor, 'last_mtime') and abs(current_mtime - editor.last_mtime) < 2.0:
                        return
                except OSError:
                    pass

                # Değişiklik oldu, kullanıcıya sor
                display_name = os.path.basename(editor.file_path)
                if messagebox.askyesno("Dosya Değişti", f"'{display_name}' dosyası harici olarak değiştirildi.\nYeniden yüklemek ister misiniz?"):
                    editor.load_file(path)
                    self._update_tab_visuals(name)
                break

    # === Görünüm ve Tema ===

    def apply_theme(self, theme: Dict[str, Any]):
        """TabManager ve tüm editörlere temayı uygular."""
        self.current_theme = theme
        
        self.configure(
            segmented_button_fg_color=theme["tab_bg"],
            segmented_button_selected_color=theme["tab_selected"],
            segmented_button_selected_hover_color=theme["tab_selected"],
            segmented_button_unselected_color=theme["tab_bg"],
            segmented_button_unselected_hover_color=theme["tab_hover"],
            text_color=theme["fg"]
        )
        
        for editor in self.editors.values():
            editor.apply_theme(theme)

    # === Görünüm Eylemleri (Satır Numaraları, Minimap vb.) ===

    def _toggle_editor_feature(self, feature_method_name: str) -> Optional[bool]:
        """Bir özelliği tüm editörlerde açar/kapatır."""
        current_editor = self.get_current_editor()
        if not current_editor:
            return None
            
        method = getattr(current_editor, feature_method_name)
        new_state = method() # Aktif editörü değiştir
        
        # Diğerlerini senkronize et
        for editor in self.editors.values():
            getattr(editor, feature_method_name)(new_state)
            
        return new_state

    def toggle_line_numbers(self): return self._toggle_editor_feature('toggle_line_numbers')
    def toggle_minimap(self): return self._toggle_editor_feature('toggle_minimap')
    def toggle_word_wrap(self): return self._toggle_editor_feature('toggle_word_wrap')

    def get_view_states(self) -> Dict[str, Any]:
        """Mevcut görünüm durumlarını döndürür."""
        editor = self.get_current_editor()
        if editor:
            return editor.get_view_states()
        return {"line_numbers": True, "minimap": True, "word_wrap": False}

    # === Editör Proxy Yöntemleri ===

    def _proxy_editor_action(self, action_name: str):
        """Bir eylem dizesini mevcut editör örneğine proxy eder."""
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
