# Markdown Render Aracı (Markdown Renderer)

`MarkdownRenderer`, Markdown önizleme motorunun kalbidir. Ham Markdown metnini işler ve bir `tkinter.Text` bileşenini biçimlendirilmiş metin, resimler ve etkileşimli öğelerle doldurur.

## Temel Sorumluluklar

- **Ayrıştırma (Parsing)**: Markdown satırlarını tarar ve başlıklar, listeler, tablolar ve kod blokları gibi öğeleri tanımlar.
- **Biçimlendirme**: Metin aralıklarına karmaşık tag tabanlı stiller uygular (kalın, italik, linkler vb.).
- **Etkileşimli Öğeler**: Tıklanabilir bağlantılar, kopyala butonu olan kod blokları ve görev listeleri için etkileşimli onay kutuları oluşturur.
- **Multimedya Desteği**: PIL kullanarak yerel ve uzak görselleri çeker ve görüntüler.
- **Gelişmiş Düzenler**: İç içe listeler, alıntılar ve tablolar gibi karmaşık yapıları Unicode karakterleri kullanarak çizer.

## Temel Özellikler

- **GFM Uyarıları**: `> [!NOTE]` ve `> [!WARNING]` gibi GitHub tarzı uyarıları özel ikonlar ve kenarlıklarla destekler.
- **Görev Listesi İlerlemesi**: `[x]` görev listeleri için otomatik olarak bir ilerleme çubuğu hesaplar ve görüntüler.
- **Dipnotlar ve Çapalar**: Belge genelindeki dipnotları toplar ve doküman içi navigasyon sağlayan çapaları (anchors) destekler.
- **Kod Bloğu Vurgulama**: Çeşitli diller için satır bazlı sözdizimi vurgulaması sağlamak üzere `MarkdownHighlighter` ile entegre olur.
- **Matematik ve Diyagramlar**: LaTeX matematik `$$` blokları ve Mermaid diyagramları için yer tutucular sağlar.
- **Emoji Desteği**: `:smile:` gibi kısayolları gerçek emoji karakterleriyle değiştirir.

## Önemli Metotlar

- `render(text)`: Birincil giriş noktası. Bileşeni temizler ve çok aşamalı bir ayrıştırma ve render döngüsü yürütür.
- `_insert_code_block(code, lang)`: Kopyalama butonu ve satır numaraları içeren özel bir kod alanı oluşturur.
- `_insert_table(rows)`: Sütun genişliklerini hesaplar ve görsel bir Unicode tablo çizer.
- `_insert_image(alt, url)`: Resim yükleme, boyutlandırma ve metin akışı içinde görüntüleme işlemlerini yönetir.

## Entegrasyon

Editördeki ham metni zengin bir görsel önizlemeye dönüştürmek için `MarkdownPreview` bileşeni tarafından kullanılır.

```python
self.renderer = MarkdownRenderer(self.preview_text, self.styler)
self.renderer.render(current_markdown_text)
```
