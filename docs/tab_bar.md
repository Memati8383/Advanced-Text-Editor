# Sekme Çubuğu (Tab Bar)

`TabBar` bileşeni, doküman sekmeleri için modern ve kaydırılabilir bir taşıyıcıdır. Açık olan dosyaları temsil eden sekmelerin görsel sunumunu ve düzenini yönetir.

## Temel Sorumluluklar

- **Sekme Butonu Yönetimi**: Her açık dosyayı temsil eden butonların oluşturulması, kaldırılması ve güncellenmesi.
- **Kaydırılabilir Taşıyıcı**: Çok sayıda sekme açıldığında yatayda gezinmeyi sağlamak için `CTkScrollableFrame` kullanır.
- **Görsel Geri Bildirim**: Aktif olan sekmeyi vurgular.
- **Tema Desteği**: Renkleri ve kenarlıkları uygulamanın genel temasına göre dinamik olarak günceller.

## Temel Özellikler

- **Yatay Kaydırma**: Çok sayıda dosyanın açık olduğu projeleri sorunsuzca yönetir.
- **Aktif Durum Vurgusu**: Mevcut sekme, kenarlık ve benzersiz bir arka plan rengiyle görsel olarak ayırt edilir.
- **Temiz API**: Sekme ekleme, kaldırma ve etkinleştirme için basit metotlar sunar.

## Önemli Metotlar

- `add_tab_button(name)`: Belirli bir etiketle yeni bir sekme butonu ekler.
- `remove_tab_button(name)`: Benzersiz yol/isim bilgisine göre bir sekmeyi kaldırır.
- `set_active_tab(name)`: Bir sekmeyi aktif olarak işaretlemek için tüm butonların stilini günceller.
- `update_tab_text(name, text)`: Sekme etiketini değiştirir (örneğin kaydedilmemiş değişiklikler için `*` ekler).
- `apply_theme(theme)`: Bileşenin dahili stil sözlüğünü günceller ve görünür buton renklerini yeniler.

## Entegrasyon

`TabBar`, dokümanlar arası geçiş ve dosya açma/kapama mantığını koordine eden `TabManager` tarafından yönetilir.

```python
self.tab_bar = TabBar(self, on_tab_click=self.on_tab_click)
self.tab_bar.pack(side="top", fill="x")
```
