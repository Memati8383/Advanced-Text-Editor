# Yardım İçeriği Sağlayıcı (Help Content Provider)

`HelpContentProvider` sınıfı, Yardım Merkezi'nde görüntülenen yerelleştirilmiş içerikleri yöneten ve sağlayan bir yardımcı sınıftır. İçerik mantığını arayüzden ayırır.

## Temel Sorumluluklar

- **Yerelleştirme Entegrasyonu**: Yardım konuları için çoklu dil desteği sağlamak üzere `LanguageManager`'dan dizeleri çeker.
- **Dinamik İçerik Oluşturma**: Performans istatistikleri ve sistem bilgileri gibi dinamik raporlar hesaplar.
- **Kısayol Gösterimi**: `ShortcutManager`'dan mevcut klavye kısayollarını çeker ve yardım metnine formatlar.
- **Şablon Yönetimi**: Statik yardım şablonlarına dinamik veri enjekte etmek için format dizelerini kullanır.

## Ana İçerik Kategorileri

1. **Hızlı Başlangıç**: Editörün temel tanıtımı.
2. **Kısayollar Kılavuzu**: Mevcut tüm tuş atamalarının dinamik listesi.
3. **Çoklu İmleç Kılavuzu**: Editörün çoklu imleç düzenleme özelliklerinin kullanımı.
4. **Tema Kılavuzu**: Temaların nasıl özelleştirileceği ve değiştirileceği hakkında bilgi.
5. **İpuçları ve Püf Noktaları**: İleri düzey kullanıcılar için kullanım ipuçları.
6. **Desteklenen Formatlar**: Editörün açabildiği ve renklendirebildiği dosya uzantılarının listesi.
7. **Performans Raporu**: Bellek kullanımı, CPU yükü ve sistem bilgileri dahil gerçek zamanlı veriler.
8. **SSS**: Sıkça sorulan sorular.
9. **Markdown Kılavuzu**: Markdown düzenleme ve önizleme temelleri.
10. **Resim Görüntüleyici**: Entegre resim görüntüleyicinin kullanımı.

## Önemli Metotlar

- `get_performance_report(app_instance)`: `PerformanceMonitor`'dan veri toplar ve yerelleştirme şablonuyla eşleştirir.
- `get_shortcuts()`: Kullanımdaki *gerçek* kısayolları göstermek için `ShortcutManager` ile etkileşim kurar.
- `get_supported_formats()`: Desteklenen dosya tiplerini listeler.

## Kullanım Örneği

```python
from text_editor.ui.help_content import HelpContentProvider

# Performans raporu al
report_text = HelpContentProvider.get_performance_report(main_window)

# Güncel kısayollar metnini al
shortcuts_text = HelpContentProvider.get_shortcuts()
```
