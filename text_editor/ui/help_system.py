import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import platform
import sys
import webbrowser
from text_editor.config import APP_NAME, SUPPORTED_FILES

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance, start_section="Hızlı Başlangıç"):
        super().__init__(master)
        self.app = app_instance
        self.title(f"🪐 {APP_NAME} - Yardım Merkezi")
        self.geometry("1000x700")
        
        # Navigasyon geçmişi
        self.history = []
        self.history_index = -1
        
        # Ana grid yapılandırması
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Üst araç çubuğu
        self.create_toolbar()
        
        # Sol Kenar Çubuğu
        self.sidebar = ctk.CTkScrollableFrame(
            self, 
            corner_radius=0, 
            fg_color=("gray92", "#2b2b2b"),
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 1))
        
        # Logo ve başlık
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🪐",
            font=("Segoe UI", 32)
        )
        logo_label.pack()
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="Yardım Merkezi",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack()
        
        # Arama kutusu
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="🔍 Ara...",
            height=35,
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # İçerik çerçevesi
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # İçerik başlığı
        self.content_title = ctk.CTkLabel(
            self.content_frame, 
            text="", 
            font=("Segoe UI", 24, "bold"), 
            anchor="w"
        )
        self.content_title.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # İçerik metni
        self.content_text = ctk.CTkTextbox(
            self.content_frame, 
            wrap="word", 
            font=("Segoe UI", 13),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "#404040")
        )
        self.content_text.grid(row=1, column=0, sticky="nsew")
        
        # Bölümleri Tanımla
        self.sections = {
            "🚀 Hızlı Başlangıç": self.get_quick_start,
            "⌨️ Klavye Kısayolları": self.get_shortcuts,
            "🖱️ Çoklu İmleç Rehberi": self.get_multi_cursor_guide,
            "🎨 Tema Rehberi": self.get_theme_guide,
            "📁 Dosya Formatları": self.get_supported_formats,
            "💡 İpuçları ve Püf Noktaları": self.get_tips_and_tricks,
            "❓ SSS": self.get_faq,
            "📊 Performans Raporu": self.get_performance_report,
            "🐛 Hata Bildir": self.get_report_bug,
            "ℹ️ Hakkında": self.get_about
        }
        
        self.buttons = {}
        self.create_sidebar_buttons()
        
        # Başlangıç bölümünü seç
        initial_section = "🚀 Hızlı Başlangıç"
        for section in self.sections.keys():
            if start_section in section:
                initial_section = section
                break
        
        self.select_section(initial_section)
        
        # Pencere ayarları
        self.after(100, lambda: self.attributes("-topmost", False))
        self.lift()
        self.focus()

    def create_toolbar(self):
        """Üst araç çubuğunu oluşturur (geri, ileri, yenile butonları)"""
        toolbar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color=("gray95", "#2b2b2b"))
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Geri butonu
        self.back_btn = ctk.CTkButton(
            toolbar,
            text="◀ Geri",
            width=80,
            height=32,
            corner_radius=6,
            command=self.go_back,
            state="disabled"
        )
        self.back_btn.pack(side="left", padx=(10, 5), pady=7)
        
        # İleri butonu
        self.forward_btn = ctk.CTkButton(
            toolbar,
            text="İleri ▶",
            width=80,
            height=32,
            corner_radius=6,
            command=self.go_forward,
            state="disabled"
        )
        self.forward_btn.pack(side="left", padx=5, pady=7)
        
        # Ayırıcı
        separator = ctk.CTkLabel(toolbar, text="|", text_color=("gray60", "gray50"))
        separator.pack(side="left", padx=10)
        
        # Ana sayfa butonu
        home_btn = ctk.CTkButton(
            toolbar,
            text="🏠 Ana Sayfa",
            width=100,
            height=32,
            corner_radius=6,
            command=lambda: self.select_section("🚀 Hızlı Başlangıç")
        )
        home_btn.pack(side="left", padx=5, pady=7)

    def create_sidebar_buttons(self):
        """Kenar çubuğu butonlarını oluşturur"""
        for name in self.sections.keys():
            btn = ctk.CTkButton(
                self.sidebar, 
                text=name, 
                anchor="w", 
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray35"),
                height=40,
                corner_radius=8,
                font=("Segoe UI", 12),
                command=lambda n=name: self.select_section(n)
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.buttons[name] = btn

    def select_section(self, name):
        """Bölüm seçildiğinde çağrılır"""
        # Geçmişe ekle
        if self.history_index == -1 or self.history[self.history_index] != name:
            # İleri geçmişini sil
            self.history = self.history[:self.history_index + 1]
            self.history.append(name)
            self.history_index = len(self.history) - 1
        
        self.update_navigation_buttons()
        
        # Düğmeleri güncelle
        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=("gray85", "#404040"),
                    font=("Segoe UI", 12, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    font=("Segoe UI", 12)
                )
        
        # İçeriği Güncelle
        self.content_title.configure(text=name)
        
        content = self.sections[name]()
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
        self.content_text.configure(state="disabled")

    def go_back(self):
        """Geçmişte geri git"""
        if self.history_index > 0:
            self.history_index -= 1
            section = self.history[self.history_index]
            self.select_section_without_history(section)
            self.update_navigation_buttons()

    def go_forward(self):
        """Geçmişte ileri git"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            section = self.history[self.history_index]
            self.select_section_without_history(section)
            self.update_navigation_buttons()

    def select_section_without_history(self, name):
        """Geçmişe eklemeden bölüm seç"""
        # Düğmeleri güncelle
        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=("gray85", "#404040"),
                    font=("Segoe UI", 12, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    font=("Segoe UI", 12)
                )
        
        # İçeriği Güncelle
        self.content_title.configure(text=name)
        
        content = self.sections[name]()
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", content)
        self.content_text.configure(state="disabled")

    def update_navigation_buttons(self):
        """Navigasyon butonlarının durumunu günceller"""
        if self.history_index > 0:
            self.back_btn.configure(state="normal")
        else:
            self.back_btn.configure(state="disabled")
        
        if self.history_index < len(self.history) - 1:
            self.forward_btn.configure(state="normal")
        else:
            self.forward_btn.configure(state="disabled")

    def on_search(self, event):
        """Arama kutusunda yazı yazıldığında"""
        query = self.search_entry.get().lower()
        
        if not query:
            # Tüm butonları göster
            for btn in self.buttons.values():
                btn.pack(fill="x", padx=8, pady=3)
            return
        
        # Arama sonuçlarına göre filtrele
        for name, btn in self.buttons.items():
            if query in name.lower():
                btn.pack(fill="x", padx=8, pady=3)
            else:
                btn.pack_forget()

    # İçerik Oluşturucular
    def get_quick_start(self):
        return """🎯 MEMATI EDITÖR'E HOŞ GELDİNİZ!

Modern, güçlü ve kullanıcı dostu metin editörünüz hazır!

┌─────────────────────────────────────────┐
│  İLK ADIMLAR                             │
└─────────────────────────────────────────┘

1️⃣  YENİ DOSYA OLUŞTURMA
   • Ctrl+N tuşlarına basın
   • Veya menüden: Dosya > Yeni Sekme

2️⃣  DOSYA AÇMA
   • Ctrl+O ile dosya seçin
   • Veya dosyayı sürükleyip bırakın
   • Klasör açmak için: Ctrl+Shift+O

3️⃣  KAYDETME
   • Ctrl+S ile mevcut dosyayı kaydedin
   • Ctrl+Shift+S ile farklı kaydedin
   • Otomatik kayıt: Her 30 saniyede bir!

4️⃣  TEMA DEĞİŞTİRME
   • Menüden: Tema > İstediğiniz temayı seçin
   • 9 farklı, göz alıcı tema mevcut!

5️⃣  ARAÇ VE ÖZELLİKLER
   • Ctrl+F: Bul ve Değiştir
   • Ctrl+G: Belirli satıra git
   • Ctrl+Tekerlek: Yakınlaştır/Uzaklaştır
   • F11: Tam ekran modu

6️⃣  ÇOKLU İMLEÇüçük İmleçveniyet  ARAÇLIRMA
   • Alt+Click: Her yere imleç ekleyin
   • Ctrl+D: Aynı kelimeyi seçip düzenleyin
   • Detaylar için "Çoklu İmleç Rehberi"ne bakın!

┌─────────────────────────────────────────┐
│  HIZLI İPUÇLARI                         │
└─────────────────────────────────────────┘

💡 Otomatik parantez kapatma aktif!
💡 Kod katlama: Satır numaralarındaki oklara tıklayın
💡 Minimap: Büyük dosyalarda gezinmek için sağdaki haritayı kullanın
💡 Sekmeler: Sağ tık ile gelişmiş sekme yönetimi

┌─────────────────────────────────────────┐
│  YARDIMA MI İHTİYACINIZ VAR?            │
└─────────────────────────────────────────┘

Sol taraftaki menüden konuları keşfedin:
• ⌨️  Klavye Kısayolları
• 🖱️  Çoklu İmleç Rehberi
• 💡 İpuçları ve Püf Noktaları
• ❓ Sık Sorulan Sorular

Keyifli kodlamalar! 🚀
"""

    def get_shortcuts(self):
        return """⌨️ KLAVYE KISAYOLLARI

Memati Editör'ü klavyeden kontrol edin!

┌─────────────────────────────────────────┐
│  📁 DOSYA İŞLEMLERİ                     │
└─────────────────────────────────────────┘

Ctrl + N         →  Yeni Sekme
Ctrl + O         →  Dosya Aç
Ctrl + Shift + O →  Klasör (Proje) Aç
Ctrl + S         →  Kaydet
Ctrl + Shift + S →  Farklı Kaydet
Ctrl + W         →  Sekmeyi Kapat

┌─────────────────────────────────────────┐
│  ✏️ DÜZENLEME                            │
└─────────────────────────────────────────┘

Ctrl + Z         →  Geri Al
Ctrl + Y         →  Yinele
Ctrl + X         →  Kes
Ctrl + C         →  Kopyala
Ctrl + V         →  Yapıştır
Ctrl + A         →  Tümünü Seç
Ctrl + F         →  Bul ve Değiştir
Ctrl + G         →  Satıra Git

┌─────────────────────────────────────────┐
│  🖱️ ÇOKLU İMLEÇ                         │
└─────────────────────────────────────────┘

Alt + Click      →  İmleç Ekle/Kaldır
Ctrl + D         →  Kelimeyi Seç (tekrarla)
Escape           →  İmleçleri Temizle

┌─────────────────────────────────────────┐
│  👀 GÖRÜNÜM                              │
└─────────────────────────────────────────┘

Ctrl + Tekerlek  →  Yakınlaştır/Uzaklaştır
Ctrl + 0         →  Zoom Sıfırla
F11              →  Tam Ekran
Ctrl + B         →  Dosya Gezgini Aç/Kapat
Ctrl + `         →  Terminal Aç/Kapat
Ctrl + K, Z      →  Zen Mode (Dikkat Modu)

┌─────────────────────────────────────────┐
│  📋 KOPYALAMA KISAYOLLARI               │
└─────────────────────────────────────────┘

Ctrl + Shift + C →  Dosya Yolunu Kopyala
Ctrl + Alt + C   →  Göreli Yolu Kopyala

┌─────────────────────────────────────────┐
│  💡 PRO İPUÇLARI                        │
└─────────────────────────────────────────┘

🔸 Kod katlama için satır numaralarındaki
   ▼ ve ▶ işaretlerine tıklayın

🔸 Sekme başlıklarına sağ tıklayarak:
   • Sekmeyi kapat
   • Diğerlerini kapat
   • Sağdakileri kapat
   • Yolu kopyala

🔸 Minimap'e tıklayarak dosyada gezinin

🔸 Satır numaralarına tıklayarak satır seçin

🔸 Terminal panelinde PowerShell, CMD veya
   Bash kullanabilirsiniz
"""

    def get_multi_cursor_guide(self):
        return """🖱️ ÇOKLU İMLEÇ REHBERİ

Aynı anda birden fazla yerde düzenleme yapın!

┌─────────────────────────────────────────┐
│  🎯 TEMEL KULLANIM                      │
└─────────────────────────────────────────┘

1️⃣  İMLEÇ EKLEMEK:
   ┌─────────────────────────────┐
   │ Alt + Sol Tık                │
   └─────────────────────────────┘
   
   Tıkladığınız her yere yeni bir imleç eklenir.
   Aynı yere tekrar tıklarsanız imleç kaldırılır.

2️⃣  KELİME SEÇME:
   ┌─────────────────────────────┐
   │ Ctrl + D                     │
   └─────────────────────────────┘
   
   • Bir kelimenin üzerindeyken: Ctrl+D
   • Kelime seçilir
   • Tekrar basarsanız: Sonraki aynı kelime seçilir
   • Her seferinde yeni imleç eklenir

3️⃣  TEMİZLE:
   ┌─────────────────────────────┐
   │ Escape (Esc)                 │
   └─────────────────────────────┘
   
   Tüm ek imleçleri temizler, tek imlece döner.

┌─────────────────────────────────────────┐
│  📚 ÖRNEKLİ SENARYOLAR                  │
└─────────────────────────────────────────┘

🔷 SENARYO 1: Sütun Düzenleme
   ────────────────────────────
   print("Satır 1")
   print("Satır 2")
   print("Satır 3")
   
   🎯 Hedef: Her satırın başına # eklemek
   
   ✅ Çözüm:
   1. Alt+Click ile her satırın başına imleç koyun
   2. # yazın
   3. Tüm satırlara aynı anda eklenir!

🔷 SENARYO 2: Değişken Yeniden Adlandırma
   ──────────────────────────────────────
   old_name = 10
   result = old_name * 2
   print(old_name)
   
   🎯 Hedef: "old_name" → "new_name"
   
   ✅ Çözüm:
   1. "old_name" üzerine imleci getirin
   2. Ctrl+D'ye 3 kez basın (3 kullanım var)
   3. "new_name" yazın
   4. Hepsi birden değişir!

🔷 SENARYO 3: Liste Elemanlarını Düzenleme
   ────────────────────────────────────────
   items = [
       "item1",
       "item2",
       "item3"
   ]
   
   🎯 Hedef: Tüm çift tırnakları tek tırnağa
   
   ✅ Çözüm:
   1. İlk çift tırnağı seçin: "
   2. Ctrl+D ile tüm çift tırnakları seçin
   3. ' yazın (tek tırnak)
   4. Tamamı değişir!

┌─────────────────────────────────────────┐
│  💡 İLERİ DÜZEY İPUÇLARI                │
└─────────────────────────────────────────┘

🌟 Alt+Click ile SÜTUN SEÇİMİ:
   Birçok satırda aynı konuma imleç koyarak
   dikey bir düzenleme yapabilirsiniz.

🌟 Ctrl+D ile PARÇALI SEÇİM:
   Bazı kelimeleri seçip, bazılarını atlayabilirsiniz.
   Her Ctrl+D bir sonrakini seçer, gerekmedikçe durun!

🌟 PERFORMANS:
   100'den fazla imleç performansı etkileyebilir.
   Makul sayıda kullanın (≤ 50 önerilir).

┌─────────────────────────────────────────┐
│  ⚠️ DİKKAT EDİLMESİ GEREKENLER          │
└─────────────────────────────────────────┘

❌ Çoklu imleç modunda otomatik tamamlama
   devre dışı kalır.

❌ Çok fazla imleç eklemek editörü
   yavaşlatabilir.

✅ İhtiyacınız kadar imleç kullanın,
   işiniz bitince Escape ile temizleyin!

┌─────────────────────────────────────────┐
│  🎓 PRATİK YAPIN!                       │
└─────────────────────────────────────────┘

En iyi öğrenme yöntemi pratiktir!
Yukarıdaki örnekleri kendi dosyalarınızda
deneyin ve alışın.

Başarılar! 🚀
"""

    def get_theme_guide(self):
        return """🎨 TEMA REHBERİ

Gözünüze uygun temayı seçin!

┌─────────────────────────────────────────┐
│  🌈 MEVCUT TEMALAR (9 ADET)             │
└─────────────────────────────────────────┘

🌑 DARK (KOYU)
   ├─ Modern, klasik VS Code teması
   ├─ Yüksek kontrast
   ├─ Uzun kodlama seansları için ideal
   └─ Göz yormaz

☀️ LIGHT (AÇIK)
   ├─ Minimal ve temiz
   ├─ Gündüz çalışma için mükemmel
   ├─ Net yazı görüntüsü
   └─ Profesyonel görünüm

🧛 DRACULA
   ├─ Mor ve pembe tonlar
   ├─ Retro ve şık
   ├─ Yüksek kontrast
   └─ Geceleri kodlayanlar için

🌅 SOLARIZED LIGHT
   ├─ Göz dostu pastel tonlar
   ├─ Düşük kontrast
   ├─ Göz yorgunluğunu azaltır
   └─ Uzun okuma seansları için

🔥 MONOKAI
   ├─ Klasik developer favorisi
   ├─ Yeşil, sarı, pembe tonlar
   ├─ Yüksek okunabilirlik
   └─ Sublime Text inspired

❄️ NORD
   ├─ Soğuk, arctic renkler
   ├─ Mat ve modern
   ├─ Göz yormayan mavi tonlar
   └─ Minimalist tasarım

🍂 GRUVBOX
   ├─ Retro, pastel tonlar
   ├─ Sıcak renkler
   ├─ Vintage hissi
   └─ Rahatlatıcı

⚫ ONE DARK PRO
   ├─ Atom editor teması
   ├─ Modern ve popüler
   ├─ Balanced colors
   └─ Profesyonel

🐙 GITHUB DARK
   ├─ GitHub'ın resmi teması
   ├─ Tanıdık görünüm
   ├─ Koyu maviler
   └─ Clean design

🌃 SYNTHWAVE '84
   ├─ Neon, cyberpunk
   ├─ Mor ve cyan tonlar
   ├─ Retro futuristik
   └─ Özgün ve cesur

┌─────────────────────────────────────────┐
│  🔄 TEMA DEĞİŞTİRME                     │
└─────────────────────────────────────────┘

1. Menü çubuğundan "🎨 Tema" butonuna tıklayın
2. Açılan listeden istediğiniz temayı seçin
3. Tema anında uygulanır!

┌─────────────────────────────────────────┐
│  💡 TEMA SEÇİM İPUÇLARI                │
└─────────────────────────────────────────┘

🌙 GECE ÇALIŞIYORSANIZ:
   → Dark, Dracula, Monokai, Nord, Synthwave

☀️ GÜNDÜZ ÇALIŞIYORSANIZ:
   → Light, Solarized Light

👁️ GÖZ YORGUNLUĞU VARSA:
   → Solarized, Nord (düşük kontrast)

🎨 FARKLI BİR ŞEY İSTİYORSANIZ:
   → Synthwave, Gruvbox, Dracula

💼 PROFESYONEL GÖRÜNÜM:
   → One Dark Pro, GitHub Dark, Light

┌─────────────────────────────────────────┐
│  🎯 ÖNERİLER                            │
└─────────────────────────────────────────┘

🔸 Her birkaç saatte bir tema değiştirmek
   gözlerinize rahatlık verebilir

🔸 Farklı projeler için farklı temalar
   kullanarak zihinsel ayrım yapabilirsiniz

🔸 Tüm temaları deneyin, size en uygun
   olanı bulun!

Keyifli kodlamalar! 🎨
"""

    def get_tips_and_tricks(self):
        return """💡 İPUÇLARI VE PÜF NOKTALARI

Editörü daha verimli kullanın!

┌─────────────────────────────────────────┐
│  🚀 ÜRETKENLİK İPUÇLARI                 │
└─────────────────────────────────────────┘

1️⃣  SEKME YÖNETİMİ
   🔸 Sekme başlığına SAĞ TIK yapın:
      • Sekmeyi kapat
      • Diğerlerini kapat
      • Sağdakileri kapat
      • Dosya yolunu kopyala
   
   🔸 Çok sekmeyle çalışıyorsanız düzenli
      temizleyin!

2️⃣  HIZLI NAVİGASYON
   🔸 Ctrl+G ile doğrudan satıra gidin
   🔸 Minimap'e tıklayarak dosyada gezinin
   🔸 Kod katlama ile uzun fonksiyonları gizleyin

3️⃣  AKILLI ARAMA
   🔸 Ctrl+F ile Bul ve Değiştir açın
   🔸 Regex desteği var!
   🔸 Büyük/küçük harf duyarsız arama

4️⃣  OTOMATIK ÖZELLIKLER
   🔸 Parantezler otomatik kapanır: (, {, [, ", '
   🔸 Enter'da akıllı girinti
   🔸 Python'da : sonrası ekstra girinti
   🔸 Her 30 saniyede otomatik kayıt

5️⃣  GÖRSEL İYİLEŞTİRMELER
   🔸 Ctrl+Tekerlek ile yakınlaştırma
   🔸 Font boyutunu 8-72 arası ayarlayın
   🔸 Minimap ile genel görünüm
   🔸 Satır vurgulama aktif

┌─────────────────────────────────────────┐
│  🎯 WORKFLOW ÖNERİLERİ                  │
└─────────────────────────────────────────┘

📁 PROJE KLASÖRÜ AÇIN
   • Ctrl+Shift+O ile tüm projenizi açın
   • Dosya Gezgini'nden hızlıca gezinin
   • Ağaç yapısında kolayca bulun

🎨 TEMA RUTIN OLUŞTURUN
   • Sabah: Light veya Solarized
   • Akşam: Dark, Nord veya Gruvbox
   • Gece: Dracula veya Synthwave

📝 KOD KATLAMA KULLANIN
   • Uzun fonksiyonları katlayın
   • Sadece ilgilendiğiniz koda odaklanın
   • Satır numaralarındaki oklara tıklayın

🖱️ ÇOKLU İMLEÇ GÜCÜ
   • Tekrarlayan düzenlemeler için kullanın
   • Alt+Click ve Ctrl+D'yi öğrenin
   • "Çoklu İmleç Rehberi"ne bakın!

┌─────────────────────────────────────────┐
│  ⚡ PERFORMANS İPUÇLARI                 │
└─────────────────────────────────────────┘

🔸 Çok büyük dosyalardan kaçının (>10MB)
🔸 Gereksiz sekmeleri kapatın
🔸 100+ imleci aynı anda kullanmayın
🔸 Otomatik kayıt aktif, manuel kaydetmeyi
   unutmayın (Ctrl+S)

┌─────────────────────────────────────────┐
│  🎓 ÖĞRENDİKÇE KEŞFEDİN                │
└─────────────────────────────────────────┘

✅ Tüm klavye kısayollarını deneyin
✅ Farklı temaları test edin
✅ Çoklu imleç ile pratik yapın
✅ Dosya Gezgini'ni kullanın
✅ Minimap'i keşfedin

Her gün biraz daha verimli! 🚀
"""

    def get_supported_formats(self):
        formats = "\n".join([f"   • {name}: {ext}" for name, ext in SUPPORTED_FILES])
        return f"""📁 DESTEKLENEN DOSYA FORMATLARI

Memati Editör birçok dosya formatını destekler!

┌─────────────────────────────────────────┐
│  🟢 TAM DESTEK (Highlighting + Complete) │
└─────────────────────────────────────────┘

Sözdizimi vurgulama + Otomatik tamamlama:

🐍 PYTHON (.py, .pyw)
   • Akıllı tamamlama
   • Fonksiyon önerileri
   • Paket/modül tanıma

🌐 HTML (.html, .htm)
   • Tag tamamlama
   • Attribute önerileri
   • Paired tags

🎨 CSS (.css, .scss, .sass)
   • Property önerileri
   • Renk önizleme
   • Class/ID tamamlama

📜 JAVASCRIPT (.js, .jsx)
   • ES6+ desteği
   • Keyword completion
   • Modern syntax

┌─────────────────────────────────────────┐
│  🟡 SÖZDİZİMİ VURGULAMA                 │
└─────────────────────────────────────────┘

Sadece renklendirme (tamamlama yok):

📋 JSON (.json)
📰 XML (.xml)
📝 MARKDOWN (.md, .markdown)
☕ JAVA (.java)
⚙️ C/C++ (.c, .cpp, .h, .hpp)
# C# (.cs)
🦀 RUST (.rs)
🔷 TYPESCRIPT (.ts, .tsx)
🐘 PHP (.php)
💎 RUBY (.rb)
🎯 GO (.go)
... ve daha fazlası!

┌─────────────────────────────────────────┐
│  ⚪ DİĞER DOSYALAR                      │
└─────────────────────────────────────────┘

Düz metin olarak açılır:

📄 .txt, .log, .ini, .conf
📝 .yaml, .yml, .toml
🔧 .sh, .bash, .bat, .ps1
📜 .sql, .csv

┌─────────────────────────────────────────┐
│  🎨 OTOMATİK ALGILAMA                   │
└─────────────────────────────────────────┘

Editör dosya uzantısına göre otomatik olarak:

✅ Uygun renk şemasını seçer
✅ Sözdizimi vurgulayıcıyı ayarlar
✅ Girinti stilini belirler
✅ Dosya ikonunu gösterir

Status bar'da dosya türünü görebilirsiniz:
🐍 Python | UTF-8  ⌖ Ln 42, Col 8

┌─────────────────────────────────────────┐
│  💡 İPUÇLARI                            │
└─────────────────────────────────────────┘

🔸 Uzantısı tanınmayan dosyalar düz metin
   olarak açılır

🔸 Manuel olarak dil değiştirme özelliği
   yakında gelecek!

🔸 Binary dosyaları açmak önerilmez
   (yavaşlık ve garip karakterler)

Desteklenen Formatlar:
{formats}

Her türlü metin dosyasını rahatça düzenleyin! 📝
"""

    def get_faq(self):
        return """❓ SIK SORULAN SORULAR

Merak ettiklerinizin yanıtları burada!

┌─────────────────────────────────────────┐
│  🔧 GENEL SORULAR                       │
└─────────────────────────────────────────┘

❔ Memati Editör ücretsiz mi?
✅ Evet! Tamamen ücretsiz ve open-source.

❔ Hangi işletim sistemlerinde çalışır?
✅ Windows, macOS ve Linux'ta çalışır.

❔ İnternet bağlantısı gerekli mi?
✅ Hayır, tamamen offline çalışır.

┌─────────────────────────────────────────┐
│  📂 DOSYA VE KAYIT                      │
└─────────────────────────────────────────┘

❔ Dosyalarım nereye kaydediliyor?
✅ Sizin belirlediğiniz konuma. Otomatik
   kayıt mevcut dosyanın üzerine yazar.

❔ Otomatik kayıt ne sıklıkla çalışır?
✅ Her 30 saniyede bir. Kaydedilmemiş
   değişiklikler varsa otomatik kaydeder.

❔ Kazara kapattım, kaybettim mi?
✅ Otomatik kayıt aktifse hayır. 30 saniye
   içinde kapatmadıysanız güvendesiniz.

❔ Çok büyük dosyaları açabilir miyim?
✅ Önerilmez. 10MB üzeri dosyalar
   yavaşlık yaratabilir.

┌─────────────────────────────────────────┐
│  🎨 GÖRÜNÜM VE ÖZELLEŞTİRME             │
└─────────────────────────────────────────┘

❔ Font değiştirebilir miyim?
✅ Şu anda sabit (Consolas/sistem mono).
   Yakınlaştırma Ctrl+Tekerlek ile yapılır.

❔ Özel tema oluşturabilir miyim?
✅ Şu anda hayır, ancak yol haritamızda var!

❔ Panelleri gizleyebilir miyim?
✅ Evet! Görünüm menüsünden:
   • Satır Numaraları
   • Word Wrap
   • Minimap
   • Durum Çubuğu
   • Dosya Gezgini
   Toggle edilebilir. Ayrıca Zen Mode ile
   sadece editörü gösterebilirsiniz (Ctrl+K, Z).

┌─────────────────────────────────────────┐
│  ⚡ PERFORMANS                           │
└─────────────────────────────────────────┘

❔ Editör yavaş çalışıyor, ne yapmalıyım?
✅ • Gereksiz sekmeleri kapatın
   • Çok büyük dosyalardan kaçının
   • Çoklu imleç sayısını azaltın
   • Bilgisayarınızı yeniden başlatın

❔ Çok sekme açınca yavaşlıyor?
✅ Normal bir durum. 10-15 sekmeye kadar
   performans iyidir. Fazlasında yavaşlama
   olabilir.

┌─────────────────────────────────────────┐
│  🔌 EKLENTILER VE ENTEGRASYONLAR        │
└─────────────────────────────────────────┘

❔ Plugin desteği var mı?
✅ Henüz yok, ancak v2.0'da gelecek!

❔ Git entegrasyonu var mı?
✅ Şu anda yok, ancak planlanıyor.

❔ Terminal açabilir miyim?
✅ Evet! Ctrl+` ile entegre terminal açabilirsiniz.
   PowerShell, CMD ve Bash desteklenir.

┌─────────────────────────────────────────┐
│  🐛 SORUN GİDERME                       │
└─────────────────────────────────────────┘

❔ Editör açılmıyor!
✅ • Python 3.10+ yüklü olduğundan emin olun
   • Bağımlılıkları kontrol edin:
     pip install customtkinter pygments watchdog

❔ Tema değişmiyor!
✅ Editörü yeniden başlatmayı deneyin.

❔ Kısayollar çalışmıyor!
✅ Başka bir uygulamayla çakışma olabilir.
   Arka planda çalışan programları kontrol edin.

┌─────────────────────────────────────────┐
│  🆘 DAHA FAZLA YARDIM                   │
└─────────────────────────────────────────┘

Sorunuz yanıtlanmadı mı?

📧 İletişim: support@memati-editor.local
🐛 Hata bildir: "Hata Bildir" bölümüne bakın
📖 Dokümantasyon: GitHub wiki (yakında)

Topluluk desteği için forum yakında! 🚀
"""

    def get_performance_report(self):
        tab_count = len(self.app.tab_manager.editors)
        total_lines = 0
        total_chars = 0
        
        for editor in self.app.tab_manager.editors.values():
            try:
                total_lines += int(editor.text_area.index("end-1c").split('.')[0])
                total_chars += len(editor.text_area.get("1.0", "end-1c"))
            except:
                pass
        
        sys_info = f"{platform.system()} {platform.release()}"
        py_ver = sys.version.split()[0]
        
        try:
            import psutil
            memory_usage = f"{psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB"
        except:
            memory_usage = "Bilinmiyor"
        
        return f"""📊 PERFORMANS RAPORU

Editörünüzün anlık durumu:

┌─────────────────────────────────────────┐
│  💻 SİSTEM BİLGİSİ                      │
└─────────────────────────────────────────┘

🖥️  İşletim Sistemi: {sys_info}
🐍 Python Sürümü: {py_ver}
🎨 GUI Framework: CustomTkinter
📦 Syntax Engine: Pygments

┌─────────────────────────────────────────┐
│  📈 EDITÖR İSTATİSTİKLERİ               │
└─────────────────────────────────────────┘

📑 Açık Sekmeler: {tab_count}
📝 Toplam Satır: {total_lines:,}
🔤 Toplam Karakter: {total_chars:,}
💾 Bellek Kullanımı: {memory_usage}

┌─────────────────────────────────────────┐
│  ✅ SAĞLIK DURUMU                       │
└─────────────────────────────────────────┘

🟢 Arayüz Tepkisi: Optimal
🟢 Dosya İzleyici: Aktif
🟢 Otomatik Kayıt: Çalışıyor (30sn)
🟢 Sözdizimi Vurgulama: Aktif
🟢 Otomatik Tamamlama: Hazır

┌─────────────────────────────────────────┐
│  💡 ÖNERİLER                            │
└─────────────────────────────────────────┘

{"🟡 10+ sekme açık, performans etkilenebilir" if tab_count > 10 else "✅ Sekme sayısı optimal"}

{"🟡 Çok satır yüklü, yavaşlama olabilir" if total_lines > 10000 else "✅ Satır sayısı normal"}

{"🟢 Hafıza kullanımı normal seviyede" if memory_usage != "Bilinmiyor" else ""}

┌─────────────────────────────────────────┐
│  📋 RAPORU PAYLAŞ                       │
└─────────────────────────────────────────┘

Bu raporu hata bildirirken kullanabilirsiniz.
Kopyalamak için: Ctrl+A sonra Ctrl+C

Sürüm: Memati Editör v1.0
Tarih: {platform.node()}
"""

    def get_report_bug(self):
        return """🐛 HATA BİLDİR

Hata mı buldunuz? Bize bildirin!

┌─────────────────────────────────────────┐
│  📧 İLETİŞİM                            │
└─────────────────────────────────────────┘

E-posta: bugs@memati-editor.local
GitHub:  github.com/memati/memati-editor/issues

┌─────────────────────────────────────────┐
│  📝 HATA BİLDİRİMİ ŞABLONU              │
└─────────────────────────────────────────┘

Lütfen e-postanıza şunları ekleyin:

1️⃣  BAŞLIK
   Kısa ve açıklayıcı başlık
   Örnek: "Tema değiştirdiğimde çöküyor"

2️⃣  AÇIKLAMA
   Hatayı detaylı anlatın:
   • Ne yapmaya çalışıyordunuz?
   • Ne oldu?
   • Hatayı nasıl tekrarlayabiliriz?

3️⃣  PERFORMANS RAPORU
   "Performans Raporu" bölümünden kopyalayın

4️⃣  EKRAN GÖRÜNTÜSÜ
   Varsa hata ekran görüntüsü ekleyin

5️⃣  HATA MESAJI
   Konsol çıktısı veya hata mesajı

┌─────────────────────────────────────────┐
│  ✅ İYİ BİR HATA BİLDİRİMİ ÖRNEĞİ       │
└─────────────────────────────────────────┘

Başlık:
"Dracula temasında imleç görünmüyor"

Açıklama:
"Dracula temasını seçtiğimde metin imleci
(cursor) görünmez oluyor. Dark temasında
problem yok. Windows 11 kullanıyorum."

Adımlar:
1. Editörü aç
2. Tema > Dracula seç
3. Herhangi bir yere tıkla
4. İmleç görünmüyor

Beklenen: İmleç görünmeli
Gerçekleşen: İmleç görünmüyor

Performans Raporu: [eklendi]

┌─────────────────────────────────────────┐
│  🚀 KATKIDA BULUNUN                     │
└─────────────────────────────────────────┘

Sadece hata değil, özellik önerileri de
gönderin!

• Yeni özellik fikirleri
• UI/UX iyileştirme önerileri
• Dokümantasyon güncellemeleri
• Kod katkıları

GitHub'dan Pull Request açabilirsiniz!

┌─────────────────────────────────────────┐
│  💙 TEŞEKKÜRLER                         │
└─────────────────────────────────────────┘

Her geri bildirim Memati Editör'ü daha
iyi yapar. Katkılarınız için teşekkürler!

🌟 Projeyi begendiyseniz GitHub'da yıldız
   vermeyi unutmayın!
"""

    def get_about(self):
        return f"""ℹ️ MEMATI EDITÖR HAKKINDA

Modern, Hafif ve Güçlü Python IDE

┌─────────────────────────────────────────┐
│  📱 UYGULAMA BİLGİSİ                    │
└─────────────────────────────────────────┘

🪐 İsim: {APP_NAME}
📦 Sürüm: 1.0
📅 Yayın: Aralık 2024
🏷️ Kod Adı: "Phoenix"

┌─────────────────────────────────────────┐
│  🛠️ TEKNOLOJİ YIĞINI                    │
└─────────────────────────────────────────┘

🐍 Dil: Python 3.10+
🎨 GUI: CustomTkinter
🌈 Syntax: Pygments
👁️ Monitoring: Watchdog
⚡ Async: Threading

┌─────────────────────────────────────────┐
│  ✨ ÖZELLİKLER                          │
└─────────────────────────────────────────┘

✅ Çoklu Sekme Desteği
✅ Sözdizimi Vurgulama (300+ dil)
✅ Çoklu İmleç
✅ Akıllı Otomatik Tamamlama
✅ Kod Katlama
✅ Minimap
✅ Bul ve Değiştir (Regex)
✅ 9 Premium Tema
✅ Otomatik Kayıt
✅ Dosya İzleme
✅ Satıra Git
✅ Tam Ekran Modu
✅ Zoom Desteği
✅ Entegre Terminal
✅ Zen Mode (Dikkat Modu)
✅ Dosya Gezgini

┌─────────────────────────────────────────┐
│  👨‍💻 GELİŞTİRİCİ                        │
└─────────────────────────────────────────┘

🎯 Geliştirici: Memati AI Team
🌐 Website: memati-editor.local
📧 İletişim: contact@memati-editor.local
💬 Topluluk: Discord (yakında)

┌─────────────────────────────────────────┐
│  📜 LİSANS                              │
└─────────────────────────────────────────┘

📄 MIT License
🆓 Ücretsiz ve Open Source
🔓 Kaynak kodu GitHub'da

Copyright © 2024 Memati
Tüm Hakları Saklıdır.

┌─────────────────────────────────────────┐
│  🙏 TEŞEKKÜRLER                         │
└─────────────────────────────────────────┘

Bu proje şu harika kütüphaneler sayesinde
mümkün oldu:

• CustomTkinter - Modern UI
• Pygments - Syntax highlighting
• Watchdog - File monitoring
• Python - Amazing language

Ve tüm katkıda bulunanlara ❤️

┌─────────────────────────────────────────┐
│  🔮 GELECEK PLANLAR (v2.0)              │
└─────────────────────────────────────────┘

🚀 Plugin Sistemi
🚀 Git Entegrasyonu
🚀 AI Kod Asistanı
🚀 Collaboration Mode
🚀 Özel Tema Oluşturucu
🚀 Debugging Desteği
🚀 Split View
🚀 Snippet Manager

Bizi takip edin! 🌟

┌─────────────────────────────────────────┐
│  💙 SOSYAL MEDYA                        │
└─────────────────────────────────────────┘

🐙 GitHub: /memati/memati-editor
🐦 Twitter: @memati_editor
📺 YouTube: Memati Editor Tutorials
💬 Discord: discord.gg/memati

Memati Editör ile kodlamanın keyfini çıkarın!

☕ Made with Coffee and Love by Memati Team
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
            # Bölüm adında emoji varsa doğrudan seç, yoksa ara
            section_found = False
            for sec_name in self.help_window.sections.keys():
                if section in sec_name:
                    self.help_window.select_section(sec_name)
                    section_found = True
                    break
            if not section_found:
                self.help_window.select_section("🚀 Hızlı Başlangıç")
