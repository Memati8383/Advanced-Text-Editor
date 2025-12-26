import tkinter as tk
import re
import json
import os
from typing import List, Dict, Set, Any, Optional, Callable
from text_editor.theme_config import THEMES, DARK_THEME

class CompletionProvider:
    """
    Tamamlama mantığını ve veri kaynağını yönetir.
    Dil anahtar kelimelerini ve belgedeki mevcut kelimeleri sağlar.
    """
    def __init__(self):
        self.languages: Dict[str, List[Dict[str, str]]] = {}
        self.snippets: Dict[str, List[Dict[str, str]]] = {}
        self.cache: Set[str] = set()
        self.load_data()
        
    def load_data(self) -> None:
        """Dil ve snippet verilerini JSON'dan yükler."""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 1. Dilleri Yükle
        try:
            lang_path = os.path.join(base_path, "data", "languages.json")
            if os.path.exists(lang_path):
                with open(lang_path, "r", encoding="utf-8") as f:
                    self.languages = json.load(f)
        except Exception as e:
            print(f"AutoCompleter: Diller yüklenirken hata: {e}")

        # 2. Snippet'lar Yükle
        try:
            snippet_path = os.path.join(base_path, "data", "snippets.json")
            if os.path.exists(snippet_path):
                with open(snippet_path, "r", encoding="utf-8") as f:
                    self.snippets = json.load(f)
        except Exception as e:
            print(f"AutoCompleter: Snippet'lar yüklenirken hata: {e}")

    def update_cache(self, text: str) -> None:
        """Belgedeki kelimeleri performans için önbelleğe alır."""
        self.cache = set(re.findall(r'\b[a-zA-Z_]\w+\b', text))

    def get_suggestions(self, word_start: str, language: str) -> List[Dict[str, str]]:
        """Verilen başlangıca göre akıllı (fuzzy-like) önerileri döndürür."""
        suggestions: List[Dict[str, Any]] = []
        word_start_lower = word_start.lower()
        
        def calculate_score(word: str, query: str) -> int:
            word_l = word.lower()
            query_l = query.lower()
            
            if word_l == query_l: return 0
            if word_l.startswith(query_l): return 1
            
            # Fuzzy match: query'deki karakterlerin sırasıyla word içinde geçmesi
            idx = 0
            match_count = 0
            for char in query_l:
                found_idx = word_l.find(char, idx)
                if found_idx != -1:
                    match_count += 1
                    idx = found_idx + 1
                else:
                    break
            
            if match_count == len(query_l):
                return 2  # Fuzzy match (karakterler sırayla var)
                
            if query_l in word_l: return 3 # Herhangi bir yerde geçiyor
            return 4

        # 1. Snippet'lar
        lang_snippets = self.snippets.get(language, [])
        for s in lang_snippets:
            prefix_l = s["prefix"].lower()
            if word_start_lower in prefix_l:
                suggestions.append({
                    "word": s["prefix"],
                    "type": "snippet",
                    "description": s.get("description", ""),
                    "body": s["body"],
                    "score": calculate_score(s["prefix"], word_start_lower)
                })

        # 2. Sabit Dil Anahtar Kelimeleri
        lang_keywords = self.languages.get(language, [])
        for item in lang_keywords:
            word_l = item["word"].lower()
            if word_start_lower in word_l:
                if not any(s["word"] == item["word"] for s in suggestions):
                    item_copy = item.copy()
                    item_copy["score"] = calculate_score(item["word"], word_start_lower)
                    suggestions.append(item_copy)
                
        # 3. Önbellekteki Belge Kelimeleri
        existing_words = {s["word"] for s in suggestions}
        for w in self.cache:
            w_l = w.lower()
            if word_start_lower in w_l and w not in existing_words and w != word_start:
                suggestions.append({
                    "word": w, 
                    "type": "text", 
                    "score": calculate_score(w, word_start_lower) + 1 # Text daha düşük öncelik
                })
                
        # Sıralama: Score (düşük iyi) -> Tip (snippet > keyword > text) -> Alfabetik
        type_order = {"snippet": 0, "keyword": 1, "function": 1, "tag": 1, "property": 1, "text": 2}
        suggestions.sort(key=lambda x: (x["score"], type_order.get(x["type"], 3), x["word"]))
        
        return suggestions[:15] # İlk 15 sonucu döndür

class CompletionPopup:
    """Açılır pencere UI'ını (toplevel) yönetir."""
    def __init__(self, editor: tk.Text, on_select: Callable[[str], None]):
        self.editor = editor
        self.on_select_callback = on_select
        self.window: Optional[tk.Toplevel] = None
        self.listbox: Optional[tk.Listbox] = None
        self.current_suggestions: List[Dict[str, str]] = []
        self.theme: Dict[str, Any] = DARK_THEME

    def update_theme(self, theme_data: Any = "Dark") -> None:
        """Tema renklerini günceller."""
        if isinstance(theme_data, dict):
            self.theme = theme_data
        else:
            self.theme = THEMES.get(theme_data, DARK_THEME)
            
        if self.window:
            self._setup_style()

    def _setup_style(self) -> None:
        """Liste kutusu renklerini temaya göre ayarlar."""
        if not self.window or not self.listbox: return
        
        bg = self.theme.get("menu_bg", "#2d2d30")
        fg = self.theme.get("menu_fg", "#d4d4d4")
        sel_bg = self.theme.get("accent_color", "#007acc")
        sel_fg = "#ffffff"
        
        self.listbox.configure(bg=bg, fg=fg, selectbackground=sel_bg, selectforeground=sel_fg)

    def show(self, suggestions: List[Dict[str, str]], x: int, y: int) -> None:
        """Önerileri içeren popup penceresini gösterir."""
        self.current_suggestions = suggestions
        
        if not self.window:
            self.window = tk.Toplevel(self.editor)
            self.window.wm_overrideredirect(True)
            self.window.attributes("-topmost", True)
            
            self.listbox = tk.Listbox(self.window, font=("Consolas", 10), bd=0, highlightthickness=1)
            self.listbox.pack(fill="both", expand=True)
            
            self.listbox.bind("<Double-Button-1>", self.on_select)
            self._setup_style()

        self.listbox.delete(0, "end")
        for s in suggestions:
            prefix = " \u25A4 " if s["type"] == "snippet" else " \u2022 "
            desc = f" ({s['description']})" if s.get("description") else ""
            display_text = f"{prefix}{s['word']}{desc}"
            self.listbox.insert("end", display_text)
            
        self.listbox.selection_set(0)
        
        # Pencere boyutlandırma
        req_height = min(len(suggestions) * 22 + 5, 250)
        req_width = 300
        
        screen_width = self.editor.winfo_screenwidth()
        screen_height = self.editor.winfo_screenheight()
        
        final_x, final_y = x, y + 25
        if final_y + req_height > screen_height:
            final_y = y - req_height - 5
            
        self.window.geometry(f"{req_width}x{req_height}+{final_x}+{final_y}")
        self.window.deiconify()

    def hide(self) -> None:
        """Popup penceresini kapatır."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.listbox = None

    def on_select(self, event: Any = None) -> str:
        """Kullanıcının bir öneri seçmesi durumunda tetiklenir."""
        if not self.listbox: return "break"
        selection = self.listbox.curselection()
        if not selection: return "break"
        
        index = selection[0]
        if index < len(self.current_suggestions):
            item = self.current_suggestions[index]
            self.on_select_callback(item)
        return "break"

    def move_selection(self, delta: int) -> None:
        """Klavye ile liste içinde yukarı/aşağı gezinmeyi sağlar."""
        if not self.listbox: return
        current = self.listbox.curselection()
        next_idx = current[0] + delta if current else 0
            
        if 0 <= next_idx < self.listbox.size():
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(next_idx)
            self.listbox.see(next_idx)

class SnippetSession:
    """Aktif bir snippet oturumunu ve durak noktalarını yönetir."""
    def __init__(self, editor: tk.Text, body: str, start_pos: str):
        self.editor = editor
        self.body = body
        self.marks: List[str] = []
        self.current_idx = 0
        self.active = True
        
        self.setup(start_pos)
        
    def setup(self, start_pos: str) -> None:
        # Placeholder'ları bul: ${1:default}, $1, ${0} vb.
        pattern = re.compile(r'\$\{(\d+):?([^}]*)\}|\$(\d+)')
        
        # Girintiyi (indentation) koru
        line_idx = start_pos.split('.')[0]
        line_content = self.editor.get(f"{line_idx}.0", start_pos)
        indent = re.match(r'^\s*', line_content).group(0)
        
        # Snippet gövdesini girintiye göre düzenle (ilk satır hariç)
        lines = self.body.split('\n')
        indented_body = lines[0]
        if len(lines) > 1:
            indented_body += '\n' + '\n'.join(indent + l if l.strip() else l for l in lines[1:])
        
        processed_body = ""
        last_end = 0
        placeholders = []
        
        for match in pattern.finditer(indented_body):
            processed_body += indented_body[last_end:match.start()]
            order = int(match.group(1) or match.group(3))
            default = match.group(2) or ""
            
            start_in_processed = len(processed_body)
            processed_body += default
            end_in_processed = len(processed_body)
            
            placeholders.append({
                "order": order,
                "default": default,
                "start": start_in_processed,
                "end": end_in_processed
            })
            last_end = match.end()
            
        processed_body += indented_body[last_end:]
        self.editor.insert(start_pos, processed_body)
        
        placeholders.sort(key=lambda x: (x["order"] if x["order"] > 0 else 999))
        line, col = map(int, start_pos.split('.'))
        
        # Tag konfigürasyonu (hafif vurgu için)
        self.editor.tag_configure("snippet_focus", background="#3e4451")
        
        for i, p in enumerate(placeholders):
            prefix = processed_body[:p["start"]]
            p_lines = prefix.split('\n')
            p_row = line + len(p_lines) - 1
            p_col = (col if len(p_lines) == 1 else 0) + len(p_lines[-1])
            
            p_end_prefix = processed_body[:p["end"]]
            pe_lines = p_end_prefix.split('\n')
            pe_row = line + len(pe_lines) - 1
            pe_col = (col if len(pe_lines) == 1 else 0) + len(pe_lines[-1])
            
            mark_start = f"snip_{i}_s"
            mark_end = f"snip_{i}_e"
            self.editor.mark_set(mark_start, f"{p_row}.{p_col}")
            self.editor.mark_set(mark_end, f"{pe_row}.{pe_col}")
            self.editor.mark_gravity(mark_start, "left")
            self.editor.mark_gravity(mark_end, "right")
            self.marks.append(mark_start)
            self.marks.append(mark_end)
            
        if self.marks:
            self.jump_to(0)
        else:
            self.active = False

    def jump_to(self, index: int) -> None:
        if 0 <= index < (len(self.marks) // 2):
            self.current_idx = index
            s_mark = self.marks[index * 2]
            e_mark = self.marks[index * 2 + 1]
            
            self.editor.tag_remove("sel", "1.0", "end")
            self.editor.tag_remove("snippet_focus", "1.0", "end")
            self.editor.mark_set("insert", s_mark)
            
            # Odaklanılan alanı işaretle
            self.editor.tag_add("snippet_focus", s_mark, e_mark)
            
            # Eğer default değer varsa seç
            if self.editor.index(s_mark) != self.editor.index(e_mark):
                self.editor.tag_add("sel", s_mark, e_mark)
        else:
            self.active = False
            self.clear_marks()

    def next(self) -> bool:
        if not self.active: return False
        self.jump_to(self.current_idx + 1)
        return self.active

    def clear_marks(self) -> None:
        self.editor.tag_remove("snippet_focus", "1.0", "end")
        for m in self.marks:
            self.editor.mark_unset(m)
        self.marks = []

class AutoCompleter:
    """
    Düzenleyici için otomatik tamamlama servisi.
    Kullanıcı girişlerini dinler ve önerileri Popup üzerinden sunar.
    """
    def __init__(self, editor_widget: tk.Text):
        self.editor = editor_widget
        self.provider = CompletionProvider()
        self.popup = CompletionPopup(editor_widget, self.handle_selection)
        self.snippet_session: Optional[SnippetSession] = None
        self.current_language = "text"
        self._after_id: Optional[str] = None
        self._cache_timer: Optional[str] = None
        
        # Olay Bağlamaları
        self.editor.bind("<KeyRelease>", self.on_key_release, add="+")
        self.editor.bind("<FocusOut>", self.on_focus_out, add="+")
        self.editor.bind("<Button-1>", self.on_click, add="+")
        
        # Periyodik önbellek güncelleme
        self.schedule_cache_update()

    def set_language(self, lexer_name: str) -> None:
        """Aktif dili ayarlar."""
        name = lexer_name.lower()
        
        # Yaygın eşleşmeler
        if "python" in name: self.current_language = "python"
        elif "html" in name: self.current_language = "html"
        elif "css" in name: self.current_language = "css"
        elif "javascript" in name or "js" in name: self.current_language = "javascript"
        elif "typescript" in name or "ts" in name: self.current_language = "typescript"
        elif "markdown" in name or "md" in name: self.current_language = "markdown"
        elif "cpp" in name or "c++" in name: self.current_language = "cpp"
        elif "java" in name: self.current_language = "java"
        elif "go" in name: self.current_language = "go"
        elif "rust" in name: self.current_language = "rust"
        elif "php" in name: self.current_language = "php"
        elif "ruby" in name: self.current_language = "ruby"
        elif "bash" in name or "sh" in name: self.current_language = "bash"
        elif "yaml" in name or "yml" in name: self.current_language = "yaml"
        elif "json" in name: self.current_language = "json"
        else:
            # Eğer yukarıdakilerden biri değilse, doğrudan ismi kullanmayı dene
            # (Pygments lexer isimleri genellikle dil isimleriyle eşleşir)
            self.current_language = name.split()[0] if name else "text"

    def update_theme(self, theme_data: Any) -> None:
        """Tema değişikliğini popup'a iletir."""
        self.popup.update_theme(theme_data)

    def schedule_cache_update(self) -> None:
        """Belge içeriğini periyodik olarak önbelleğe alır."""
        if self._cache_timer:
            self.editor.after_cancel(self._cache_timer)
        self._cache_timer = self.editor.after(5000, self._update_cache_now)
        
    def _update_cache_now(self) -> None:
        """Önbelleği hemen günceller ve bir sonraki güncellemeyi planlar."""
        try:
            full_text = self.editor.get("1.0", "end")
            self.provider.update_cache(full_text)
        except Exception:
            pass
        self.schedule_cache_update()

    def on_key_release(self, event: tk.Event) -> None:
        """Tuş bırakıldığında tamamlama mantığını tetikler."""
        if self._after_id:
            self.editor.after_cancel(self._after_id)
            
        keys_to_ignore = [
            "Up", "Down", "Left", "Right", "Return", "Escape", "Tab", 
            "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"
        ]
        if event.keysym in keys_to_ignore:
            return

        if len(event.char) == 1 or event.keysym == "BackSpace":
             # 250ms hareketsizlik sonrası tetikle (debounce)
             self._after_id = self.editor.after(250, self.trigger_completion)

    def trigger_completion(self) -> None:
        """Ekranda uygun öneriler varsa popup'ı gösterir."""
        try:
            current_idx = self.editor.index("insert")
            line_start = f"{current_idx.split('.')[0]}.0"
            text_upto_cursor = self.editor.get(line_start, current_idx)
            
            # Markdown için özel karakterleri de dahil et, diğer diller için \w yeterli
            if self.current_language == "markdown":
                match = re.search(r'([a-zA-Z0-9_#\-\*\>\[]+)$', text_upto_cursor)
                min_len = 1
            else:
                match = re.search(r'(\w+)$', text_upto_cursor)
                min_len = 2
                
            if not match or len(match.group(1)) < min_len:
                self.popup.hide()
                return
                
            word = match.group(1)
            suggestions = self.provider.get_suggestions(word, self.current_language)
            
            if not suggestions:
                self.popup.hide()
                return
                
            bbox = self.editor.bbox("insert")
            if bbox:
                x, y, _, _ = bbox
                root_x = self.editor.winfo_rootx() + x
                root_y = self.editor.winfo_rooty() + y
                self.popup.show(suggestions, root_x, root_y)
                
        except Exception as e:
            print(f"AutoCompleter: Tamamlama hatası: {e}")

    def handle_selection(self, item: Dict[str, str]) -> None:
        """Seçilen öğeyi tipine göre işler."""
        if item["type"] == "snippet":
            self.expand_snippet(item)
        else:
            self.insert_text(item["word"])
        
        self.popup.hide()
        self.provider.update_cache(self.editor.get("1.0", "end"))
        self.editor.focus_set()

    def insert_text(self, text: str) -> None:
        """Basit metin ekleme."""
        current_idx = self.editor.index("insert")
        line_start = f"{current_idx.split('.')[0]}.0"
        text_upto_cursor = self.editor.get(line_start, current_idx)
        
        # Trigger ile aynı regex'i kullan
        if self.current_language == "markdown":
            match = re.search(r'([a-zA-Z0-9_#\-\*\>\[]+)$', text_upto_cursor)
        else:
            match = re.search(r'(\w+)$', text_upto_cursor)
        
        if match:
            start_del = f"insert-{len(match.group(1))}c"
            self.editor.delete(start_del, "insert")
        
        self.editor.insert("insert", text)

    def expand_snippet(self, item: Dict[str, Any]) -> None:
        """Snippet'ı genişletir ve oturumu başlatır."""
        # Prefix'i sil
        current_idx = self.editor.index("insert")
        line_start = f"{current_idx.split('.')[0]}.0"
        text_upto_cursor = self.editor.get(line_start, current_idx)
        
        if self.current_language == "markdown":
            match = re.search(r'([a-zA-Z0-9_#\-\*\>\[]+)$', text_upto_cursor)
        else:
            match = re.search(r'(\w+)$', text_upto_cursor)
        
        insert_pos = self.editor.index("insert")
        if match:
            # Prefix'in başlangıç konumunu mutlak formata çevir
            insert_pos = self.editor.index(f"insert-{len(match.group(1))}c")
            self.editor.delete(insert_pos, "insert")

        # Yeni snippet oturumu başlat (start_pos artık 'line.col' formatında)
        self.snippet_session = SnippetSession(self.editor, item["body"], insert_pos)

    def handle_key(self, event: tk.Event) -> Optional[str]:
        """Tuş basımlarını popup veya snippet oturumuna göre yönetir."""
        # 1. Popup açıksa
        if self.popup.window:
            if self.handle_popup_key(event.keysym):
                return "break"
        
        # 2. Snippet oturumu aktifse ve Tab basıldıysa
        if self.snippet_session and self.snippet_session.active:
            if event.keysym == "Tab":
                if self.snippet_session.next():
                    return "break"
                else:
                    self.snippet_session = None
            elif event.keysym == "Escape":
                self.snippet_session.active = False
                self.snippet_session.clear_marks()
                self.snippet_session = None
        
        return None

    def handle_popup_key(self, key: str) -> bool:
        """Popup içindeki gezinmeyi yönetir."""
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

    def on_focus_out(self, event: Any) -> None:
        """Odak kaybedildiğinde popup'ı kapatır."""
        self.editor.after(150, self.check_focus)

    def check_focus(self) -> None:
        """Odak durumunu kontrol eder ve gerekirse kapatır."""
        if self.popup.window:
            focus_w = self.editor.focus_get()
            if focus_w != self.popup.listbox and focus_w != self.editor:
                self.popup.hide()

    def on_click(self, event: Any) -> None:
        """Tıklama durumunda popup'ı kapatır."""
        self.popup.hide()

