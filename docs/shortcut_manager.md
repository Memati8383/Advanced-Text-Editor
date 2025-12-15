# Kısayol Yöneticisi (Shortcut Manager)

`ShortcutManager` sınıfı, uygulamanın klavye kısayollarını merkezi bir yerden yönetmeyi sağlar. Kısayolların tanımlanması, kaydedilmesi, yüklenmesi ve kullanıcı dostu metinlere dönüştürülmesi işlemlerinden sorumludur.

## `ShortcutManager` Sınıfı

`text_editor.utils.shortcut_manager.ShortcutManager`

Singleton tasarım desenini kullanır.

### Özellikler

*   **Varsayılan Kısayollar:** `DEFAULT_SHORTCUTS` sözlüğünde tanımlı zengin bir varsayılan kısayol setine sahiptir.
*   **Kalıcılık:** Kısayollar `~/.memati_editor/keybindings.json` dosyasında saklanır. Kullanıcı özelleştirmeleri yeniden başlatmalarda korunur.
*   **Aksiyon ID'leri:** Kısayollar, tuş kombinasyonları yerine (örn. `<Control-s>`) aksiyon ID'leri (örn. `save_file`) ile eşleştirilir. Bu sayede kod içinde tuş kombinasyonu hardcode edilmez.
*   **UI Metadata:** Ayarlar penceresi gibi arayüzler için her kısayolun kategorisini ve etiketini (`SHORTCUT_METADATA`) tutar.

### Önemli Metotlar

*   `get(action_id)`: Belirtilen aksiyon için Tkinter formatında tuş kombinasyonunu döner (örn. `<Control-s>`).
*   `set(action_id, sequence)`: Bir aksiyonun kısayolunu değiştirir ve diske kaydeder.
*   `get_display_string(sequence)`: Tkinter formatındaki kısayolu (örn. `<Control-n>`) okunabilir formata (örn. `Ctrl+N`) çevirir. Menülerde göstermek için idealdir.
*   `reset_to_defaults()`: Tüm kısayolları fabrika ayarlarına döndürür.

### Kullanıcı Tarafı

Kullanıcılar için kısayol listesi [SHORTCUTS.md](SHORTCUTS.md) dosyasında bulunmaktadır.
