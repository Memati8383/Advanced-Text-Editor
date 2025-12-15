# Bağlam Menüsü (Context Menu)

`ModernContextMenu` sınıfı, uygulama genelinde kullanılan, işletim sistemi temasından bağımsız, modern ve özelleştirilebilir bir sağ tık menüsü sağlar.

## `ModernContextMenu` Sınıfı

`text_editor.ui.context_menu.ModernContextMenu`

`customtkinter.CTkToplevel` sınıfından türetilmiştir. Sistem kaynaklı menüler yerine, uygulama temasıyla uyumlu bir `Toplevel` pencere olarak render edilir.

### Özellikler

*   **Tema Desteği:** Arka plan, metin, vurgu ve kenarlık renkleri tamamen özelleştirilebilir.
*   **Odak Yönetimi:** Menü açıldığında odağı alır ve dışarı tıklandığında veya odak kaybedildiğinde otomatik olarak kapanır.
*   **Klavye Desteği:** `Escape` tuşu ile kapatılabilir.

### Kullanım

Genellikle `_on_right_click` gibi olay işleyicileri içinde oluşturulur:

```python
from text_editor.ui.context_menu import ModernContextMenu

def show_context_menu(event):
    commands = [
        ("Kopyala", copy_func),
        ("Yapıştır", paste_func),
        "-",  # Ayırıcı
        ("Sil", delete_func)
    ]
    
    ModernContextMenu(
        master=parent_widget,
        commands=commands,
        x=event.x_root,
        y=event.y_root,
        theme=current_theme_dict
    )
```

### Yapı

Menü öğeleri `commands` listesi ile verilir. Her öğe ya bir `tuple` (Etiket, Fonksiyon) ya da bir ayırıcı (`"-"`) stringidir.
