# Markdown Snippet'ları (Markdown Snippets)

Bu dokümantasyon, zengin belge biçimlendirme ve özel bileşenler için editördeki tüm Markdown snippet'larını listeler.

## Başlıklar ve Metin
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `h1` - `h6` | Başlıklar | `# Başlık 1` ile `###### Başlık 6` arası |
| `bold` | Kalın metin | `**metin**` |
| `italic` | İtalik metin | `*metin*` |
| `strike` | Üstü çizili metin | `~~metin~~` |
| `ic` | Satır içi kod | `` `kod` `` |
| `code` | Kod bloğu | ` ```python \n ... \n ``` ` |
| `hr` | Yatay çizgi | `---` |

## Etkileşimli ve Özel Bölümler
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `mermaid` | Mermaid diyagramı | graph TD taslağı |
| `math` | Matematik bloğu (LaTeX) | `$$ ... $$` |
| `imath` | Satır içi matematik (LaTeX) | `$ ... $` |
| `footnote` | Markdown dipnotu | `[^1]` ve tanımı |
| `details` | Detay/Özet daraltma | `<details><summary>...</summary>...</details>` |
| `toc` | İçindekiler Tablosu | Çapa bağlantıları listesi |

## GFM Uyarıları (Admonitions)
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `note` | Bilgi notu | `> [!NOTE]` |
| `tip` | Faydalı ipucu | `> [!TIP]` |
| `important` | Kritik bilgi | `> [!IMPORTANT]` |
| `warning` | Uyarı mesajı | `> [!WARNING]` |
| `caution` | Dikkat (Olumsuz sonuçlar) | `> [!CAUTION]` |

## Listeler ve Tablolar
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `ul` | Sırasız liste | `- öğe` |
| `ol` | Sıralı liste | `1. öğe` |
| `task` | Görev listesi öğesi | `- [ ] görev` |
| `taskdone` | Tamamlanmış görev | `- [x] görev` |
| `table` | Markdown tablosu | `| Başlık | ...` |

## Meta ve Bağlantılar
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `link` | Markdown bağlantısı | `[Metin](url)` |
| `img` | Markdown resmi | `![açıklama](url)` |
| `badge` | Shields.io Rozeti | `[![açıklama](rozet_url)](baglanti_url)` |
| `kbd` | Klavye tuşu etiketi | `<kbd>tuş</kbd>` |
| `comment` | HTML Yorumu | `<!-- ... -->` |
| `anchor` | HTML Çapası (Anchor) | `<a name="..."></a>` |
| `def` | Tanım listesi | `Terim \n : Tanım` |
| `abbr` | Kısaltma | `*[Kısaltma]: Tam Açıklama` |
