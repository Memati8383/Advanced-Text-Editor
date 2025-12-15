# Tema Yapılandırması (Theme Configuration)

Tema sistemi, uygulamanın tüm görsel bileşenlerinin renk şemalarını merkezi bir dosyadan yönetmeyi sağlar. `text_editor/theme_config.py` dosyası, önceden tanımlanmış temaları ve tema yönetim fonksiyonlarını içerir.

## Tema Yapısı

Her tema, Python sözlüğü (dict) olarak tanımlanır ve aşağıdaki anahtarları içerir:

*   **type:** Temel CustomTkinter teması ("Dark" veya "Light").
*   **bg:** Ana pencere arka plan rengi.
*   **fg:** Genel metin rengi.
*   **menu_bg / menu_fg:** Menü çubuğu renkleri.
*   **tab_bg / tab_selected / tab_hover:** Sekme renkleri.
*   **editor_bg / editor_fg:** Kod editörü renkleri.
*   **line_num_bg / line_num_fg:** Satır numaraları alanı renkleri.
*   **status_bg / status_fg:** Durum çubuğu renkleri.
*   **caret:** İmleç (kürsör) rengi.
*   **accent_color:** Vurgu rengi (seçimler, butonlar vb. için).
*   **pygments_style:** Sözdizimi vurgulama için Pygments stili (örn. "monokai").
*   **terminal_bg / terminal_fg:** Terminal paneli renkleri.

## Dahili Temalar

Aşağıdaki temalar varsayılan olarak gelir:

1.  **Dark (VS Code Dark):** Varsayılan koyu tema.
2.  **Light (VS Code Light):** Varsayılan açık tema.
3.  **Dracula:** Popüler Dracula renk paleti.
4.  **Solarized Light & Dark:** Göz yormayan Solarized paletleri.
5.  **Monokai:** Klasik Monokai renkleri.
6.  **Nord:** Soğuk, mavimsi Nord paleti.
7.  **Gruvbox:** Retro tarzı sıcak renkler.
8.  **One Dark Pro:** Atom editöründen esinlenen tema.
9.  **GitHub Dark:** GitHub'ın koyu modu.
10. **Tokyo Night, Cobalt2, Ayu Dark** ve daha fazlası.

## Tema Yönetimi

*   `get_theme(theme_name)`: Adı verilen temanın sözlüğünü döner.
*   `get_available_themes()`: Mevcut tüm temaların isim listesini döner.

Yeni bir tema eklemek için `THEMES` sözlüğüne yeni bir giriş eklemek yeterlidir.
