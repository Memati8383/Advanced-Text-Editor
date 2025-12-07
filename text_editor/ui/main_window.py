import customtkinter as ctk
from text_editor.config import APP_NAME
from text_editor.ui.tab_manager import TabManager
from text_editor.ui.status_bar import StatusBar
from text_editor.ui.file_explorer import FileExplorer
import tkinter as tk
import os

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Menu
        self.grid_rowconfigure(1, weight=1) # Tabs
        self.grid_rowconfigure(2, weight=0) # Status

        # 1. Initialize Components
        self.status_bar = StatusBar(self) # Init status bar first
        self.tab_manager = TabManager(self)
        
        # File Explorer
        # Important: Pass a lambda to wrap the open method, or ensure open_file handles arguments
        self.file_explorer = FileExplorer(self, open_file_callback=self.open_file_from_explorer)

        # 2. Create Layout
        # Menu Bar (Row 0)
        self.create_custom_menu()
        
        # File Explorer (Row 1, Column 0)
        self.file_explorer.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(10, 0))
        
        # Tab Manager (Row 1, Column 1)
        self.tab_manager.grid(row=1, column=1, sticky="nsew", padx=10, pady=(10, 0))

        # Status Bar (Row 2, spanning all)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Update weights (Col 0: Sidebar, Col 1: Main)
        self.grid_columnconfigure(0, weight=0, minsize=200) # Sidebar fixed width initially? or resizable
        self.grid_columnconfigure(1, weight=1)

    def open_file_from_explorer(self, file_path):
        # Helper to open specific path
        # We need to expose a method in TabManager or reuse logic
        # Ideally open_file in TabManager should accept an optional path
        self.tab_manager.open_file(path=file_path)

    def open_folder(self):
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.file_explorer.set_root_path(folder_path)
            self.title(f"{APP_NAME} - {os.path.basename(folder_path)}")

    def create_custom_menu(self):
        # Frame for the menu bar
        self.menu_frame = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=("white", "#2b2b2b"))
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        # Grid layout for menu buttons
        self.menu_buttons = []
        
        # Helper to create menu buttons
        def add_menu_btn(text, command, pass_widget=False):
            btn = ctk.CTkButton(self.menu_frame, text=text, width=60, height=30, 
                                fg_color="transparent", hover_color=("gray75", "gray25"),
                                font=("Segoe UI", 12), anchor="w")
            if pass_widget:
                btn.configure(command=lambda: command(btn))
            else:
                btn.configure(command=command)
                
            btn.pack(side="left", padx=2)
            self.menu_buttons.append(btn)

        # File
        add_menu_btn("Dosya", self.show_file_menu, pass_widget=True)
        # Edit
        add_menu_btn("Düzenle", self.tab_manager.show_find_replace, pass_widget=False)
        # View (Theme)
        v_btn = add_menu_btn("Tema", self.show_theme_menu, pass_widget=True)
        # Help
        # Direct action
        add_menu_btn("Yardım", lambda: self.help_system.open_help("Hızlı Başlangıç"), pass_widget=False)
        
        # Initialize Help System
        from text_editor.ui.help_system import HelpSystem
        self.help_system = HelpSystem(self)

        # Keyboard Shortcuts
        self.bind("<Control-n>", lambda e: self.tab_manager.add_new_tab())
        self.bind("<Control-o>", lambda e: self.tab_manager.open_file())
        self.bind("<Control-Shift-O>", lambda e: self.open_folder())
        self.bind("<Control-s>", lambda e: self.tab_manager.save_current_file())
        self.bind("<Control-Shift-s>", lambda e: self.tab_manager.save_current_file_as())
        self.bind("<Control-f>", lambda e: self.tab_manager.show_find_replace())
        self.bind("<Control-g>", lambda e: self.tab_manager.show_goto_line())
        self.bind("<F11>", self.toggle_fullscreen)
        
        # Apply initial theme
        self.after(100, lambda: self.apply_theme("Dark"))

    def show_file_menu(self, button):
        # Quick and dirty dropdown using tkinter menu at mouse position
        # Or ideally a custom frame. For now, let's use a popup menu style.
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Yeni Sekme (Ctrl+N)", command=self.tab_manager.add_new_tab)
        menu.add_command(label="Dosya Aç (Ctrl+O)", command=self.tab_manager.open_file)
        menu.add_command(label="Klasör Aç (Ctrl+Shift+O)", command=self.open_folder)
        menu.add_command(label="Kaydet (Ctrl+S)", command=self.tab_manager.save_current_file)
        menu.add_command(label="Farklı Kaydet (Ctrl+Shift+S)", command=self.tab_manager.save_current_file_as)
        menu.add_separator()
        menu.add_command(label="Bul (Ctrl+F)", command=self.tab_manager.show_find_replace)
        menu.add_command(label="Satıra Git (Ctrl+G)", command=self.tab_manager.show_goto_line)
        menu.add_separator()
        menu.add_command(label="Çıkış", command=self.quit)
        
        self.popup_menu(menu, button)

    def popup_menu(self, menu, button):
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def show_theme_menu(self, button):
        # Create a popup menu for themes
        menu = tk.Menu(self, tearoff=0)
        from text_editor.theme_config import get_available_themes
        
        for theme_name in get_available_themes():
            menu.add_command(label=theme_name, command=lambda t=theme_name: self.change_theme(t))
            
        self.popup_menu(menu, button)

    def change_theme(self, theme_name):
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name):
        from text_editor.theme_config import get_theme
        theme = get_theme(theme_name)
        
        # Set base appearance mode (Light/Dark)
        ctk.set_appearance_mode(theme["type"])
        
        # 1. Menu Bar
        self.menu_frame.configure(fg_color=theme["menu_bg"])
        for btn in self.menu_buttons:
            btn.configure(text_color=theme["menu_fg"], hover_color=theme["menu_hover"])

        # 2. Status Bar
        self.status_bar.configure(fg_color=theme["status_bg"])
        self.status_bar.message_label.configure(text_color=theme["status_fg"])
        self.status_bar.info_label.configure(text_color=theme["status_fg"])

        # 3. Tab Manager
        self.tab_manager.configure(
            segmented_button_fg_color=theme["tab_bg"],
            segmented_button_selected_color=theme["tab_selected"],
            segmented_button_selected_hover_color=theme["tab_selected"],
            segmented_button_unselected_color=theme["tab_bg"],
            segmented_button_unselected_hover_color=theme["tab_hover"],
            text_color=theme["fg"]
        )
        
        # 4. Editors
        for editor in self.tab_manager.editors.values():
            editor.apply_theme(theme)
            
        # 5. File Explorer
        self.file_explorer.update_theme(theme)
        self.file_explorer.configure(fg_color=theme["tab_bg"])

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))
