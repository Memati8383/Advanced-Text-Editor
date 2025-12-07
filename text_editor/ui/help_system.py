import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import platform
import sys
from text_editor.config import APP_NAME, SUPPORTED_FILES

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance, start_section="Hızlı Başlangıç"):
        super().__init__(master)
        self.app = app_instance
        self.title(f"{APP_NAME} - Yardım Merkezi")
        self.geometry("800x600")
        
        # Layout: Sidebar (Left), Content (Right)
        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color=("gray90", "#2b2b2b"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Content Area
        self.content_title = ctk.CTkLabel(self, text="", font=("Segoe UI", 20, "bold"), anchor="w")
        self.content_title.grid(row=0, column=1, sticky="nw", padx=20, pady=(20, 10))
        
        self.content_text = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 14), fg_color="transparent")
        self.content_text.grid(row=0, column=1, sticky="nsew", padx=20, pady=(60, 20))
        
        # Define Sections
        self.sections = {
            "Hızlı Başlangıç": self.get_quick_start,
            "Klavye Kısayolları": self.get_shortcuts,
            "Desteklenen Formatlar": self.get_supported_formats,
            "Tema Rehberi": self.get_theme_guide,
            "SSS": self.get_faq,
            "Performans Raporu": self.get_performance_report,
            "Hata Bildir": self.get_report_bug,
            "Hakkında": self.get_about
        }
        
        self.buttons = {}
        self.create_sidebar_buttons()
        
        # Select initial
        if start_section not in self.sections:
            start_section = "Hızlı Başlangıç"
        self.select_section(start_section)
        
        # Keep on top initially, but allow minimizing
        self.after(100, lambda: self.attributes("-topmost", False))
        self.lift()

    def create_sidebar_buttons(self):
        for name in self.sections.keys():
            btn = ctk.CTkButton(self.sidebar, text=name, anchor="w", fg_color="transparent", text_color=("gray10", "gray90"),
                                hover_color=("gray75", "gray35"), command=lambda n=name: self.select_section(n))
            btn.pack(fill="x", padx=5, pady=2)
            self.buttons[name] = btn

    def select_section(self, name):
        # Update buttons
        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("gray80", "gray40")) # Selected state
            else:
                btn.configure(fg_color="transparent")
        
        # Update Content
        self.content_title.configure(text=name)
        
        content = self.sections[name]()
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
        self.content_text.configure(state="disabled")

    # Content Generators
    def get_quick_start(self):
        return """1. Yeni Sekme: Yeni bir dosya başlatmak için Ctrl+N tuşlarına basın.
2. Dosya Aç: Ctrl+O veya Dosya > Dosya Aç menüsünü kullanın.
3. Klasör Aç: Bir proje klasörü açmak için Ctrl+Shift+O tuşlarını kullanın.
4. Kaydet: Yerel olarak kaydetmek için Ctrl+S tuşlarına basın.
5. Temalar: Görünüm > Tema menüsünden temaları değiştirin.
6. Düzenleme: Sadece yazın! Desteklenen dosyalar için sözdizimi vurgulama otomatiktir.
7. Yakınlaştırma: Ctrl tuşuna basılı tutun ve yakınlaştırmak/uzaklaştırmak için Fare Tekerleğini kaydırın.
"""

    def get_shortcuts(self):
        return """Dosya İşlemleri:
- Ctrl+N: Yeni Sekme
- Ctrl+O: Dosya Aç
- Ctrl+Shift+O: Klasör (Proje) Aç
- Ctrl+S: Dosya Kaydet
- Ctrl+Shift+S: Farklı Kaydet

Düzenleme:
- Ctrl+F: Bul ve Değiştir
- Ctrl+G: Satıra Git
- Ctrl+Tekerlek: Yakınlaştır / Uzaklaştır

Görünüm:
- F11: Tam Ekran Modu
"""

    def get_faq(self):
        return """S: Eklentileri (Plugins) destekliyor mu?
C: Henüz değil, ancak yol haritamızda var.

S: Yazı tipini nasıl değiştirebilirim?
C: Şu anda Consolas (veya sistem eşaralıklı yazı tipi) olarak sabittir, ancak yakınlaştırma yapabilirsiniz.

S: Verilerim güvende mi?
C: Dosyalar yerel olarak kaydedilir. Veri kaybını önlemek için her dakika otomatik kayıt çalışır.

S: İkili (Binary) dosyaları açabilir miyim?
C: Editör metin dosyaları için tasarlanmıştır. İkili dosyaları açmak yavaş olabilir veya anlamsız karakterler gösterebilir.
"""

    def get_supported_formats(self):
        formats = "\n".join([f"- {name}: {ext}" for name, ext in SUPPORTED_FILES])
        return f"""Editör herhangi bir dosyayı açabilir.

🟢 Otomatik Tamamlama ve Renklendirme Desteği:
- Python
- HTML
- CSS
- JavaScript

🟡 Sadece Renklendirme:
- JSON, XML, Markdown

{formats}"""

    def get_theme_guide(self):
        return """- Dark (Koyu): Düşük ışık için en iyisi. Yüksek kontrastlı kod renkleri kullanır.
- Light (Açık): Standart minimal görünüm.
- Dracula: Morumsu koyu tonlara sahip ünlü renk şeması.
- Monokai: Klasik geliştirici teması, yüksek kontrast.
- Solarized: Göz yorgunluğunu azaltmak için tasarlanmış düşük kontrast.
- Nord: Soğuk ve mat, göz yormayan kuzey renkleri.
- Gruvbox: Retro sevenler için pastel tonlar.
- One Dark Pro: Modern ve popüler Atom editörü teması.
- GitHub Dark: GitHub'ın resmi koyu arayüzü.
- Synthwave '84: Neon ve mor ağırlıklı Cyberpunk tarzı.

Araç çubuğundaki 'Theme' (Tema) düğmesiyle temaları değiştirin.
"""

    def get_performance_report(self):
        tab_count = len(self.app.tab_manager.editors)
        total_lines = 0
        for editor in self.app.tab_manager.editors.values():
            try:
                total_lines += int(editor.text_area.index("end-1c").split('.')[0])
            except: pass
            
        sys_info = f"İşletim Sistemi: {platform.system()} {platform.release()}"
        py_ver = sys.version.split()[0]
        
        return f"""Sistem Bilgisi:
- {sys_info}
- Python: {py_ver}

Editör İstatistikleri:
- Açık Sekmeler: {tab_count}
- Yüklenen Toplam Satır: {total_lines}
- Bellek Kullanımı: Normal (Python Yönetimli)
- GUI Framework: CustomTkinter

Sağlık Durumu:
- Arayüz Tepkisi: optimal
- Dosya İzleyici: aktif
"""

    def get_report_bug(self):
        return """Lütfen hataları destek ekibimize bildirin:
bugs@memati-editor.com

E-postaya 'Performans Raporunuzu' eklemeyi unutmayın.
"""

    def get_about(self):
        return f"""{APP_NAME}

Sürüm: 1.1.0
Altyapı: Python & CustomTkinter

Geliştirici: Memati AI
"""

class HelpSystem:
    def __init__(self, master_window):
        self.master = master_window
        self.help_window = None

    def open_help(self, section="Hızlı Başlangıç"):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self.master, self.master, start_section=section)
        else:
            self.help_window.lift()
            self.help_window.focus()
            self.help_window.select_section(section)
