# Markdown Yardımcı Araçları (Markdown Utils)

Markdown modülü altındaki `utils.py`, metin işleme ve zenginleştirme için kullanılan küçük hacimli ancak kritik fonksiyonları içerir.

## Temel Fonksiyonlar

### 1. `auto_link_urls(text)`
- **Amacı**: Düz metin halindeki URL'leri otomatik olarak tıklanabilir Markdown bağlantılarına dönüştürür.
- **Çalışma Şekli**: Metni regex ile tarar, `http/https` veya `www` ile başlayan adresleri bulur. Eğer adres zaten bir Markdown bağlantısı içindeyse (örn: `[text](url)`) onu atlar.
- **Örnek**: `www.google.com` -> `[www.google.com](http://www.google.com)`

### 2. `load_emoji_map()`
- **Amacı**: Yaygın olarak kullanılan emoji kısayollarını (shortcodes) ve bunlara karşılık gelen emoji karakterlerini içeren bir sözlük döndürür.
- **Kapsam**: `:smile:`, `:heart:`, `:rocket:`, `:bulb:` gibi popüler kodları içerir.

### 3. `replace_emoji_shortcuts(text, emoji_map)`
- **Amacı**: Metin içindeki `:kod:` formatındaki emoji kısayollarını gerçek Unicode emoji karakterleriyle değiştirir.
- **Kullanım**: `MarkdownRenderer` tarafından metin biçimlendirilmeden önce çağrılır.

## Kullanım Alanı

Bu yardımcı araçlar, render işleminin başında metni "temizlemek" ve "zenginleştirmek" (pre-process) için kullanılır. Bu sayede kullanıcının her şeyi manuel olarak Markdown formatında yazmasına gerek kalmaz (örn: linklerin otomatik tanınması).

```python
from .utils import auto_link_urls, replace_emoji_shortcuts

clean_text = auto_link_urls(raw_text)
rich_text = replace_emoji_shortcuts(clean_text, emoji_map)
```
