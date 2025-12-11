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
            **kwargs
        )
        
        self.main_text = main_text
        self.highlighter: Optional[SyntaxHighlighter] = SyntaxHighlighter(self)
        self.current_lexer: Optional[Lexer] = get_lexer_by_name("text")
        
        self._configure_appearance()
        self._bind_events()

    def _configure_appearance(self) -> None:
        """Başlangıç görünümünü ve yazı tipi ayarlarını yapılandırır."""
        self.configure(font=(FONT_FAMILY, MINIMAP_FONT_SIZE))
        # Varsayılan görünüm alanı rengi - ince bir vurgu.
        # İdeal olarak, bu rengin configure_colors tarafından temaya uyacak şekilde güncellenmesi gerekir.
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
        Ana düzenleyiciden metni alır ve sözdizimi vurgulamasını yeniden uygular.
        """
        # Ana düzenleyiciden geçerli içeriği al
        content = self.main_text.get("1.0", "end")
        
        # Minimap içeriğini güncelle
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", content)
        self.configure(state="disabled")
        
        self._highlight_content(content)
        self._update_viewport_indicator()

    def _highlight_content(self, content: str) -> None:
        """
        Minimap içeriğine sözdizimi vurgulaması uygular.
        
        Argümanlar:
            content: Vurgulanacak metin içeriği.
        """
        if self.highlighter and self.current_lexer:
            try:
                self.highlighter.highlight(content, self.current_lexer)
            except Exception:
                # Kullanıcı arayüzü bozulmasını önlemek için hataları bastır
                pass

    def on_scroll(self, *args: Any) -> None:
        """
        Ana metin düzenleyici kaydırıldığında çağrılan geri çağırma işlevi.
        Minimap'in dikey görünümünü senkronize eder ve görünüm alanı göstergesini günceller.
        
        Argümanlar:
            *args: Kaydırma komutu tarafından iletilen kaydırma argümanları.
        """
        self.yview_moveto(args[0])
        self._update_viewport_indicator()

    def _update_viewport_indicator(self) -> None:
        """
        Kodun şu anda görünen kısmını göstermek için görünüm alanı vurgulayıcısını günceller.
        """
        try:
            # Önceki vurgulamayı kaldır
            self.tag_remove(VIEWPORT_TAG, "1.0", "end")
            
            # Ana metinde görünen aralığı hesapla
            # @0,0 görünen sol üst karakterdir
            start_index = self.main_text.index("@0,0")
            
            # Görünen alt karakter. Pencere yüksekliği kullanılır.
            height = self.main_text.winfo_height()
            end_index = self.main_text.index(f"@0,{height}")
            
            # Vurgulamayı minimap'teki karşılık gelen aralığa uygula
            # Not: start_index ve end_index, her iki pencere öğesiyle de uyumlu "line.char" biçimindedir
            # (satır numaralarının eşleştiği varsayılarak).
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
        
        Argümanlar:
            y_coord: Pencere öğesi aracılığıyla tıklama/sürükleme olayının Y koordinatı.
        """
        try:
            # Tıklanan Y koordinatındaki satır numarasını belirle
            index = self.index(f"@0,{y_coord}")
            line_num = int(index.split('.')[0])
            
            # Satır numarasına göre kaydırma oranını hesapla
            total_lines = int(self.index("end-1c").split('.')[0])
            if total_lines > 0:
                fraction = (line_num - 1) / total_lines
                self.main_text.yview_moveto(fraction)
        except Exception:
            pass

    def configure_colors(self, bg: str, fg: str) -> None:
        """
        Minimap'in arka plan ve ön plan renklerini günceller.
        
        Argümanlar:
            bg: Arka plan renk onaltılık (hex) dizesi.
            fg: Ön plan renk onaltılık (hex) dizesi.
        """
        self.configure(bg=bg, fg=fg)
        
        # Uygun bir görünüm alanı rengi hesaplayın (arka plandan biraz daha açık/farklı)
        # Basitlik sağlamak adına, biraz zıtlık oluşturan bir renk seçerek yarı saydam görünümlü bir efekt oluşturuyoruz.
        # Gerçek saydamlığı kolayca yapamadığımızdan, sadece sabit kodlanmış uyumlu bir renk ayarlayabilir veya varsayılanı bırakabiliriz.
        # Akıllıca bir yol, arka plan parlaklığını kontrol etmek ve daha açık veya daha koyu seçmektir.
        # Şimdilik, burada açıkça belirtilmedikçe _configure_appearance içinde ayarlanan varsayılana güveneceğiz.
        # Tam olarak entegre etmek için belirli bir 'seçim' veya 'vurgu' rengine ihtiyacımız olabilir.

    def set_lexer(self, lexer: Any) -> None:
        """
        Sözdizimi lexer'ını ayarlar ve içeriği yeniler.
        
        Argümanlar:
            lexer: Pygments lexer örneği.
        """
        self.current_lexer = lexer
        self.update_content()

    def update_style(self, style_name: str) -> None:
        """
        Sözdizimi vurgulama stil şemasını günceller.
        
        Argümanlar:
            style_name: Pygments stilinin adı.
        """
        if self.highlighter:
            self.highlighter.update_style(style_name)
            self.update_content()
