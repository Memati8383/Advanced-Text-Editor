# Menü Çubuğu (Menu Bar)

`MenuBar` bileşeni, uygulama için modern ve etkileşimli bir üst navigasyon çubuğu sağlar. Özel butonlar kullanır ve şık dropdown menüleri göstermek için `ModernMenuBar` ile entegre çalışır.

## Temel Sorumluluklar

- **Açılır Menüler**: Dosya, Düzen, Görünüm, Tema ve Yardım ana kategorilerini yönetir.
- **Dinamik İçerik**: "Son Kullanılan Dosyalar" veya "Mevcut Temalar" gibi dinamik öğeleri menülere doldurur.
- **Kısayol Entegrasyonu**: `ShortcutManager`'dan gelen klavye kısayollarını menü etiketlerinin yanında görüntüler.
- **Yerelleştirme**: Tüm etiketler `LanguageManager` kullanılarak otomatik olarak yerelleştirilir.
- **Erişim**: Dahili eğitim moduna ve ayarlar penceresine doğrudan erişim sağlar.

## Temel Özellikler

- **Modern Estetik**: Özel stiller, emojiler ve pürüzsüz hover efektleri kullanır.
- **Son Dosyalar**: Son açılan dosyaların listesini ve bu listeyi temizleme imkanı sunar.
- **Tema Seçimi**: Tüm mevcut temaları benzersiz simgelerle listeler.
- **Görünüm Kontrolleri**: Minimap, Satır Numaraları ve Terminal gibi arayüz öğelerini açıp kapatmak için onay kutuları sağlar.
- **Versiyon Bilgisi**: Uygulamanın güncel sürüm numarasını gösterir.

## Menü Kategorileri

1. **Dosya Menüsü**: Yeni Sekme, Dosya/Klasör Aç, Son Dosyalar, Kaydet/Farklı Kaydet, Bul/Değiştir ve Çıkış.
2. **Düzen Menüsü**: Geri Al, Yinele, Kes, Kopyala, Yapıştır, Satırı Çoğalt, Satırı Yukarı/Aşağı Kaydır vb.
3. **Görünüm Menüsü**: Satır Numaraları, Sözcük Kaydırma, Minimap, Durum Çubuğı, Dosya Gezgini, Terminal, Markdown Önizleme ve Zen Modu.
4. **Tema Menüsü**: Tüm mevcut renk temalarının listesi.
5. **Yardım Menüsü**: Yardım Sistemi'ne doğrudan bağlantı.

## Önemli Metotlar

- `_setup_ui()`: Logoyu ve ana kategori butonlarını başlatır.
- `apply_theme(theme)`: Menü çubuğu renklerini ve sınırlarını seçilen temayla eşleşecek şekilde günceller.
- `show_file_menu()`, `show_edit_menu()` vb.: Belirli dropdown menülerin yapısını tanımlayan ve gösterilmesini tetikleyen fonksiyonlar.

## Entegrasyon

`MenuBar`, `MainWindow`'un en üstüne yerleştirilir ve uygulama çapındaki komutlar için merkezi bir durak görevi görür.

```python
self.menu_bar = MenuBar(self)
self.menu_bar.pack(side="top", fill="x")
```
