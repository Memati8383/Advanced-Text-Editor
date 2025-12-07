import tkinter as tk
from text_editor.config import FONT_FAMILY

class Minimap(tk.Text):
    def __init__(self, master, main_text, **kwargs):
        super().__init__(master, width=20, wrap="none", bd=0, highlightthickness=0, state="disabled", **kwargs)
        self.main_text = main_text
        
        # Micro font for minimap effect
        self.configure(font=(FONT_FAMILY, 2))
        
        # Disable interactions that shouldn't happen
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_wheel)
        
    def update_content(self, event=None):
        # Get content from main text
        content = self.main_text.get("1.0", "end")
        
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", content)
        self.configure(state="disabled")
        
        # Sync color tags (Basic implementation - re-applying all tags is heavy)
        # For a simple minimap, we might skip full highlighting or just do basic coloring if performance allows.
        # Copying tags is complex. Let's stick to text structure first.
    
    def on_scroll(self, *args):
        # Called when main text scrolls
        self.yview_moveto(args[0])

    def on_click(self, event):
        self.jump_to(event.y)
        return "break"

    def on_drag(self, event):
        self.jump_to(event.y)
        return "break"

    def on_wheel(self, event):
        # Propagate wheel to main text
        self.main_text.event_generate("<MouseWheel>", delta=event.delta)
        return "break"

    def jump_to(self, y):
        # Calculate percentage
        height = self.winfo_height()
        if height == 0: return
        
        fraction = y / height
        self.main_text.yview_moveto(fraction)
        
    def configure_colors(self, bg, fg):
        self.configure(bg=bg, fg=fg)
