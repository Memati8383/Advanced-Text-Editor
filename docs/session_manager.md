# 📁 Session Manager

`SessionManager`, uygulamanın çalışma oturumlarını yöneten yardımcı sınıftır. Editör kapatıldığında açık olan dosyaları, aktif sekmeyi ve uygulama durumunu kaydederek bir sonraki açılışta kullanıcının kaldığı yerden devam etmesini sağlar.

## 🚀 Temel Görevler

1.  **Oturum Kaydı:** Açık olan tüm dosyaların yollarını ve imleç konumlarını bir yapılandırma dosyasında saklar.
2.  **Oturum Yükleme:** Uygulama açıldığında son oturumu otomatik olarak geri yükler.
3.  **Hata Kurtarma:** Beklenmedik kapanmalarda son geçerli oturumu korur.

## ⌨️ Önemli Metodlar

*   `save_session(open_files, active_index)`: Mevcut sekmeleri ve odaklanılan dosyayı kaydeder.
*   `load_session()`: Kayıtlı oturumu döndürür.
*   `clear_session()`: Oturum verilerini temizler.

## ⚙️ Yapılandırma

Oturum verileri genellikle JSON formatında kullanıcının yerel uygulama veri klasöründe saklanır.
