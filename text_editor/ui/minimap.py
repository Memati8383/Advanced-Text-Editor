import tkinter as tk
from typing import Any, Optional

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name

from text_editor.config import FONT_FAMILY
from text_editor.utils.highlighter import SyntaxHighlighter

# Yapılandırma Sabitleri
MINIMAP_WIDTH: int = 20
MINIMAP_FONT_SIZE: int = 2
VIEWPORT_TAG: str = "viewport"
MAX_HIGHLIGHT_CHARS: int = 100000  # Büyük dosyalar için vurgulamayı devre dışı bırak


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
            **kwargs
        )
        
        self.main_text = main_text
        self.highlighter: Optional[SyntaxHighlighter] = SyntaxHighlighter(self)
        self.current_lexer: Optional[Lexer] = get_lexer_by_name("text")
        
        self._update_pending = False
        self._last_content: Optional[str] = None
        
        self._configure_appearance()
        self._bind_events()

    def _configure_appearance(self) -> None:
        """Başlangıç görünümünü ve yazı tipi ayarlarını yapılandırır."""
        self.configure(font=(FONT_FAMILY, MINIMAP_FONT_SIZE))
        # Varsayılan görünüm alanı rengi - tema ile güncellenecek
        self.tag_configure(VIEWPORT_TAG, background="#3e3e42") 

    def _bind_events(self) -> None:
        """Fare etkileşimlerini ve kaydırma olaylarını bağlar."""
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<MouseWheel>", self._on_wheel)
        # Linux kaydırma düğmeleri desteği
        self.bind("<Button-4>", self._on_wheel)
        self.bind("<Button-5>", self._on_wheel)

    def update_content(self, event: Optional[tk.Event] = None) -> None:
        """
        Minimap içeriğini ana metin düzenleyici ile senkronize eder.
        Performans için debouncing (gecikmeli işlem) kullanır.
        """
        if self._update_pending:
            return
            
        self._update_pending = True
        self.after(50, self._perform_update) # 50ms debounce

    def _perform_update(self) -> None:
        """Gerçek içerik güncelleme işlemi."""
        self._update_pending = False
        try:
            # Ana düzenleyiciden geçerli içeriği al
            content = self.main_text.get("1.0", "end-1c")
            
            # OPTİMİZASYON: İçerik değişmediyse yeniden çizme
            if content == self._last_content:
                self._update_viewport_indicator()
                return
            
            self._last_content = content
            
            # Minimap içeriğini güncelle
            self.configure(state="normal")
            self.delete("1.0", "end")
            self.insert("1.0", content)
            
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
            # @0,0 görünen alanın sol üst köşesidir
            start_index = self.main_text.index("@0,0")
            
            # Pencere yüksekliğini al
            height = self.main_text.winfo_height()
            
            # Görünen alanın sonunu hesapla
            end_index = self.main_text.index(f"@0,{height}")
            
            # Vurgulamayı minimap'teki karşılık gelen aralığa uygula
            self.tag_add(VIEWPORT_TAG, start_index, end_index)
            
        except Exception:
            pass

    def _on_click(self, event: tk.Event) -> str:
        """Dosyadaki belirli bir satıra atlamak için fare tıklamasını işler."""
        self._jump_to_position(event.y)
        return "break"

    def _on_drag(self, event: tk.Event) -> str:
        """Dosyayı kaydırmak için fare sürüklemesini işler."""
        self._jump_to_position(event.y)
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

    def _jump_to_position(self, y_coord: int) -> None:
        """
        Y koordinatına göre hedef satırı hesaplar ve ana düzenleyiciyi kaydırır.
        """
        try:
            # Tıklanan Y koordinatındaki satır numarasını belirle
            index = self.index(f"@0,{y_coord}")
            line_num = int(index.split('.')[0])
            
            # Toplam satır sayısını al
            total_lines = int(self.index("end-1c").split('.')[0])
            
            if total_lines > 0:
                # Satır numarasına göre kaydırma oranını hesapla
                # Daha doğal bir kaydırma için tıklanan noktayı merkeze almak yerine
                # scrollbar mantığıyla (üst taraf) hareket ettiriyoruz.
                fraction = (line_num - 1) / total_lines
                self.main_text.yview_moveto(fraction)
        except Exception:
            pass

    def configure_colors(self, bg: str, fg: str) -> None:
        """
        Minimap'in arka plan ve ön plan renklerini günceller.
        """
        self.configure(bg=bg, fg=fg)
        
        # Görünüm alanı rengini dinamik olarak ayarla
        # Basit bir zıtlık mantığı: Koyu tema için daha açık, açık tema için daha koyu gri
        try:
            # Rengin parlaklığını kontrol etmek karmaşık olabilir, bu yüzden varsayımda bulunuyoruz
            # Genellikle hex kodları #RRGGBB formatındadır.
            if len(bg) == 7:
                r = int(bg[1:3], 16)
                g = int(bg[3:5], 16)
                b = int(bg[5:7], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                
                if brightness < 128: # Koyu tema
                    viewport_bg = "#454545" # Biraz daha açık koyu gri
                else: # Açık tema
                    viewport_bg = "#e0e0e0" # Hafif gri
            else:
                viewport_bg = "#3e3e42"
                
            self.tag_configure(VIEWPORT_TAG, background=viewport_bg)
        except Exception:
             self.tag_configure(VIEWPORT_TAG, background="#3e3e42")

    def set_lexer(self, lexer: Any) -> None:
        """Sözdizimi lexer'ını ayarlar ve içeriği yeniler."""
        self.current_lexer = lexer
        self._last_content = None # Önbelleği geçersiz kıl
        self.update_content() # Debounce devreye girer

    def update_style(self, style_name: str) -> None:
        """Sözdizimi vurgulama stil şemasını günceller."""
        if self.highlighter:
            self.highlighter.update_style(style_name)
            self._last_content = None # Önbelleği geçersiz kıl
            self.update_content()
