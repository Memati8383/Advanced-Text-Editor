import tkinter as tk
from typing import Any, Optional, Tuple

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name

from text_editor.config import FONT_FAMILY
from text_editor.utils.highlighter import SyntaxHighlighter

# Yapılandırma Sabitleri
MINIMAP_WIDTH: int = 20
MINIMAP_FONT_SIZE: int = 2
VIEWPORT_TAG: str = "viewport"
HOVER_TAG: str = "hover"
MAX_HIGHLIGHT_CHARS: int = 100000  # Büyük dosyalar için vurgulamayı devre dışı bırak
UPDATE_DELAY_MS: int = 50


class Minimap(tk.Text):
    """
    Ana metin düzenleyici içeriğinin küçültülmüş bir önizlemesini görüntüleyen minimap aracı.
    Görsel genel bakış ve doğrudan gezinme işlevselliği sağlar.
    """

    def __init__(self, master: tk.Widget, main_text: tk.Text, **kwargs: Any) -> None:
        """
        Minimap aracını başlatır.

        Argümanlar:
            master: Ebeveyn pencere öğesi.
            main_text: Senkronize edilecek ana metin düzenleyici pencere öğesi.
            **kwargs: Metin (Text) pencere öğesi için ek yapılandırma seçenekleri.
        """
        super().__init__(
            master,
            width=MINIMAP_WIDTH,
            wrap="none",
            bd=0,
            highlightthickness=0,
            state="disabled",
            cursor="arrow",
            exportselection=False,
            takefocus=False,
            **kwargs
        )
        
        self.main_text = main_text
        self.highlighter: Optional[SyntaxHighlighter] = SyntaxHighlighter(self)
        self.current_lexer: Optional[Lexer] = get_lexer_by_name("text")
        
        self._update_task: Optional[str] = None
        self._last_content_hash: Optional[int] = None
        
        self._configure_appearance()
        self._bind_events()

    def _configure_appearance(self) -> None:
        """Başlangıç görünümünü ve yazı tipi ayarlarını yapılandırır."""
        self.configure(font=(FONT_FAMILY, MINIMAP_FONT_SIZE))
        # Başlangıç viewport rengi (configure_colors ile güncellenecek)
        self.tag_configure(VIEWPORT_TAG, background="#3e3e42", borderwidth=0)

    def _bind_events(self) -> None:
        """Fare etkileşimlerini ve kaydırma olaylarını bağlar."""
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)
        # Linux kaydırma düğmeleri desteği
        self.bind("<Button-4>", self._on_wheel)
        self.bind("<Button-5>", self._on_wheel)

    def update_content(self, event: Optional[tk.Event] = None) -> None:
        """
        Minimap içeriğini ana metin düzenleyici ile senkronize eder.
        Performans için debouncing (gecikmeli güncelleme) kullanır.
        """
        if self._update_task:
            self.after_cancel(self._update_task)
            
        self._update_task = self.after(UPDATE_DELAY_MS, self._perform_update)

    def force_update(self) -> None:
        """Anlık güncellemeyi zorlar (debouncing olmadan)."""
        if self._update_task:
            self.after_cancel(self._update_task)
            self._update_task = None
        self._perform_update()

    def _perform_update(self) -> None:
        """Gerçek içerik güncelleme işlemi."""
        self._update_task = None
        try:
            # Ana düzenleyiciden geçerli içeriği al
            content = self.main_text.get("1.0", "end-1c")
            content_hash = hash(content)
            
            # OPTİMİZASYON: İçerik değişmediyse sadece görünüm alanını güncelle
            if self._last_content_hash == content_hash:
                self._update_viewport_indicator()
                return
            
            self._last_content_hash = content_hash
            
            # Minimap içeriğini güncelle
            self.configure(state="normal")
            self.replace("1.0", "end", content)
            
            # OPTİMİZASYON: Çok büyük dosyalarda vurgulamayı atla
            if len(content) < MAX_HIGHLIGHT_CHARS:
                self._highlight_content(content)
            
            self.configure(state="disabled")
            
            # Görünüm alanını güncelle
            self._update_viewport_indicator()
        except Exception:
            pass

    def _highlight_content(self, content: str) -> None:
        """Minimap içeriğine sözdizimi vurgulaması uygular."""
        if self.highlighter and self.current_lexer:
            try:
                self.highlighter.highlight(content, self.current_lexer)
            except Exception:
                pass

    def on_scroll(self, *args: Any) -> None:
        """
        Ana metin düzenleyici kaydırıldığında çağrılan geri çağırma işlevi.
        Minimap'in dikey görünümünü senkronize eder ve görünüm alanı göstergesini günceller.
        """
        self.yview_moveto(args[0])
        self._update_viewport_indicator()

    def _update_viewport_indicator(self) -> None:
        """Kodun şu anda görünen kısmını göstermek için görünüm alanı vurgulayıcısını günceller."""
        try:
            self.tag_remove(VIEWPORT_TAG, "1.0", "end")
            
            # Ana metinde görünen aralığı hesapla
            start_index = self.main_text.index("@0,0")
            height = self.main_text.winfo_height()
            end_index = self.main_text.index(f"@0,{height}")
            
            # Vurgulamayı minimap'teki karşılık gelen aralığa uygula
            self.tag_add(VIEWPORT_TAG, start_index, end_index)
            self.tag_raise(VIEWPORT_TAG)
            
        except Exception:
            pass

    def _on_click(self, event: tk.Event) -> str:
        """Tıklanan konumu merkeze alacak şekilde kaydırır."""
        self._jump_to_position(event.y, center=True)
        return "break"

    def _on_drag(self, event: tk.Event) -> str:
        """Sürükleme sırasında konumu günceller."""
        self._jump_to_position(event.y, center=True)
        return "break"

    def _on_wheel(self, event: tk.Event) -> str:
        """Tutarlı kaydırma sağlamak için fare tekerleği olaylarını ana metin düzenleyiciye iletir."""
        if hasattr(event, "delta") and event.delta:
            self.main_text.event_generate("<MouseWheel>", delta=event.delta)
        elif event.num == 4:
             self.main_text.event_generate("<Button-4>")
        elif event.num == 5:
             self.main_text.event_generate("<Button-5>")
        return "break"

    def _jump_to_position(self, y_coord: int, center: bool = True) -> None:
        """
        Verilen Y koordinatına göre ana düzenleyiciyi kaydırır.
        
        Argümanlar:
            y_coord: Tıklanan yerin Y piksel koordinatı
            center: True ise, tıklanan satırı ekranın ortasına getirmeye çalışır.
        """
        try:
            # Tıklanan Y koordinatındaki satır numarasını belirle
            index = self.index(f"@0,{y_coord}")
            target_line = int(index.split('.')[0])
            
            # Toplam satır sayısını al
            total_lines_index = self.index("end-1c")
            total_lines = int(total_lines_index.split('.')[0])
            
            if total_lines <= 0:
                return

            if center:
                # Görünür satır sayısını tahmin et
                try:
                    top_idx = self.main_text.index("@0,0")
                    bottom_idx = self.main_text.index(f"@0,{self.main_text.winfo_height()}")
                    visible_lines = float(bottom_idx) - float(top_idx)
                except ValueError:
                    visible_lines = 30.0 # Varsayılan değer

                # Hedef satırı ortaya almak için üst satırı hesapla
                top_line = target_line - (visible_lines / 2)
                if top_line < 1:
                    top_line = 1
                
                fraction = (top_line - 1) / total_lines
            else:
                fraction = (target_line - 1) / total_lines

            self.main_text.yview_moveto(fraction)
            
        except Exception:
            pass

    def configure_colors(self, bg: str, fg: str) -> None:
        """Minimap'in arka plan ve ön plan renklerini günceller."""
        self.configure(bg=bg, fg=fg)
        
        # Görünüm alanı rengini dinamik olarak ayarla (kontrast oluşturacak şekilde)
        try:
            viewport_bg = self._calculate_viewport_color(bg)
            self.tag_configure(VIEWPORT_TAG, background=viewport_bg)
            
            hover_bg = self._calculate_hover_color(bg)
            self.tag_configure(HOVER_TAG, background=hover_bg)
        except Exception:
            self.tag_configure(VIEWPORT_TAG, background="#3e3e42")
            self.tag_configure(HOVER_TAG, background="#4e4e52")

    def _calculate_viewport_color(self, bg_color: str) -> str:
        """Arka plan rengine göre uygun bir viewport rengi hesaplar."""
        try:
            # winfo_rgb kullanarak rengi ayrıştır (isimleri ve hex kodlarını destekler)
            # winfo_rgb 16-bit değerler döndürür (0-65535), 8-bite çeviriyoruz
            rgb = self.winfo_rgb(bg_color)
            r, g, b = rgb[0] // 256, rgb[1] // 256, rgb[2] // 256
            
            # Parlaklık hesapla (Luma)
            brightness = (r * 0.299 + g * 0.587 + b * 0.114)
            
            # Eğer arka plan koyu ise, viewport daha açık olmalı (ama çok parlak değil)
            # Eğer arka plan açık ise, viewport daha koyu olmalı
            
            if brightness < 128:  # Koyu Tema
                # Rengi biraz aç (%20)
                factor = 1.2
                new_r = min(255, int(r * factor + 30))
                new_g = min(255, int(g * factor + 30))
                new_b = min(255, int(b * factor + 30))
            else:  # Açık Tema
                # Rengi koyulaştır (%20)
                factor = 0.8
                new_r = max(0, int(r * factor - 30))
                new_g = max(0, int(g * factor - 30))
                new_b = max(0, int(b * factor - 30))
                
            return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
        except Exception:
            return "#3e3e42"

    def _calculate_hover_color(self, bg_color: str) -> str:
        """Arka plan rengine göre uygun bir hover (üzerine gelme) rengi hesaplar."""
        try:
            rgb = self.winfo_rgb(bg_color)
            r, g, b = rgb[0] // 256, rgb[1] // 256, rgb[2] // 256
            
            brightness = (r * 0.299 + g * 0.587 + b * 0.114)
            
            if brightness < 128:  # Koyu Tema
                # Viewport'tan daha hafif bir aydınlatma
                factor = 1.1
                new_r = min(255, int(r * factor + 15))
                new_g = min(255, int(g * factor + 15))
                new_b = min(255, int(b * factor + 15))
            else:  # Açık Tema
                # Viewport'tan daha hafif bir koyulaştırma
                factor = 0.95
                new_r = max(0, int(r * factor - 10))
                new_g = max(0, int(g * factor - 10))
                new_b = max(0, int(b * factor - 10))
                
            return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
        except Exception:
            return "#4e4e52"

    def _on_motion(self, event: tk.Event) -> None:
        """Fare hareketi sırasında altındaki satırı vurgular."""
        try:
            # Önceki vurguyu temizle
            self.tag_remove(HOVER_TAG, "1.0", "end")
            
            # Fare konumundaki satırı bul
            index = self.index(f"@0,{event.y}")
            line = index.split('.')[0]
            
            # Sadece fare altındaki satırı vurgula
            self.tag_add(HOVER_TAG, f"{line}.0", f"{line}.end+1c")
        except Exception:
            pass

    def _on_leave(self, event: tk.Event) -> None:
        """Fare minimap'ten ayrıldığında vurguyu temizler."""
        self.tag_remove(HOVER_TAG, "1.0", "end")

    def set_lexer(self, lexer: Any) -> None:
        """Sözdizimi lexer'ını ayarlar ve içeriği yeniler."""
        self.current_lexer = lexer
        self._last_content_hash = None # Zorla yenile
        self.update_content()

    def update_style(self, style_name: str) -> None:
        """Sözdizimi vurgulama stil şemasını günceller."""
        if self.highlighter:
            self.highlighter.update_style(style_name)
            self._last_content_hash = None # Zorla yenile
            self.update_content()
