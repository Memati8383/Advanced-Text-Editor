# ⚙️ Settings Module

Bu dizin, uygulamanın ayarlar penceresini oluşturan panel bileşenlerini içerir. Ayarlar sistemi, `SettingsManager` ile entegre çalışır ve kullanıcı tercihlerini kalıcı olarak saklar.

## 📂 Dosya Yapısı

*   **`base_panel.py`**: Tüm ayar panelleri için temel sınıf (`SettingsPanel`). Ortak UI öğelerini ve düzeni sağlar.
*   **`general_panel.py`**: Dil seçimi, otomatik kayıt ve temel uygulama ayarları.
*   **`appearance_panel.py`**: (Gelecekte) Görünüm ile ilgili spesifik ayarlar.
*   **`editor_panel.py`**: Font boyutu, font ailesi, satır numaraları, word wrap gibi editör spesifik ayarlar.
*   **`theme_panel.py`**: Tema seçimi ve tema önizleme alanı.
*   **`shortcuts_panel.py`**: Klavye kısayollarını görüntüleme ve (gelecekte) düzenleme paneli.
*   **`terminal_panel.py`**: Terminal kabuk (shell) seçimi ve terminal ayarları.
*   **`view_panel.py`**: Arayüz bileşenlerinin (Minimap, Status Bar vb.) görünürlük ayarları.
*   **`advanced_panel.py`**: Veri yönetimi (Ayarları dışa aktar/içe aktar) ve deneysel özellikler.

## 🛠️ Panel Ekleme Rehberi

Yeni bir ayar kategorisi eklemek için:

1.  `base_panel.py` içindeki `SettingsPanel` sınıfından türeyen yeni bir sınıf oluşturun.
2.  `_setup_ui` metodunu override ederek ayar kontrollerini (switch, combobox vb.) ekleyin.
3.  `SettingsManager` üzerinden değerleri okuyun ve güncelleyin.
4.  `settings_dialog.py` içindeki `_create_panels` metoduna yeni panelinizi kaydedin.

## 🎨 Tasarım Prensipleri

*   Her panel temiz ve düzenli bir dikey yerleşime (`pack`) sahip olmalıdır.
*   Ayar grupları için `CTkLabel` ile başlıklar kullanılmalıdır.
*   Değişiklikler anında (`command` callbackleri ile) uygulanmalı veya `SettingsManager`'a kaydedilmelidir.
