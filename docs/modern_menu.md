# Modern Menü Sistemi

Standart işletim sistemi menü çubuğu yerine, uygulamanın estetiğine uygun, tamamen özelleştirilebilir bir menü sistemi sunar. `ModernMenuBar` ve `ModernDropdownMenu` sınıflarından oluşur.

## `ModernMenuBar` Sınıfı

`text_editor.ui.modern_menu.ModernMenuBar`

Menü çubuğunun mantıksal yöneticisidir. Hangi dropdown menünün açık olduğunu takip eder ve etkileşimleri yönetir.

*   `show_dropdown(button, items)`: Bir butonun altında dropdown menü açar.
*   `close_active_menu()`: Açık olan menüyü kapatır.

## `ModernDropdownMenu` Sınıfı

`text_editor.ui.modern_menu.ModernDropdownMenu`

Dropdown menünün görsel bileşenidir. `CTkToplevel` olarak render edilir.

### Özellikler

*   **İkon Desteği:** Menü öğelerinin solunda ikonlar (emoji veya karakter) gösterilebilir.
*   **Kısayol Gösterimi:** Menü öğelerinin sağında klavye kısayolları (örn. `Ctrl+S`) hizalı bir şekilde gösterilebilir.
*   **Animasyon:** Açılışta hafif bir "fade-in" (belirme) animasyonu vardır.
*   **Alt Menü (Submenu):** (Geliştirme aşamasında) Alt menü ok işaretlerini destekler.
*   **Ayırıcılar:** Menü öğeleri arasında ayırıcı çizgiler eklenebilir.

### Menü Öğesi Yapısı

Menü öğeleri sözlük (dictionary) listesi olarak tanımlanır:

```python
{
    "label": "Kaydet",
    "icon": "💾",
    "shortcut": "Ctrl+S",
    "command": save_function,
    "separator": False  # veya True ise diğer alanlara gerek yok
}
```

### Görünüm

Menü, `theme` parametresi ile alınan renk şemasına (arka plan, metin rengi, vurgu rengi vb.) tam uyum sağlar.
