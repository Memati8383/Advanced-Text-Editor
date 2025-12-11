"""
Ayarlar Penceresi
Uygulamanın tüm ayarlarını merkezi bir yerden yönetmek için kullanılır.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, colorchooser, font as tkfont
import json
import os
from typing import Dict, Any, Callable
from text_editor.utils.shortcut_manager import ShortcutManager


class SettingsDialog(ctk.CTkToplevel):
    """
    Kapsamlı ayarlar penceresi.
    Tüm uygulama ayarlarını kategorilere ayırarak gösterir ve düzenlemeye olanak tanır.
    """
    
    # Tüm ayarlar listesi (arama için optimizasyon)
    ALL_SETTINGS = {
        "Uygulama Adı": ("Genel", "app_name", "🌐"),
        "Yazı Tipi": ("Genel", "font_family", "🔤"),
        "Yazı Boyutu": ("Genel", "font_size", "📏"),
        "Satır Numaraları": ("Editör", "show_line_numbers", "🔢"),
        "Kelime Kaydırma": ("Editör", "word_wrap", "↩️"),
        "Minimap": ("Editör", "show_minimap", "🗺️"),
        "Tab Boyutu": ("Editör", "tab_size", "⏩"),
        "Otomatik Kaydetme": ("Editör", "auto_save", "💾"),
        "Kaydetme Aralığı": ("Editör", "auto_save_interval", "⏱️"),
        "Parantez Eşleştirme": ("Editör", "bracket_matching", "🔗"),
        "Sözdizimi Vurgulama": ("Editör", "syntax_highlighting", "🎨"),
        "Durum Çubuğu": ("Görünüm", "show_status_bar", "📊"),
        "Dosya Gezgini": ("Görünüm", "show_file_explorer", "📁"),
        "Terminal Görünürlüğü": ("Görünüm", "show_terminal", "💻"),
        "Tam Ekran Başlat": ("Görünüm", "start_fullscreen", "🖥️"),
        "Tema": ("Tema", "theme", "🎨"),
        "Terminal Tipi": ("Terminal", "terminal_type", "⌨️"),
        "Terminal Yazı Boyutu": ("Terminal", "terminal_font_size", "📏"),
        "Geçmiş Satır Sayısı": ("Terminal", "terminal_history", "📜"),
        "Performans Modu": ("Gelişmiş", "performance_mode", "⚡"),
        "Otomatik Yedekleme": ("Gelişmiş", "auto_backup", "🔄"),
        "Maksimum Dosya Boyutu": ("Gelişmiş", "max_file_size", "📦"),
        "Hata Raporlama": ("Gelişmiş", "error_reporting", "🐛"),
    }
    
    # Çeviriler (Sadece Türkçe)
    TRANSLATIONS = {
        "Türkçe": {
            "window_title": "⚙️ Ayarlar",
            "panel_title": "⚙️ Ayarlar",
            "search_placeholder": "🔍 Ayar ara...",
            "categories": {
                "Genel": "Genel",
                "Editör": "Editör",
                "Görünüm": "Görünüm",
                "Tema": "Tema",
                "Klavye Kısayolları": "Klavye Kısayolları",
                "Terminal": "Terminal",
                "Gelişmiş": "Gelişmiş"
            },
            "buttons": {
                "reset": "🔄 Varsayılana Dön",
                "cancel": "❌ İptal",
                "apply": "✅ Uygula"
            },
            "no_limit": "Değişiklik Yok",
            "settings": {
                "app_name": {"label": "Uygulama Adı", "desc": "Başlık çubuğunda görünen uygulama adı"},
                "font_family": {"label": "Yazı Tipi", "desc": "Editörde kullanılacak yazı tipi ailesi"},
                "font_size": {"label": "Yazı Boyutu", "desc": "Editör yazı tipi boyutu (8-32)"},
                "show_line_numbers": {"label": "Satır Numaraları", "desc": "Editörde satır numaralarını göster"},
                "word_wrap": {"label": "Kelime Kaydırma", "desc": "Uzun satırları otomatik olarak kaydır"},
                "show_minimap": {"label": "Minimap", "desc": "Kod haritasını göster"},
                "tab_size": {"label": "Tab Boyutu", "desc": "Tab karakterinin kaç boşluk genişliğinde olacağı"},
                "auto_save": {"label": "Otomatik Kaydetme", "desc": "Değişiklikleri otomatik kaydet"},
                "auto_save_interval": {"label": "Kaydetme Aralığı", "desc": "Otomatik kaydetme sıklığı (saniye)"},
                "bracket_matching": {"label": "Parantez Eşleştirme", "desc": "İmleç parantez üzerindeyken eşini vurgula"},
                "syntax_highlighting": {"label": "Sözdizimi Vurgulama", "desc": "Kod renklendirmesini etkinleştir"},
                "show_status_bar": {"label": "Durum Çubuğu", "desc": "Alt kısımdaki bilgi çubuğunu göster"},
                "show_file_explorer": {"label": "Dosya Gezgini", "desc": "Sol taraftaki dosya ağacını göster"},
                "show_terminal": {"label": "Terminal Görünürlüğü", "desc": "Alt taraftaki terminal panelini göster"},
                "start_fullscreen": {"label": "Tam Ekran Başlat", "desc": "Uygulamayı tam ekran modunda başlat"},
                "theme_select": {"label": "Tema Seçimi", "desc": "Editör görünüm temasını seçin"},
                "terminal_type": {"label": "Terminal Tipi", "desc": "Kullanılacak kabuk (shell) türü"},
                "terminal_font_size": {"label": "Yazı Boyutu", "desc": "Terminal yazı tipi boyutu"},
                "terminal_history": {"label": "Geçmiş Limiti", "desc": "Terminal çıktısı için satır limiti"},
                "performance_mode": {"label": "Performans Modu", "desc": "Bazı görsel efektleri devre dışı bırakarak performansı artır"},
                "auto_backup": {"label": "Otomatik Yedekleme", "desc": "Dosyaları periyodik olarak .bak dosyasına yedekle"},
                "max_file_size": {"label": "Maksimum Dosya Boyutu", "desc": "Editörün açabileceği maksimum dosya boyutu (MB)"},
                "error_reporting": {"label": "Hata Raporlama", "desc": "Hata oluştuğunda geliştiriciye rapor gönder"},
                "seconds": "saniye",
                "selected": "✅ Seçildi",
                "preview": "Önizle",
                "apply_text": "Uygula"
            }
        }
    }

    def __init__(self, parent, current_settings: Dict[str, Any], on_apply: Callable):
        super().__init__(parent)
        
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.original_settings = current_settings.copy()  # Orijinal ayarları sakla
        self.on_apply_callback = on_apply
        self.modified_settings = {}
        self._current_category = "Genel"
        
        # Sadece Türkçe
        self.current_lang = "Türkçe"
        trans = self.TRANSLATIONS[self.current_lang]
        
        # Pencere ayarları
        self.title(trans["window_title"])
        self.geometry("950x700")
        self.minsize(850, 650)
        
        # Pencereyi merkeze al
        self.center_window()
        
        # Modal yap
        self.transient(parent)
        self.grab_set()
        
        # Ana container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sol panel (kategoriler)
        self.create_category_panel()
        
        # Sağ panel (ayarlar içeriği)
        self.create_content_panel()
        
        # Alt panel (butonlar)
        self.create_button_panel()
        
        # İlk kategoriyi göster
        self.show_category("Genel")
        
        # Tema uygula
        self.apply_theme()
        
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştirir."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    
    def get_text(self, category, key):
        """Çeviri sözlüğünden metin çeker."""
        try:
            return self.TRANSLATIONS[self.current_lang][category][key]
        except KeyError:
            # Anahtar eksikse Türkçe'ye geri dön
            try:
                return self.TRANSLATIONS["Türkçe"][category][key]
            except:
                return key
                
    def get_setting_text(self, key):
        """Ayarla ilgili label ve description döndürür."""
        try:
            data = self.TRANSLATIONS[self.current_lang]["settings"][key]
            return data["label"], data["desc"]
        except:
             return key, ""
             
    def create_category_panel(self):
        """Sol taraftaki kategori panelini oluşturur."""
        self.category_frame = ctk.CTkFrame(self.main_container, width=220, corner_radius=10)
        self.category_frame.pack(side="left", fill="y", padx=(0, 10))
        self.category_frame.pack_propagate(False)
        
        # Başlık ve değişiklik göstergesi
        header_frame = ctk.CTkFrame(self.category_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        trans = self.TRANSLATIONS[self.current_lang]
        
        self.panel_title_label = ctk.CTkLabel(
            header_frame,
            text=trans["panel_title"],
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.panel_title_label.pack(side="left")
        
        # Değişiklik sayacı badge
        self.changes_badge = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#ff6b6b", "#cc5555"),
            corner_radius=10,
            width=24,
            height=24
        )
        # Başlangıçta gizle
        
        # Arama kutusu
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        search_frame = ctk.CTkFrame(self.category_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=trans["search_placeholder"],
            textvariable=self.search_var,
            height=32,
            corner_radius=8
        )
        self.search_entry.pack(fill="x")
        
        # Ayırıcı
        separator = ctk.CTkFrame(self.category_frame, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        # Kategoriler
        self.categories = {
            "Genel": "🌐",
            "Editör": "📝",
            "Görünüm": "👁️",
            "Tema": "🎨",
            "Klavye Kısayolları": "⌨️",
            "Terminal": "💻",
            "Gelişmiş": "⚡"
        }
        
        self.category_buttons = {}
        for category, icon in self.categories.items():
            # Kategori ismini dile göre çevir
            display_name = trans["categories"].get(category, category)
            
            btn = ctk.CTkButton(
                self.category_frame,
                text=f"{icon}  {display_name}",
                command=lambda c=category: self.show_category(c),
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("gray80", "gray25")
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.category_buttons[category] = btn
        
        # Alt kısma versiyon bilgisi
        version_frame = ctk.CTkFrame(self.category_frame, fg_color="transparent")
        version_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        version_label = ctk.CTkLabel(
            version_frame,
            text="Memati Editör v2.0",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        version_label.pack()
    
    def _on_search_change(self, *args):
        """Arama değiştiğinde çağrılır."""
        query = self.search_var.get().lower().strip()
        if query:
            self.show_search_results(query)
        else:
            # Aramayı temizle, mevcut kategoriye dön
            self.show_category(self._current_category if hasattr(self, '_current_category') else "Genel")
    
    def show_search_results(self, query: str):
        """Arama sonuçlarını gösterir."""
        # Başlığı güncelle
        self.content_title.configure(text=f"🔍 Arama: \"{query}\"")
        
        # İçeriği temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Sınıf sabitini kullan (optimizasyon)
        results = []
        for name, (category, key, icon) in self.ALL_SETTINGS.items():
            if query in name.lower() or query in category.lower() or query in key.lower():
                current_value = self.current_settings.get(key, "—")
                results.append((name, category, key, icon, current_value))
        
        # Sonuç sayısını göster
        result_count_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"📊 {len(results)} sonuç bulundu",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        result_count_label.pack(anchor="w", pady=(0, 10))
        
        if results:
            for name, category, key, icon, current_value in results:
                result_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=8)
                result_frame.pack(fill="x", pady=5)
                
                # Üst kısım: İkon ve isim
                header_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=15, pady=(10, 2))
                
                ctk.CTkLabel(
                    header_frame,
                    text=f"{icon} {name}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w"
                ).pack(side="left")
                
                # Mevcut değer
                value_text = str(current_value)[:30] + "..." if len(str(current_value)) > 30 else str(current_value)
                ctk.CTkLabel(
                    header_frame,
                    text=f"= {value_text}",
                    font=ctk.CTkFont(size=11),
                    text_color=("gray50", "gray60")
                ).pack(side="right")
                
                cat_btn = ctk.CTkButton(
                    result_frame,
                    text=f"📁 {category} kategorisine git →",
                    fg_color="transparent",
                    hover_color=("gray80", "gray25"),
                    anchor="w",
                    height=30
                )
                cat_btn.pack(fill="x", padx=10, pady=(0, 10))
        else:
            no_result_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            no_result_frame.pack(expand=True, fill="both")
            
            ctk.CTkLabel(
                no_result_frame,
                text="🔍",
                font=ctk.CTkFont(size=48)
            ).pack(pady=(50, 10))
            
            ctk.CTkLabel(
                no_result_frame,
                text="Sonuç bulunamadı",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack()
            
            ctk.CTkLabel(
                no_result_frame,
                text="Farklı anahtar kelimeler deneyin",
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60")
            ).pack(pady=(5, 0))
    
    def _goto_category(self, category: str):
        """Kategoriye git ve aramayı temizle."""
        self.search_var.set("")
        self.show_category(category)
    
    def _update_changes_badge(self):
        """Gelişmiş değişiklik badge'ini günceller."""
        # Gerçek değişiklik sayısını hesapla (orijinalden farklı olanlar)
        real_changes = 0
        for key, value in self.modified_settings.items():
            original = self.original_settings.get(key)
            if value != original:
                real_changes += 1
        
        if real_changes > 0:
            # Badge'i göster ve renklendi
            if real_changes >= 5:
                badge_color = ("#e74c3c", "#c0392b")  # Kırmızı - çok değişiklik
            elif real_changes >= 3:
                badge_color = ("#f39c12", "#d68910")  # Turuncu - orta
            else:
                badge_color = ("#27ae60", "#1e8449")  # Yeşil - az
            
            self.changes_badge.configure(
                text=str(real_changes),
                fg_color=badge_color
            )
            self.changes_badge.pack(side="right", padx=(5, 0))
            
            # Pencere başlığını güncelle
            self.title(f"⚙️ Ayarlar ({real_changes} değişiklik)")
        else:
            self.changes_badge.pack_forget()
            self.title("⚙️ Ayarlar")
            
    def create_content_panel(self):
        """Sağ taraftaki içerik panelini oluşturur."""
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Başlık
        self.content_title = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.content_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Ayırıcı
        separator = ctk.CTkFrame(self.content_frame, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=20, pady=(0, 15))
        
        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
    def create_button_panel(self):
        """Alt kısımdaki buton panelini oluşturur."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Sağ tarafa hizala
        right_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_frame.pack(side="right")
        
        trans = self.TRANSLATIONS[self.current_lang]
        
        # Varsayılana Dön butonu
        self.reset_btn = ctk.CTkButton(
            right_frame,
            text=trans["buttons"]["reset"],
            command=self.reset_to_defaults,
            width=150,
            height=35,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.reset_btn.pack(side="left", padx=5)
        
        # İptal butonu
        self.cancel_btn = ctk.CTkButton(
            right_frame,
            text=trans["buttons"]["cancel"],
            command=self.cancel,
            width=100,
            height=35,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        # Uygula butonu
        self.apply_btn = ctk.CTkButton(
            right_frame,
            text=trans["buttons"]["apply"],
            command=self.apply_settings,
            width=100,
            height=35,
            corner_radius=8
        )
        self.apply_btn.pack(side="left", padx=5)
        
    def show_category(self, category: str):
        """Seçilen kategoriyi gösterir."""
        # Mevcut kategoriyi kaydet
        self._current_category = category
        
        # Tüm butonları normal yap
        for btn in self.category_buttons.values():
            btn.configure(fg_color="transparent")
            
        # Seçili butonu vurgula
        self.category_buttons[category].configure(fg_color=("gray75", "gray28"))
        
        # Başlığı güncelle
        icon = self.categories[category]
        
        # Çevrilmiş kategori adını kullan
        display_name = self.TRANSLATIONS[self.current_lang]["categories"].get(category, category)
        self.content_title.configure(text=f"{icon} {display_name}")
        
        # İçeriği temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Kategori içeriğini göster
        if category == "Genel":
            self.show_general_settings()
        elif category == "Editör":
            self.show_editor_settings()
        elif category == "Görünüm":
            self.show_view_settings()
        elif category == "Tema":
            self.show_theme_settings()
        elif category == "Klavye Kısayolları":
            self.show_keyboard_shortcuts()
        elif category == "Terminal":
            self.show_terminal_settings()
        elif category == "Gelişmiş":
            self.show_advanced_settings()
            
    def create_setting_row(self, parent, label_text, description=""):
        """
        Ayar satırı oluşturur ve widget için container frame döndürür.
        Grid Layout kullanılır: Sol (Label) - Sağ (Widget Container)
        """
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=7, padx=5)
        
        # Grid ayarları: Sol taraf genişler, sağ taraf widget kadar yer kaplar
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=0)
        
        # Sol Taraf - Label ve Açıklama
        left_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        label = ctk.CTkLabel(
            left_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(anchor="w")
        
        if description:
            desc_label = ctk.CTkLabel(
                left_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60"),
                anchor="w",
                wraplength=350,
                justify="left"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
            
        # Sağ Taraf - Widget Container
        right_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e")
        
        return right_frame
        
    def show_general_settings(self):
        """Genel ayarları gösterir."""
        # Uygulama Adı
        container = self.create_setting_row(
            self.scrollable_frame,
            "Uygulama Adı",
            "Başlık çubuğunda görünen uygulama adı"
        )
        app_name_entry = ctk.CTkEntry(
            container,
            width=200,
            placeholder_text="Uygulama Adı"
        )
        app_name_entry.insert(0, self.current_settings.get("app_name", "Memati Editör"))
        app_name_entry.configure(state="readonly")
        app_name_entry.pack(side="right")
        
        # Yazı Tipi
        font_families = list(tkfont.families())
        font_families.sort()
        font_var = tk.StringVar(value=self.current_settings.get("font_family", "Consolas"))
        
        container = self.create_setting_row(
            self.scrollable_frame,
            "Yazı Tipi",
            "Editörde kullanılacak yazı tipi ailesi"
        )
        font_combo = ctk.CTkComboBox(
            container,
            values=font_families,
            variable=font_var,
            width=200,
            command=lambda choice: self.update_setting("font_family", choice)
        )
        font_combo.pack(side="right")
        
        # Yazı Boyutu
        container = self.create_setting_row(
            self.scrollable_frame,
            "Yazı Boyutu",
            "Editör yazı tipi boyutu (8-32)"
        )
        
        font_size_var = tk.IntVar(value=self.current_settings.get("font_size", 14))
        
        def decrease_font():
            current = font_size_var.get()
            if current > 8:
                font_size_var.set(current - 1)
                self.update_setting("font_size", current - 1)
                
        def increase_font():
            current = font_size_var.get()
            if current < 32:
                font_size_var.set(current + 1)
                self.update_setting("font_size", current + 1)
        
        # Kontrolleri sağ container içine ekle
        plus_btn = ctk.CTkButton(container, text="+", width=30, command=increase_font)
        plus_btn.pack(side="right", padx=(5, 0))
        
        size_label = ctk.CTkLabel(
            container,
            textvariable=font_size_var,
            width=30,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        size_label.pack(side="right")
        
        minus_btn = ctk.CTkButton(container, text="-", width=30, command=decrease_font)
        minus_btn.pack(side="right")
        

        
    def show_editor_settings(self):
        """Editör ayarlarını gösterir."""
        # Satır Numaraları
        line_numbers_var = tk.BooleanVar(value=self.current_settings.get("show_line_numbers", True))
        lbl, desc = self.get_setting_text("show_line_numbers")
        
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=line_numbers_var,
            command=lambda: self.update_setting("show_line_numbers", line_numbers_var.get())
        ).pack(side="right")
        
        # Word Wrap
        word_wrap_var = tk.BooleanVar(value=self.current_settings.get("word_wrap", False))
        lbl, desc = self.get_setting_text("word_wrap")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=word_wrap_var,
            command=lambda: self.update_setting("word_wrap", word_wrap_var.get())
        ).pack(side="right")
        
        # Minimap
        minimap_var = tk.BooleanVar(value=self.current_settings.get("show_minimap", True))
        lbl, desc = self.get_setting_text("show_minimap")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=minimap_var,
            command=lambda: self.update_setting("show_minimap", minimap_var.get())
        ).pack(side="right")
        
        # Tab Boyutu
        tab_size_var = tk.IntVar(value=self.current_settings.get("tab_size", 4))
        lbl, desc = self.get_setting_text("tab_size")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        combo = ctk.CTkComboBox(
            container,
            values=["2", "4", "8"],
            variable=tk.StringVar(value=str(tab_size_var.get())),
            width=100,
            command=lambda choice: self.update_setting("tab_size", int(choice))
        )
        combo.pack(side="right")
        
        # Otomatik Kaydetme
        auto_save_var = tk.BooleanVar(value=self.current_settings.get("auto_save", True))
        lbl, desc = self.get_setting_text("auto_save")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=auto_save_var,
            command=lambda: self.update_setting("auto_save", auto_save_var.get())
        ).pack(side="right")
        
        # Otomatik Kaydetme Aralığı
        auto_save_interval_var = tk.IntVar(value=self.current_settings.get("auto_save_interval", 30))
        lbl, desc = self.get_setting_text("auto_save_interval")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        sec_text = self.TRANSLATIONS[self.current_lang]["settings"].get("seconds", "saniye")
        ctk.CTkLabel(container, text=sec_text, font=ctk.CTkFont(size=11)).pack(side="right", padx=(5, 0))
        
        ctk.CTkLabel(
            container,
            textvariable=auto_save_interval_var,
            width=30,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        ctk.CTkSlider(
            container,
            from_=10,
            to=120,
            number_of_steps=11,
            variable=auto_save_interval_var,
            width=150,
            command=lambda val: self.update_setting("auto_save_interval", int(val))
        ).pack(side="right", padx=(0, 10))
        
        # Parantez Eşleştirme
        bracket_match_var = tk.BooleanVar(value=self.current_settings.get("bracket_matching", True))
        lbl, desc = self.get_setting_text("bracket_matching")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=bracket_match_var,
            command=lambda: self.update_setting("bracket_matching", bracket_match_var.get())
        ).pack(side="right")
        
        # Sözdizimi Vurgulama
        syntax_highlight_var = tk.BooleanVar(value=self.current_settings.get("syntax_highlighting", True))
        lbl, desc = self.get_setting_text("syntax_highlighting")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=syntax_highlight_var,
            command=lambda: self.update_setting("syntax_highlighting", syntax_highlight_var.get())
        ).pack(side="right")
        
    def show_view_settings(self):
        """Görünüm ayarlarını gösterir."""
        # Durum Çubuğu
        status_bar_var = tk.BooleanVar(value=self.current_settings.get("show_status_bar", True))
        lbl, desc = self.get_setting_text("show_status_bar")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=status_bar_var,
            command=lambda: self.update_setting("show_status_bar", status_bar_var.get())
        ).pack(side="right")
        
        # Dosya Gezgini
        file_explorer_var = tk.BooleanVar(value=self.current_settings.get("show_file_explorer", True))
        lbl, desc = self.get_setting_text("show_file_explorer")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=file_explorer_var,
            command=lambda: self.update_setting("show_file_explorer", file_explorer_var.get())
        ).pack(side="right")
        
        # Terminal
        terminal_var = tk.BooleanVar(value=self.current_settings.get("show_terminal", False))
        lbl, desc = self.get_setting_text("show_terminal")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=terminal_var,
            command=lambda: self.update_setting("show_terminal", terminal_var.get())
        ).pack(side="right")
        
        # Tam Ekran Başlangıç
        fullscreen_var = tk.BooleanVar(value=self.current_settings.get("start_fullscreen", False))
        lbl, desc = self.get_setting_text("start_fullscreen")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=fullscreen_var,
            command=lambda: self.update_setting("start_fullscreen", fullscreen_var.get())
        ).pack(side="right")
        
    def show_theme_settings(self):
        """Tema ayarlarını gösterir."""
        from text_editor.theme_config import get_available_themes
        
        # Tema Seçimi
        themes = get_available_themes()
        current_theme_name = self.current_settings.get("theme", "Dark")
        self.theme_var = tk.StringVar(value=current_theme_name)
        
        # Kart referanslarını sakla
        self.theme_cards = {}
        
        lbl, desc = self.get_setting_text("theme_select")
        
        # Başlık ve açıklama
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text=lbl,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
            anchor="w"
        ).pack(anchor="w")
        
        # Grid container
        self.theme_grid_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.theme_grid_frame.pack(fill="both", expand=True)
        self.theme_grid_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Temaları oluştur
        for i, theme_name in enumerate(themes):
            self.create_theme_card(self.theme_grid_frame, theme_name, i)
            
    def create_theme_card(self, parent, theme_name, index):
        """Modelleştirilmiş, etkileşimli tema kartı oluşturur."""
        from text_editor.theme_config import get_theme
        theme = get_theme(theme_name)
        
        is_selected = (theme_name == self.theme_var.get())
        
        # Kart Çerçevesi
        # Border rengini seçili duruma göre ayarla
        border_color = theme["accent_color"] if is_selected else "gray60"
        if not is_selected and theme.get("type") == "Dark":
            border_color = "gray40" 
            
        card = ctk.CTkFrame(
            parent,
            fg_color=theme["bg"],
            corner_radius=12,
            border_width=3 if is_selected else 1,
            border_color=border_color,
            cursor="hand2" 
        )
        
        # Şebeke Yerleşimi (3 sütun)
        row = index // 3
        col = index % 3
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Referansı kaydet
        self.theme_cards[theme_name] = card
        
        # Tıklama Event Handler (Closure ile theme_name'i yakala)
        def on_click(event=None):
            self.select_theme(theme_name)
            
        # Kartın kendisine ve içindeki tüm bileşenlere tıklama özelliği ekle
        card.bind("<Button-1>", on_click)
        
        # Önizleme Alanı
        preview_frame = ctk.CTkFrame(card, fg_color="transparent", height=90)
        preview_frame.pack(fill="x", padx=10, pady=10)
        preview_frame.pack_propagate(False)
        preview_frame.bind("<Button-1>", on_click)
        
        # Sahte Kod Bloğu
        code_bg = theme["editor_bg"]
        code_fg = theme["fg"]
        
        code_preview = ctk.CTkFrame(preview_frame, fg_color=code_bg, corner_radius=6)
        code_preview.pack(fill="both", expand=True)
        code_preview.bind("<Button-1>", on_click)
        
        # Renkleri temadan çek
        func_color = theme.get("status_bg", "#8be9fd") # fonksiyon ismi için
        string_color = theme.get("line_num_fg", "#f1fa8c") # string için
        
        # Kod satırları
        # 1. def hello():
        line1 = ctk.CTkLabel(
            code_preview,
            text=f"def {theme_name.lower().replace(' ', '_')}():",
            text_color=code_fg,
            font=ctk.CTkFont(family="Consolas", size=10),
            anchor="w"
        )
        line1.pack(padx=8, pady=(8, 0), fill="x")
        line1.bind("<Button-1>", on_click)
        
        # 2.    return "World"
        line2 = ctk.CTkLabel(
            code_preview,
            text='    return "World"',
            text_color=string_color, 
            font=ctk.CTkFont(family="Consolas", size=10),
            anchor="w"
        )
        line2.pack(padx=8, pady=(2, 8), fill="x")
        line2.bind("<Button-1>", on_click)
        
        # Alt Bilgi (İsim ve Durum)
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=(0, 12))
        footer.bind("<Button-1>", on_click)
        
        # Tema Adı
        name_label = ctk.CTkLabel(
            footer, 
            text=theme_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme["fg"]
        )
        name_label.pack(side="left")
        name_label.bind("<Button-1>", on_click)
        
        # Seçili İkonu
        if is_selected:
            check_icon = ctk.CTkLabel(
                footer,
                text="✅",
                font=ctk.CTkFont(size=14),
                text_color=theme["accent_color"]
            )
            check_icon.pack(side="right")
            check_icon.bind("<Button-1>", on_click)
            # Referans kaydet
            card.check_icon = check_icon
            
    def select_theme(self, theme_name):
        """Bir tema seçildiğinde çalışır."""
        prev_theme = self.theme_var.get()
        # Eğer zaten seçiliyse işlem yapma
        if prev_theme == theme_name:
            return

        self.theme_var.set(theme_name)
        
        # Ayarı güncelle
        self.update_setting("theme", theme_name)
        
        # Uygulamaya anlık uygula
        if hasattr(self.parent, 'apply_theme'):
            self.parent.apply_theme(theme_name)
            
        # --- UI Güncellemesi (Yeniden çizmeden) ---
        from text_editor.theme_config import get_theme
        
        # 1. Eski seçili kartı normale döndür
        if prev_theme in self.theme_cards:
            old_card = self.theme_cards[prev_theme]
            old_theme_data = get_theme(prev_theme)
            
            border_col = "gray40" if old_theme_data.get("type") == "Dark" else "gray60"
            old_card.configure(border_width=1, border_color=border_col)
            
            # Varsa check ikonunu kaldır
            if hasattr(old_card, 'check_icon'):
                old_card.check_icon.destroy()
                delattr(old_card, 'check_icon')

        # 2. Yeni seçili kartı vurgula
        if theme_name in self.theme_cards:
            new_card = self.theme_cards[theme_name]
            new_theme_data = get_theme(theme_name)
            
            new_card.configure(border_width=3, border_color=new_theme_data["accent_color"])
            
            # Check ikonu ekle (eğer yoksa)
            if not hasattr(new_card, 'check_icon'):
                footer = new_card.winfo_children()[-1] # Footer son eleman
                check_icon = ctk.CTkLabel(
                    footer,
                    text="✅",
                    font=ctk.CTkFont(size=14),
                    text_color=new_theme_data["accent_color"]
                )
                check_icon.pack(side="right")
                
                # Ona da click event ekle
                def on_click_check(event=None):
                    self.select_theme(theme_name)
                check_icon.bind("<Button-1>", on_click_check)
                
                new_card.check_icon = check_icon
        
    def show_terminal_settings(self):
        """Terminal ayarlarını gösterir."""
        # Terminal Tipi
        lbl, desc = self.get_setting_text("terminal_type")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        system_shells = ["PowerShell", "Command Prompt", "Bash"] if os.name == "nt" else ["Bash", "Sh", "Zsh"]
        current_shell = self.current_settings.get("terminal_type", system_shells[0])
        
        combo = ctk.CTkComboBox(
            container,
            values=system_shells,
            command=lambda val: self.update_setting("terminal_type", val)
        )
        combo.set(current_shell)
        combo.pack(side="right")
        
        # Yazı Boyutu
        term_font_var = tk.IntVar(value=self.current_settings.get("terminal_font_size", 12))
        lbl, desc = self.get_setting_text("terminal_font_size")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkLabel(
            container,
            textvariable=term_font_var,
            width=30,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        ctk.CTkSlider(
            container,
            from_=8,
            to=24,
            number_of_steps=16,
            variable=term_font_var,
            width=150,
            command=lambda val: self.update_setting("terminal_font_size", int(val))
        ).pack(side="right", padx=(0, 10))
        
        # Geçmiş Limiti
        lbl, desc = self.get_setting_text("terminal_history")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        terminal_history_var = tk.IntVar(value=self.current_settings.get("terminal_history", 1000))
        
        ctk.CTkLabel(
            container,
            textvariable=terminal_history_var,
            width=40,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        ctk.CTkSlider(
            container,
            from_=100,
            to=5000,
            number_of_steps=49,
            variable=terminal_history_var,
            width=150,
            command=lambda val: self.update_setting("terminal_history", int(val))
        ).pack(side="right", padx=(0, 10))
        
    def show_advanced_settings(self):
        """Gelişmiş ayarları gösterir."""
        # Performans Modu
        perf_var = tk.BooleanVar(value=self.current_settings.get("performance_mode", False))
        lbl, desc = self.get_setting_text("performance_mode")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=perf_var,
            command=lambda: self.update_setting("performance_mode", perf_var.get())
        ).pack(side="right")
        
        # Otomatik Yedekleme
        backup_var = tk.BooleanVar(value=self.current_settings.get("auto_backup", True))
        lbl, desc = self.get_setting_text("auto_backup")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=backup_var,
            command=lambda: self.update_setting("auto_backup", backup_var.get())
        ).pack(side="right")
        
        # Maksimum Dosya Boyutu
        size_var = tk.IntVar(value=self.current_settings.get("max_file_size", 10))
        lbl, desc = self.get_setting_text("max_file_size")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkLabel(
            container,
            text="MB",
            font=ctk.CTkFont(size=12)
        ).pack(side="right", padx=(5, 0))
        
        ctk.CTkEntry(
            container,
            textvariable=size_var,
            width=60
        ).pack(side="right")
        
        # Hata Raporlama
        error_var = tk.BooleanVar(value=self.current_settings.get("error_reporting", True))
        lbl, desc = self.get_setting_text("error_reporting")
        container = self.create_setting_row(self.scrollable_frame, lbl, desc)
        
        ctk.CTkSwitch(
            container,
            text="",
            variable=error_var,
            command=lambda: self.update_setting("error_reporting", error_var.get())
        ).pack(side="right")
        
        # Ayırıcı
        ctk.CTkFrame(self.scrollable_frame, height=2, fg_color=("gray70", "gray30")).pack(fill="x", pady=20)
        
        # Ayarları Dışa Aktar
        export_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="📤 Ayarları Dışa Aktar", # Bunu da çevirebiliriz ama şimdilik kalsın veya hızlıca ekleyelim
            command=self.export_settings,
            height=35,
            corner_radius=8
        )
        export_btn.pack(pady=(20, 5), fill="x")
        
        # Ayarları İçe Aktar
        import_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="📥 Ayarları İçe Aktar",
            command=self.import_settings,
            height=35,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        import_btn.pack(pady=5, fill="x")
        

        
    def show_keyboard_shortcuts(self):
        """Klavye kısayollarını gösterir ve düzenlemeye izin verir."""
        shortcut_manager = ShortcutManager.get_instance()
        shortcuts = shortcut_manager.shortcuts
        metadata = shortcut_manager.SHORTCUT_METADATA
        
        # Kategorilere göre grupla
        grouped_shortcuts = {}
        for action_id, sequence in shortcuts.items():
            meta = metadata.get(action_id, {"category": "Diğer", "label": action_id})
            category = meta["category"]
            if category not in grouped_shortcuts:
                grouped_shortcuts[category] = []
            grouped_shortcuts[category].append((action_id, meta["label"], sequence))
            
        # UI Oluştur
        for category, items in grouped_shortcuts.items():
            # Kategori başlığı
            category_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=category,
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w"
            )
            category_label.pack(anchor="w", pady=(15, 5))
            
            # Ayırıcı
            separator = ctk.CTkFrame(
                self.scrollable_frame,
                height=1,
                fg_color=("gray70", "gray30")
            )
            separator.pack(fill="x", pady=(0, 10))
            
            # Kısayollar
            for action_id, label, sequence in items:
                display_seq = shortcut_manager.get_display_string(sequence)
                
                shortcut_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                shortcut_frame.pack(fill="x", pady=3)
                
                action_label = ctk.CTkLabel(
                    shortcut_frame,
                    text=label,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                action_label.pack(side="left")
                
                # Düzenlenebilir Buton
                shortcut_btn = ctk.CTkButton(
                    shortcut_frame,
                    text=display_seq if display_seq else "Yok",
                    font=ctk.CTkFont(size=11, family="Courier New"),
                    fg_color=("gray80", "gray25"),
                    text_color=("black", "white"),
                    hover_color=("gray70", "gray35"),
                    corner_radius=6,
                    height=24,
                    width=100,
                    command=lambda aid=action_id: self.start_shortcut_recording(aid)
                )
                shortcut_btn.pack(side="right")
        
        # En alta varsayılanlara sıfırla butonu
        reset_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        reset_frame.pack(fill="x", pady=(30, 20), padx=10)
        
        reset_btn = ctk.CTkButton(
            reset_frame,
            text="Varsayılanlara Sıfırla (Reset)",
            fg_color="#dc3545",
            hover_color="#c82333",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.reset_shortcuts_command
        )
        reset_btn.pack(side="right")
        
    def reset_shortcuts_command(self):
        """Kısayolları sıfırlar ve UI'ı yeniler."""
        manager = ShortcutManager.get_instance()
        manager.reset_to_defaults()
        self.show_settings_content('shortcuts')
        
    def start_shortcut_recording(self, action_id):
        # ... implementation continues below ...
        """Kısayol kaydetme diyaloğunu başlatır."""
        manager = ShortcutManager.get_instance()
        current_seq = manager.get(action_id)
        display_current = manager.get_display_string(current_seq)
        meta = manager.SHORTCUT_METADATA.get(action_id, {})
        action_label = meta.get("label", action_id)

        # Modal Diyalog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Kısayol Ata")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Ortala
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        # İçerik
        ctk.CTkLabel(
            dialog, 
            text=f"'{action_label}' için yeni kısayol",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(
            dialog,
            text="İstediğiniz tuş kombinasyonuna basın...\n(İptal etmek için ESC)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=5)
        
        shortcut_display = ctk.CTkLabel(
            dialog,
            text=display_current,
            font=ctk.CTkFont(size=24, weight="bold", family="Courier New"),
            fg_color=("gray90", "gray20"),
            corner_radius=8,
            width=200,
            height=50
        )
        shortcut_display.pack(pady=20)
        
        # Tuş Yakalama
        current_keys = set()
        
        def on_key_press(event):
            # Modifier tuşlarını kontrol et
            is_ctrl = (event.state & 0x4) != 0
            is_alt = (event.state & 0x20000) != 0 or (event.state & 0x20) != 0 # Windows vs Linux alt
            is_shift = (event.state & 0x1) != 0
            
            keys = []
            if is_ctrl: keys.append("Control")
            if is_alt: keys.append("Alt")
            if is_shift: keys.append("Shift")
            
            # Ana tuş (Modifier değilse)
            if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
                keys.append(event.keysym)
            
            # Tkinter formatı oluştur: <Control-Key-c> gibi
            # Basitleştirilmiş format: <Control-c>
            
            # Eğer sadece modifier varsa gösterme
            if not keys or (len(keys) == 1 and keys[0] in ("Control", "Alt", "Shift")):
                shortcut_display.configure(text=" + ".join(keys) + " ...")
                return

            # Sequence oluştur
            parts = []
            if "Control" in keys: parts.append("Control")
            if "Alt" in keys: parts.append("Alt")
            if "Shift" in keys: parts.append("Shift")
            
            # Son tuşu ekle (varsa ve modifier değilse)
            last_key = keys[-1]
            if last_key not in ("Control", "Alt", "Shift"):
                # Özel isimlendirmeleri düzelt (örn: return -> Return)
                parts.append(last_key)
            
            sequence = f"<{'-'.join(parts)}>"
            
            # Görselleştir
            shortcut_display.configure(text=manager.get_display_string(sequence))
            
            # ESC iptal eder
            if event.keysym == "Escape":
                dialog.destroy()
                return

            # Kaydet ve kapat
            # Kullanıcıya onay sorabiliriz veya direkt kaydedebiliriz.
            # Şimdilik direkt kaydediyoruz ama bir "Kaydet" butonu daha güvenli olabilir.
            # Ancak UX açısından tuşa basınca algılaması daha hızlı.
            
            # Onay butonu aktifleşsin
            save_btn.configure(state="normal", command=lambda: apply_shortcut(sequence))
            
        def apply_shortcut(seq):
            manager.set(action_id, seq)
            dialog.destroy()
            # Listeyi yenilemek için paneli güncelle
            self.show_category("Klavye Kısayolları")
            
        save_btn = ctk.CTkButton(
            dialog,
            text="Kaydet",
            state="disabled",
            width=100
        )
        save_btn.pack(side="left", padx=20, pady=20, expand=True)
        
        cancel_btn = ctk.CTkButton(
            dialog,
            text="İptal",
            command=dialog.destroy,
            fg_color="transparent",
            border_width=1,
            width=100
        )
        cancel_btn.pack(side="right", padx=20, pady=20, expand=True)
        
        dialog.bind("<Key>", on_key_press)
        dialog.focus_set()
                
    def show_terminal_settings(self):
        """Terminal ayarlarını gösterir."""
        # Terminal Tipi
        terminal_type_var = tk.StringVar(value=self.current_settings.get("terminal_type", "PowerShell"))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Terminal Tipi",
            "Kullanılacak terminal türü"
        )
        ctk.CTkComboBox(
            container,
            values=["PowerShell", "CMD", "Bash"],
            variable=terminal_type_var,
            width=200,
            command=lambda choice: self.update_setting("terminal_type", choice)
        ).pack(side="right")
        
        # Terminal Yazı Boyutu
        terminal_font_size_var = tk.IntVar(value=self.current_settings.get("terminal_font_size", 12))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Terminal Yazı Boyutu",
            "Terminal yazı tipi boyutu"
        )
        combo = ctk.CTkComboBox(
            container,
            values=["10", "11", "12", "13", "14", "16"],
            width=100,
            command=lambda choice: self.update_setting("terminal_font_size", int(choice))
        )
        combo.set(str(terminal_font_size_var.get()))
        combo.pack(side="right")
        
        # Terminal Geçmişi
        terminal_history_var = tk.IntVar(value=self.current_settings.get("terminal_history", 1000))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Geçmiş Satır Sayısı",
            "Terminal geçmişinde tutulacak satır sayısı"
        )
        
        ctk.CTkLabel(
            container,
            textvariable=terminal_history_var,
            width=40,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", padx=5)
        
        ctk.CTkSlider(
            container,
            from_=100,
            to=5000,
            number_of_steps=49,
            variable=terminal_history_var,
            width=150,
            command=lambda val: self.update_setting("terminal_history", int(val))
        ).pack(side="right", padx=(0, 10))
        
    def show_advanced_settings(self):
        """Gelişmiş ayarları gösterir."""
        # Performans Modu
        performance_var = tk.BooleanVar(value=self.current_settings.get("performance_mode", False))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Performans Modu",
            "Bazı görsel efektleri devre dışı bırakarak performansı artır"
        )
        ctk.CTkSwitch(
            container,
            text="",
            variable=performance_var,
            command=lambda: self.update_setting("performance_mode", performance_var.get())
        ).pack(side="right")
        
        # Yedekleme
        backup_var = tk.BooleanVar(value=self.current_settings.get("auto_backup", True))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Otomatik Yedekleme",
            "Dosyaların otomatik yedeğini al"
        )
        ctk.CTkSwitch(
            container,
            text="",
            variable=backup_var,
            command=lambda: self.update_setting("auto_backup", backup_var.get())
        ).pack(side="right")
        
        # Maksimum Dosya Boyutu (MB)
        max_file_size_var = tk.IntVar(value=self.current_settings.get("max_file_size", 10))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Maksimum Dosya Boyutu",
            "Açılabilecek maksimum dosya boyutu"
        )
        
        ctk.CTkLabel(container, text="MB", font=ctk.CTkFont(size=11)).pack(side="right", padx=(5, 0))
        
        ctk.CTkLabel(
            container,
            textvariable=max_file_size_var,
            width=40,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        ctk.CTkSlider(
            container,
            from_=1,
            to=100,
            number_of_steps=99,
            variable=max_file_size_var,
            width=150,
            command=lambda val: self.update_setting("max_file_size", int(val))
        ).pack(side="right", padx=(0, 10))
        
        # Hata Raporlama
        error_reporting_var = tk.BooleanVar(value=self.current_settings.get("error_reporting", True))
        container = self.create_setting_row(
            self.scrollable_frame,
            "Hata Raporlama",
            "Hataları otomatik olarak raporla"
        )
        ctk.CTkSwitch(
            container,
            text="",
            variable=error_reporting_var,
            command=lambda: self.update_setting("error_reporting", error_reporting_var.get())
        ).pack(side="right")
        
        # Ayarları Dışa Aktar
        export_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="📤 Ayarları Dışa Aktar",
            command=self.export_settings,
            height=35,
            corner_radius=8
        )
        export_btn.pack(pady=(20, 5), fill="x")
        
        # Ayarları İçe Aktar
        import_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="📥 Ayarları İçe Aktar",
            command=self.import_settings,
            height=35,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        import_btn.pack(pady=5, fill="x")
        
    def update_setting(self, key: str, value: Any):
        """
        Ayarı günceller.
        Eğer değer orijinal değerle aynıysa, değişiklik listesinden kaldırır.
        """
        original_value = self.original_settings.get(key)
        
        if value == original_value:
            # Orijinal değere dönüldü, değişiklik listesinden kaldır
            self.modified_settings.pop(key, None)
        else:
            # Gerçek bir değişiklik
            self.modified_settings[key] = value
        
        # current_settings'i de güncelle (canlı önizleme için)
        self.current_settings[key] = value
        self._update_changes_badge()
        
    def apply_settings(self):
        """Değişiklikleri uygular."""
        if self.modified_settings:
            # Mevcut ayarları güncelle
            self.current_settings.update(self.modified_settings)
            
            # Callback'i çağır
            if self.on_apply_callback:
                self.on_apply_callback(self.current_settings)
                
            # Ayarları kaydet
            self.save_settings()
            
        self.destroy()
        
    def cancel(self):
        """Değişiklikleri iptal eder ve pencereyi kapatır."""
        self.destroy()
        
    def reset_to_defaults(self):
        """Tüm ayarları varsayılan değerlere döndürür."""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Varsayılana Dön",
            "Tüm ayarlar varsayılan değerlere dönecek. Emin misiniz?",
            parent=self
        )
        
        if result:
            self.current_settings = self.get_default_settings()
            self.modified_settings = self.current_settings.copy()
            # Mevcut kategoriyi yeniden göster
            current_category = None
            for category, btn in self.category_buttons.items():
                if btn.cget("fg_color") != "transparent":
                    current_category = category
                    break
            if current_category:
                self.show_category(current_category)
                
    def get_default_settings(self) -> Dict[str, Any]:
        """Varsayılan ayarları döndürür."""
        return {
            "app_name": "Memati Editör",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "Türkçe",
            "show_line_numbers": True,
            "word_wrap": False,
            "show_minimap": True,
            "tab_size": 4,
            "auto_save": True,
            "auto_save_interval": 30,
            "bracket_matching": True,
            "syntax_highlighting": True,
            "show_status_bar": True,
            "show_file_explorer": True,
            "show_terminal": False,
            "start_fullscreen": False,
            "theme": "Dark",
            "terminal_type": "PowerShell",
            "terminal_font_size": 12,
            "terminal_history": 1000,
            "performance_mode": False,
            "auto_backup": True,
            "max_file_size": 10,
            "error_reporting": True
        }
        
    def save_settings(self):
        """Ayarları dosyaya kaydeder."""
        settings_dir = os.path.join(os.path.expanduser("~"), ".memati_editor")
        os.makedirs(settings_dir, exist_ok=True)
        
        settings_file = os.path.join(settings_dir, "settings.json")
        
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.current_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilemedi: {e}")
            
    def load_settings(self) -> Dict[str, Any]:
        """Ayarları dosyadan yükler."""
        settings_file = os.path.join(
            os.path.expanduser("~"),
            ".memati_editor",
            "settings.json"
        )
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ayarlar yüklenemedi: {e}")
                
        return self.get_default_settings()
        
    def export_settings(self):
        """Ayarları dışa aktarır."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Ayarları Dışa Aktar",
            defaultextension=".json",
            filetypes=[("JSON Dosyası", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.current_settings, f, indent=4, ensure_ascii=False)
                    
                from tkinter import messagebox
                messagebox.showinfo(
                    "Başarılı",
                    "Ayarlar başarıyla dışa aktarıldı!",
                    parent=self
                )
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror(
                    "Hata",
                    f"Ayarlar dışa aktarılamadı:\n{e}",
                    parent=self
                )
                
    def import_settings(self):
        """Ayarları içe aktarır."""
        from tkinter import filedialog, messagebox
        
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Ayarları İçe Aktar",
            filetypes=[("JSON Dosyası", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported_settings = json.load(f)
                    
                self.current_settings.update(imported_settings)
                self.modified_settings = self.current_settings.copy()
                
                # Mevcut kategoriyi yeniden göster
                current_category = None
                for category, btn in self.category_buttons.items():
                    if btn.cget("fg_color") != "transparent":
                        current_category = category
                        break
                if current_category:
                    self.show_category(current_category)
                    
                messagebox.showinfo(
                    "Başarılı",
                    "Ayarlar başarıyla içe aktarıldı!",
                    parent=self
                )
            except Exception as e:
                messagebox.showerror(
                    "Hata",
                    f"Ayarlar içe aktarılamadı:\n{e}",
                    parent=self
                )
                
    def apply_theme(self):
        """Mevcut temayı pencereye uygular."""
        # Bu metod parent'tan tema bilgisini alıp uygulayabilir
        pass
