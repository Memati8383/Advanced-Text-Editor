# Dil Yöneticisi (Language Manager)

`LanguageManager` sınıfı, uygulamanın çoklu dil desteğini (i18n) yöneten temel bileşendir. UI metinlerinin ve mesajların seçilen dile göre dinamik olarak yüklenmesini sağlar.

## `LanguageManager` Sınıfı

`text_editor.utils.language_manager.LanguageManager`

Singleton tasarım desenini kullanır.

### Çalışma Prensibi

1.  **JSON Dosyaları:** Çeviriler `text_editor/locales/` dizini altında JSON dosyaları olarak saklanır (`tr.json`, `en.json`, vb.).
2.  **Yükleme:** `load_language(code)` metodu ile ilgili JSON dosyası belleğe yüklenir.
3.  **Erişim:** `get(key_path)` metodu ile, nokta notasyonu kullanılarak çevirilere erişilir (örn. `menu.file.save`).

### Önemli Metotlar

*   `load_language(lang_code)`: Dil koduna göre (örn. "tr", "en") veya dil adına göre (örn. "Türkçe") dili yükler.
*   `get(key_path, default)`: İstenen anahtarın karşılığını döner. Eğer anahtar bulunamazsa varsayılan değeri veya anahtarın yolunu döner.
    *   Örnek: `lang.get("menu.items.save")` -> "Kaydet"

### Desteklenen Diller

Desteklenen dillerin listesi ve dil dosyalarının yapısı hakkında bilgi için [languages.md](languages.md) dosyasına bakınız.
