# Ana Pencere (Main Window)

`MainWindow` sınıfı, uygulamanın ana penceresini ve tüm üst düzey bileşenlerin koordinasyonunu yönetir. Uygulamanın giriş noktası `main.py` olsa da, tüm görsel yapı ve mantık burada birleştirilir.

## `MainWindow` Sınıfı

`text_editor.ui.main_window.MainWindow`

`customtkinter.CTk` sınıfından türetilmiştir. Uygulamanın kök penceresidir.

### Temel Sorumluluklar

1.  **Bileşen Yönetimi:**
    *   `TabManager`: Sekmeleri ve editörleri yönetir.
    *   `FileExplorer`: Sol taraftaki dosya gezgini paneli.
    *   `StatusBar`: Alt kısımdaki durum çubuğu.
    *   `ModernMenuBar`: Üst kısımdaki özel menü çubuğu.
    *   `TerminalPanel`: Entegre terminal.
    *   `MarkdownPreview`: Markdown önizleme paneli.

2.  **Düzen (Layout):**
    *   Grid sistemi kullanarak bileşenleri yerleştirir (Menü, Explorer, Editör, Terminal, StatusBar).
    *   Panellerin (Explorer, Terminal, vb.) görünürlüğünü yönetir (`grid` ve `grid_remove` ile).

3.  **Olay Yönetimi (Event Handling):**
    *   Klavye kısayollarını dinler ve ilgili işlemleri tetikler.
    *   Zen modu gibi genel görünüm değişikliklerini yönetir.
    *   Tema değişikliklerini tüm alt bileşenlere uygular.

### Önemli Metotlar

*   `create_custom_menu()`: Özel tasarım menü çubuğunu oluşturur.
*   `apply_theme(theme_name)`: Seçilen temayı tüm uygulamaya ve alt bileşenlere uygular.
*   `toggle_zen_mode()`: Zen modunu (dikkat dağıtmayan mod) açar/kapatır.
*   `toggle_file_explorer()`, `toggle_terminal()`, `toggle_status_bar()`, `toggle_markdown_preview()`: İlgili panellerin görünürlüğünü değiştirir.
*   `show_file_menu()`, `show_edit_menu()`, `show_view_menu()`, `show_theme_menu()`: Dropdown menüleri tetikler.

### Zen Modu

Zen modu, kullanıcının sadece koda odaklanmasını sağlamak için tüm yan panelleri (dosya gezgini, terminal, menü, durum çubuğu) gizler ve editörü tam ekran yapar. `Esc` veya sağ üstteki çıkış butonu ile çıkılabilir.
