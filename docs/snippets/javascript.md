# Javascript Snippet'ları (Javascript Snippets)

Bu dokümantasyon, modern ESM ve React spesifik şablonlar dahil olmak üzere editördeki tüm Javascript snippet'larını listeler.

## Temel Sözdizimi
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `clg` | Konsola yazdırma (Console log) | `console.log(obj);` |
| `func` | Fonksiyon tanımı | `function name(params) { ... }` |
| `afunc` | Asenkron Fonksiyon | `async function name(params) { ... }` |
| `arrow` | Ok fonksiyonu (Arrow function) | `const name = () => { ... };` |

## Döngüler ve Diziler
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `for` | Standart for döngüsü | `for (let i = 0; i < array.length; i++) { ... }` |
| `foreach` | Array.forEach | `array.forEach(item => { ... });` |
| `map` | Array.map | `const newArr = array.map(item => { ... });` |

## ESM Modülleri
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `import` | ESM İçe Aktarma (Import) | `import { name } from 'module';` |
| `export` | ESM Dışa Aktarma (Export) | `export const name = value;` |

## Ağ ve Tarayıcı
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `fetch` | Asenkron Veri Çekme (Fetch) | `const response = await fetch(url);` |

## React
| Önek (Prefix) | Açıklama | Örnek İçerik |
| :--- | :--- | :--- |
| `react_comp` | React Bileşeni (Component) | Fonksiyonel bileşen şablonu |
| `usestate` | React useState | `const [val, setVal] = useState(...);` |
| `useeffect` | React useEffect | `useEffect(() => { ... }, []);` |
