# Resim Görüntüleyici (Image Viewer)

Advanced Text Editor, çeşitli resim formatlarını doğrudan editör sekmelerinde görüntüleyebilen dahili bir Resim Görüntüleyici içerir. Güçlü resim işleme yetenekleri için Pillow (PIL) kütüphanesini kullanır.

## Özellikler

- **Yakınlaştırma ve Kaydırma (Zoom & Pan):** Fare imlecine odaklı yumuşak yakınlaştırma ve sezgisel kaydırma kontrolleri.
- **Döndürme (Rotation):** Görselleri sağa veya sola 90 derece döndürme imkanı.
- **Pencereye Sığdır (Fit to Window):** Görseli mevcut pencere boyutuna otomatik olarak sığdırır.
- **Şeffaflık Desteği:** Şeffaf görselleri (PNG vb.) dama tahtası deseni üzerinde görüntüler.
- **Performans:** Etkileşim sırasında "Hızlı Mod" ve boşta dururken "Yüksek Kalite" render modu ile optimize edilmiş performans.

## Desteklenen Formatlar

Görüntüleyici, yüklü olan Pillow kütüphanesinin desteklediği tüm formatları açabilir, örneğin:
- PNG
- JPEG / JPG
- GIF (Statik)
- BMP
- WEBP
- TIFF
- ICO

## Araç Çubuğu Kontrolleri

| Buton | Açıklama |
| :--- | :--- |
| **Original** (1:1) | Görünümü %100 yakınlaştırma ve 0 döndürme açısına sıfırlar. |
| **Fit** (↔) | "Pencereye Sığdır" modunu açar/kapatır. |
| **Zoom In** (+) | Yakınlaştırma seviyesini artırır. |
| **Zoom Out** (-) | Yakınlaştırma seviyesini azaltır. |
| **Rotate Left** (⟲) | Görseli saat yönünün tersine 90° döndürür. |
| **Rotate Right** (⟳) | Görseli saat yönünde 90° döndürür. |

## Klavye Kısayolları

| Eylem | Kısayol |
| :--- | :--- |
| **Yakınlaştır** | `+` veya `=` veya `Fare Tekerleği Yukarı` |
| **Uzaklaştır** | `-` veya `Fare Tekerleği Aşağı` |
| **Sağa Döndür** | `R` |
| **Sola Döndür** | `L` |
| **Pencereye Sığdır** | `F` |
| **Görünümü Sıfırla** | `0` (Sıfır) |
| **Yukarı Kaydır** | `Yukarı Ok Tuşu` |
| **Aşağı Kaydır** | `Aşağı Ok Tuşu` |
| **Sola Kaydır** | `Sol Ok Tuşu` |
| **Sağa Kaydır** | `Sağ Ok Tuşu` |

## Fare İşlemleri

- **Zoom:** Fare tekerleğini kullanarak imleç konumuna doğru yakınlaşın veya uzaklaşın.
- **Pan:** Görseli tıklayıp sürükleyerek hareket ettirin.
