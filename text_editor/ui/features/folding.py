class CodeFolder:
    def __init__(self, editor):
        self.editor = editor
        self.text_area = editor.text_area

    def is_line_foldable(self, line_num):
        """
        Bir satırın katlanabilir olup olmadığını girintisine (indentation) bakarak belirler.
        Eğer sonraki satırın girintisi daha fazlaysa, bu satır bir blok başlangıcıdır.
        """
        try:
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            if not line_text.strip():
                return False
                
            indent_current = len(line_text) - len(line_text.lstrip())
            
            # Girintiyi kontrol etmek için bir sonraki boş olmayan satırı bul
            next_line_num = line_num + 1
            while True:
                if self.text_area.compare(f"{next_line_num}.0", ">=", "end"):
                    return False # EOF'a ulaşıldı
                    
                next_line_text = self.text_area.get(f"{next_line_num}.0", f"{next_line_num}.end")
                if next_line_text.strip():
                    break
                next_line_num += 1
            
            indent_next = len(next_line_text) - len(next_line_text.lstrip())
            
            return indent_next > indent_current
        except Exception:
            return False

    def is_line_folded(self, line_num):
        """Bir satırın şu anda katlanmış durumda olup olmadığını kontrol eder."""
        tag_name = f"fold_{line_num}"
        ranges = self.text_area.tag_ranges(tag_name)
        return bool(ranges)

    def toggle_fold(self, line_num):
        """
        Belirtilen satırdaki kod bloğunu katlar veya açar.
        Katlama işlemi metni gizlemek (elide) için etiketler (tags) kullanır.
        """
        if not self.is_line_foldable(line_num):
            return

        tag_name = f"fold_{line_num}"
        
        if self.is_line_folded(line_num):
            # Katlamayı aç
            self.text_area.tag_delete(tag_name)
        else:
            # Katla
            # Başlangıç girintisini bul
            line_text = self.text_area.get(f"{line_num}.0", f"{line_num}.end")
            start_indent = len(line_text) - len(line_text.lstrip())
            
            # Bitiş satırını bul
            current_line = line_num + 1
            while True:
                if self.text_area.compare(f"{current_line}.0", ">=", "end"):
                    break
                    
                content = self.text_area.get(f"{current_line}.0", f"{current_line}.end")
                
                # Eğer boş olmayan satır aynı veya daha az girintiye sahipse, blok bitti
                if content.strip():
                    curr_indent = len(content) - len(content.lstrip())
                    if curr_indent <= start_indent:
                        break
                
                current_line += 1
            
            # Blok line_num+1'den current_line-1'e kadardır
            # SONRAKİ satırdan başlayarak, kesme satırının başına kadar katlamak istiyoruz.
            # Yani aralık: line_num+1.0'dan current_line.0'a
            
            end_line = current_line
            
            self.text_area.tag_add(tag_name, f"{line_num+1}.0", f"{end_line}.0")
            self.text_area.tag_config(tag_name, elide=True)
            self.text_area.tag_raise(tag_name) # Katlamanın her şeyi gizlediğinden emin ol
            
        if hasattr(self.editor, 'line_numbers'):
            self.editor.line_numbers.redraw()
        
        if hasattr(self.editor, 'minimap'):
            self.editor.minimap.update_content()
