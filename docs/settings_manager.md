# ⚙️ Settings Manager

`SettingsManager`, uygulamanın tüm yapılandırma ayarlarını merkezi olarak yöneten bir Singleton sınıftır. Tema seçiminden yazı tipi boyutuna kadar tüm kullanıcı tercihleri burada saklanır.

## 🚀 Temel Özellikler

*   **Kalıcı Depolama:** Ayarları `settings.json` dosyasında saklar.
*   **Varsayılan Değerler:** Her ayar için güvenli varsayılan değerler sunar.
*   **Dışa/İçe Aktarma:** Kullanıcıların ayarlarını yedeklemesine veya başka bir cihaza taşımasına olanak tanır.
*   **Anlık Güncelleme:** Uygulama çalışırken ayarların anında değiştirilmesini sağlar.

## ⌨️ Önemli Metodlar

*   `get(key, default)`: Belirli bir ayarın değerini döndürür.
*   `set(key, value)`: Bir ayarı günceller ve diske kaydeder.
*   `reset_to_defaults()`: Tüm ayarları orijinal hallerine döndürür.
*   `export_settings(path)`: Ayarları belirtilen dosyaya yedekler.
*   `import_settings(path)`: Yedeklenmiş ayarları yükler.

## 🕒 Son Kullanılan Dosyalar

SettingsManager ayrıca "Recent Files" (Son Kullanılan Dosyalar) listesini de yönetir. `add_recent_file()` metodu ile açılan her yeni dosya listeye eklenir.
