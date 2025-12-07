import customtkinter as ctk

class GoToLineDialog(ctk.CTkToplevel):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.title("Satıra Git")
        self.geometry("300x120")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Center dialog
        self.center_window()
        
        # UI
        self.lbl = ctk.CTkLabel(self, text="Satır Numarası Girin:")
        self.lbl.pack(pady=(15, 5))
        
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=5, padx=20, fill="x")
        self.entry.bind("<Return>", self.go_to_line)
        self.entry.focus_set()
        
        self.btn = ctk.CTkButton(self, text="Git", command=self.go_to_line, width=100)
        self.btn.pack(pady=10)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def go_to_line(self, event=None):
        line_num = self.entry.get().strip()
        if not line_num.isdigit():
            return
            
        line_num = int(line_num)
        
        try:
            # Check range
            total_lines = int(self.editor.text_area.index("end-1c").split('.')[0])
            if 1 <= line_num <= total_lines:
                self.editor.text_area.mark_set("insert", f"{line_num}.0")
                self.editor.text_area.see(f"{line_num}.0")
                
                # Highlight the line briefly (optional, maybe just selection)
                self.editor.text_area.tag_remove("sel", "1.0", "end")
                self.editor.text_area.tag_add("sel", f"{line_num}.0", f"{line_num+1}.0")
                
                self.destroy()
        except:
            pass
