import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from text_editor.ui.editor import CodeEditor
from text_editor.utils.file_monitor import FileMonitor
from text_editor.theme_config import DARK_THEME

class TabManager(ctk.CTkTabview):
    """
    Çoklu sekme ve editör yönetimini sağlayan sınıf.
    Her sekme kendi bağımsız CodeEditor örneğini barındırır.
    Dosya açma, kaydetme, otomatik kayıt ve dosya izleme işlemlerini yönetir.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.editors = {} # Sekme adını CodeEditor örneğiyle eşleştir
        self.current_theme = DARK_THEME
        self.untitled_count = 0
        
        self.file_monitor = FileMonitor(self.on_file_changed)
        
        # Otomatik kayıt sayacı
        self.auto_save_interval = 30000 # 30 saniye
        self.after(self.auto_save_interval, self.auto_save_loop)

        # İlk sekme
        self.add_new_tab()
        
        # Modern Stil (Sekme ekledikten sonra veya güvenli bir şekilde yapılandır)
        # Aslında CTkTabview hatası: oluşturulursa geçerli sekmenin ayarlanması gerekir mi?
        # Güvenli bahis: Önce temelleri yapılandırın, ancak renkler iç duruma bağlı olabilir mi?
        # Hata, _current_name'in başlangıçta boş dize olduğunu ima ediyor.
        # İlk sekmeyi ekledikten SONRA yapılandırmayı deneyelim.
        
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
        self._segmented_button.configure(font=("Segoe UI", 13))

    def auto_save_loop(self):
        """
        Belirli aralıklarla (varsayılan 30sn) değişiklik yapılmış dosyaları otomatik kaydeder.
        Sessizce çalışır ve durum çubuğunu günceller.
        """
        for editor in self.editors.values():
            if editor.file_path and editor.content_modified:
                # Sessizce kaydedebilir veya ayarı kontrol edebiliriz
                # Şimdilik sessiz kayıt
                editor.save_file()
                
                # Ana pencere üzerinden durum çubuğunu güncelle
                try:
                    # winfo_toplevel kullanarak MainWindow'a doğrudan eriş
                    main_window = self.winfo_toplevel()
                    if hasattr(main_window, 'status_bar') and main_window.status_bar:
                        main_window.status_bar.set_message(f"Kaydedildi: {os.path.basename(editor.file_path)}", "success")
                        # 2 saniye sonra sıfırla
                        self.after(2000, lambda: main_window.status_bar.set_message("Hazır", "ready") if hasattr(main_window, 'status_bar') and main_window.status_bar else None)
                except Exception as e:
                    print(f"Auto-save status update error: {e}")
                    print(f"Auto-saved {editor.file_path}")
        
        self.after(self.auto_save_interval, self.auto_save_loop)

    def add_new_tab(self, name=None):
        """
        Yeni bir sekme ve içinde yeni bir CodeEditor oluşturur.
        Eğer isim verilmezse "Adsız-X" şeklinde isimlendirir.
        """
        if name is None:
            self.untitled_count += 1
            name = f"Adsız-{self.untitled_count}"
        
        # Benzersiz isim sağla
        original_name = name
        counter = 1
        while name in self.editors:
            name = f"{original_name} ({counter})"
            counter += 1

        self.add(name)
        self.set(name)
        
        # Sağ Tıklamayı Sekme Düğmesine Bağla
        # CTk yapısında bu sekme için özel düğmeyi bulmamız gerekiyor
        # self._segmented_button._buttons_dict[name] düğmedir
        if hasattr(self, "_segmented_button") and name in self._segmented_button._buttons_dict:
            btn = self._segmented_button._buttons_dict[name]
            btn.bind("<Button-3>", lambda e, n=name: self.show_context_menu(e, n))
        
        # Yeni sekmede Editör Oluştur
        tab_frame = self.tab(name)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        editor = CodeEditor(tab_frame)
        if self.current_theme:
            editor.apply_theme(self.current_theme)
        editor.grid(row=0, column=0, sticky="nsew")
        
        self.editors[name] = editor
        return name

    def show_context_menu(self, event, tab_name):
        """Sekme başlığına sağ tıklandığında açılan menüyü gösterir."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Kapat '{tab_name}'", command=lambda: self.close_tab(tab_name))
        menu.add_command(label="Diğerlerini Kapat", command=lambda: self.close_others(tab_name))
        menu.add_command(label="Sağdakileri Kapat", command=lambda: self.close_right(tab_name))
        menu.add_separator()
        menu.add_command(label="📋 Dosya Yolunu Kopyala", command=lambda: self.copy_path(tab_name))
        menu.add_command(label="📋 Göreli Yolu Kopyala", command=lambda: self.copy_relative_path(tab_name))
        menu.add_command(label="📋 Dosya Adını Kopyala", command=lambda: self.copy_filename(tab_name))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def close_tab(self, name):
        # Kaydedilmemiş değişiklikleri kontrol etmeye izin verilsin mi?
        # Şimdilik doğrudan kapat veya mantık kullan
        self.delete(name)
        if name in self.editors:
            del self.editors[name]

    def close_others(self, keeper_name):
        """Belirtilen sekme hariç diğer tüm sekmeleri kapatır."""
        # Kapatılacak sekmelerin listesi
        # yineleme sırasında self.editors anahtarları değişebilir, bu yüzden listeyi kopyala
        all_tabs = list(self.editors.keys())
        for tab in all_tabs:
            if tab != keeper_name:
                self.close_tab(tab)

    def close_right(self, boundary_name):
        """Belirtilen sekmenin sağındaki tüm sekmeleri kapatır."""
        all_tabs = list(self.editors.keys())
        # CTkTabview, editors sözlüğünde sırayı kesin olarak garanti etmez,
        # ancak _segmented_button._value_list genellikle sırayı tutar.
        try:
            ordered_tabs = self._segmented_button._value_list
        except:
            ordered_tabs = all_tabs
            
        start_closing = False
        for tab in ordered_tabs:
            if start_closing:
                self.close_tab(tab)
            if tab == boundary_name:
                start_closing = True

    def copy_path(self, name=None):
        """Dosyanın tam yolunu panoya kopyalar."""
        if name is None:
            name = self.get_current_tab_name()
        
        editor = self.editors.get(name)
        if editor and editor.file_path:
            self.clipboard_clear()
            self.clipboard_append(editor.file_path)
            self.update()
            self._show_copy_feedback("Dosya yolu kopyalandı")
            return True
        else:
            self._show_copy_feedback("Dosya kaydedilmemiş", "warning")
            return False
    
    def copy_relative_path(self, name=None):
        """Dosyanın göreli yolunu panoya kopyalar (proje klasörüne göre)."""
        if name is None:
            name = self.get_current_tab_name()
        
        editor = self.editors.get(name)
        if editor and editor.file_path:
            # Ana pencereden proje kökünü al
            try:
                main_window = self.winfo_toplevel()
                if hasattr(main_window, 'file_explorer') and main_window.file_explorer.root_path:
                    project_root = main_window.file_explorer.root_path
                    relative_path = os.path.relpath(editor.file_path, project_root)
                else:
                    # Proje kökü yoksa, çalışma dizinine göre al
                    relative_path = os.path.relpath(editor.file_path)
            except ValueError:
                # Farklı sürücülerde (Windows) ValueError olabilir
                relative_path = editor.file_path
            
            self.clipboard_clear()
            self.clipboard_append(relative_path)
            self.update()
            self._show_copy_feedback("Göreli yol kopyalandı")
            return True
        else:
            self._show_copy_feedback("Dosya kaydedilmemiş", "warning")
            return False
    
    def copy_filename(self, name=None):
        """Dosya adını panoya kopyalar."""
        if name is None:
            name = self.get_current_tab_name()
        
        editor = self.editors.get(name)
        if editor and editor.file_path:
            filename = os.path.basename(editor.file_path)
            self.clipboard_clear()
            self.clipboard_append(filename)
            self.update()
            self._show_copy_feedback("Dosya adı kopyalandı")
            return True
        else:
            self._show_copy_feedback("Dosya kaydedilmemiş", "warning")
            return False
    
    def copy_directory_path(self, name=None):
        """Dosyanın bulunduğu klasörün yolunu panoya kopyalar."""
        if name is None:
            name = self.get_current_tab_name()
        
        editor = self.editors.get(name)
        if editor and editor.file_path:
            dir_path = os.path.dirname(editor.file_path)
            self.clipboard_clear()
            self.clipboard_append(dir_path)
            self.update()
            self._show_copy_feedback("Klasör yolu kopyalandı")
            return True
        else:
            self._show_copy_feedback("Dosya kaydedilmemiş", "warning")
            return False
    
    def _show_copy_feedback(self, message, msg_type="success"):
        """Kopyalama işlemi için durum çubuğunda geri bildirim gösterir."""
        try:
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'status_bar') and main_window.status_bar:
                main_window.status_bar.set_message(message, msg_type)
        except:
            pass
            
    def get_current_tab_name(self):
        return self.get()

    def get_current_editor(self):
        name = self.get_current_tab_name()
        if name in self.editors:
            return self.editors[name]
        return None

    def open_file(self, path=None):
        """
        Bir dosyayı yeni bir sekmede açar.
        Eğer dosya zaten açıks o sekmeye odaklanır.
        Eğer mevcut sekme boş ve isimsiz ise onu kullanır.
        """
        file_path = path
        if not file_path:
            file_path = filedialog.askopenfilename()
            
        if file_path:
            filename = os.path.basename(file_path)
            # Zaten açık mı kontrol et
            for t_name, editor in self.editors.items():
                if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(file_path):
                    self.set(t_name)
                    return
            
            # Mevcut sekme boş ve isimsiz ise, onu kullan
            current_name = self.get_current_tab_name()
            current_editor = self.get_current_editor()
            
            # "Adsız" ve boş içerik olup olmadığını basit kontrol (yaklaşık)
            if "Adsız" in current_name and not current_editor.content_modified and \
               len(current_editor.text_area.get("1.0", "end-1c")) == 0:
                # Sekmeyi yeniden adlandır (CTk yeniden adlandırmayı kolayca desteklemez, bu yüzden kapat ve yeni aç)
                self.close_current_tab()
            
            tab_name = self.add_new_tab(filename)
            self.editors[tab_name].load_file(file_path)
            # Tam yolu editörde sakla
            self.editors[tab_name].file_path = file_path
            self.editors[tab_name].set_lexer_from_file(file_path)
            
            # Dosyayı izle
            self.file_monitor.add_file(file_path)

    def show_goto_line(self):
        editor = self.get_current_editor()
        if editor:
            from text_editor.ui.goto_line import GoToLineDialog
            GoToLineDialog(self, editor)

    def save_current_file(self):
        editor = self.get_current_editor()
        if editor:
            if editor.file_path:
                editor.save_file()
                # Güvenli status bar erişimi
                try:
                    main_window = self.winfo_toplevel()
                    if hasattr(main_window, 'status_bar') and main_window.status_bar:
                        main_window.status_bar.set_message(f"Kaydedildi: {os.path.basename(editor.file_path)}", "success")
                        self.after(2000, lambda: main_window.status_bar.set_message("Hazır", "ready") if hasattr(main_window, 'status_bar') and main_window.status_bar else None)
                except:
                    pass
            else:
                self.save_current_file_as()

    def save_current_file_as(self):
        """Aktif dosya için 'Farklı Kaydet' diyaloğunu açar."""
        editor = self.get_current_editor()
        if editor:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if file_path:
                editor.file_path = file_path
                editor.save_file()
                
                # Sekmeyi yeniden adlandırmamız gerekiyor mu kontrol et
                old_name = self.get_current_tab_name()
                new_name = os.path.basename(file_path)
                
                if old_name != new_name:
                    # Sekme yeniden adlandırma geçici çözümü: Yeni oluştur, içeriği taşı (veya yeniden yükle), eskisini kapat
                    # Yeniden yükleme tutarlılık için daha güvenlidir
                    self.add_new_tab(new_name)
                    new_editor = self.editors[new_name]
                    new_editor.text_area.insert("1.0", editor.text_area.get("1.0", "end-1c"))
                    new_editor.file_path = file_path
                    new_editor.set_lexer_from_file(file_path)
                    
                    # Eski sekmeyi kaldır
                    self.close_tab(old_name)
                    self.set(new_name)

    def close_current_tab(self):
        name = self.get_current_tab_name()
        if name:
            self.close_tab(name)

    def show_find_replace(self):
        # Bunu daha sonra uygulayacağız
        from text_editor.ui.search_dialog import SearchDialog
        SearchDialog(self)

    def on_file_changed(self, path):
        """Dosya izleyici (FileMonitor) tarafından dosya değişikliği algılandığında çağrılır."""
        # İş parçacığından çağrıldı, ana iş parçacığında zamanlamak için after kullanın
        self.after(0, lambda: self.handle_file_change(path))

    def handle_file_change(self, path):
        # Bu dosyanın açık olup olmadığını kontrol et
        for tab_name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(path):
                # Kullanıcıya sor
                response = messagebox.askyesno("File Changed", f"The file '{tab_name}' has been modified externally.\nDo you want to reload it?")
                if response:
                    editor.load_file(path)
                break

    def apply_theme(self, theme):
        """Mevcut temayı tüm açık editörlere ve sekme yöneticisinin kendisine uygular."""
        self.current_theme = theme
        
        # TabView'ın kendi stilini güncelle
        self.configure(
            segmented_button_fg_color=theme["tab_bg"],
            segmented_button_selected_color=theme["tab_selected"],
            segmented_button_selected_hover_color=theme["tab_selected"],
            segmented_button_unselected_color=theme["tab_bg"],
            segmented_button_unselected_hover_color=theme["tab_hover"],
            text_color=theme["fg"]
        )
        
        # Tüm açık editörleri güncelle
        for editor in self.editors.values():
            editor.apply_theme(theme)

    # === Satır İşlemleri (Menü Proxy Fonksiyonları) ===
    
    def duplicate_line(self):
        """Mevcut editörde satır çoğaltma işlemini tetikler."""
        editor = self.get_current_editor()
        if editor:
            editor.duplicate_line()
    
    def move_line_up(self):
        """Mevcut editörde satırı yukarı taşıma işlemini tetikler."""
        editor = self.get_current_editor()
        if editor:
            editor.move_line_up()
    
    def move_line_down(self):
        """Mevcut editörde satırı aşağı taşıma işlemini tetikler."""
        editor = self.get_current_editor()
        if editor:
            editor.move_line_down()
    
    def delete_line(self):
        """Mevcut editörde satır silme işlemini tetikler."""
        editor = self.get_current_editor()
        if editor:
            editor.delete_line()
    
    def join_lines(self):
        """Mevcut editörde satır birleştirme işlemini tetikler."""
        editor = self.get_current_editor()
        if editor:
            editor.join_lines()

    # === Görünüm Ayarları (Proxy Fonksiyonları) ===
    
    def toggle_line_numbers(self):
        """Tüm editörlerde satır numaralarını gösterir/gizler."""
        # Mevcut durumu al (ilk editörden)
        editor = self.get_current_editor()
        if not editor:
            return False
        
        new_state = editor.toggle_line_numbers()
        
        # Tüm editörlere uygula
        for ed in self.editors.values():
            ed.toggle_line_numbers(new_state)
        
        return new_state
    
    def toggle_minimap(self):
        """Tüm editörlerde minimap'i gösterir/gizler."""
        editor = self.get_current_editor()
        if not editor:
            return False
        
        new_state = editor.toggle_minimap()
        
        # Tüm editörlere uygula
        for ed in self.editors.values():
            ed.toggle_minimap(new_state)
        
        return new_state
    
    def toggle_word_wrap(self):
        """Tüm editörlerde satır sarmayı açar/kapatır."""
        editor = self.get_current_editor()
        if not editor:
            return False
        
        new_state = editor.toggle_word_wrap()
        
        # Tüm editörlere uygula
        for ed in self.editors.values():
            ed.toggle_word_wrap(new_state)
        
        return new_state
    
    def get_view_states(self):
        """Mevcut görünüm durumlarını döndürür."""
        editor = self.get_current_editor()
        if editor:
            return editor.get_view_states()
        return {
            "line_numbers": True,
            "minimap": True,
            "word_wrap": False
        }
