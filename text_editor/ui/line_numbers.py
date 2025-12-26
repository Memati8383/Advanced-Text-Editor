import tkinter as tk
from text_editor.config import FONT_FAMILY, FONT_SIZE

class LineNumbers(tk.Text):
    """
    Ana metin editörünün sol tarafında satır numaralarını gösteren bileşen.
    Metin editörü ile senkronize çalışır ve sadece görünür satırları çizer.
    Ayrıca kod katlama (folding) işaretçilerini de gösterir.
    """
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=8, padx=4, pady=5, highlightthickness=0, bd=0, 
                         font=(FONT_FAMILY, FONT_SIZE), state="disabled", cursor="arrow", wrap="none", **kwargs)
        self.text_widget = text_widget
        # redundant bindings removed to prevent multiple redraws and jumping issues
        # self.text_widget.bind("<<Change>>", self.redraw)
        # self.text_widget.bind("<Configure>", self.redraw)
        self.bind("<Button-1>", self.on_click)

    def redraw(self, *args):
        """
        Satır numaralarını yeniden çizer.
        Tüm dosyayı işler ve text_widget ile senkronize scrolling sağlar.
        """
        self.configure(state="normal")
        self.delete("1.0", "end")
        
        # Metin içeriğini al
        try:
            full_content = self.text_widget.get("1.0", "end-1c")
        except:
             # Widget destroyed
            return

        lines = full_content.split('\n')
        total_lines = len(lines)
        
        # Katlanmış satırları belirle
        folded_lines = set()
        try:
            for tag in self.text_widget.tag_names():
                if tag.startswith("fold_"):
                    try:
                        line_num = int(tag.split('_')[1])
                        folded_lines.add(line_num)
                    except:
                        pass
        except:
            pass
        
        # Girinti hesaplama yardımcısı
        def get_indent(s):
            return len(s) - len(s.lstrip())
            
        buffer = []
        
        for i, line_content in enumerate(lines):
            linenum = i + 1
            marker = "  " # Varsayılan: 2 boşluk
            
            # Katlanabilirlik kontrolü
            if line_content.strip():
                curr_indent = get_indent(line_content)
                
                # Sonraki satırları kontrol et
                for j in range(i + 1, total_lines):
                    next_line = lines[j]
                    if next_line.strip():
                        # İlk dolu satırı bulduk
                        if get_indent(next_line) > curr_indent:
                            if linenum in folded_lines:
                                marker = "▶ "
                            else:
                                marker = "▼ "
                        break
            
            buffer.append(f"{marker}{linenum:>4}\n")
        
        self.insert("1.0", "".join(buffer))
        
        # Katlama etiketlerini uygula
        try:
            for tag in self.text_widget.tag_names():
                if tag.startswith("fold_"):
                    ranges = self.text_widget.tag_ranges(tag)
                    if ranges:
                        self.tag_add(tag, *ranges)
                        self.tag_config(tag, elide=True)
        except:
             pass

        # Scrolling'i senkronize et (Async yap ki render tamamlansın)
        def sync_scroll():
            try:
                self.yview_moveto(self.text_widget.yview()[0])
            except:
                pass
                
        self.after_idle(sync_scroll)
            
        self.configure(state="disabled")

    def on_click(self, event):
        """
        Satır numaraları alanına tıklama olayını işler.
        """
        try:
            index = self.index(f"@{event.x},{event.y}")
            line_idx = int(index.split('.')[0])
            
            # Basitleştirilmiş mantık: LineNumbers satır indeksi == Gerçek satır numarası
            # Master (CodeEditor) üzerinde toggle_fold metodunu çağırır
            if hasattr(self.master, 'toggle_fold'):
                self.master.toggle_fold(line_idx)
        except Exception:
            pass
