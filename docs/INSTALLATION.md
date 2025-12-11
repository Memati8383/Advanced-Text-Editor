# 📥 Kurulum Rehberi

Memati Editör'ü bilgisayarınıza kurmak ve çalıştırmak için aşağıdaki adımları izleyin.

## 📋 Gereksinimler

*   **İşletim Sistemi:** Windows, macOS veya Linux
*   **Python:** 3.10 veya daha yeni bir sürüm
*   **Pip:** Python paket yöneticisi

## 🚀 Adım Adım Kurulum

### 1. Projeyi Klonlayın

Terminal veya komut istemcisini açın ve projeyi indirin:

```bash
git clone https://github.com/memati/memati-editor.git
cd memati-editor
```

(Eğer git yüklü değilse, projeyi ZIP olarak indirip çıkarabilirsiniz.)

### 2. Sanal Ortam Oluşturun (Önerilen)

Bağımlılıkların sistem genelindeki Python kurulumunuzu etkilememesi için sanal ortam kullanmanız önerilir.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin

Projenin çalışması için gerekli kütüphaneleri `requirements.txt` dosyasından yükleyin (eğer dosya yoksa aşağıdaki komutu kullanın):

```bash
pip install customtkinter pygments watchdog pypiwin32
```

*Not: `pypiwin32` sadece Windows için gereklidir.*

## ▶️ Çalıştırma

Kurulum tamamlandıktan sonra editörü başlatmak için:

```bash
python run_editor.py
```

## 🛠️ Sorun Giderme

*   **ModuleNotFoundError:** Bağımlılıkların yüklü olduğundan emin olun (`pip list`).
*   **Tkinter Hatası:** Python kurulumunuzda Tkinter'in dahil olduğundan emin olun (Genellikle varsayılan olarak gelir).
*   **Terminal Font Sorunu:** Terminalde garip karakterler görüyorsanız, `Nerd Font` destekli bir yazı tipi kullanmayı deneyin.
