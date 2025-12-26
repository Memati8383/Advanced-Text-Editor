# ✨ Editor Features Module

Bu dizin, editörün temel metin düzenleme yeteneklerini genişleten modüler özellikleri içerir. Ana `Editor` sınıfını şişirmek yerine, karmaşık mantığa sahip özellikler burada izole edilir.

## 🚀 Mevcut Özellikler

*   **`folding.py`**: **Kod Katlama (Code Folding)** sistemini yönetir. Fonksiyon, sınıf ve girintili blokların gizlenmesini/gösterilmesini sağlar.
*   **`multi_cursor.py`**: **Çoklu İmleç (Multi-Cursor)** desteğini sağlar. `Alt+Click` ile yeni imleç ekleme ve `Ctrl+D` ile kelime seçme mantığını yönetir.

## 🛠️ Yeni Özellik Ekleme

Yeni bir editör özelliği eklerken:

1.  Özelliği bağımsız bir sınıf olarak tanımlayın.
2.  `Editor` instance'ını referans olarak alın.
3.  Gerekli event binding'lerini (`<Button-1>`, `<Key>`, vb.) bu modül içinde tanımlayın.
4.  `Editor` sınıfı içinde bu özelliği initialize edin.

## 🎯 Amaç

Bu modüler yapı sayesinde:
*   Kod okunabilirliği artar.
*   Özellikler birbirinden bağımsız olarak test edilebilir.
*   Yeni karmaşık özellikler (örneğin: Git entegrasyonu görselleştirmesi, hata ayıklama işaretçileri) kolayca eklenebilir.
