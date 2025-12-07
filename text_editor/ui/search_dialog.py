import customtkinter as ctk

class SearchDialog(ctk.CTkToplevel):
    def __init__(self, tab_manager):
        super().__init__()
        self.tab_manager = tab_manager
        self.title("Bul ve Değiştir")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make it stay on top
        self.attributes("-topmost", True)
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        
        # Find
        ctk.CTkLabel(self, text="Aranan:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.find_entry = ctk.CTkEntry(self)
        self.find_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Replace
        ctk.CTkLabel(self, text="Yeni Değer:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.replace_entry = ctk.CTkEntry(self)
        self.replace_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(self.btn_frame, text="Sonrakini Bul", command=self.find_next).pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="Değiştir", command=self.replace_one).pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="Tümünü Değiştir", command=self.replace_all).pack(side="left", padx=5)

    def get_current_text_widget(self):
        editor = self.tab_manager.get_current_editor()
        if editor:
            return editor.text_area
        return None

    def find_next(self):
        text_widget = self.get_current_text_widget()
        if not text_widget: return
        
        search_str = self.find_entry.get()
        if not search_str: return
        
        # Start from current insert position
        start_pos = text_widget.index("insert")
        
        # Search
        pos = text_widget.search(search_str, start_pos, stopindex="end")
        
        if not pos:
            # Wrap around
            pos = text_widget.search(search_str, "1.0", stopindex=start_pos)
            
        if pos:
            # Select found text
            length = len(search_str)
            end_pos = f"{pos}+{length}c"
            text_widget.tag_remove("sel", "1.0", "end")
            text_widget.tag_add("sel", pos, end_pos)
            text_widget.mark_set("insert", end_pos)
            text_widget.see(pos)
            return True
        return False

    def replace_one(self):
        text_widget = self.get_current_text_widget()
        if not text_widget: return
        
        # If selection matches find string, replace it
        # Otherwise find next
        
        search_str = self.find_entry.get()
        replace_str = self.replace_entry.get()
        
        try:
            sel_start = text_widget.index("sel.first")
            sel_end = text_widget.index("sel.last")
            selected_text = text_widget.get(sel_start, sel_end)
            
            if selected_text == search_str:
                text_widget.delete(sel_start, sel_end)
                text_widget.insert(sel_start, replace_str)
                # Find next
                self.find_next()
            else:
                self.find_next()
        except:
            self.find_next()

    def replace_all(self):
        text_widget = self.get_current_text_widget()
        if not text_widget: return
        
        search_str = self.find_entry.get()
        replace_str = self.replace_entry.get()
        
        if not search_str: return
        
        # Count replacements
        count = 0
        
        # Start from beginning
        start = "1.0"
        while True:
            pos = text_widget.search(search_str, start, stopindex="end")
            if not pos:
                break
            
            end_pos = f"{pos}+{len(search_str)}c"
            text_widget.delete(pos, end_pos)
            text_widget.insert(pos, replace_str)
            
            start = f"{pos}+{len(replace_str)}c"
            count += 1
            
        print(f"Toplam {count} değişiklik yapıldı.")
