<div align="center">

# 🪐 Memati Editör

**Modern, Hafif ve Güçlü Bir Python IDE'si**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Lisans](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)](https://github.com/Memati8383/Advanced-Text-Editor)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://img.shields.io/github/downloads/Memati8383/Advanced-Text-Editor/total.svg)](https://github.com/Memati8383/Advanced-Text-Editor/releases)
[![Issues](https://img.shields.io/github/issues/Memati8383/Advanced-Text-Editor.svg)](https://github.com/Memati8383/Advanced-Text-Editor/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Stars](https://img.shields.io/github/stars/Memati8383/Advanced-Text-Editor.svg)](https://github.com/Memati8383/Advanced-Text-Editor/stargazers)


<br>
<p align="center">
  <b>Memati Editör</b>; hız, estetik ve üretkenliği bir araya getiren <i>yeni nesil</i> bir kod editörüdür.
  <br><br>
  Modern <b>CustomTkinter</b> arayüzü, akıllı kodlama yardımcıları ve göz alıcı temaları ile
  hem başlangıç seviyesindeki kullanıcılara hem de profesyonellere <b>premium</b> bir deneyim sunar.
  <br>
  <i>Sadece kod yazmayın, kodun sanatını icra edin.</i>
</p>

</div>

---

## ✨ Öne Çıkan Özellikler

### 🚀 **Gelişmiş Kodlama Araçları**
- **🧠 Akıllı Otomatik Tamamlama**: Yazarken size yardımcı olan bağlamsal öneriler.
- **📂 Kod Katlama (Code Folding)**: Fonksiyon ve sınıf bloklarını katlayarak kod karmaşasını azaltın.
- **⚖️ Akıllı Girinti & Parantez**: Otomatik girinti ve parantez/tırnak kapatma ile hatasız yazım.
- **🖱️ Çoklu İmleç**: Alt+Click ile birden fazla yerde aynı anda düzenleme yapın.
  - Alt+Click: Tıklanan yere imleç ekle/kaldır
  - Ctrl+D: Seçili kelimeyi bul ve bir sonrakini seç
  - Escape: Tüm ek imleçleri temizle
- **🗺️ Mini Harita (Minimap)**: Dosyanızın önizlemesi ile büyük dosyalarda kaybolmadan gezinin.
- **🔍 Gelişmiş Arama**: Regex destekli güçlü Bul ve Değiştir aracı.
- **🔢 Satıra Git**: `Ctrl+G` ile kodunuzun derinliklerine hızla ulaşın.

### 🎨 **Modern Arayüz & Deneyim**
- **💎 9 Premium Tema**: **Dracula**, **Monokai**, **Solarized**, **Nord**, **Gruvbox**, **One Dark Pro**, **GitHub Dark**, **Synthwave '84** ve **Light**.
- **🎨 Modern Menüler**: Emoji ikonlu, fade-in animasyonlu, stilize dropdown menüler.
- **📊 Gelişmiş Durum Çubuğu**: Dinamik ikonlar, hover efektleri ve detaylı bilgi gösterimi.
- **🔎 Dinamik Yakınlaştırma**: `Ctrl + Tekerlek` ile editör yazı boyutunu ve arayüzü ölçeklendirin.
- **📑 Sekme Yönetimi**: Sürükle-bırak hissi veren, sağ tık menülü (Diğerlerini/Sağdakileri Kapat) gelişmiş sekme sistemi.
- **🖥️ Çerçevesiz Tam Ekran**: `F11` ile tamamen koda odaklanın.
- **📁 Gelişmiş Dosya Gezgini**: Ağaç yapısı, her dosya için özel ikon, 100+ uzantı desteği.
- **⌨️ Entegre Terminal**: PowerShell/Bash desteği, tema uyumu, komut geçmişi ile güçlü terminal.

### 📄 **Dosya Desteği**
- **🌍 100+ Dosya Formatı**: Python, JavaScript, TypeScript, React, Vue, Java, C++, Rust, Go ve daha fazlası.
- **🎨 Akıllı İkon Sistemi**: Her dosya türü için özel emoji ikonu (🐍 Python, ⚛️ React, 🔷 TypeScript, vb.)
- **📦 Özel Dosya Tanıma**: package.json, Dockerfile, README.md, LICENSE gibi özel dosyalar otomatik tanınır.
- **🎯 Otomatik Algılama**: Dosya uzantısına göre syntax highlighting ve ikon seçimi.

### 🛡️ **Güvenlik ve Performans**
- **💾 Sessiz Otomatik Kayıt**: Kodunuzu yazarken arka planda otomatik olarak güvenceye alın.
- **👀 Canlı Dosya İzleme**: Dosyalar başka bir programda değiştiğinde sizi uyarır ve senkronize eder.
- **🎨 Zengin Sözdizimi Vurgulama**: `Pygments` motoru ile 300+ dil desteği (Python, JS, HTML, CSS, C++, Java vb.).

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- **Python 3.10** veya daha yeni bir sürüm.
- **Git** (isteğe bağlı, indirmek için gerekli).

### ⚡ Hızlı Başlangıç

Aşağıdaki adımları takiperek geliştirme ortamınızı 1 dakika içinde hazırlayın:

1. **Projeyi Bilgisayarınıza İndirin**
   ```bash
   git clone https://github.com/Memati8383/Advanced-Text-Editor.git
   cd Advanced-Text-Editor
   ```

2. **Sanal Ortamı Oluşturun (Önerilen)**
   Projeyi izole bir ortamda çalıştırmak için:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Bağımlılıkları Yükleyin**
   ```bash
   pip install customtkinter pygments watchdog
   ```

4. **Uygulamayı Başlatın**
   ```bash
   python run_editor.py
   ```

---

## ⌨️ Klavye Kısayolları

| Kategori | Kısayol | İşlem |
| :--- | :--- | :--- |
| **📁 Dosya** | <kbd>Ctrl</kbd> + <kbd>N</kbd> | Yeni Sekme Aç |
| | <kbd>Ctrl</kbd> + <kbd>O</kbd> | Dosya Aç |
| | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>O</kbd> | Klasör (Proje) Aç |
| | <kbd>Ctrl</kbd> + <kbd>S</kbd> | Kaydet |
| | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | Farklı Kaydet |
| **✏️ Düzenleme** | <kbd>Ctrl</kbd> + <kbd>F</kbd> | Bul ve Değiştir |
| | <kbd>Ctrl</kbd> + <kbd>G</kbd> | Satıra Git |
| **🔢 Satır İşlemleri** | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> | Satırı Çoğalt (Alta Kopyala) |
| | <kbd>Alt</kbd> + <kbd>↑</kbd> | Satırı Yukarı Taşı |
| | <kbd>Alt</kbd> + <kbd>↓</kbd> | Satırı Aşağı Taşı |
| | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>K</kbd> | Satırı Sil |
| | <kbd>Ctrl</kbd> + <kbd>J</kbd> | Satırları Birleştir |
| **🖱️ Çoklu İmleç** | <kbd>Alt</kbd> + <kbd>Click</kbd> | Yeni İmleç Ekle/Kaldır |
| | <kbd>Ctrl</kbd> + <kbd>D</kbd> | Kelimeyi Bul ve Seç |
| | <kbd>Escape</kbd> | İmleçleri Temizle |
| **👁️ Görünüm** | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>L</kbd> | Satır Numaraları Aç/Kapat |
| | <kbd>Alt</kbd> + <kbd>Z</kbd> | Satır Sarma (Word Wrap) |
| | <kbd>Ctrl</kbd> + <kbd>M</kbd> | Minimap Aç/Kapat |
| | <kbd>Ctrl</kbd> + <kbd>B</kbd> | Dosya Gezgini Aç/Kapat |
| | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>M</kbd> | Durum Çubuğu Aç/Kapat |
| | <kbd>Ctrl</kbd> + <kbd>K</kbd>, <kbd>Z</kbd> | Zen Modu |
| | <kbd>F11</kbd> | Tam Ekran Modu |
| | <kbd>Ctrl</kbd> + <kbd>Tekerlek</kbd> | Yakınlaştır / Uzaklaştır |
| **⌨️ Terminal** | <kbd>Ctrl</kbd> + <kbd>`</kbd> | Terminal Aç/Kapat |
| **📋 Kopyalama** | <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd> | Dosya Yolunu Kopyala |
| | <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>C</kbd> | Göreli Yolu Kopyala |

---

## 📝 Sürüm Notları

### 🚀 v1.0 - İlk Resmi Sürüm (Aralık 2024)

**Görünüm & UX İyileştirmeleri:**
- ✨ Modern menü sistemi (emoji ikonlu, animasyonlu dropdownlar)
- 📊 Gelişmiş durum çubuğu (4 bölümlü, hover efektleri)
- 🎨 Zenginleştirilmiş temalar (accent colors)

**Dosya Sistemi:**
- 🌍 100+ dosya formatı desteği
- 🎨 Her dosya için özel emoji ikonu
- 📦 Özel dosyalar (package.json, Dockerfile, etc.)

**Yeni Özellikler:**
- 🖱️ Çoklu imleç desteği (Alt+Click, Ctrl+D)
- 🔢 Satır işlemleri (Çoğalt, Taşı, Sil, Birleştir)
- ❓ Modern help system (arama, navigasyon)
- 📚 10 kapsamlı yardım bölümü

---

## 🤝 Topluluk ve Katkı

Bu proje açık kaynaklıdır ve topluluk katkılarıyla büyümektedir. Her türlü destek (kod, hata bildirimi, özellik önerisi) bizim için değerlidir!

### 🌟 Nasıl Katkıda Bulunabilirim?

1. **🍴 Fork Edin**: Sağ üstteki butonu kullanarak projeyi kendi hesabınıza çatallayın.
2. **🌿 Dal Oluşturun**: Geliştirme yapmak için yeni bir dal açın:
   ```bash
   git checkout -b ozellik/YeniOzellik
   ```
3. **💻 Kodlayın**: Değişikliklerinizi yapın ve açıklayıcı bir mesajla commit'leyin:
   ```bash
   git commit -m 'feat: Yeni muazzam özellik eklendi'
   ```
4. **🚀 Gönderin**: Değişiklikleri dalınıza pushlayın:
   ```bash
   git push origin ozellik/YeniOzellik
   ```
5. **🔀 PR Açın**: Ana repoya bir Pull Request gönderin ve kodunuzu inceleyelim!

> 🐛 **Hata mı buldunuz?** Lütfen [Issues](https://github.com/Memati8383/Advanced-Text-Editor/issues) sayfasından bildirin.
> ⭐ **Beğendiniz mi?** Projeye yıldız vererek destek olabilirsiniz!

---

<div align="center">
  <br>
  <p><sub>Bu proje <b>MIT Lisansı</b> altında lisanslanmıştır.</sub></p>
  <p>Copyright © 2024 Memati. Tüm Hakları Saklıdır.</p>
  <p><sub><i>Memati tarafından ☕ ve ❤️ ile kodlandı.</i></sub></p>
</div>
