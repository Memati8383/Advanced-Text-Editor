# Python Snippet'ları (Python Snippets)

Bu dokümantasyon, editördeki mevcut tüm Python snippet'larını listeler ve bunların nasıl tetikleneceğini açıklar.

## Genel Yapı
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `main` | main() fonksiyonu ile ana blok | `if __name__ == "__main__": ...` |
| `def` | Tip ipuçları içeren fonksiyon | `def name(params) -> None: ...` |
| `adef` | Asenkron fonksiyon | `async def name(params) -> None: ...` |
| `class` | Tip ipuçları içeren sınıf | `class Name: ...` |
| `super` | Üst sınıf (super) init çağrısı | `super().__init__(...)` |
| `lambda` | Lambda fonksiyonu | `lambda x: x * 2` |

## Gelişmiş Yapılar
| Önek (Prefix) | Açıklama | Kullanım |
| :--- | :--- | :--- |
| `decorator` | Fonksiyon dekoratörü | Özel dekoratörler için şablon |
| `contextmanager` | Bağlam yöneticisi (Context manager) | Yield ile kurulum/kapanış mantığı |
| `property` | Getter ve Setter | `@property` ve `@setter` şablonu |
| `dataclass` | Dataclass snippet'ı | `@dataclass` tanımı |
| `pydantic` | Pydantic modeli | `BaseModel` kalıtımı |
| `enum` | Enum sınıfı | `Enum` tanımı |

## Kontrol Akışı
| Önek (Prefix) | Açıklama |
| :--- | :--- |
| `if` | Standart if ifadesi |
| `ife` | if-else ifadesi |
| `for` | for döngüsü |
| `while` | while döngüsü |
| `match` | Match ifadesi (Python 3.10+) |
| `try` | try-except bloğu |
| `trye` | Tam try-except-else-finally bloğu |

## Kütüphaneler ve Araçlar
| Önek (Prefix) | Açıklama |
| :--- | :--- |
| `fastapi` | Temel FastAPI uygulama şablonu |
| `flask` | Temel Flask uygulama şablonu |
| `tkapp` | Minimal Tkinter Uygulama sınıfı |
| `pytest` | Pytest test şablonu |
| `argparse` | Argüman ayrıştırıcı (argparse) şablonu |
| `logging` | Standart logging yapılandırması |

## Veri ve Girdi/Çıktı (IO)
| Önek (Prefix) | Açıklama |
| :--- | :--- |
| `json_read` | JSON dosyasını okuma ve yükleme |
| `json_write` | JSON dosyasına yazma ve kaydetme |
| `lc` | Liste kapsamı (List comprehension) |
| `dc` | Sözlük kapsamı (Dict comprehension) |
| `timeit` | Çalışma süresini ölçme |
