import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from text_editor.config import FONT_FAMILY, FONT_SIZE
from text_editor.utils.highlighter import SyntaxHighlighter
from text_editor.utils.autocompleter import AutoCompleter
from text_editor.ui.minimap import Minimap
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, TextLexer

class LineNumbers(tk.Text):
    """
    Ana metin editörünün sol tarafında satır numaralarını gösteren bileşen.
    Metin editörü ile senkronize çalışır ve sadece görünür satırları çizer.
    Ayrıca kod katlama (folding) işaretçilerini de gösterir.
    """
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=8, padx=4, highlightthickness=0, bd=0, 
                         font=(FONT_FAMILY, FONT_SIZE), state="disabled", cursor="arrow", wrap="none", **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind("<<Change>>", self.redraw)
        self.text_widget.bind("<Configure>", self.redraw)
        self.bind("<Button-1>", self.on_click)

    def redraw(self, *args):
        """
        Satır numaralarını yeniden çizer.
        Performans için sadece o anda ekranda görünen satırları işler.
        Metin içeriği değiştiğinde veya kaydırma yapıldığında çağrılır.
        """
        self.configure(state="normal")
        self.delete("1.0", "end")
        
        i = self.text_widget.index("@0,0")
        try:
             # Durdurma koşulunu belirlemek için son görünür satır indeksini tanımla
            end_index = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
        except:
             return

        while True:
            # Dosyanın sonunu veya görünür alanı geçip geçmediğimizi kontrol et
            if self.text_widget.compare(i, ">", end_index) and self.text_widget.compare(i, "!=", end_index):
               break
               
            # EOF (Dosya Sonu) için ek güvenlik
            if self.text_widget.compare(i, "==", "end"):
                break

            dline = self.text_widget.dlineinfo(i)
            
            # Sadece görünürse çiz (dline None değilse)
            if dline is not None:
                linenum = str(i).split(".")[0]
                
                # Katlama özelliğini kontrol et
                marker = "  " # Hizalama için 2 boşluk
                if self.master.is_line_foldable(int(linenum)):
                    if self.master.is_line_folded(int(linenum)):
                        marker = "▶ " # Kapalı
                    else:
                        marker = "▼ " # Açık

                # Biçimlendirme: İşaretçi Sol, Satır Numarası Sağ
                # "marker linenum"
                display_text = f"{marker}{linenum:>4}\n"
                self.insert("end", display_text)
            
            # Gizli olsa bile mantıksal satırı her zaman artır
            i = self.text_widget.index(f"{i}+1line")

        self.configure(state="disabled")

    def on_click(self, event):
        """
        Satır numaraları alanına tıklama olayını işler.
        Özellikle kod katlama (folding) oklarına tıklanıp tıklanmadığını kontrol eder.
        """
        # Tıklanan y konumundan kesin satır numarasını belirle
        index = self.index(f"@{event.x},{event.y}")
        line_idx = int(index.split('.')[0])
        
        line_content = self.get(f"{line_idx}.0", f"{line_idx}.end")
        if not line_content.strip():
            return
            
        try:
            # "▼   10" veya "     10" içinden sayıyı ayıkla
            # Boşluklara göre ayır ve sayı olan kısmı bul
            parts = line_content.split()
            actual_line_num = None
            for p in parts:
                if p.isdigit():
                    actual_line_num = int(p)
                    break
            
            if actual_line_num:
                self.master.toggle_fold(actual_line_num)
        except ValueError:
            pass

class CodeEditor(ctk.CTkFrame):
    """
    Sözdizimi vurgulama, satır numaraları, minimap ve otomatik tamamlama
    özelliklerine sahip gelişmiş metin editörü bileşeni.
    """
    def __init__(self, master, file_path=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.file_path = file_path
        self.content_modified = False
        self.font_size = FONT_SIZE
        
        # Çoklu imleç desteği
        self.cursors = []  # [(satır, sütun), ...] formatında imleç pozisyonları
        self.cursor_tags = []  # İmleçlerin görsel işaretçileri
        self.multi_cursor_mode = False  # Çoklu imleç modunda mıyız?
        
        # Yerleşimi yapılandır
        self.grid_columnconfigure(0, weight=0) # Satır numaraları
        self.grid_columnconfigure(1, weight=1) # Metin alanı
        self.grid_columnconfigure(3, weight=0) # Minimap (Sağ taraf)
        self.grid_rowconfigure(0, weight=1)

        # Metin Alanı (Daha iyi etiket desteği için standart tk.Text kullanılıyor)
        # Bir çerçeveye mi saracağız yoksa doğrudan mı yerleştireceğiz? Doğrudan ızgaraya yerleştiriliyor.
        self.text_area = tk.Text(self, wrap="none", undo=True, font=(FONT_FAMILY, self.font_size),
                                 bd=0, highlightthickness=0, padx=5, pady=5)
        self.text_area.grid(row=0, column=1, sticky="nsew")

        # Satır Numaraları
        self.line_numbers = LineNumbers(self, self.text_area) # text_widget'ı doğrudan geçir
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        # LineNumbers'ı bağla (__init__ içinde zaten yapıldı, ancak referans için gerekirse saklayın veya kaldırın)
        # self.line_numbers.text_widget = self.text_area

        # Kaydırma çubukları
        self.scrollbar_y = ctk.CTkScrollbar(self, command=self.on_scroll_y)
        self.scrollbar_y.grid(row=0, column=2, sticky="ns")
        
        # Minimap
        self.minimap = Minimap(self, self.text_area)
        self.minimap.grid(row=0, column=3, sticky="ns")
        
        self.scrollbar_x = ctk.CTkScrollbar(self, command=self.text_area.xview, orientation="horizontal")
        self.scrollbar_x.grid(row=1, column=1, sticky="ew")
        
        self.text_area.configure(yscrollcommand=self.on_text_scroll, xscrollcommand=self.scrollbar_x.set)
        self.line_numbers.configure(yscrollcommand=self.on_line_scroll)
        # Minimap kaydırması on_text_scroll kancalarıyla yönetilir
        
        # Editörün ana metin alanı ile satır numaraları ve minimap arasındaki
        # kaydırma senkronizasyonunu sağlar.

        # Sözdizimi Vurgulayıcı
        self.highlighter = SyntaxHighlighter(self.text_area)
        
        # Otomatik Tamamlayıcı
        self.completer = AutoCompleter(self.text_area)
        
        # Olaylar
        self.text_area.bind("<<Change>>", self.on_content_change)
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<Key>", self.on_key_press)
        self.text_area.bind("<ButtonRelease-1>", self.on_click)
        
        # Yakınlaştırma Olayları (Ctrl + Tekerlek)
        self.text_area.bind("<Control-MouseWheel>", self.on_zoom)
        self.text_area.bind("<Control-Button-4>", lambda e: self.change_font_size(1))
        self.text_area.bind("<Control-Button-5>", lambda e: self.change_font_size(-1))
        
        # Çoklu İmleç Olayları
        self.text_area.bind("<Alt-Button-1>", self.add_cursor_at_click)  # Alt+Click ile imleç ekle
        self.text_area.bind("<Control-d>", self.select_next_occurrence)  # Ctrl+D ile kelime seç
        self.text_area.bind("<Escape>", self.clear_extra_cursors)  # Escape ile imlçleri temizle
        
        # Satır İşlemleri Kısayolları
        self.text_area.bind("<Control-Shift-D>", self.duplicate_line)  # Satırı çoğalt
        self.text_area.bind("<Alt-Up>", self.move_line_up)  # Satırı yukarı taşı
        self.text_area.bind("<Alt-Down>", self.move_line_down)  # Satırı aşağı taşı
        self.text_area.bind("<Control-Shift-K>", self.delete_line)  # Satırı sil
        self.text_area.bind("<Control-j>", self.join_lines)  # Satırları birleştir
        
        # İlk Kurulum
        if file_path:
            self.load_file(file_path)
            self.set_lexer_from_file(file_path)
        else:
            self.set_lexer_by_name("text")

    def set_lexer_from_file(self, filename):
        """Dosya uzantısına göre uygun sözdizimi vurgulayıcıyı (lexer) ayarlar."""
        lexer = self.highlighter.set_lexer_from_filename(filename)
        self.minimap.set_lexer(lexer)
        if lexer and self.completer:
            self.completer.set_language(lexer.name)
            
    def set_lexer_by_name(self, name):
        lexer = self.highlighter.set_lexer_by_name(name)
        self.minimap.set_lexer(lexer)
        if lexer and self.completer:
            self.completer.set_language(lexer.name)

    def on_key_press(self, event):
        """
        Tuş basımlarını yakalar ve özel işlemler (otomatik tamamlama, 
        akıllı girinti, parantez kapatma) uygular.
        Çoklu imleç modunda ise tüm imlçlere aynı işlemi uygular.
        """
        # Çoklu imleç modunda yazı yazma
        if self.multi_cursor_mode and len(self.cursors) > 0:
            if event.char and not event.state & 0x4:  # Ctrl tuşu basılı değilse
                self.insert_at_all_cursors(event.char)
                return "break"
            elif event.keysym == "BackSpace":
                self.delete_at_all_cursors("backspace")
                return "break"
            elif event.keysym == "Delete":
                self.delete_at_all_cursors("delete")
                return "break"
        
        # Önce otomatik tamamlama gezinme kontrolü
        res = self.completer.handle_key(event)
        if res == "break":
            return "break"
            
        # Parantezleri otomatik kapatma
        char = event.char
        pairs = {
            '(': ')',
            '{': '}',
            '[': ']',
            '"': '"',
            "'": "'"
        }
        
        if char in pairs:
            self.text_area.insert("insert", pairs[char])
            self.text_area.mark_set("insert", "insert-1c")
            
        # Akıllı Girinti
        if event.keysym == "Return":
            # Mevcut satırı al
            current_idx = self.text_area.index("insert")
            line_idx = current_idx.split('.')[0]
            line_text = self.text_area.get(f"{line_idx}.0", "end-1c") # tüm satırı al
            
            # Basit girinti: önceki satır boşluklarıyla eşleştir
            indent = ""
            for char in line_text:
                if char in [' ', '\t']:
                    indent += char
                else:
                    break
            
            # Eğer : ile bitiyorsa ekstra girinti (Python'a özgü, ancak yeterince genel)
            if line_text.strip().endswith(":"):
                indent += "    "
            
            # Önce varsayılan enter işleminin yapılmasına izin verilsin mi? Hayır, araya girmemiz gerek
            self.text_area.after(1, lambda: self.text_area.insert("insert", indent))

    def on_content_change(self, event=None):
        self.content_modified = True
        self.update_line_numbers()
        self.update_status_bar()

    def update_line_numbers(self):
        self.line_numbers.redraw()
        
    def update_status_bar(self):
        # Mümkünse sekme yöneticisini / ana pencereyi bilgilendir
        pass

    def on_text_scroll(self, *args):
        self.scrollbar_y.set(*args)
        self.line_numbers.yview_moveto(args[0])
        self.minimap.on_scroll(*args)

    def on_line_scroll(self, *args):
        self.text_area.yview_moveto(args[0])
        self.scrollbar_y.set(*args)
        self.minimap.yview_moveto(args[0])

    def on_key_release(self, event=None):
        if event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R"]:
            self.content_modified = True
            self.minimap.update_content()
            
        self.update_line_numbers()
        self.update_status_bar()
        if event and event.keysym in ["Return", "BackSpace", "Delete", "space"]:
             self.highlighter.highlight()

    def on_click(self, event):
        self.highlighter.highlight_current_line()
        # Durum çubuğunda imleç konumunu güncelle
        try:
            index = self.text_area.index("insert")
            line, col = index.split('.')
            
            # Toplam satır sayısını al
            total_lines = int(self.text_area.index("end-1c").split('.')[0])
            
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'status_bar'):
                # Yeni API'yi kullan (total_lines parametresi ile)
                main_window.status_bar.set_cursor_info(line, col, total_lines)
                
                # Dosya tipini belirle ve güncelle
                if self.file_path:
                    from text_editor.utils.file_icons import FileIcons
                    import os
                    
                    filename = os.path.basename(self.file_path)
                    file_info = FileIcons.get_info(filename)
                    
                    main_window.status_bar.set_file_info(
                        file_info["type"], 
                        "UTF-8"
                    )
        except:
            pass

    def load_file(self, file_path):
        """Belirtilen yoldaki dosyayı okur ve editöre yükler."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_area.delete('1.0', 'end')
                self.text_area.insert('1.0', content)
                self.update_line_numbers()
                self.minimap.update_content()
                self.highlighter.highlight()
                self.content_modified = False
        except Exception as e:
            print(f"Error loading file: {e}")
            messagebox.showerror("Error", f"Could not load file: {e}")

    def save_file(self):
        """Editördeki içeriği mevcut dosya yoluna kaydeder."""
        if self.file_path:
            try:
                content = self.text_area.get('1.0', 'end-1c') # Sondaki fazladan yeni satırı alma
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.content_modified = False
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        return False

    def on_zoom(self, event):
        if event.delta > 0:
            self.change_font_size(1)
        else:
            self.change_font_size(-1)
        return "break"

    def change_font_size(self, delta):
        new_size = self.font_size + delta
        if 8 <= new_size <= 72:
            self.font_size = new_size
            new_font = (FONT_FAMILY, self.font_size)
            
            self.text_area.configure(font=new_font)
            self.line_numbers.configure(font=new_font)

    def on_scroll_y(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    # === Görünüm Ayarları ===
    
    def toggle_line_numbers(self, show=None):
        """
        Satır numaralarını gösterir/gizler.
        show: True (göster), False (gizle), None (tersine çevir)
        """
        if not hasattr(self, '_line_numbers_visible'):
            self._line_numbers_visible = True
        
        if show is None:
            self._line_numbers_visible = not self._line_numbers_visible
        else:
            self._line_numbers_visible = show
        
        if self._line_numbers_visible:
            self.line_numbers.grid(row=0, column=0, sticky="ns")
        else:
            self.line_numbers.grid_remove()
        
        return self._line_numbers_visible
    
    def toggle_minimap(self, show=None):
        """
        Minimap'i gösterir/gizler.
        show: True (göster), False (gizle), None (tersine çevir)
        """
        if not hasattr(self, '_minimap_visible'):
            self._minimap_visible = True
        
        if show is None:
            self._minimap_visible = not self._minimap_visible
        else:
            self._minimap_visible = show
        
        if self._minimap_visible:
            self.minimap.grid(row=0, column=3, sticky="ns")
        else:
            self.minimap.grid_remove()
        
        return self._minimap_visible
    
    def toggle_word_wrap(self, enable=None):
        """
        Satır sarma (word wrap) özelliğini açar/kapatır.
        enable: True (aç), False (kapat), None (tersine çevir)
        """
        if not hasattr(self, '_word_wrap_enabled'):
            self._word_wrap_enabled = False  # Varsayılan: kapalı
        
        if enable is None:
            self._word_wrap_enabled = not self._word_wrap_enabled
        else:
            self._word_wrap_enabled = enable
        
        if self._word_wrap_enabled:
            self.text_area.configure(wrap="word")
            # Word wrap açıkken yatay scrollbar'ı gizle
            self.scrollbar_x.grid_remove()
        else:
            self.text_area.configure(wrap="none")
            self.scrollbar_x.grid(row=1, column=1, sticky="ew")
        
        return self._word_wrap_enabled
    
    def get_view_states(self):
        """Mevcut görünüm durumlarını döndürür."""
        return {
            "line_numbers": getattr(self, '_line_numbers_visible', True),
            "minimap": getattr(self, '_minimap_visible', True),
            "word_wrap": getattr(self, '_word_wrap_enabled', False)
        }

    def apply_theme(self, theme):
        """
        Verilen tema sözlüğündeki renkleri editörün tüm bileşenlerine uygular.
        (Metin alanı, satır numaraları, minimap ve vurgulama stili)
        """
        # Metin Alanı renklerini güncelle
        self.text_area.configure(
            bg=theme["editor_bg"],
            fg=theme["editor_fg"],
            insertbackground=theme["caret"],
            selectbackground=theme.get("menu_hover", "#3c3c3c")
        )
        
        # Satır Numaraları renklerini güncelle
        self.line_numbers.configure(
            bg=theme["line_num_bg"],
            fg=theme["line_num_fg"]
        )
        
        # Minimap renklerini güncelle
        self.minimap.configure_colors(
            bg=theme["editor_bg"],
            fg=theme["fg"]
        )
        
        # Yeni arka planda sözdizimi renklerinin iyi görünmesini sağlamak için yeniden vurgula
        style_name = theme.get("pygments_style", "monokai")
        self.highlighter.update_style(style_name)
        self.minimap.update_style(style_name)

    # Katlama Uygulaması
    def is_line_foldable(self, line_num):
        """
        Bir satırın katlanabilir olup olmadığını girintisine (indentation) bakarak belirler.
        Eğer sonraki satırın girintisi daha fazlaysa, bu satır bir blok başlangıcıdır.
        """
        try:
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            if not line_text.strip():
                return False
                
            indent_current = len(line_text) - len(line_text.lstrip())
            
            # Girintiyi kontrol etmek için bir sonraki boş olmayan satırı bul
            next_line_num = line_num + 1
            while True:
                if self.text_area.compare(f"{next_line_num}.0", ">=", "end"):
                    return False # EOF'a ulaşıldı
                    
                next_line_text = self.text_area.get(f"{next_line_num}.0", f"{next_line_num}.end")
                if next_line_text.strip():
                    break
                next_line_num += 1
            
            indent_next = len(next_line_text) - len(next_line_text.lstrip())
            
            return indent_next > indent_current
        except Exception:
            return False

    def is_line_folded(self, line_num):
        """Bir satırın şu anda katlanmış durumda olup olmadığını kontrol eder."""
        tag_name = f"fold_{line_num}"
        ranges = self.text_area.tag_ranges(tag_name)
        return bool(ranges)

    def toggle_fold(self, line_num):
        """
        Belirtilen satırdaki kod bloğunu katlar veya açar.
        Katlama işlemi metni gizlemek (elide) için etiketler (tags) kullanır.
        """
        if not self.is_line_foldable(line_num):
            return

        tag_name = f"fold_{line_num}"
        
        if self.is_line_folded(line_num):
            # Katlamayı aç
            self.text_area.tag_delete(tag_name)
        else:
            # Katla
            # Başlangıç girintisini bul
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            start_indent = len(line_text) - len(line_text.lstrip())
            
            # Bitiş satırını bul
            current_line = line_num + 1
            while True:
                if self.text_area.compare(f"{current_line}.0", ">=", "end"):
                    break
                    
                content = self.text_area.get(f"{current_line}.0", f"{current_line}.end")
                
                # Eğer boş olmayan satır aynı veya daha az girintiye sahipse, blok bitti
                if content.strip():
                    curr_indent = len(content) - len(content.lstrip())
                    if curr_indent <= start_indent:
                        break
                
                current_line += 1
            
            # Blok line_num+1'den current_line-1'e kadardır
            # SONRAKİ satırdan başlayarak, kesme satırının başına kadar katlamak istiyoruz.
            # Yani aralık: line_num+1.0'dan current_line.0'a
            
            end_line = current_line
            
            self.text_area.tag_add(tag_name, f"{line_num+1}.0", f"{end_line}.0")
            self.text_area.tag_config(tag_name, elide=True)
            self.text_area.tag_raise(tag_name) # Katlamanın her şeyi gizlediğinden emin ol
            
        self.line_numbers.redraw()
        # Ayrıca minimap'i güncelle
        self.minimap.update_content()

    # === Çoklu İmleç İşlevleri ===
    
    def add_cursor_at_click(self, event):
        """
        Alt+Click ile tıklanan yere yeni bir imleç ekler.
        """
        # Tıklanan pozisyonu al
        index = self.text_area.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split('.'))
        
        # Bu pozisyonda zaten imleç var mı kontrol et
        cursor_pos = (line, col)
        if cursor_pos in self.cursors:
            # Varsa kaldır
            self.cursors.remove(cursor_pos)
        else:
            # Yoksa ekle
            self.cursors.append(cursor_pos)
        
        # Çoklu imleç modunu etkinleştir
        if len(self.cursors) > 0:
            self.multi_cursor_mode = True
        else:
            self.multi_cursor_mode = False
        
        self.update_cursor_visuals()
        return "break"
    
    def clear_extra_cursors(self, event=None):
        """
        Escape tuşu ile tüm ek imlçleri temizler.
        """
        self.cursors = []
        self.multi_cursor_mode = False
        self.update_cursor_visuals()
        return "break"
    
    def update_cursor_visuals(self):
        """
        Ekrandaki imleç görsellerini günceller.
        """
        # Önce eski cursor tag'lerini temizle
        for tag in self.cursor_tags:
            self.text_area.tag_delete(tag)
        self.cursor_tags = []
        
        # Yeni cursor tag'leri oluştur
        for i, (line, col) in enumerate(self.cursors):
            tag_name = f"cursor_{i}"
            self.cursor_tags.append(tag_name)
            
            # İmleç pozisyonunu işaretle
            try:
                self.text_area.tag_add(tag_name, f"{line}.{col}")
                self.text_area.tag_config(tag_name, background="#0078D7", foreground="white")
            except:
                pass
    
    def insert_at_all_cursors(self, char):
        """
        Tüm imlçlere aynı anda karakter ekler.
        """
        # Önce tüm pozisyonları güncelle (sondan başa doğru)
        self.cursors.sort(reverse=True)
        
        for i, (line, col) in enumerate(self.cursors):
            try:
                self.text_area.insert(f"{line}.{col}", char)
                # Pozisyonu güncelle
                self.cursors[i] = (line, col + len(char))
            except:
                pass
        
        # Ana imlece de ekle
        self.text_area.insert("insert", char)
        
        self.update_cursor_visuals()
    
    def delete_at_all_cursors(self, direction="backspace"):
        """
        Tüm imleçlerde silme işlemi yapar.
        direction: "backspace" veya "delete"
        """
        # Sondan başa doğru sıralayarak sil
        self.cursors.sort(reverse=True)
        
        for i, (line, col) in enumerate(self.cursors):
            try:
                if direction == "backspace" and col > 0:
                    self.text_area.delete(f"{line}.{col-1}", f"{line}.{col}")
                    self.cursors[i] = (line, col - 1)
                elif direction == "delete":
                    self.text_area.delete(f"{line}.{col}", f"{line}.{col+1}")
            except:
                pass
        
        # Ana imlçte de sil
        if direction == "backspace":
            self.text_area.delete("insert-1c", "insert")
        else:
            self.text_area.delete("insert", "insert+1c")
        
        self.update_cursor_visuals()
    
    # === Satır İşlemleri ===
    
    def duplicate_line(self, event=None):
        """
        Mevcut satırı (veya seçili satırları) kopyalayıp altına yapıştırır.
        Kısayol: Ctrl+Shift+D
        """
        try:
            # Seçili metin var mı kontrol et
            try:
                # Seçili satırları kopyala
                start_idx = self.text_area.index("sel.first linestart")
                end_idx = self.text_area.index("sel.last lineend")
                selected_lines = self.text_area.get(start_idx, end_idx)
            except tk.TclError:
                # Seçim yoksa, mevcut satırı al
                current_line = self.text_area.index("insert").split('.')[0]
                selected_lines = self.text_area.get(f"{current_line}.0", f"{current_line}.end")
                end_idx = f"{current_line}.end"
            
            # Satır sonunu ekle ve kopyalanan metni yapıştır
            self.text_area.insert(end_idx, "\n" + selected_lines)
            
            # İçerik değişikliğini bildir
            self.content_modified = True
            self.update_line_numbers()
            self.highlighter.highlight()
            self.minimap.update_content()
            
        except Exception as e:
            print(f"Satır çoğaltma hatası: {e}")
        
        return "break"
    
    def move_line_up(self, event=None):
        """
        Mevcut satırı (veya seçili satırları) bir üst satıra taşır.
        Kısayol: Alt+Up
        """
        try:
            # Mevcut satır bilgisini al
            current_pos = self.text_area.index("insert")
            current_line = int(current_pos.split('.')[0])
            
            # İlk satırsa taşıyamayız
            if current_line == 1:
                return "break"
            
            # Seçim varsa tüm seçili satırları taşı
            try:
                start_line = int(self.text_area.index("sel.first").split('.')[0])
                end_line = int(self.text_area.index("sel.last").split('.')[0])
                if start_line == 1:
                    return "break"
            except tk.TclError:
                start_line = current_line
                end_line = current_line
            
            # Taşınacak satırları al
            lines_text = self.text_area.get(f"{start_line}.0", f"{end_line}.end")
            
            # Üst satırı al
            upper_line_text = self.text_area.get(f"{start_line - 1}.0", f"{start_line - 1}.end")
            
            # Satırları değiştir
            self.text_area.delete(f"{start_line - 1}.0", f"{end_line}.end")
            self.text_area.insert(f"{start_line - 1}.0", lines_text + "\n" + upper_line_text)
            
            # İmleci yeni pozisyona taşı
            col = current_pos.split('.')[1]
            self.text_area.mark_set("insert", f"{current_line - 1}.{col}")
            
            # İçerik değişikliğini bildir
            self.content_modified = True
            self.update_line_numbers()
            self.highlighter.highlight()
            self.minimap.update_content()
            
        except Exception as e:
            print(f"Satır yukarı taşıma hatası: {e}")
        
        return "break"
    
    def move_line_down(self, event=None):
        """
        Mevcut satırı (veya seçili satırları) bir alt satıra taşır.
        Kısayol: Alt+Down
        """
        try:
            # Mevcut satır bilgisini al
            current_pos = self.text_area.index("insert")
            current_line = int(current_pos.split('.')[0])
            total_lines = int(self.text_area.index("end-1c").split('.')[0])
            
            # Son satırsa taşıyamayız
            if current_line >= total_lines:
                return "break"
            
            # Seçim varsa tüm seçili satırları taşı
            try:
                start_line = int(self.text_area.index("sel.first").split('.')[0])
                end_line = int(self.text_area.index("sel.last").split('.')[0])
                if end_line >= total_lines:
                    return "break"
            except tk.TclError:
                start_line = current_line
                end_line = current_line
            
            # Taşınacak satırları al
            lines_text = self.text_area.get(f"{start_line}.0", f"{end_line}.end")
            
            # Alt satırı al
            lower_line_text = self.text_area.get(f"{end_line + 1}.0", f"{end_line + 1}.end")
            
            # Satırları değiştir
            self.text_area.delete(f"{start_line}.0", f"{end_line + 1}.end")
            self.text_area.insert(f"{start_line}.0", lower_line_text + "\n" + lines_text)
            
            # İmleci yeni pozisyona taşı
            col = current_pos.split('.')[1]
            self.text_area.mark_set("insert", f"{current_line + 1}.{col}")
            
            # İçerik değişikliğini bildir
            self.content_modified = True
            self.update_line_numbers()
            self.highlighter.highlight()
            self.minimap.update_content()
            
        except Exception as e:
            print(f"Satır aşağı taşıma hatası: {e}")
        
        return "break"
    
    def delete_line(self, event=None):
        """
        Mevcut satırı (veya seçili satırları) siler.
        Kısayol: Ctrl+Shift+K
        """
        try:
            # Seçim varsa tüm seçili satırları sil
            try:
                start_line = int(self.text_area.index("sel.first").split('.')[0])
                end_line = int(self.text_area.index("sel.last").split('.')[0])
            except tk.TclError:
                current_pos = self.text_area.index("insert")
                start_line = int(current_pos.split('.')[0])
                end_line = start_line
            
            total_lines = int(self.text_area.index("end-1c").split('.')[0])
            
            # Satırları sil
            if end_line < total_lines:
                # Son satır değilse, satır sonu dahil sil
                self.text_area.delete(f"{start_line}.0", f"{end_line + 1}.0")
            else:
                # Son satırsa, önceki satırın sonundan itibaren sil
                if start_line > 1:
                    self.text_area.delete(f"{start_line - 1}.end", f"{end_line}.end")
                else:
                    # Tek satırlık dosya
                    self.text_area.delete("1.0", "end")
            
            # İçerik değişikliğini bildir
            self.content_modified = True
            self.update_line_numbers()
            self.highlighter.highlight()
            self.minimap.update_content()
            
        except Exception as e:
            print(f"Satır silme hatası: {e}")
        
        return "break"
    
    def join_lines(self, event=None):
        """
        Mevcut satırı bir sonraki satırla birleştirir.
        Seçili satırlar varsa hepsini tek satırda birleştirir.
        Kısayol: Ctrl+J
        """
        try:
            # Seçim varsa tüm seçili satırları birleştir
            try:
                start_line = int(self.text_area.index("sel.first").split('.')[0])
                end_line = int(self.text_area.index("sel.last").split('.')[0])
            except tk.TclError:
                current_pos = self.text_area.index("insert")
                start_line = int(current_pos.split('.')[0])
                total_lines = int(self.text_area.index("end-1c").split('.')[0])
                
                # Son satırsa birleştirme yapılamaz
                if start_line >= total_lines:
                    return "break"
                    
                end_line = start_line + 1
            
            # Tüm satırları al
            all_text = self.text_area.get(f"{start_line}.0", f"{end_line}.end")
            
            # Satır sonlarını boşlukla değiştir (gereksiz boşlukları kaldır)
            joined_text = " ".join(line.strip() for line in all_text.split("\n"))
            
            # Eski satırları sil ve birleştirilmiş metni ekle
            self.text_area.delete(f"{start_line}.0", f"{end_line}.end")
            self.text_area.insert(f"{start_line}.0", joined_text)
            
            # İçerik değişikliğini bildir
            self.content_modified = True
            self.update_line_numbers()
            self.highlighter.highlight()
            self.minimap.update_content()
            
        except Exception as e:
            print(f"Satır birleştirme hatası: {e}")
        
        return "break"

    def select_next_occurrence(self, event=None):
        """
        Ctrl+D ile seçili kelimeyi bulur ve bir sonrakini seçer.
        Seçili kelime yoksa, imleçteki kelimeyi seçer.
        """
        try:
            # Seçili metin var mı?
            try:
                selected_text = self.text_area.get("sel.first", "sel.last")
            except:
                # Seçili metin yoksa, imlçteki kelimeyi al
                current_pos = self.text_area.index("insert")
                line, col = current_pos.split('.')
                line_text = self.text_area.get(f"{line}.0", f"{line}.end")
                
                # Kelimenin başını ve sonunu bul
                col = int(col)
                start_col = col
                end_col = col
                
                # Geriye doğru git
                while start_col > 0 and line_text[start_col - 1].isalnum() or (start_col > 0 and line_text[start_col - 1] == '_'):
                    start_col -= 1
                
                # İleriye doğru git
                while end_col < len(line_text) and (line_text[end_col].isalnum() or line_text[end_col] == '_'):
                    end_col += 1
                
                if start_col == end_col:
                    return "break"
                
                selected_text = line_text[start_col:end_col]
                self.text_area.tag_add("sel", f"{line}.{start_col}", f"{line}.{end_col}")
            
            # Bir sonraki oluşumu bul
            start_pos = self.text_area.index("sel.last")
            next_pos = self.text_area.search(selected_text, start_pos, stopindex="end")
            
            if next_pos:
                # Bir sonraki oluşumu seçmek yerine, oraya bir imleç ekleyelim
                line, col = map(int, next_pos.split('.'))
                cursor_pos = (line, col)
                
                if cursor_pos not in self.cursors:
                    self.cursors.append(cursor_pos)
                    self.multi_cursor_mode = True
                    self.update_cursor_visuals()
                    
                    # Seçimi yeni pozisyona taşı
                    end_col = col + len(selected_text)
                    self.text_area.tag_remove("sel", "1.0", "end")
                    self.text_area.tag_add("sel", f"{line}.{col}", f"{line}.{end_col}")
        except Exception as e:
            print(f"Select next occurrence error: {e}")
        
        return "break"
