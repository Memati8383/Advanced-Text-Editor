# Satır Numaraları (Line Numbers)

`LineNumbers` sınıfı, ana metin alanının solunda satır numaralarını ve kod katlama (folding) işaretçilerini gösteren özelleştirilmiş bir `tkinter.Text` bileşenidir.

## Temel Sorumluluklar

- **Satır Numaralandırma**: Tüm dosya için satır numaralarını otomatik olarak hesaplar ve görüntüler.
- **Katlama İşaretçileri**: Girintiye dayalı kod bloklarını algılar ve genişletme (`▼`) veya daraltma (`▶`) işaretçilerini gösterir.
- **Kaydırma Senkronizasyonu**: Ana editör bileşeni ile mükemmel dikey hizalamayı korur.
- **Katlama Etkileşimi**: Kod bloklarını daraltmak veya genişletmek için işaretçilere yapılan tıklamaları işler.

## Temel Özellikler

- **Dinamik İşaretçiler**: Bir kod bloğunun o an gizli veya görünür olmasına bağlı olarak `▼` ve `▶` işaretçileri durum değiştirir.
- **Verimli Çizim**: Büyük dosyalarda performansı artırmak için tüm numaraları tek bir işlemle toplu olarak ekler.
- **Gizli Satır Desteği**: Satır numaralarının editördeki görünümle eşleşmesini sağlamak için gizli (elided) metin aralıklarını doğru işler.

## Önemli Metotlar

- `redraw()`: Satır numaralarını yenileyen ana döngü. Katlanabilir satırları hesaplar ve uygun işaretçileri uygular.
- `on_click(event)`: Çubuğa yapılan tıklamaları üst editördeki `toggle_fold` çağrısına dönüştürür.
- `sync_scroll()`: Metin değişikliklerinden veya kaydırmadan sonra dikey görünümün editörle eşleşmesini sağlamak için `after_idle` kullanır.

## Entegrasyon

`LineNumbers` bileşeni tipik olarak bir editör içinde oluşturulur ve olay bağlamaları veya doğrudan `redraw` çağrıları ile senkronize tutulur.

```python
self.line_numbers = LineNumbers(self, self.text_area)
self.line_numbers.pack(side="left", fill="y")
```
