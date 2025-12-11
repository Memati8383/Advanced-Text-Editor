import tkinter as tk
import re
import json
import os
import threading
from text_editor.theme_config import THEMES, DARK_THEME

class CompletionProvider:
    """Tamamlama mantığını ve veri kaynağını yönetir."""
    def __init__(self):
        self.languages = {}
        self.cache = set()
        self.load_languages()
        
    def load_languages(self):
        """Diller dosyasını JSON'dan yükler."""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_path, "data", "languages.json")
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    self.languages = json.load(f)
            else:
                print(f"Dil dosyası bulunamadı: {data_path}")
                self.languages = {}
        except Exception as e:
            print(f"Diller yüklenirken hata: {e}")
            self.languages = {}

    def update_cache(self, text):
        """Belgedeki kelimeleri performans için önbelleğe alır."""
        # Basit regex ile kelimeleri ayıkla (uzunluğu 2'den büyük olanlar)
        self.cache = set(re.findall(r'\b[a-zA-Z_]\w+\b', text))

    def get_suggestions(self, word_start, language):
        """Verilen başlangıca göre önerileri döndürür."""
        suggestions = []
        word_start = word_start.lower()
        
        # 1. Sabit Dil Anahtar Kelimeleri
        lang_keywords = self.languages.get(language, [])
        for item in lang_keywords:
            if item["word"].lower().startswith(word_start):
                suggestions.append(item)
                
        # 2. Önbellekteki Belge Kelimeleri
        # (Anahtar kelimelerde zaten varsa ekleme)
        existing_words = {s["word"] for s in suggestions}
        
        for w in self.cache:
            if w.lower().startswith(word_start) and w not in existing_words and w != word_start:
                suggestions.append({"word": w, "type": "text"})
                
        # Sıralama: Kısalığa ve alfabetik sıraya göre
        suggestions.sort(key=lambda x: (len(x["word"]), x["word"]))
        return suggestions

class CompletionPopup:
    """Açılır pencere UI'ını yönetir."""
    def __init__(self, editor, on_select):
        self.editor = editor
        self.on_select_callback = on_select
        self.window = None
        self.listbox = None
        self.current_suggestions = []
        self.theme = DARK_THEME # Varsayılan

    def update_theme(self, theme_data="Dark"):
        """Tema renklerini günceller. İsim veya sözlük alabilir."""
        if isinstance(theme_data, dict):
            self.theme = theme_data
        else:
            self.theme = THEMES.get(theme_data, DARK_THEME)
            
        if self.window:
            self.setup_style()

    def setup_style(self):
        if not self.window or not self.listbox: return
        
        bg = self.theme.get("menu_bg", "#2d2d30")
        fg = self.theme.get("menu_fg", "#d4d4d4")
        sel_bg = self.theme.get("accent_color", "#007acc")
        sel_fg = "#ffffff"
        
        self.listbox.configure(bg=bg, fg=fg, selectbackground=sel_bg, selectforeground=sel_fg)

    def show(self, suggestions, x, y):
        self.current_suggestions = suggestions
        
        if not self.window:
            self.window = tk.Toplevel(self.editor)
            self.window.wm_overrideredirect(True)
            self.window.attributes("-topmost", True)
            
            self.listbox = tk.Listbox(self.window, font=("Consolas", 10), bd=0, highlightthickness=1)
            self.listbox.pack(fill="both", expand=True)
            
            self.listbox.bind("<Double-Button-1>", self.on_select)
            self.listbox.bind("<Return>", self.on_select)
            self.listbox.bind("<Tab>", self.on_select)
            self.listbox.bind("<Right>", self.on_select)
            
            self.setup_style()

        self.listbox.delete(0, "end")
        for s in suggestions:
            # Tip bilgisini de gösterelim (örn: "print (function)")
            display_text = f"{s['word']}   \u203a {s['type']}"
            self.listbox.insert("end", display_text)
            
        self.listbox.selection_set(0)
        
        # Konumlandırma Hesaplaması (Ekran dışına taşmayı önleme)
        req_height = min(len(suggestions) * 18 + 5, 200)
        req_width = 250
        
        screen_width = self.editor.winfo_screenwidth()
        screen_height = self.editor.winfo_screenheight()
        
        final_x = x
        final_y = y + 20 # İmlecin biraz altı
        
        if final_y + req_height > screen_height:
            final_y = y - req_height - 5 # İmlecin üstüne al
            
        if final_x + req_width > screen_width:
            final_x = screen_width - req_width - 10

        self.window.geometry(f"{req_width}x{req_height}+{final_x}+{final_y}")
        self.window.deiconify()

    def hide(self):
        if self.window:
            self.window.destroy()
            self.window = None
            self.listbox = None

    def on_select(self, event=None):
        if not self.listbox: return "break"
        selection = self.listbox.curselection()
        if not selection: return "break"
        
        index = selection[0]
        if index < len(self.current_suggestions):
            item = self.current_suggestions[index]
            self.on_select_callback(item["word"])
        return "break"

    def move_selection(self, delta):
        if not self.listbox: return
        current = self.listbox.curselection()
        if not current:
            next_idx = 0
        else:
            next_idx = current[0] + delta
            
        if 0 <= next_idx < self.listbox.size():
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(next_idx)
            self.listbox.see(next_idx)

class AutoCompleter:
    def __init__(self, editor_widget):
        self.editor = editor_widget
        self.provider = CompletionProvider()
        self.popup = CompletionPopup(editor_widget, self.insert_completion)
        self.current_language = "text"
        self._after_id = None
        self._cache_timer = None
        
        # Olay Bağlamaları
        self.editor.bind("<KeyRelease>", self.on_key_release)
        self.editor.bind("<FocusOut>", self.on_focus_out)
        self.editor.bind("<Button-1>", self.on_click)
        
        # İlk önbellek oluşturma (gecikmeli)
        self.schedule_cache_update()

    def set_language(self, lexer_name):
        lexer_name = lexer_name.lower()
        if "python" in lexer_name: self.current_language = "python"
        elif "html" in lexer_name: self.current_language = "html"
        elif "css" in lexer_name: self.current_language = "css"
        elif "javascript" in lexer_name or "js" in lexer_name: self.current_language = "javascript"
        else: self.current_language = "text"

    def update_theme(self, theme_data):
        """Tema değişikliğini popup'a iletir."""
        self.popup.update_theme(theme_data)

    def schedule_cache_update(self):
        """Belge önbelleğini periyodik veya olay bazlı günceller."""
        if self._cache_timer:
            self.editor.after_cancel(self._cache_timer)
        # 2 saniye hareketsizlikte cache güncelle
        self._cache_timer = self.editor.after(2000, self._update_cache_now)
        
    def _update_cache_now(self):
        try:
            full_text = self.editor.get("1.0", "end")
            self.provider.update_cache(full_text)
        except Exception:
            pass

    def on_key_release(self, event):
        # Cache'i güncelleme tetikleyicisi (her tuşta değil, debounce'lu cache)
        self.schedule_cache_update()
        
        # Debounce: Kullanıcı yazmayı durdurana kadar bekle (200ms)
        if self._after_id:
            self.editor.after_cancel(self._after_id)
            
        keys_to_ignore = ["Up", "Down", "Left", "Right", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]
        if event.keysym in keys_to_ignore:
            return

        if len(event.char) == 1 or event.keysym == "BackSpace":
             self._after_id = self.editor.after(200, self.trigger_completion)

    def trigger_completion(self):
        try:
            # İmleç konumunu ve kelimeyi al
            current_idx = self.editor.index("insert")
            line_start = f"{current_idx.split('.')[0]}.0"
            text_upto_cursor = self.editor.get(line_start, current_idx)
            
            match = re.search(r'(\w+)$', text_upto_cursor)
            if not match:
                self.popup.hide()
                return
                
            word = match.group(1)
            if len(word) < 2: # En az 2 harf
                self.popup.hide()
                return

            suggestions = self.provider.get_suggestions(word, self.current_language)
            
            if not suggestions:
                self.popup.hide()
                return
                
            # Popup konumunu hesapla
            bbox = self.editor.bbox("insert")
            if bbox:
                x, y, w, h = bbox
                root_x = self.editor.winfo_rootx() + x
                root_y = self.editor.winfo_rooty() + y
                self.popup.show(suggestions, root_x, root_y)
                
        except Exception as e:
            print(f"Tamamlama hatası: {e}")

    def insert_completion(self, text):
        # Mevcut yazılan yarım kelimeyi sil ve doğrusunu ekle
        current_idx = self.editor.index("insert")
        line_start = f"{current_idx.split('.')[0]}.0"
        text_upto_cursor = self.editor.get(line_start, current_idx)
        match = re.search(r'(\w+)$', text_upto_cursor)
        
        if match:
            # Otomatik tamamlama yapıldığında olayları geçici olarak durdurabiliriz
            start_del = f"insert-{len(match.group(1))}c"
            self.editor.delete(start_del, "insert")
            self.editor.insert("insert", text)
            self.popup.hide()
            # Cache güncelle
            self._update_cache_now()
        
        self.editor.focus_set()

    def handle_key(self, event):
        """Editörden gelen tuş olaylarını işler (Geriye dönük uyumluluk)."""
        if self.handle_arrow_key(event.keysym):
            return "break"
        return None

    def handle_arrow_key(self, key):
        """Editör tarafından çağrılır. Popup açıksa gezinmeyi yönetir."""
        if self.popup.window:
            if key == "Down":
                self.popup.move_selection(1)
                return True
            elif key == "Up":
                self.popup.move_selection(-1)
                return True
            elif key in ["Return", "Tab"]:
                self.popup.on_select()
                return True
            elif key == "Escape":
                self.popup.hide()
                return True
        return False

    def on_focus_out(self, event):
        # Popup dışında bir yere tıklandığında kapat (kısa gecikmeli)
        self.editor.after(100, self.check_focus)

    def check_focus(self):
        # Eğer odak popup'a veya editöre değilse kapat
        if self.popup.window:
            focus_w = self.editor.focus_get()
            if focus_w != self.popup.listbox and focus_w != self.editor:
                self.popup.hide()

    def on_click(self, event):
        self.popup.hide()
