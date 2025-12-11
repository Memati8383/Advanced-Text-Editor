# Dil Desteği (Language Support)

Advanced Text Editor, çeşitli programlama dilleri için sözdizimi vurgulama (syntax highlighting) ve otomatik tamamlama özelliklerini sağlamak amacıyla veri odaklı bir yapı kullanır.

## Yapılandırma

Dil tanımları `text_editor/data/languages.json` dosyasında saklanır. Bu JSON dosyası, çekirdek koda dokunmadan yeni diller eklemeyi veya mevcut dilleri düzenlemeyi kolaylaştırır.

## JSON Yapısı

JSON dosyasındaki her dil girişi şu yapıyı takip eder:

```json
"LanguageName": {
    "keywords": ["ayrılmış", "kelimeler", "listesi"],
    "types": ["yerleşik", "tipler", "listesi"],
    "functions": ["yaygın", "fonksiyonlar"],
    "string_char": "\"",           // veya "'"
    "comment": "//",               // Tek satırlık yorum işareti
    "multiline_comment": ["/*", "*/"] // Opsiyonel: Çok satırlı yorum başlangıç ve bitişi
}
```

### Alanlar

- **keywords:** Kontrol akışı, tanımlamalar vb. için kullanılan ayrılmış kelimeler. (Anahtar Kelime rengi ile vurgulanır).
- **types:** Yerleşik veri tipleri veya sınıflar (Tip rengi ile vurgulanır).
- **functions:** Yerleşik veya yaygın kütüphane fonksiyonları (Fonksiyon rengi ile vurgulanır).
- **string_char:** Metin dizilerini (string) belirtmek için kullanılan karakter.
- **comment:** Tek satırlık yorumu başlatan karakter dizisi.
- **multiline_comment:** Blok yorumlar için başlangıç ve bitiş işaretlerini içeren iki elemanlı liste.

## Yeni Bir Dil Ekleme

Yeni bir dil desteği eklemek için:

1. `text_editor/data/languages.json` dosyasını açın.
2. Dilin adıyla yeni bir anahtar (key) ekleyin (örn. "Rust").
3. O dile özgü `keywords` (anahtar kelimeler), `types` (tipler) ve `functions` (fonksiyonlar) listelerini doldurun.
4. Yorum ve string sözdizimini tanımlayın.
5. Dosyayı kaydedin.
6. Uygulamayı yeniden başlatın.

Değişiklikler `SyntaxHighlighter` ve `AutoCompleter` tarafından otomatik olarak algılanacak, yeni dil için vurgulama ve öneriler aktif hale gelecektir.
