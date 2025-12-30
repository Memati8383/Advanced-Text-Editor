class MultiCursorManager:
    def __init__(self, editor):
        self.editor = editor
        self.text_area = editor.text_area
        self.cursors = [] # (line, col) tuples
        self.active = False
        
    def add_cursor_at_click(self, event):
        """Alt+Click ile tıklanan yere yeni bir imleç ekler."""
        # Tıklanan pozisyonu al
        index = self.text_area.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split('.'))
        
        # Bu pozisyonda zaten imleç var mı kontrol et
        cursor_pos = (line, col)
        if cursor_pos in self.cursors:
            # Varsa kaldır
            self.cursors.remove(cursor_pos)
        else:
            # Yoksa ekle
            self.cursors.append(cursor_pos)
        
        self.update_state()
        self.update_visuals()
        return "break"
    
    def clear_cursors(self, event=None):
        """Tüm ek imlçleri temizler."""
        self.cursors = []
        self.update_state()
        self.update_visuals()
        # "break" dönmeyebiliriz, belki ESC başka şeyler de yapıyordur (Completion popup vs)
        # Ancak orijinal kodda break vardı.
        return "break"
    
    def update_state(self):
        """Aktiflik durumunu günceller."""
        self.active = len(self.cursors) > 0
        self.editor.multi_cursor_mode = self.active # Geriye dönük uyumluluk için

    def update_visuals(self):
        """Ekrandaki imleç görsellerini günceller."""
        # Önce eski cursor tag'lerini temizle
        for tag in self.text_area.tag_names():
            if tag.startswith("multi_cursor_"):
                self.text_area.tag_delete(tag)
        
        # Yeni cursorları çiz
        for i, (line, col) in enumerate(self.cursors):
            # İmleç pozisyonu
            pos = f"{line}.{col}"
            
            # Tag oluştur
            tag_name = f"multi_cursor_{i}"
            
            # Eğer o satır o an ekranda görünüyorsa
            # (Tkinter zaten görünmeyeni optimize eder ama logic burası)
            # İmleç = yanıp sönen ince çizgi. 
            # Tkinter text widget'ında özel karakter yerine background color kullanmak daha kolay olabilir
            # veya 'insert' mark'ı simüle eden ince bir dikdörtgen.
            # Ancak en basit yöntem 1 karakterlik alana 'cursor' stili vermektir.
            
            # Orijinal implementasyonda nasıl yapıldığını bilmediğimiz için
            # Standart bir dikey çizgi simülasyonu yapalım:
            # Seçim rengi gibi arka plan vermek:
            
            self.text_area.tag_add(tag_name, pos)
            self.text_area.tag_config(tag_name, background="red", foreground="white") # Geçici görsel
            
            # Daha iyi bir görsel için: Theme içindeki accent color'ı almalı
            # Ama şimdilik basit tutalım.
    
    def insert_at_all_cursors(self, char):
        """Tüm imlçlere karakter ekler."""
        # Ters sırayla işle ki indeksler kaymasın
        sorted_cursors = sorted(self.cursors, key=lambda x: (x[0], x[1]), reverse=True)
        
        new_cursors = []
        for line, col in sorted_cursors:
            pos = f"{line}.{col}"
            self.text_area.insert(pos, char)
            new_cursors.append((line, col + 1))
            
        self.cursors = new_cursors
        self.update_visuals()

    def delete_at_all_cursors(self, direction="backspace"):
        """Tüm imlçlerde silme yapar."""
        sorted_cursors = sorted(self.cursors, key=lambda x: (x[0], x[1]), reverse=True)
        
        new_cursors = []
        for line, col in sorted_cursors:
            pos = f"{line}.{col}"
            
            if direction == "backspace":
                if col > 0:
                    self.text_area.delete(f"{pos}-1c", pos)
                    new_cursors.append((line, col - 1))
                else:
                    # Satır birleştirme vs. karmaşık durumlar, şimdilik atla
                    new_cursors.append((line, col))
            else: # delete
                self.text_area.delete(pos, f"{pos}+1c")
                new_cursors.append((line, col))
                
        self.cursors = new_cursors
        self.update_visuals()
