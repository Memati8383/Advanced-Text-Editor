import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=30, **kwargs)
        self.grid_columnconfigure(0, weight=1)  # Spacer
        self.grid_columnconfigure(1, weight=0)  # Info

        # Left side message
        self.message_label = ctk.CTkLabel(self, text="Antigravity Editor", anchor="w")
        self.message_label.grid(row=0, column=0, sticky="ew", padx=10)

        # Right side info (Cursor position, Encoding, etc.)
        self.info_label = ctk.CTkLabel(self, text="Ln 1, Col 1 | UTF-8", anchor="e")
        self.info_label.grid(row=0, column=1, sticky="w", padx=10)

    def set_message(self, message):
        self.message_label.configure(text=message)

    def set_info(self, info):
        self.info_label.configure(text=info)
