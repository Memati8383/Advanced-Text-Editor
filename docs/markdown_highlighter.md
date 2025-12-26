# Markdown Sözdizimi Vurgulayıcı (Markdown Highlighter)

`MarkdownHighlighter` sınıfı, Markdown önizleme penceresindeki kod blokları için temel sözdizimi renklendirmesi sağlar. Bağımsız bir bileşen olarak, kod bloklarının içindeki metni analiz eder ve dillere özgü renkleri uygular.

## Temel Sorumluluklar

- **Dil Algılama**: Kod bloklarının başında belirtilen dilleri (py, js, html, vb.) tanır.
- **Sözdizimi Analizi**: Satır bazında analiz yaparak anahtar kelimeleri, dizeleri (strings), sayıları, yorumları ve fonksiyonları ayırt eder.
- **Renk Uygulama**: `MarkdownStyler` tarafından tanımlanan renkleri kullanarak metin bileşenine stil tag'leri ekler.

## Desteklenen Diller

- **Python**: `def`, `class`, `import` gibi anahtar kelimeler ve `#` yorumları.
- **JavaScript**: `function`, `const`, `async/await` gibi anahtar kelimeler ve `//` veya `/* */` yorumları.
- **Java/C/C++**: Tipik C tarzı sözdizimi ve veri tipleri.
- **HTML/CSS**: Etiket isimleri ve stil özellikleri.
- **SQL**: Temel veri sorgulama ve tanımlama komutları.

## Önemli Metotlar

- `highlight_line(line, lang)`: Verilen bir satırı belirli bir dilin kurallarına göre analiz eder ve parçalara ayırarak renklendirilmiş olarak metin bileşenine yerleştirir.

## Entegrasyon

`MarkdownRenderer` tarafından kod blokları oluşturulurken her satır için çağrılır.

```python
self.highlighter = MarkdownHighlighter(text_widget, styler)
# Bir kod bloğu işlenirken:
self.highlighter.highlight_line(line + "\n", lang)
```
