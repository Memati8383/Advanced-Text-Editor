# Dosya İkonları (File Icons)

`FileIcons` sınıfı, dosya gezgini, sekme başlıkları ve diğer UI alanlarında dosya türlerini görselleştirmek için kullanılır. SVG veya PNG görselleri yerine, platformlar arası uyumlu ve hafif olan emoji/karakter tabanlı ikonları kullanır.

## `FileIcons` Sınıfı

`text_editor.utils.file_icons.FileIcons`

Tamamen statik metodlardan oluşan bir yardımcı sınıftır.

### Özellikler

*   **Geniş Uzantı Desteği:** Programlama dillerinden (`.py`, `.js`, `.rs`) resim dosyalarına, arşivlerden veritabanı dosyalarına kadar yüzlerce uzantıyı tanır.
*   **Tam İsim Eşleşmesi:** Sadece uzantıya değil, özel dosya isimlerine de bakar (örn. `Dockerfile`, `package.json`, `Makefile`, `.gitignore`).
*   **Renk Kodları:** Her dosya türü için o dile/formata özgü bir marka rengi (hex kodu) tanımlıdır (örn. Python için mavi `#3776ab`, JS için sarı `#f7df1e`).

### Metotlar

*   `get_icon(filename)`: Dosya adı için uygun emoji ikonunu döner (örn. "🐍").
*   `get_color(filename)`: Dosya türüyle ilişkili rengi döner.
*   `get_type(filename)`: Dosya türünün insan tarafından okunabilir adını döner (örn. "Python Script").
*   `get_info(filename)`: Yukarıdaki tüm bilgileri bir sözlük olarak döner.

### Yardımcı Metotlar

Ayrıca dosya türü tespiti için helper metotlar içerir:
*   `is_image(filename)`
*   `is_video(filename)`
*   `is_audio(filename)`
*   `is_archive(filename)`
