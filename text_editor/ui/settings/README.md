# ⚙️ Settings Module

Bu dizin, uygulamanın ayarlar penceresini oluşturan panel bileşenlerini içerir. Ayarlar sistemi, `SettingsManager` ile entegre çalışır ve kullanıcı tercihlerini kalıcı olarak saklar.

## 📂 Dosya Yapısı

- **`base_panel.py`**: Tüm ayar panelleri için temel sınıf (`BaseSettingsPanel`). Ortak UI öğelerini, widget metodlarını ve layout yardımcılarını sağlar.
- **`general_panel.py`**: Dil seçimi, font ayarları ve temel uygulama ayarları.
- **`editor_panel.py`**: Font boyutu, satır numaraları, word wrap, kod katlama gibi editör spesifik ayarlar.
- **`view_panel.py`**: Arayüz bileşenlerinin (Panel görünürlüğü, Animasyonlar, Tab bar) görünürlük ayarları.
- **`theme_panel.py`**: Tema seçimi ve tema önizleme alanı.
- **`shortcuts_panel.py`**: Klavye kısayollarını görüntüleme, arama ve düzenleme paneli.
- **`terminal_panel.py`**: Terminal kabuk (shell) seçimi, cursor ve terminal ayarları.
- **`advanced_panel.py`**: Veri yönetimi (Ayarları dışa aktar/içe aktar), performans ve hata ayıklama.

## 🧩 BaseSettingsPanel Widget Metodları

Panel geliştirirken kullanılabilecek hazır widget metodları:

### Temel Widgetlar

- `add_switch(key, on_change)` - Boolean ayar için switch
- `add_combo(key, values, width, is_int, on_change)` - Seçenek listesi
- `add_slider(key, from_, to, steps, show_value, unit, on_change)` - Sayısal değer
- `add_entry(key, placeholder, width, readonly, validation, on_change)` - Metin girişi
- `add_number_stepper(key, min_val, max_val, step, width)` - +/- artırma kontrolü

### Gelişmiş Widgetlar

- `add_segmented_control(key, values, on_change)` - Segmented button
- `add_color_picker(key, on_change)` - Renk seçici
- `add_radio_group(key, options, orientation, on_change)` - Radio button grubu
- `add_file_picker(key, file_types, mode, on_change)` - Dosya/klasör seçici
- `add_text_area(key, height, placeholder, on_change)` - Çok satırlı metin
- `add_accordion_section(title, description, expanded, icon)` - Açılır/kapanır bölüm
- `add_chips(key, options, multi_select, on_change)` - Chip/etiket seçici
- `add_key_value_editor(key, on_change)` - Anahtar-değer düzenleyici

### Bilgi ve Görsel Widgetlar

- `add_info_card(icon, title, description, card_type)` - Bilgi kartı
- `add_button_row(buttons)` - Buton satırı
- `add_badge(text, badge_type)` - Rozet etiketi
- `_add_section_header(title, description, icon)` - Bölüm başlığı

### Yardımcı Metodlar

- `_create_row_frame(label_text, description, tooltip)` - Ayar satırı çerçevesi
- `_add_tooltip(widget, text, delay_ms, position)` - Gelişmiş tooltip
- `_validate_input(value, rule)` - Input doğrulama
- `get_widget(key)` - Cache'lenmiş widget'ı getir

## 🛠️ Panel Ekleme Rehberi

Yeni bir ayar kategorisi eklemek için:

1.  `base_panel.py` içindeki `BaseSettingsPanel` sınıfından türeyen yeni bir sınıf oluşturun.
2.  `_setup_content` metodunu override ederek ayar kontrollerini ekleyin.
3.  Hazır widget metodlarını kullanarak hızlıca UI oluşturun.
4.  `settings_dialog.py` içindeki kategori mapping'ine yeni panelinizi ekleyin.

### Örnek Panel

```python
from text_editor.ui.settings.base_panel import BaseSettingsPanel

class MySettingsPanel(BaseSettingsPanel):
    def _setup_content(self) -> None:
        # Bölüm başlığı
        self._add_section_header("🔧 Ayarlarım", "Özel ayarlar")

        # Switch ekle
        self.add_switch("my_toggle")

        # Slider ekle
        self.add_slider("my_value", 0, 100, unit="%")

        # Bilgi kartı
        self.add_info_card("💡", "İpucu", "Yararlı bilgi")
```

## 🎨 Tasarım Prensipleri

- Her panel temiz ve düzenli bir dikey yerleşime sahip olmalıdır.
- Ayar grupları `_add_section_header` ile başlatılmalıdır.
- Hazır widget metodları kullanarak tutarlılık sağlanmalıdır.
- Değişiklikler anında `update_setting` ile kaydedilmelidir.
- Validation kullanarak kullanıcı girdileri doğrulanmalıdır.

## 🆕 v2.0 Güncellemeler

- ✅ Gelişmiş tooltip sistemi (delay, pozisyon, fade-in animasyonu)
- ✅ Radio button grubu desteği
- ✅ Dosya/klasör seçici widget
- ✅ Çok satırlı text area
- ✅ Accordion (açılır/kapanır) bölümler
- ✅ Chip/etiket seçici
- ✅ Anahtar-değer düzenleyici
- ✅ Badge/rozet etiketi
- ✅ Kısayol arama özelliği
- ✅ Kısayol çakışma kontrolü
- ✅ Tek tek kısayol temizleme butonu
