import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os

class FileExplorer(ctk.CTkFrame):
    def __init__(self, master, open_file_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.open_file_callback = open_file_callback
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Heading
        self.lbl_title = ctk.CTkLabel(self, text="Dosya Gezgini", font=("Segoe UI", 13, "bold"), anchor="w")
        self.lbl_title.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Treeview for files
        # CustomTkinter doesn't have a Treeview, so we use ttk.Treeview with dark styling
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Styling the Treeview
        self.style = ttk.Style()
        self.style.theme_use("clam") # 'clam' is easier to customize than 'winnative'
        
        self.configure_style()
        
        # Initial population (Current Directory)
        self.populate_tree(os.getcwd())

    def set_root_path(self, path):
        self.populate_tree(path)
        
    def configure_style(self):
        # We need to set colors based on current theme manually since ttk doesn't auto-sync with CTk
        # Default dark mode style
        bg_color = "#252526"
        fg_color = "#d4d4d4"
        sel_bg = "#37373d"
        
        self.style.configure("Treeview", 
                             background=bg_color, 
                             foreground=fg_color, 
                             fieldbackground=bg_color,
                             borderwidth=0,
                             font=("Segoe UI", 11))
        
        self.style.map("Treeview", 
                       background=[('selected', sel_bg)], 
                       foreground=[('selected', '#ffffff')])

    def populate_tree(self, path):
        # Clear existing
        self.tree.delete(*self.tree.get_children())
        
        # Root node
        root_node = self.tree.insert("", "end", text=os.path.basename(path), open=True, values=[path])
        self.process_directory(root_node, path)

    def process_directory(self, parent, path):
        try:
            # Sort: Directories first, then files
            entries = os.listdir(path)
            dirs = sorted([e for e in entries if os.path.isdir(os.path.join(path, e)) and not e.startswith('.')])
            files = sorted([e for e in entries if os.path.isfile(os.path.join(path, e)) and not e.startswith('.')])
            
            for d in dirs:
                abspath = os.path.join(path, d)
                node = self.tree.insert(parent, "end", text=f"📁 {d}", values=[abspath], open=False)
                # We can load subdirs lazily, but for now let's just insert a dummy so it's expandable using event
                # Or simplier: just load one level deep?
                # Let's load everything recursively? No, infinite for large dirs.
                # Let's insert a dummy child to make it expandable
                self.tree.insert(node, "end", text="loading...", values=["DUMMY"])
                
            for f in files:
                abspath = os.path.join(path, f)
                # Icons would be nice, using emoji for now
                self.tree.insert(parent, "end", text=f"📄 {f}", values=[abspath])
                
        except PermissionError:
            pass
            
        # Bind expand event to lazy load
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)

    def on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id: return
        
        # Check if dummy exists
        children = self.tree.get_children(item_id)
        if children and self.tree.item(children[0], "values")[0] == "DUMMY":
            # Remove dummy
            self.tree.delete(children[0])
            
            # Load actual content
            parent_path = self.tree.item(item_id, "values")[0]
            self.process_directory(item_id, parent_path)

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        file_path = self.tree.item(item_id, "values")[0]
        
        if os.path.isfile(file_path):
            self.open_file_callback(file_path)

    def update_theme(self, theme):
        # Apply theme colors to Treeview
        bg = theme.get("tab_bg", "#252526") # Use tab background or slightly different
        fg = theme.get("fg", "#d4d4d4")
        sel = theme.get("menu_hover", "#37373d")
        
        self.style.configure("Treeview", 
                             background=bg, 
                             foreground=fg, 
                             fieldbackground=bg)
        
        self.style.map("Treeview", 
                       background=[('selected', sel)], 
                       foreground=[('selected', fg)])
