import shutil
import subprocess
from tkinter import simpledialog, messagebox
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
from typing import Callable, Optional, Tuple, List, Dict, Any, Union
from text_editor.utils.file_icons import FileIcons

from text_editor.ui.context_menu import ModernContextMenu

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

    @staticmethod
    def create_file(path: str) -> bool:
        try:
            with open(path, 'w') as f:
                pass
            return True
        except OSError:
            return False

    @staticmethod
    def create_directory(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def delete_path(path: str) -> bool:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except OSError:
            return False

    @staticmethod
    def rename_path(src: str, dst: str) -> bool:
        try:
            os.rename(src, dst)
            return True
        except OSError:
            return False

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
        self.context_menu_window = None
        self.current_theme_colors = None
        self.root_path: Optional[str] = None
        self.search_var = tk.StringVar()
        
        # Arayüz Kurulumu
        self._configure_grid()
        self._create_widgets()
        self._setup_tree_style()
        self._bind_events()
        self._setup_search()
        
        # Veri Kurulumu
        self._setup_color_tags()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Ağaç artık 2. satırda

    def _create_widgets(self):
        # Başlık Etiketi
        self.title_label = ctk.CTkLabel(
            self, 
            text="Dosya Gezgini", 
            font=("Segoe UI", 13, "bold"), 
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        
        # Arama Çubuğu
        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="Ara...",
            height=28,
            font=("Segoe UI", 12),
            border_width=1
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Ağaç Görünümü (Treeview)
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Kaydırma Çubuğu
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.scrollbar.grid(row=2, column=1, sticky="ns", pady=5)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def _setup_search(self):
        """Arama dinleyicisini ayarlar."""
        self.search_var.trace_add("write", self._on_search_change)

    def _on_search_change(self, *args):
        """Arama metni değiştiğinde çalışır."""
        query = self.search_var.get().strip()
        if not self.root_path:
            return
            
        if not query:
            # Arama boşsa normal görünüme dön
            self.populate_tree(self.root_path)
            return
            
        # Arama yap
        self._perform_search(query)

    def _perform_search(self, query: str):
        """Dosya sisteminde yinelemeli arama yapar ve sonuçları listeler."""
        self.tree.delete(*self.tree.get_children())
        query_lower = query.lower()
        
        count = 0
        MAX_RESULTS = 100  # Performans için limit
        
        # Sonuç başlığı
        self.tree.insert("", "end", text=f"🔍 Sonuçlar: '{query}'", open=True, tags=(self.TAG_FOLDER,))
        
        try:
            for root, dirs, files in os.walk(self.root_path):
                # Gizli klasörleri atla
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Dosyaları kontrol et
                for filename in files:
                    if query_lower in filename.lower():
                        if count >= MAX_RESULTS:
                            self.tree.insert("", "end", text="... daha fazla sonuç ...", tags=(self.TAG_FOLDER,))
                            return
                            
                        full_path = os.path.join(root, filename)
                        icon = FileIcons.get_icon(filename)
                        tag = self._get_file_tag(filename)
                        
                        # Gösterim: dosya_adı (klasör_adı)
                        rel_path = os.path.relpath(root, self.root_path)
                        display_text = f"{icon} {filename}"
                        if rel_path != ".":
                            display_text += f" ({rel_path})"
                            
                        self.tree.insert(
                            "", 
                            "end", 
                            text=display_text, 
                            values=[full_path], 
                            tags=(tag,)
                        )
                        count += 1
                        
                # Klasörleri kontrol et
                for dirname in dirs:
                    if query_lower in dirname.lower():
                        if count >= MAX_RESULTS: return
                        
                        full_path = os.path.join(root, dirname)
                        
                        self.tree.insert(
                            "",
                            "end",
                            text=f"📁 {dirname}",
                            values=[full_path],
                            tags=(self.TAG_FOLDER,)
                        )
                        count += 1
                        
        except Exception as e:
            print(f"Arama hatası: {e}")

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
        self.tree.bind("<Button-3>", self._on_right_click)

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
        self.root_path = path
        self.search_var.set("")
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

    def _on_right_click(self, event):
        """Sağ tık olayını yönetir ve modern menüyü gösterir."""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            # Tıklanan öğeyi seç
            self.tree.selection_set(item_id)
            
            # Eski menü varsa kapat
            if self.context_menu_window:
                self.context_menu_window.close()
                self.context_menu_window = None

            # Menü komutlarını hazırla
            commands = [
                ("Yeni Dosya", self._context_new_file),
                ("Yeni Klasör", self._context_new_folder),
                "-",
                ("Aç", self._context_open),
                "-",
                ("Yeniden Adlandır", self._context_rename),
                ("Sil", self._context_delete),
                "-",
                ("Yolu Kopyala", self._context_copy_path)
            ]
            
            if os.name == 'nt':
                commands.append(("Klasörde Göster", self._context_show_in_explorer))
            
            # Tema renklerini hazırla
            menu_theme = None
            if self.current_theme_colors:
                # Kenarlık rengi için accent_color veya varsayılan gri kullan
                border_color = self.current_theme_colors.get("accent_color", "#454545")
                # Eğer accent color çok parlaksa ve bu bir border ise, belki daha soft bir şey istenebilir
                # Ama şimdilik accent color uyumlu görünüyor. Alternatif olarak menu_fg'nin şeffaf hali vb.
                # Daha güvenli bir varsayılan:
                if "border" in self.current_theme_colors:
                    border_color = self.current_theme_colors["border"]
                
                menu_theme = {
                    "bg": self.current_theme_colors.get("menu_bg", "#2b2b2b"),
                    "border": border_color,
                    "hover": self.current_theme_colors.get("menu_hover", "#094771"),
                    "text": self.current_theme_colors.get("menu_fg", "#cccccc"),
                    "separator": border_color
                }

            # Menüyü oluştur ve göster
            self.context_menu_window = ModernContextMenu(
                self.winfo_toplevel(), # Ana pencere üzerinde gösterilsin
                commands,
                event.x_root,
                event.y_root,
                theme=menu_theme
            )

    def _get_selected_path_and_parent(self) -> Tuple[Optional[str], Optional[str]]:
        """Seçili öğenin yolunu ve ebeveyn düğüm ID'sini döndürür."""
        selection = self.tree.selection()
        if not selection:
            return None, None
        
        item_id = selection[0]
        path = self.tree.item(item_id, "values")[0]
        parent_id = self.tree.parent(item_id)
        return path, parent_id

    def _refresh_node(self, node_id: str):
        """Belirtilen düğümün içeriğini yeniler."""
        if not node_id: # Root durumunda
            # Root'un kendisini yeniden yüklemek yerine, sadece çocuklarını silebiliriz
            # Ama root genelde boştur (""), treeview root'u.
            # Bizim _load_directory_nodes path istiyor.
            # Root path'i bulmamız lazım.
            # Mevcut yapıda root node insert edilmiş ve biz onun çocuklarını yüklüyoruz.
            return

        # Düğümün yolunu bul
        path = self.tree.item(node_id, "values")[0]
        
        # Mevcut çocukları temizle
        self.tree.delete(*self.tree.get_children(node_id))
        
        # Yeniden yükle
        self._load_directory_nodes(node_id, path)

    def _context_new_file(self):
        path, _ = self._get_selected_path_and_parent()
        if not path: return

        # Eğer dosya seçildiyse onun bulunduğu klasöre, klasör seçildiyse içine
        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        parent_node = self.tree.selection()[0] if os.path.isdir(path) else self.tree.parent(self.tree.selection()[0])

        dialog = ctk.CTkInputDialog(text="Dosya Adı:", title="Yeni Dosya")
        name = dialog.get_input()
        
        if name:
            new_path = os.path.join(target_dir, name)
            if FileSystemManager.create_file(new_path):
                self._refresh_node(parent_node)
                # Yeni dosyayı açalım
                if not self.tree.item(parent_node, "open"):
                     self.tree.item(parent_node, open=True) # Ebeveyni genişlet

    def _context_new_folder(self):
        path, _ = self._get_selected_path_and_parent()
        if not path: return

        target_dir = path if os.path.isdir(path) else os.path.dirname(path)
        parent_node = self.tree.selection()[0] if os.path.isdir(path) else self.tree.parent(self.tree.selection()[0])

        dialog = ctk.CTkInputDialog(text="Klasör Adı:", title="Yeni Klasör")
        name = dialog.get_input()
        
        if name:
            new_path = os.path.join(target_dir, name)
            if FileSystemManager.create_directory(new_path):
                self._refresh_node(parent_node)
                if not self.tree.item(parent_node, "open"):
                     self.tree.item(parent_node, open=True)

    def _context_rename(self):
        path, parent_id = self._get_selected_path_and_parent()
        if not path: return

        old_name = os.path.basename(path)
        dialog = ctk.CTkInputDialog(text="Yeni Ad:", title="Yeniden Adlandır")
        # Pre-fill (varsayılan değer) desteği CTkInputDialog'da standart yok, boş gelecek.
        
        new_name = dialog.get_input()
        if new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            if FileSystemManager.rename_path(path, new_path):
                self._refresh_node(parent_id)

    def _context_delete(self):
        path, parent_id = self._get_selected_path_and_parent()
        if not path: return
        
        if messagebox.askyesno("Sil", f"'{os.path.basename(path)}' öğesini silmek istediğinize emin misiniz?"):
            if FileSystemManager.delete_path(path):
                self._refresh_node(parent_id)

    def _context_open(self):
        """Seçili dosyayı açar."""
        self._on_double_click(None)

    def _context_copy_path(self):
        """Seçili dosyanın yolunu panoya kopyalar."""
        selection = self.tree.selection()
        if selection:
            path = self.tree.item(selection[0], "values")[0]
            self.clipboard_clear()
            self.clipboard_append(path)
            self.update() # Pano güncellemesi için gerekli olabilir

    def _context_show_in_explorer(self):
        """Seçili dosyayı sistem dosya gezgininde gösterir."""
        selection = self.tree.selection()
        if selection:
            path = self.tree.item(selection[0], "values")[0]
            try:
                path = os.path.normpath(path)
                if os.path.isdir(path):
                    os.startfile(path)
                else:
                    # Dosya ise seçili olarak aç (Windows için)
                    subprocess.Popen(f'explorer /select,"{path}"')
            except Exception as e:
                print(f"Klasör açma hatası: {e}")

    def update_theme(self, theme: Dict[str, Any]):
        """Ağaç görünümü renklerini standart tema sözlüğüne göre günceller."""
        # Tema renklerini sakla
        self.current_theme_colors = theme
        
        # Yedek değerler sağlamlığı garanti eder
        bg = theme.get("tab_bg", "#252526")
        fg = theme.get("fg", "#d4d4d4")
        sel_bg = theme.get("menu_hover", "#37373d")
        
        # Varsa seçim metni rengini kullan, yoksa standart fg kullan
        sel_fg = theme.get("fg", "#ffffff")
        
        self._apply_theme_colors(bg, fg, sel_bg, sel_fg)




