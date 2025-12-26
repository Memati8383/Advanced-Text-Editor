# Markdown Stil Yöneticisi (Markdown Styler)

`MarkdownStyler` sınıfı, Markdown önizlemesinin görsel temasını ve tipografisini yönetir. Uygulamanın genel teması ile Markdown önizlemesi için gereken özel `tkinter.Text` tag yapılandırmaları arasında köprü görevi görür.

## Temel Sorumluluklar

- **Tema Eşleştirme**: Ham tema renklerini (örneğin `accent_color`) belirli Markdown rollerine (örneğin `h1` veya `link`) dönüştürür.
- **Tag Yapılandırması**: Başlıklar, listeler, kodlar ve daha fazlası için onlarca `tkinter` tag'ini programlı olarak ayarlar.
- **Duyarlı Boyutlandırma**: Tüm öğelerin yazı tipi boyutlarını temel bir boyuta ve dinamik bir yakınlaştırma seviyesine göre hesaplar.
- **GFM Estetiği**: GitHub tarzı uyarılar (Note, Tip, Warning vb.) için renk paletlerini tanımlar.

## Temel Özellikler

- **Koyu/Açık Mod Desteği**: Mevcut temanın açık veya koyu olmasına bağlı olarak renk yoğunluklarını otomatik olarak ayarlar.
- **Zoom Desteği**: Kullanıcı önizlemeyi yakınlaştırdığında veya uzaklaştırdığında tüm yazı tiplerini ve boşlukları yeniden hesaplar.
- **Tematik Tutarlılık**: Önizleme ortamının (arka plan, sözdizimi vurgulama) editörün geri kalanıyla eşleşmesini sağlar.
- **Gelişmiş Tipografi**: Okunabilirliği artırmak için farklı yazı tipi ağırlıkları ve aileleri (düz metin için Sans-serif, kod için Monospace) kullanır.

## Renk Atama Kategorileri

1. **Hiyerarşi**: `h1`'den `h6`'ya kadar farklı renk ve boyutlar.
2. **Uyarılar**: Not, İpucu, Uyarı, Önemli ve Dikkat blokları için arka planlar ve kenarlıklar.
3. **Bileşenler**: Kod bloğu başlıkları, tablo kenarlıkları ve liste işaretçileri için renkler.
4. **Sözdizimi**: Kod blokları içindeki dil anahtar kelimeleri, dizeler ve yorumlar için özel renkler.

## Önemli Metotlar

- `setup_tags(base_font_size, zoom_level)`: Stil ayarlarını metin bileşenine uygulayan ana yapılandırma döngüsü.
- `update_theme(theme)`: Dahili renk haritasını yeniler ve kesintisiz tema geçişi sağlar.

## Entegrasyon

`MarkdownStyler`, görsel tutarlılığı sağlamak için hem `MarkdownRenderer` (canlı önizleme için) hem de `MarkdownExporter` (HTML dışa aktarma için) tarafından kullanılır.

```python
self.styler = MarkdownStyler(self.text_widget, current_theme)
self.styler.setup_tags(12, 110) # %110 yakınlaştırma
```
