import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
from typing import Callable, Optional, Tuple, List, Dict, Any
from text_editor.utils.file_icons import FileIcons

class FileSystemManager:
    """
    Dosya sistemi işlemlerini güvenli bir şekilde yönetir, IO mantığını UI mantığından ayırır.
    """
    
    @staticmethod
    def get_directory_content(path: str) -> Tuple[List[str], List[str]]:
        """
        Belirli bir yol için sıralanmış dizinleri ve dosyaları getirir.
        (dizinler, dosyalar) şeklinde bir demet (tuple) döndürür.
        PermissionError hatasını düzgün bir şekilde ele alır.
        """
        try:
            entries = os.listdir(path)
        except (PermissionError, OSError):
            return [], []
            
        dirs = []
        files = []
        
        for entry in entries:
            if entry.startswith('.'):
                continue
                
            full_path = os.path.join(path, entry)
            # os.path.join'i döngü başına kabaca bir kez kullanın, ancak kontroller ucuzdur
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)
                
        return sorted(dirs), sorted(files)

class FileExplorer(ctk.CTkFrame):
    """
    Özel stillendirme ve tembel yükleme (lazy loading) özelliklerine sahip ttk.Treeview kullanan bir dosya gezgini bileşeni.
    """
    
    # Sabitler
    DUMMY_NODE_VAL = "DUMMY"
    TAG_FOLDER = "folder"
    
    def __init__(self, master, open_file_callback: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        self.open_file_callback = open_file_callback
        self._color_tags: Dict[str, str] = {}
        
        # Arayüz Kurulumu
        self._configure_grid()
        self._create_widgets()
        self._setup_tree_style()
        self._bind_events()
        
        # Veri Kurulumu
        self._setup_color_tags()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_widgets(self):
        # Başlık Etiketi
        self.title_label = ctk.CTkLabel(
            self, 
            text="Dosya Gezgini", 
            font=("Segoe UI", 13, "bold"), 
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Ağaç Görünümü (Treeview)
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Kaydırma Çubuğu
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def _setup_tree_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._apply_default_theme()

    def _apply_default_theme(self):
        """Varsayılan karanlık tema renklerini uygular."""
        self._apply_theme_colors(
            bg_color="#252526",
            fg_color="#d4d4d4",
            sel_bg_color="#37373d",
            sel_fg_color="#ffffff"
        )

    def _apply_theme_colors(self, bg_color: str, fg_color: str, sel_bg_color: str, sel_fg_color: str):
        self.style.configure(
            "Treeview", 
            background=bg_color, 
            foreground=fg_color, 
            fieldbackground=bg_color,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        
        self.style.map(
            "Treeview", 
            background=[('selected', sel_bg_color)], 
            foreground=[('selected', sel_fg_color)]
        )

    def _bind_events(self):
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)

    def _setup_color_tags(self):
        """Renkli dosya simgeleri için ağaç görünümü etiketlerini önceden yapılandırır."""
        all_colors = set()
        
        # FileIcons sınıfından renkleri topla
        for info in FileIcons.ICONS.values():
            all_colors.add(info.get("color", "#d4d4d4"))
            
        all_colors.add(FileIcons.DEFAULT_FILE["color"])
        all_colors.add(FileIcons.DEFAULT_FOLDER["color"])
        
        # Her renk için etiketleri yapılandır
        for color in all_colors:
            tag_name = f"color_{color.replace('#', '')}"
            self._color_tags[color] = tag_name
            self.tree.tag_configure(tag_name, foreground=color)
        
        # Özel klasör etiketi
        self.tree.tag_configure(self.TAG_FOLDER, foreground="#DCBF34")
        self._color_tags[self.TAG_FOLDER] = self.TAG_FOLDER

    def _get_file_tag(self, filename: str, is_folder: bool = False) -> str:
        if is_folder:
            return self._color_tags.get(self.TAG_FOLDER, "")
        
        color = FileIcons.get_color(filename)
        return self._color_tags.get(color, "")

    def set_root_path(self, path: str):
        """Kök dizini ayarlar ve ağacı yeniden doldurur."""
        self.populate_tree(path)

    def populate_tree(self, path: str):
        """Ağacı temizler ve başlangıç kök düğümünü ayarlar."""
        self.tree.delete(*self.tree.get_children())
        
        folder_name = os.path.basename(path) or path
        root_node = self.tree.insert(
            "", 
            "end", 
            text=f"📁 {folder_name}", 
            open=True, 
            values=[path], 
            tags=(self.TAG_FOLDER,)
        )
        
        self._load_directory_nodes(root_node, path)

    def _load_directory_nodes(self, parent_node: str, path: str):
        """Dosyaları/dizinleri getirir ve bunları ağaca ekler."""
        dirs, files = FileSystemManager.get_directory_content(path)
        
        # Dizinleri Ekle
        for d_name in dirs:
            full_path = os.path.join(path, d_name)
            folder_icon = FileIcons.DEFAULT_FOLDER["icon"]
            tag = self._get_file_tag(d_name, is_folder=True)
            
            node = self.tree.insert(
                parent_node, 
                "end", 
                text=f"{folder_icon} {d_name}", 
                values=[full_path], 
                open=False, 
                tags=(tag,)
            )
            
            # Tembel yükleme (lazy loading) için sahte düğüm ekle
            self.tree.insert(node, "end", text="yükleniyor...", values=[self.DUMMY_NODE_VAL])
            
        # Dosyaları Ekle
        for f_name in files:
            full_path = os.path.join(path, f_name)
            file_icon = FileIcons.get_icon(f_name)
            tag = self._get_file_tag(f_name)
            
            self.tree.insert(
                parent_node, 
                "end", 
                text=f"{file_icon} {f_name}", 
                values=[full_path], 
                tags=(tag,)
            )

    def _on_tree_open(self, event):
        """Dizin genişletmeyi yönetir (Tembel Yükleme)."""
        item_id = self.tree.focus()
        if not item_id: 
            return
        
        children = self.tree.get_children(item_id)
        if not children:
            return

        # İlk çocuğun sahte olup olmadığını kontrol et
        first_child = children[0]
        child_values = self.tree.item(first_child, "values")
        
        if child_values and child_values[0] == self.DUMMY_NODE_VAL:
            self.tree.delete(first_child)
            parent_path = self.tree.item(item_id, "values")[0]
            self._load_directory_nodes(item_id, parent_path)

    def _on_double_click(self, event):
        """Çift tıklamada dosya açmayı yönetir."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        file_path = self.tree.item(item_id, "values")[0]
        
        if os.path.isfile(file_path):
            self.open_file_callback(file_path)

    def update_theme(self, theme: Dict[str, Any]):
        """Ağaç görünümü renklerini standart tema sözlüğüne göre günceller."""
        # Yedek değerler sağlamlığı garanti eder
        bg = theme.get("tab_bg", "#252526")
        fg = theme.get("fg", "#d4d4d4")
        sel_bg = theme.get("menu_hover", "#37373d")
        
        # Varsa seçim metni rengini kullan, yoksa standart fg kullan
        sel_fg = theme.get("fg", "#ffffff")
        
        self._apply_theme_colors(bg, fg, sel_bg, sel_fg)


