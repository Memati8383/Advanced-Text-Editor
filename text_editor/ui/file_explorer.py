import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os

class FileExplorer(ctk.CTkFrame):
    def __init__(self, master, open_file_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.open_file_callback = open_file_callback
        
        # Izgara (Grid) yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Başlık
        self.lbl_title = ctk.CTkLabel(self, text="Dosya Gezgini", font=("Segoe UI", 13, "bold"), anchor="w")
        self.lbl_title.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Dosyalar için Treeview
        # CustomTkinter'da Treeview yoktur, bu yüzden karanlık stil ile ttk.Treeview kullanıyoruz
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Kaydırma çubuğu
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Olayları bağla
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Treeview Stilini Ayarla
        self.style = ttk.Style()
        self.style.theme_use("clam") # 'clam', 'winnative'e göre daha kolay özelleştirilir
        
        self.configure_style()
        
        # İlk popülasyon (Mevcut Dizin)
        # self.populate_tree(os.getcwd())  # Başlangıçta klasör otomatik olarak açılmaz

    def set_root_path(self, path):
        self.populate_tree(path)
        
    def configure_style(self):
        # Renkleri manuel olarak mevcut temaya göre ayarlamamız gerekiyor çünkü ttk, CTk ile otomatik senkronize olmuyor
        # Varsayılan karanlık mod stili
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
        # Mevcut olanı temizle
        self.tree.delete(*self.tree.get_children())
        
        # Kök düğüm
        root_node = self.tree.insert("", "end", text=os.path.basename(path), open=True, values=[path])
        self.process_directory(root_node, path)

    def process_directory(self, parent, path):
        try:
            from text_editor.utils.file_icons import FileIcons
            
            # Sırala: Önce dizinler, sonra dosyalar
            entries = os.listdir(path)
            dirs = sorted([e for e in entries if os.path.isdir(os.path.join(path, e)) and not e.startswith('.')])
            files = sorted([e for e in entries if os.path.isfile(os.path.join(path, e)) and not e.startswith('.')])
            
            for d in dirs:
                abspath = os.path.join(path, d)
                # Klasör ikonu
                folder_icon = FileIcons.DEFAULT_FOLDER["icon"]
                node = self.tree.insert(parent, "end", text=f"{folder_icon} {d}", values=[abspath], open=False)
                # Alt dizinleri geç yükleyebiliriz, ancak şimdilik genişletilebilir olması için sahte bir veri ekleyelim
                # Veya daha basit: sadece bir seviye derinliği mi yükleyelim?
                # Her şeyi özyinelemeli olarak yükleyelim mi? Hayır, büyük dizinler için sonsuz olur.
                # Genişletilebilir olması için sahte bir çocuk ekleyelim
                self.tree.insert(node, "end", text="loading...", values=["DUMMY"])
                
            for f in files:
                abspath = os.path.join(path, f)
                # Dosya türüne göre ikon al
                file_icon = FileIcons.get_icon(f)
                self.tree.insert(parent, "end", text=f"{file_icon} {f}", values=[abspath])
                
        except PermissionError:
            pass
            
        # Yavaş yükleme (lazy load) için genişletme olayını bağla
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)

    def on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id: return
        
        # Sahte veri var mı kontrol et
        children = self.tree.get_children(item_id)
        if children and self.tree.item(children[0], "values")[0] == "DUMMY":
            # Sahte veriyi kaldır
            self.tree.delete(children[0])
            
            # Gerçek içeriği yükle
            parent_path = self.tree.item(item_id, "values")[0]
            self.process_directory(item_id, parent_path)

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        file_path = self.tree.item(item_id, "values")[0]
        
        if os.path.isfile(file_path):
            self.open_file_callback(file_path)

    def update_theme(self, theme):
        # Tema renklerini Treeview'e uygula
        bg = theme.get("tab_bg", "#252526") # Sekme arka planını veya biraz farklısını kullan
        fg = theme.get("fg", "#d4d4d4")
        sel = theme.get("menu_hover", "#37373d")
        
        self.style.configure("Treeview", 
                             background=bg, 
                             foreground=fg, 
                             fieldbackground=bg)
        
        self.style.map("Treeview", 
                       background=[('selected', sel)], 
                       foreground=[('selected', fg)])
