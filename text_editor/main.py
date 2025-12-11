import customtkinter as ctk
from text_editor.config import APP_NAME, APP_SIZE, THEME_MODE, DEFAULT_THEME_COLOR
from text_editor.ui.main_window import MainWindow

def main():
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme(DEFAULT_THEME_COLOR)

    app = MainWindow()
    app.title(APP_NAME)
    app.geometry(APP_SIZE)
    app.after(0, lambda: app.state('zoomed'))
    app.mainloop()

if __name__ == "__main__":
    main()
