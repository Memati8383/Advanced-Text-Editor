# Dosya İzleyici (File Monitor)

Dosya İzleyici modülü, editörde açık olan dosyalar üzerinde yapılan harici değişiklikleri gerçek zamanlı olarak algılar. Bu sistem, üzerinde çalıştığınız bir dosya başka bir program (örn. git, başka bir editör veya build işlemleri) tarafından değiştirildiğinde sizi uyarır.

## Genel Bakış

Sistem, dosya sistemi olaylarını verimli bir şekilde izlemek için `watchdog` kütüphanesini kullanır. Ana uygulama arayüzünü (UI) kilitlememek için arka planda bir iş parçacığı (thread) olarak çalışır.

## Bileşenler

### `FileMonitor` Sınıfı
Konum: `text_editor/utils/file_monitor.py`

- **Gözlemci (Observer):** Dizinleri izlemek için `watchdog.observers.Observer` kullanır.
- **Olay İşleyici (Event Handler):** İlgili dosya olaylarını filtrelemek ve işlemek için özelleştirilmiş bir `FileSystemEventHandler` kullanır.

## Kullanım

`CodeEditor` içerisinde bir dosya açıldığında, `FileMonitor` otomatik olarak dosyanın bulunduğu dizini izlemeye başlar.

### Olay Akışı
1. **Algılama:** İzlenen bir dosya yolunda "değiştirilme" (modified) olayı algılanır.
2. **Geri Bildirim:** İzleyici, ana uygulamadaki geri çağırma (callback) fonksiyonunu tetikler.
3. **Arayüz Tepkisi:** Editör dosyanın durumunu kontrol eder:
   - Eğer **Kaydedilmiş (Clean)** durumda ise: Editör dosyayı otomatik olarak diskten yeniden yükleyebilir (ayarlara bağlı olarak).
   - Eğer **Kaydedilmemiş (Dirty)** değişiklikler varsa: Kullanıcıya değişiklikleri korumak mı yoksa diskten yeniden yüklemek mi istediği sorulur.

## Gereksinimler

- Uygulamanın çalışması için `watchdog` paketinin yüklü olması gerekir.
