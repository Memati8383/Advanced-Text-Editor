import tkinter as tk
import re

# Comprehensive Keyword Lists
KEYWORDS = {
    "python": [
        "def", "class", "print", "import", "from", "return", "if", "else", "elif",
        "while", "for", "in", "break", "continue", "try", "except", "finally",
        "True", "False", "None", "self", "super", "with", "as", "pass", "lambda",
        "async", "await", "raise", "yield", "global", "nonlocal", "assert", "del"
    ],
    "html": [
        "html", "head", "body", "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "a", "img", "ul", "ol", "li", "table", "tr", "td", "th", "form", "input",
        "button", "textarea", "select", "option", "label", "br", "hr", "meta",
        "link", "script", "style", "title", "header", "footer", "nav", "section",
        "article", "aside", "main", "canvas", "video", "audio", "iframe",
        "class", "id", "src", "href", "style", "type", "value", "placeholder"
    ],
    "css": [
        "color", "background", "background-color", "margin", "padding", "border",
        "font-family", "font-size", "font-weight", "text-align", "display",
        "position", "top", "left", "right", "bottom", "width", "height",
        "flex", "grid", "float", "overflow", "z-index", "opacity", "cursor",
        "transition", "transform", "animation", "box-shadow", "border-radius",
        "justify-content", "align-items", "flex-direction", "hover", "active", "focus"
    ],
    "javascript": [
        "function", "var", "let", "const", "if", "else", "switch", "case", "default",
        "for", "while", "do", "break", "continue", "return", "try", "catch", "throw",
        "new", "this", "class", "extends", "super", "import", "export", "from",
        "async", "await", "null", "undefined", "true", "false", "NaN", "Infinity",
        "document", "window", "console", "log", "alert", "prompt", "JSON",
        "map", "filter", "reduce", "forEach", "push", "pop", "length", "split"
    ]
}

class AutoCompleter:
    def __init__(self, editor_widget, keywords=None):
        self.editor = editor_widget
        self.current_keywords = KEYWORDS["python"] # Default
        
        # Popup listbox
        self.popup = None
        self.listbox = None
        
    def set_language(self, lexer_name):
        # Map pygments lexer names to our keyword keys
        lexer_name = lexer_name.lower()
        if "python" in lexer_name:
            self.current_keywords = KEYWORDS["python"]
        elif "html" in lexer_name:
            self.current_keywords = KEYWORDS["html"]
        elif "css" in lexer_name:
            self.current_keywords = KEYWORDS["css"]
        elif "javascript" in lexer_name or "js" in lexer_name:
            self.current_keywords = KEYWORDS["javascript"]
        else:
            self.current_keywords = [] # Empty or generic? or keep previous

    def show_suggestions(self, event=None):
        # Get word under cursor
        try:
            current_idx = self.editor.index("insert")
            line_start = f"{current_idx.split('.')[0]}.0"
            text_upto_cursor = self.editor.get(line_start, current_idx)
            
            # Regex to find the word being typed
            match = re.search(r'(\w+)$', text_upto_cursor)
            
            if not match:
                self.hide()
                return
                
            word = match.group(1)
            
            # Too short?
            if len(word) < 2:
                self.hide()
                return

            # Find suggestions
            # 1. Start with hardcoded keywords for current language
            candidates = set(k for k in self.current_keywords if k.startswith(word))
            
            # 2. Add words from current document (dynamic)
            # Limit this for performance on huge files if needed
            full_text = self.editor.get("1.0", "end")
            doc_words = re.findall(r'\w+', full_text)
            candidates.update(w for w in doc_words if w.startswith(word) and w != word)
            
            suggestions = sorted(list(candidates))
            
            if not suggestions:
                self.hide()
                return
                
            self.display_popup(suggestions, current_idx)
            
        except Exception as e:
            print(f"Autocomplete error: {e}")

    def display_popup(self, suggestions, idx):
        if self.popup:
            self.listbox.delete(0, "end")
        else:
            self.popup = tk.Toplevel(self.editor)
            self.popup.wm_overrideredirect(True)
            self.popup.attributes("-topmost", True)
            
            self.listbox = tk.Listbox(self.popup, font=("Consolas", 10), bg="#2d2d30", fg="#d4d4d4", 
                                      selectbackground="#007acc", selectforeground="white", bd=1)
            self.listbox.pack(fill="both", expand=True)
            
            self.listbox.bind("<Double-Button-1>", self.insert_selected)
            self.listbox.bind("<Return>", self.insert_selected)
            self.listbox.bind("<Tab>", self.insert_selected)
            self.editor.bind("<FocusOut>", self.on_focus_loss)
            
        # Update content
        for s in suggestions:
            self.listbox.insert("end", s)
        self.listbox.selection_set(0)
        
        # Position popup under cursor
        bbox = self.editor.bbox(idx)
        if bbox:
            x, y, w, h = bbox
            root_x = self.editor.winfo_rootx() + x
            root_y = self.editor.winfo_rooty() + y + h + 2
            
            height = min(len(suggestions)*18 + 5, 200)
            self.popup.geometry(f"200x{height}+{root_x}+{root_y}")
            self.popup.deiconify()

    def hide(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.listbox = None
            
    def insert_selected(self, event=None):
        if not self.listbox: return
        
        selection = self.listbox.curselection()
        if not selection: return
        
        selected_word = self.listbox.get(selection[0])
        
        # Replace current typed word
        current_idx = self.editor.index("insert")
        line_start = f"{current_idx.split('.')[0]}.0"
        text_upto_cursor = self.editor.get(line_start, current_idx)
        match = re.search(r'(\w+)$', text_upto_cursor)
        
        if match:
            typed_len = len(match.group(1))
            start_del = f"insert-{typed_len}c"
            self.editor.delete(start_del, "insert")
            self.editor.insert("insert", selected_word)
            
        self.hide()
        return "break"

    def on_focus_loss(self, event):
        # Needed to prevent immediate close when clicking scrollbar of listbox if we had one
        # For now, simplistic approach
        self.editor.after(100, self.hide)

    def handle_key(self, event):
        # Navigation
        if self.popup:
            if event.keysym == "Down":
                self.listbox.event_generate("<Down>")
                return "break"
            elif event.keysym == "Up":
                self.listbox.event_generate("<Up>")
                return "break"
            elif event.keysym == "Escape":
                self.hide()
                return "break"
            elif event.keysym in ["Return", "Tab"]:
                return self.insert_selected()
                
        # Trigger on alphanumeric
        if len(event.char) == 1 and (event.char.isalnum() or event.char in ['_', '-', '.']) or event.keysym == "BackSpace":
            self.editor.after(10, self.show_suggestions)

        return None
