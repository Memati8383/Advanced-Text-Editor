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
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=8, padx=4, highlightthickness=0, bd=0, 
                         font=(FONT_FAMILY, FONT_SIZE), state="disabled", cursor="arrow", wrap="none", **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind("<<Change>>", self.redraw)
        self.text_widget.bind("<Configure>", self.redraw)
        self.bind("<Button-1>", self.on_click)

    def redraw(self, *args):
        self.configure(state="normal")
        self.delete("1.0", "end")
        
        i = self.text_widget.index("@0,0")
        try:
             # Identify the last visible line index to determine stop condition
            end_index = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
        except:
             return

        while True:
            # Check if we have passed the end of the file or visual area
            if self.text_widget.compare(i, ">", end_index) and self.text_widget.compare(i, "!=", end_index):
               break
               
            # Additional safety for EOF
            if self.text_widget.compare(i, "==", "end"):
                break

            dline = self.text_widget.dlineinfo(i)
            
            # Only draw if visible (dline is not None)
            if dline is not None:
                linenum = str(i).split(".")[0]
                
                # Check for folding capability
                marker = "  " # 2 spaces for alignment
                if self.master.is_line_foldable(int(linenum)):
                    if self.master.is_line_folded(int(linenum)):
                        marker = "▶ " # Closed
                    else:
                        marker = "▼ " # Open

                # Formatting: Marker Left, Line Number Right
                # "marker linenum"
                display_text = f"{marker}{linenum:>4}\n"
                self.insert("end", display_text)
            
            # Always increment logical line, even if hidden
            i = self.text_widget.index(f"{i}+1line")

        self.configure(state="disabled")

    def on_click(self, event):
        # Determine strict line number from click y position
        index = self.index(f"@{event.x},{event.y}")
        line_idx = int(index.split('.')[0])
        
        line_content = self.get(f"{line_idx}.0", f"{line_idx}.end")
        if not line_content.strip():
            return
            
        try:
            # Parse number from "▼   10" or "     10"
            # Split by whitespace and find the part that is a digit
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
    def __init__(self, master, file_path=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.file_path = file_path
        self.content_modified = False
        self.font_size = FONT_SIZE
        
        # Configure layout
        self.grid_columnconfigure(0, weight=0) # Line numbers
        self.grid_columnconfigure(1, weight=1) # Text area
        self.grid_columnconfigure(3, weight=0) # Minimap (Right side)
        self.grid_rowconfigure(0, weight=1)

        # Text Area (Using standard tk.Text for better tag support)
        # We wrap it in a frame or place it directly? Placing directly in grid.
        self.text_area = tk.Text(self, wrap="none", undo=True, font=(FONT_FAMILY, self.font_size),
                                 bd=0, highlightthickness=0, padx=5, pady=5)
        self.text_area.grid(row=0, column=1, sticky="nsew")

        # Line Numbers
        self.line_numbers = LineNumbers(self, self.text_area) # Pass text_widget directly
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        # Link LineNumbers (Already done in init, but keep if needed for reference, or remove)
        # self.line_numbers.text_widget = self.text_area

        # Scrollbars
        self.scrollbar_y = ctk.CTkScrollbar(self, command=self.on_scroll_y)
        self.scrollbar_y.grid(row=0, column=2, sticky="ns")
        
        # Minimap
        self.minimap = Minimap(self, self.text_area)
        self.minimap.grid(row=0, column=3, sticky="ns")
        
        self.scrollbar_x = ctk.CTkScrollbar(self, command=self.text_area.xview, orientation="horizontal")
        self.scrollbar_x.grid(row=1, column=1, sticky="ew")
        
        self.text_area.configure(yscrollcommand=self.on_text_scroll, xscrollcommand=self.scrollbar_x.set)
        self.line_numbers.configure(yscrollcommand=self.on_line_scroll)
        # Minimap scroll is handled via on_text_scroll hooks

        # Syntax Highlighter
        self.highlighter = SyntaxHighlighter(self.text_area)
        
        # Auto Completer
        self.completer = AutoCompleter(self.text_area)
        
        # Events
        self.text_area.bind("<<Change>>", self.on_content_change)
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<Key>", self.on_key_press)
        self.text_area.bind("<ButtonRelease-1>", self.on_click)
        
        # Zoom Events (Ctrl + Wheel)
        self.text_area.bind("<Control-MouseWheel>", self.on_zoom)
        self.text_area.bind("<Control-Button-4>", lambda e: self.change_font_size(1))
        self.text_area.bind("<Control-Button-5>", lambda e: self.change_font_size(-1))
        
        # Initial Setup
        if file_path:
            self.load_file(file_path)
            self.set_lexer_from_file(file_path)
        else:
            self.set_lexer_by_name("text")

    def set_lexer_from_file(self, filename):
        lexer = self.highlighter.set_lexer_from_filename(filename)
        if lexer and self.completer:
            self.completer.set_language(lexer.name)
            
    def set_lexer_by_name(self, name):
        lexer = self.highlighter.set_lexer_by_name(name)
        if lexer and self.completer:
            self.completer.set_language(lexer.name)

    def on_key_press(self, event):
        # Auto-complete navigation check first
        res = self.completer.handle_key(event)
        if res == "break":
            return "break"
            
        # Auto-closing brackets
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
            
        # Smart Indent
        if event.keysym == "Return":
            # Get current line
            current_idx = self.text_area.index("insert")
            line_idx = current_idx.split('.')[0]
            line_text = self.text_area.get(f"{line_idx}.0", "end-1c") # get whole line
            
            # Simple indentation: match previous line spaces
            indent = ""
            for char in line_text:
                if char in [' ', '\t']:
                    indent += char
                else:
                    break
            
            # Extra indent if ends with : (Python specific, but generic enough)
            if line_text.strip().endswith(":"):
                indent += "    "
            
            # Allow default enter to process first? No, we need to inject
            self.text_area.after(1, lambda: self.text_area.insert("insert", indent))

    def on_content_change(self, event=None):
        self.content_modified = True
        self.update_line_numbers()
        self.update_status_bar()

    def update_line_numbers(self):
        self.line_numbers.redraw()
        
    def update_status_bar(self):
        # Notify tab manager / main window if possible
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
        # Update cursor pos in status bar
        try:
            index = self.text_area.index("insert")
            line, col = index.split('.')
            
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.set_cursor_info(line, col)
        except:
            pass

    def load_file(self, file_path):
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
        if self.file_path:
            try:
                content = self.text_area.get('1.0', 'end-1c') # Don't get the extra newline at end
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

    def apply_theme(self, theme):
        # Update Text Area colors
        self.text_area.configure(
            bg=theme["editor_bg"],
            fg=theme["editor_fg"],
            insertbackground=theme["caret"],
            selectbackground=theme.get("menu_hover", "#3c3c3c")
        )
        
        # Update Line Numbers colors
        self.line_numbers.configure(
            bg=theme["line_num_bg"],
            fg=theme["line_num_fg"]
        )
        
        # Update Minimap colors
        self.minimap.configure_colors(
            bg=theme["editor_bg"],
            fg=theme["fg"]
        )
        
        # Re-highlight to ensure syntax colors look good on new background
        style_name = theme.get("pygments_style", "monokai")
        self.highlighter.update_style(style_name)

    # Folding Implementation
    def is_line_foldable(self, line_num):
        try:
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            if not line_text.strip():
                return False
                
            indent_current = len(line_text) - len(line_text.lstrip())
            
            # Find next non-empty line to check indentation
            next_line_num = line_num + 1
            while True:
                if self.text_area.compare(f"{next_line_num}.0", ">=", "end"):
                    return False # EOF reached
                    
                next_line_text = self.text_area.get(f"{next_line_num}.0", f"{next_line_num}.end")
                if next_line_text.strip():
                    break
                next_line_num += 1
            
            indent_next = len(next_line_text) - len(next_line_text.lstrip())
            
            return indent_next > indent_current
        except Exception:
            return False

    def is_line_folded(self, line_num):
        tag_name = f"fold_{line_num}"
        ranges = self.text_area.tag_ranges(tag_name)
        return bool(ranges)

    def toggle_fold(self, line_num):
        if not self.is_line_foldable(line_num):
            return

        tag_name = f"fold_{line_num}"
        
        if self.is_line_folded(line_num):
            # Unfold
            self.text_area.tag_delete(tag_name)
        else:
            # Fold
            # Find start indent
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            start_indent = len(line_text) - len(line_text.lstrip())
            
            # Find end line
            current_line = line_num + 1
            while True:
                if self.text_area.compare(f"{current_line}.0", ">=", "end"):
                    break
                    
                content = self.text_area.get(f"{current_line}.0", f"{current_line}.end")
                
                # If non-empty line has same or less indent, block ended
                if content.strip():
                    curr_indent = len(content) - len(content.lstrip())
                    if curr_indent <= start_indent:
                        break
                
                current_line += 1
            
            # Block is from line_num+1 to current_line-1
            # We want to fold starting NEXT line, up to the start of the breaking line.
            # So range is: line_num+1.0 to current_line.0
            
            end_line = current_line
            
            self.text_area.tag_add(tag_name, f"{line_num+1}.0", f"{end_line}.0")
            self.text_area.tag_config(tag_name, elide=True)
            self.text_area.tag_raise(tag_name) # Ensure fold hides everything
            
        self.line_numbers.redraw()
        # Also update minimap
        self.minimap.update_content()
