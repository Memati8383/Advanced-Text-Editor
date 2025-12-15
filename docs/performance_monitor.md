# Performans İzleyicisi (Performance Monitor)

`PerformanceMonitor` sınıfı, uygulamanın ve sistemin kaynak kullanımını izlemek için statik metotlar sağlayan bir yardımcı sınıftır. Yardım Sistemi ve Durum Çubuğu gibi bileşenler tarafından kullanılır.

## `PerformanceMonitor` Sınıfı

`text_editor.utils.performance_monitor.PerformanceMonitor`

### Özellikler

*   **Sistem Bilgisi:** İşletim sistemi, sürümü ve mimarisi.
*   **Python Sürümü:** Çalışan Python interpreter sürümü.
*   **Bellek Kullanımı:** Uygulamanın kullandığı RAM miktarı. `psutil` kütüphanesini tercih eder, ancak mevcut değilse Windows API (`ctypes`) üzerinden fallback (yedek) yöntem kullanır.
*   **CPU Kullanımı:** İşlemci kullanım yüzdesi (`psutil` gerektirir).
*   **Thread Sayısı:** Aktif iplik sayısı.
*   **Çalışma Süresi (Uptime):** Uygulamanın ne kadar süredir açık olduğu.

### Editör İstatistikleri

`get_editor_stats(app_instance)` metodu, o anki editör durumu hakkında detaylı bilgi döner:

*   Açık sekme sayısı.
*   Toplam satır sayısı (tüm açık dosyalarda).
*   Toplam karakter sayısı.
*   Dosya türü dağılımı (örn. "2 .py, 1 .md").

### Bağımlılıklar

Modül, verimli ve platformlar arası uyumlu metrik toplama için `psutil` kütüphanesini kullanır ancak bu bir zorunluluk değildir (soft dependency).
