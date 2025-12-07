import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from text_editor.ui.editor import CodeEditor
from text_editor.utils.file_monitor import FileMonitor

class TabManager(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.editors = {} # Map tab_name to CodeEditor instance
        self.untitled_count = 0
        
        self.file_monitor = FileMonitor(self.on_file_changed)
        
        # Auto-save timer
        self.auto_save_interval = 30000 # 30 seconds
        self.after(self.auto_save_interval, self.auto_save_loop)

        # Initial tab
        self.add_new_tab()
        
        # Modern Styling (Configure AFTER adding a tab or safely)
        # Actually CTkTabview bug: needs current tab to be set if rendered?
        # Safe bet: Configure basics first, but colors might depend on internal state?
        # The error implies _current_name is empty string initially.
        # Let's try configuring AFTER adding the first tab.
        
        self.configure(
            corner_radius=8,
            fg_color="transparent",
            segmented_button_fg_color="#181818",
            segmented_button_selected_color="#1e1e1e",
            segmented_button_selected_hover_color="#252526",
            segmented_button_unselected_color="#181818",
            segmented_button_unselected_hover_color="#2d2d2d",
            text_color="#d4d4d4"
        )
        self._segmented_button.configure(font=("Segoe UI", 13))

    def auto_save_loop(self):
        for editor in self.editors.values():
            if editor.file_path and editor.content_modified:
                # We can either save silently or check setting
                # For now silent save
                editor.save_file()
                
                # Update status bar via master
                try:
                    # Access MainWindow directly using winfo_toplevel
                    main_window = self.winfo_toplevel()
                    if hasattr(main_window, 'status_bar'):
                        main_window.status_bar.set_message(f"Otomatik Kayıt: {os.path.basename(editor.file_path)}")
                        # Reset after 2 seconds
                        self.after(2000, lambda: main_window.status_bar.set_message("Memati Editör"))
                except Exception as e:
                    print(f"Auto-save status update error: {e}")
                    print(f"Auto-saved {editor.file_path}")
        
        self.after(self.auto_save_interval, self.auto_save_loop)

    def add_new_tab(self, name=None):
        if name is None:
            self.untitled_count += 1
            name = f"Adsız-{self.untitled_count}"
        
        # Ensure unique name
        original_name = name
        counter = 1
        while name in self.editors:
            name = f"{original_name} ({counter})"
            counter += 1

        self.add(name)
        self.set(name)
        
        # Bind Right Click to the Tab Button
        # We need to find the specific button for this tab in CTk structure
        # self._segmented_button._buttons_dict[name] is the button
        if hasattr(self, "_segmented_button") and name in self._segmented_button._buttons_dict:
            btn = self._segmented_button._buttons_dict[name]
            btn.bind("<Button-3>", lambda e, n=name: self.show_context_menu(e, n))
        
        # Create Editor in the new tab
        tab_frame = self.tab(name)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        editor = CodeEditor(tab_frame)
        editor.grid(row=0, column=0, sticky="nsew")
        
        self.editors[name] = editor
        return name

    def show_context_menu(self, event, tab_name):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Kapat '{tab_name}'", command=lambda: self.close_tab(tab_name))
        menu.add_command(label="Diğerlerini Kapat", command=lambda: self.close_others(tab_name))
        menu.add_command(label="Sağdakileri Kapat", command=lambda: self.close_right(tab_name))
        menu.add_separator()
        menu.add_command(label="Yolu Kopyala", command=lambda: self.copy_path(tab_name))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def close_tab(self, name):
        # Allow checking for unsaved changes?
        # For now direct close or use logic
        self.delete(name)
        if name in self.editors:
            del self.editors[name]

    def close_others(self, keeper_name):
        # List of tabs to close
        # self.editors keys might change during iteration, so copy list
        all_tabs = list(self.editors.keys())
        for tab in all_tabs:
            if tab != keeper_name:
                self.close_tab(tab)

    def close_right(self, boundary_name):
        all_tabs = list(self.editors.keys())
        # CTkTabview doesn't strictly guarantee order in editors dict, 
        # but _segmented_button._value_list usually holds the order.
        try:
            ordered_tabs = self._segmented_button._value_list
        except:
            ordered_tabs = all_tabs
            
        start_closing = False
        for tab in ordered_tabs:
            if start_closing:
                self.close_tab(tab)
            if tab == boundary_name:
                start_closing = True

    def copy_path(self, name):
        editor = self.editors.get(name)
        if editor and editor.file_path:
            self.clipboard_clear()
            self.clipboard_append(editor.file_path)
            self.update() # Keep clipboard after app closes? or just update
            
    def get_current_tab_name(self):
        return self.get()

    def get_current_editor(self):
        name = self.get_current_tab_name()
        if name in self.editors:
            return self.editors[name]
        return None

    def open_file(self, path=None):
        file_path = path
        if not file_path:
            file_path = filedialog.askopenfilename()
            
        if file_path:
            filename = os.path.basename(file_path)
            # Check if already open
            for t_name, editor in self.editors.items():
                if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(file_path):
                    self.set(t_name)
                    return
            
            # If current tab is empty and untitled, use it
            current_name = self.get_current_tab_name()
            current_editor = self.get_current_editor()
            
            # Simple check if "Untitled" and empty content (approximate)
            if "Adsız" in current_name and not current_editor.content_modified and \
               len(current_editor.text_area.get("1.0", "end-1c")) == 0:
                # Rename tab (CTk doesn't support rename easily, so close and open new)
                self.close_current_tab()
            
            tab_name = self.add_new_tab(filename)
            self.editors[tab_name].load_file(file_path)
            # Store full path in editor
            self.editors[tab_name].file_path = file_path
            self.editors[tab_name].set_lexer_from_file(file_path)
            
            # Watch file
            self.file_monitor.add_file(file_path)

    def show_goto_line(self):
        editor = self.get_current_editor()
        if editor:
            from text_editor.ui.goto_line import GoToLineDialog
            GoToLineDialog(self, editor)

    def save_current_file(self):
        editor = self.get_current_editor()
        if editor:
            if editor.file_path:
                editor.save_file()
                self.master.master.status_bar.set_message(f"Saved: {os.path.basename(editor.file_path)}")
                self.after(2000, lambda: self.master.master.status_bar.set_message("Antigravity Editor"))
            else:
                self.save_current_file_as()

    def save_current_file_as(self):
        editor = self.get_current_editor()
        if editor:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if file_path:
                editor.file_path = file_path
                editor.save_file()
                
                # Check if we need to rename the tab
                old_name = self.get_current_tab_name()
                new_name = os.path.basename(file_path)
                
                if old_name != new_name:
                    # Rename tab workaround: Create new, move content (or just reload), close old
                    # Re-loading is safer for consistency
                    self.add_new_tab(new_name)
                    new_editor = self.editors[new_name]
                    new_editor.text_area.insert("1.0", editor.text_area.get("1.0", "end-1c"))
                    new_editor.file_path = file_path
                    new_editor.set_lexer_from_file(file_path)
                    
                    # Remove the old tab
                    self.close_tab(old_name)
                    self.set(new_name)

    def close_current_tab(self):
        name = self.get_current_tab_name()
        if name:
            self.close_tab(name)

    def show_find_replace(self):
        # We'll implement this next
        from text_editor.ui.search_dialog import SearchDialog
        SearchDialog(self)

    def on_file_changed(self, path):
        # Called from thread, use after to schedule on main thread
        self.after(0, lambda: self.handle_file_change(path))

    def handle_file_change(self, path):
        # Check if we have this file open
        for tab_name, editor in self.editors.items():
            if editor.file_path and os.path.abspath(editor.file_path) == os.path.abspath(path):
                # Ask user
                response = messagebox.askyesno("File Changed", f"The file '{tab_name}' has been modified externally.\nDo you want to reload it?")
                if response:
                    editor.load_file(path)
                break
