# Markdown Dışa Aktarıcı (Markdown Exporter)

`MarkdownExporter` sınıfı, Markdown içeriğinin HTML gibi harici formatlara dönüştürülmesini sağlar ve sistem tarayıcısı ile yazdırma servisleriyle entegrasyon sunar.

## Temel Sorumluluklar

- **HTML Oluşturma**: Ham Markdown metnini, gömülü CSS içeren tam teşekküllü bir HTML5 belgesine dönüştürür.
- **Tarayıcı Entegrasyonu**: Kullanıcıların Markdown dosyalarını varsayılan web tarayıcılarında önizlemelerine olanak tanır.
- **Yazdırma Önizlemesi**: Belgenin baskıya uygun bir sürümünü oluşturur ve sistem yazdırma iletişim kutusunu açar.
- **Dosya Sistemi Etkileşimi**: Oluşturulan HTML dosyalarının yerel diske kaydedilmesini yönetir.

## Temel Özellikler

- **Tematik Tutarlılık**: Dışa aktarılan HTML, `MarkdownStyler` aracılığıyla uygulamanın mevcut temasından türetilen renkleri ve stilleri kullanır.
- **Duyarlı Tasarım**: Oluşturulan HTML, farklı ekran boyutlarına uyum sağlayan ortalanmış ve okunabilir bir düzen için CSS içerir.
- **Sözdizimi Vurgulama**: Dışa aktarılan HTML içindeki kod blokları, okunabilirliği korumak için stillendirilir.
- **Baskı Dostu CSS**: Yazdırma butonları gibi arayüz öğelerini gizlemek ve kenar boşluklarını kağıt için optimize etmek üzere otomatik olarak `@media print` kuralları enjekte eder.

## Önemli Metotlar

- `export_as_html(parent_window)`: "Farklı Kaydet" penceresini tetikler ve render edilmiş HTML'i dosyaya yazar.
- `print_preview()`: Geçici bir HTML dosyası oluşturur ve otomatik tetiklenen bir yazdırma komutuyla tarayıcıda açar.
- `open_in_browser()`: Mevcut içeriği hızlıca geçici bir dosyaya render eder ve sistem tarayıcısında başlatır.
- `convert_to_html(text)`: Markdown sözdizimini standart HTML etiketlerine dönüştürmek için kullanılan regex tabanlı dahili dönüştürücü.

## Kullanım

Genellikle bir Markdown önizleme bileşeni içinde oluşturulur ve "Dışa Aktar" veya "Yazdır" butonlarına bağlanır.

```python
self.exporter = MarkdownExporter(self.editor, self.styler)
self.exporter.export_as_html()
```
