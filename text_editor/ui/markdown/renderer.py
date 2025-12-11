import re
import os
from io import BytesIO
from urllib.request import urlopen, Request
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .highlighter import MarkdownHighlighter
from .utils import auto_link_urls, load_emoji_map, replace_emoji_shortcuts
import webbrowser

class MarkdownRenderer:
    def __init__(self, text_widget, styler, file_path=None):
        self.text_widget = text_widget
        self.styler = styler
        self.file_path = file_path
        self.highlighter = MarkdownHighlighter(text_widget, styler)
        
        self.images = {}
        self.footnotes = {}
        self.anchors = {}
        self.code_blocks = []
        self.emoji_map = load_emoji_map()
        self.task_stats = {"total": 0, "completed": 0}
        
    def render(self, text):
        """Markdown metnini render eder."""
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        
        # Durumu sıfırla
        self.footnotes = {}
        self.anchors = {}
        self.code_blocks = []
        self.task_stats = {"total": 0, "completed": 0}
        
        if not text.strip():
            self.text_widget.insert("end", "📝 Markdown içeriği ekleyin...\n", "italic")
            self.text_widget.configure(state="disabled")
            return

        lines = text.split("\n")
        
        # İlk geçiş: Dipnotları topla
        self._collect_footnotes(lines)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Kod Blokları
            if line.strip().startswith("```"):
                i = self._handle_code_block(lines, i)
                continue
                
            # Tablolar
            if "|" in line and line.strip().startswith("|"):
                i = self._handle_table(lines, i)
                continue
            
            # Başlıklar
            if line.startswith("#"):
                self._insert_heading(line)
                i += 1
                continue
                
            # Yatay Çizgi
            if re.match(r'^[\-\*_]{3,}\s*$', line.strip()):
                self.text_widget.insert("end", "─" * 60 + "\n", "hr")
                i += 1
                continue
            
            # Matematik Bloğu
            if line.strip().startswith("$$"):
                i = self._handle_math_block(lines, i)
                continue
                
            # Alıntı veya Uyarı
            if line.strip().startswith(">"):
                i = self._handle_blockquote(lines, i)
                continue
                
            # Görev Listesi
            if re.match(r'^\s*[\-\*]\s+\[[ xX]\]\s+', line):
                self._handle_task_item(line)
                i += 1
                continue
                
            # Sırasız Liste
            if re.match(r'^\s*[\-\*\+]\s+', line):
                self._handle_unordered_list_item(line)
                i += 1
                continue
                
            # Sıralı Liste
            if re.match(r'^\s*\d+\.\s+', line):
                self._handle_ordered_list_item(line)
                i += 1
                continue
            
            # Boş Satır
            if not line.strip():
                self.text_widget.insert("end", "\n")
                i += 1
                continue
            
            # HTML Detayları
            if re.match(r'^\s*<details', line, re.IGNORECASE):
                i = self._handle_details(lines, i)
                continue
                
            # HTML Blokları
            if re.match(r'^\s*<(div|p|br|sub|sup|b|i|strong|em|span|center|hr)\b', line, re.IGNORECASE):
                i = self._handle_html_block(lines, i)
                continue
                
            # Varsayılan Paragraf
            line = auto_link_urls(line)
            self._insert_formatted_text(line + "\n", "paragraph")
            i += 1

        # Render sonrası eklemeler
        if self.task_stats["total"] > 0:
            self._show_task_progress()
            
        if self.footnotes:
            self._render_footnotes()
            
        self.text_widget.configure(state="disabled")

    def _collect_footnotes(self, lines):
        for line in lines:
            match = re.match(r'^\[\^(\w+)\]:\s*(.+)$', line)
            if match:
                ref_id, content = match.groups()
                self.footnotes[ref_id] = content

    def _handle_code_block(self, lines, start_index):
        i = start_index
        lang_line = lines[i].strip()
        lang = lang_line[3:].strip()
        i += 1
        
        content = []
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith("```"):
                i += 1
                break
            content.append(line)
            i += 1
            
        code = "\n".join(content)
        
        if lang.lower() in ['mermaid', 'diagram']:
            self._insert_mermaid_diagram(code)
        else:
            self._insert_code_block(code, lang)
            
        return i

    def _insert_mermaid_diagram(self, content):
        self.text_widget.insert("end", "\n")
        self.text_widget.insert("end", "📊 Mermaid Diyagramı\n", "diagram_block")
        self.text_widget.insert("end", "─" * 40 + "\n", "hr")
        
        diagram_type = "Diyagram"
        if "graph" in content.lower():
            diagram_type = "Akış Diyagramı"
        elif "sequenceDiagram" in content:
            diagram_type = "Sıra Diyagramı"
        elif "classDiagram" in content:
            diagram_type = "Sınıf Diyagramı"
        elif "pie" in content.lower():
            diagram_type = "Pasta Grafiği"
            
        self.text_widget.insert("end", f"Tip: {diagram_type}\n", "diagram_block")
        self.text_widget.insert("end", f"Satır Sayısı: {len(content.splitlines())}\n", "diagram_block")
        self.text_widget.insert("end", "\n💡 Diyagramı görüntülemek için HTML olarak dışa aktarın.\n", "footnote_content")
        self.text_widget.insert("end", "\n")

    def _insert_code_block(self, code, lang=""):
        self.text_widget.insert("end", "\n")
        
        lang_display = lang.upper() if lang else "CODE"
        header = f"┌─ {lang_display} "
        
        block_index = len(self.code_blocks)
        self.code_blocks.append(code)
        
        self.text_widget.insert("end", header, "code_block_header")
        
        copy_tag = f"copy_code_{block_index}"
        
        self.text_widget.tag_configure(copy_tag,
            font=("Consolas", int(12 * 1.0)), # Varsayılan, ideal olarak styler konfigürasyonuyla eşleşmeli
            foreground=self.styler.colors["h2"],
            background=self.styler.colors["code_bg"]
        )
        
        self.text_widget.tag_bind(copy_tag, "<Button-1>", 
            lambda e, idx=block_index: self._copy_code_block(idx))
        self.text_widget.tag_bind(copy_tag, "<Enter>", 
            lambda e: self.text_widget.configure(cursor="hand2"))
        self.text_widget.tag_bind(copy_tag, "<Leave>", 
            lambda e: self.text_widget.configure(cursor="arrow"))

        padding = "─" * (45 - len(header))
        self.text_widget.insert("end", padding + " ", "code_block_header")
        self.text_widget.insert("end", "📋 Kopyala", copy_tag)
        self.text_widget.insert("end", "\n", "code_block_header")
        
        lines = code.split("\n")
        for i, line in enumerate(lines):
            line_num = f"│ {i+1:3} │ "
            self.text_widget.insert("end", line_num, "code_block")
            if lang:
                self.highlighter.highlight_line(line + "\n", lang)
            else:
                self.text_widget.insert("end", line + "\n", "code_block")
                
        footer = "└─────────────────────────────────────────────\n"
        self.text_widget.insert("end", footer, "code_block_header")

    def _copy_code_block(self, index):
        try:
            if 0 <= index < len(self.code_blocks):
                code = self.code_blocks[index]
                self.text_widget.clipboard_clear()
                self.text_widget.clipboard_append(code)
                # Durum mesajı için, ebeveyn pencereye erişim gerekebilir.
                # Şimdilik sadece kopyala.
        except:
            pass

    def _handle_table(self, lines, start_index):
        i = start_index
        rows = []
        rows.append(lines[i]) # İlk satır
        
        # Tablo devamını kontrol et
        if i + 1 < len(lines) and "|" in lines[i + 1]:
             i += 1
             rows.append(lines[i]) # Ayırıcı satır
             
             i += 1
             while i < len(lines) and "|" in lines[i] and lines[i].strip():
                 rows.append(lines[i])
                 i += 1
        
        if len(rows) >= 2:
             self._insert_table(rows)
        else:
             self.text_widget.insert("end", rows[0] + "\n") # Sadece metin
             
        return i

    def _insert_table(self, rows):
        if len(rows) < 2: return
        
        # Satırları ayrıştır
        parsed_rows = []
        alignments = []
        
        for idx, row in enumerate(rows):
            cells = [c.strip() for c in row.split("|") if c.strip() or c == ""]
            if cells and cells[0] == "": cells = cells[1:]
            if cells and cells[-1] == "": cells = cells[:-1]
            
            if idx == 1 and all(re.match(r'^:?-+:?$', c.strip()) for c in cells if c.strip()):
                for cell in cells:
                    cell = cell.strip()
                    if cell.startswith(":") and cell.endswith(":"): alignments.append("center")
                    elif cell.endswith(":"): alignments.append("right")
                    else: alignments.append("left")
                continue
                
            if cells:
                parsed_rows.append(cells)
                
        if len(parsed_rows) < 1: return
        
        # Sütun genişliklerini hesapla
        col_widths = []
        for col_idx in range(len(parsed_rows[0])):
            max_width = 0
            for row in parsed_rows:
                if col_idx < len(row):
                    max_width = max(max_width, len(row[col_idx]))
            col_widths.append(max(max_width + 2, 5))
            
        self.text_widget.insert("end", "\n")
        
        # Tabloyu çiz
        # Üst kenarlık
        top_border = "╔" + "╤".join("═" * (w + 2) for w in col_widths) + "╗\n"
        self.text_widget.insert("end", top_border, "table_border")
        
        # Başlık
        header = parsed_rows[0]
        header_line = "║"
        for i, cell in enumerate(header):
            width = col_widths[i] if i < len(col_widths) else 10
            align = alignments[i] if i < len(alignments) else "left"
            formatted = cell.center(width) if align == "center" else cell.rjust(width) if align == "right" else cell.ljust(width)
            header_line += f" {formatted} │"
        header_line = header_line[:-1] + "║\n"
        self.text_widget.insert("end", header_line, "table_header")
        
        # Ayırıcı
        mid = "╠" + "╪".join("═" * (w + 2) for w in col_widths) + "╣\n"
        self.text_widget.insert("end", mid, "table_border")
        
        # Veri
        for row in parsed_rows[1:]:
            row_line = "║"
            for i, cell in enumerate(row if i < len(row) else [""]):
                cell = row[i] if i < len(row) else ""
                width = col_widths[i] if i < len(col_widths) else 10
                align = alignments[i] if i < len(alignments) else "left"
                formatted = cell.center(width) if align == "center" else cell.rjust(width) if align == "right" else cell.ljust(width)
                row_line += f" {formatted} │"
            row_line = row_line[:-1] + "║\n"
            self.text_widget.insert("end", row_line, "table")
            
        # Alt
        bottom = "╚" + "╧".join("═" * (w + 2) for w in col_widths) + "╝\n"
        self.text_widget.insert("end", bottom, "table_border")

    def _handle_math_block(self, lines, start_index):
        i = start_index
        math_content = []
        
        line = lines[i].strip()
        
        # Tek satır kontrolü
        if len(line) > 2 and line.endswith("$$") and line.count("$$") >= 2:
            content = line[2:-2].strip()
            self._insert_math_block(content)
            return i + 1
            
        if len(line) > 2:
            math_content.append(line[2:].strip())
            
        i += 1
        while i < len(lines):
            if lines[i].strip().startswith("$$"):
                break
            math_content.append(lines[i])
            i += 1
            
        self._insert_math_block("\n".join(math_content))
        return i + 1

    def _insert_math_block(self, content):
        self.text_widget.insert("end", "\n")
        self.text_widget.insert("end", f"{content}\n", "math_block")
        self.text_widget.insert("end", "\n")

    def _handle_blockquote(self, lines, start_index):
        i = start_index
        quote_lines = []
        while i < len(lines) and lines[i].strip().startswith(">"):
            quote_lines.append(lines[i].strip()[1:].strip())
            i += 1
            
        full_quote = "\n".join(quote_lines)
        
        alert_match = re.match(r'^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*(.*)', full_quote, re.IGNORECASE | re.DOTALL)
        if alert_match:
            alert_type = alert_match.group(1).lower()
            alert_content = full_quote[len(alert_match.group(0)) - len(alert_match.group(2)):]
            self._insert_alert(alert_type, alert_content)
        else:
            self._insert_blockquote_content(full_quote)
            
        return i

    def _insert_blockquote_content(self, text):
        self.text_widget.insert("end", "┃ ", "list_marker")
        for line in text.split("\n"):
            self._insert_formatted_text(line + "\n", "blockquote")
            if line != text.split("\n")[-1]:
                self.text_widget.insert("end", "┃ ", "list_marker")

    def _insert_alert(self, alert_type, content):
        self.text_widget.insert("end", "\n")
        
        icons = {
            "note": "ℹ️ Note", "tip": "💡 Tip", "warning": "⚠️ Warning",
            "important": "📢 Important", "caution": "🛑 Caution"
        }
        
        icon_text = icons.get(alert_type, alert_type.title())
        self.text_widget.insert("end", f"▌ {icon_text}\n", (f"alert_{alert_type}_border", f"alert_{alert_type}_header"))
        
        for line in content.split("\n"):
            self.text_widget.insert("end", f"{line}\n", f"alert_{alert_type}_body")
            
        self.text_widget.insert("end", "\n")

    def _handle_task_item(self, line):
        match = re.match(r'^\s*[\-\*]\s+\[([xX ])\]\s+(.*)$', line)
        if match:
            checked, content = match.groups()
            is_checked = checked.lower() == 'x'
            
            checkbox = "☑ " if is_checked else "☐ "
            tag = "checkbox_checked" if is_checked else "checkbox_unchecked"
            
            self.text_widget.insert("end", checkbox, tag)
            self._insert_formatted_text(content + "\n", "list_item")
            
            self.task_stats["total"] += 1
            if is_checked: self.task_stats["completed"] += 1

    def _handle_unordered_list_item(self, line):
        list_content = re.sub(r'^\s*[\-\*\+]\s+', '', line)
        indent = len(re.match(r'^\s*', line).group()) // 2
        markers = ["•", "◦", "▪", "▫"]
        marker = markers[min(indent, len(markers) - 1)]
        
        tag = f"list_item_l{min(indent, 3)}" if indent > 0 else "list_item"
        self.text_widget.insert("end", "  " * indent + marker + " ", "list_marker")
        self._insert_formatted_text(list_content + "\n", tag)

    def _handle_ordered_list_item(self, line):
        match = re.match(r'^\s*(\d+)\.\s+(.*)$', line)
        if match:
            num, list_content = match.groups()
            indent = len(re.match(r'^\s*', line).group()) // 2
            
            tag = f"list_item_l{min(indent, 3)}" if indent > 0 else "list_item"
            self.text_widget.insert("end", "  " * indent + f"{num}. ", "list_marker")
            self._insert_formatted_text(list_content + "\n", tag)

    def _handle_details(self, lines, start_index):
        i = start_index + 1
        summary_text = ""
        details_content = []
        
        while i < len(lines):
            if re.search(r'<summary>(.*?)</summary>', lines[i], re.IGNORECASE):
                summary_match = re.search(r'<summary>(.*?)</summary>', lines[i], re.IGNORECASE)
                summary_text = summary_match.group(1)
                i += 1
                break
            i += 1
            
        while i < len(lines):
            if re.search(r'</details>', lines[i], re.IGNORECASE):
                break
            details_content.append(lines[i])
            i += 1
            
        self._insert_details(summary_text, "\n".join(details_content))
        return i + 1

    def _insert_details(self, summary, content):
        self.text_widget.insert("end", "\n")
        self.text_widget.insert("end", "▶ " + summary + "\n", "details_summary")
        self.text_widget.insert("end", content + "\n", "details_content")
        self.text_widget.insert("end", "\n")

    def _handle_html_block(self, lines, start_index):
        i = start_index
        html_content = lines[i]
        
        # Tek satır HTML
        if re.search(r'</\w+>\s*$|/>\s*$|^<br\s*/?>$|^<hr\s*/?>$', html_content, re.IGNORECASE):
            self._render_html_content(html_content)
            return i + 1
            
        while i + 1 < len(lines):
            i += 1
            html_content += "\n" + lines[i]
            if re.search(r'</div>|</p>|</center>', lines[i], re.IGNORECASE):
                break
                
        self._render_html_content(html_content)
        return i + 1

    def _render_html_content(self, html):
        is_centered = 'align="center"' in html.lower() or '<center>' in html.lower()
        
        content = html
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<hr\s*/?>', '─' * 40, content, flags=re.IGNORECASE)
        content = re.sub(r'</?div[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</?center[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</?span[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<p[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</p>', '\n', content, flags=re.IGNORECASE)
        
        self._parse_and_insert_html(content, is_centered)

    def _parse_and_insert_html(self, content, centered=False):
        base_tag = "html_center" if centered else "paragraph"
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                self.text_widget.insert("end", "\n")
                continue
                
            remaining = line
            while remaining:
                bold_match = re.search(r'<(b|strong)>(.*?)</\1>', remaining, re.IGNORECASE | re.DOTALL)
                italic_match = re.search(r'<(i|em)>(.*?)</\1>', remaining, re.IGNORECASE | re.DOTALL)
                sub_match = re.search(r'<sub>(.*?)</sub>', remaining, re.IGNORECASE | re.DOTALL)
                sup_match = re.search(r'<sup>(.*?)</sup>', remaining, re.IGNORECASE | re.DOTALL)
                
                matches = []
                if bold_match: matches.append((bold_match, "bold"))
                if italic_match: matches.append((italic_match, "italic"))
                if sub_match: matches.append((sub_match, "html_sub"))
                if sup_match: matches.append((sup_match, "html_sup"))
                
                if matches:
                    matches.sort(key=lambda x: x[0].start())
                    best_match, tag = matches[0]
                    
                    if best_match.start() > 0:
                        self.text_widget.insert("end", remaining[:best_match.start()], base_tag)
                        
                    # Group 2 handles content for b/i/strong/em (patterns with backref)
                    # Group 1 handles content for sub/sup (simple patterns)
                    content_group = 2 if tag in ["bold", "italic"] else 1
                    self.text_widget.insert("end", best_match.group(content_group), tag)
                    remaining = remaining[best_match.end():]
                else:
                    self.text_widget.insert("end", remaining, base_tag)
                    break
            self.text_widget.insert("end", "\n")

    def _insert_heading(self, line):
        level = len(re.match(r'^#+', line).group())
        level = min(level, 6)
        content = line[level:].strip()
        
        tag = f"h{level}"
        
        anchor_id = content.lower()
        anchor_id = re.sub(r'[^\w\s-]', '', anchor_id)
        anchor_id = re.sub(r'[\s_]+', '-', anchor_id)
        anchor_id = anchor_id.strip('-')
        
        self.anchors[anchor_id] = self.text_widget.index("end-1c")
        
        prefixes = {1: "📌 ", 2: "📎 ", 3: "▸ ", 4: "› ", 5: "• ", 6: "· "}
        prefix = prefixes.get(level, "")
        
        self.text_widget.insert("end", prefix + content + "\n", tag)
        
        if level == 1:
            self.text_widget.insert("end", "═" * min(len(content) + 3, 50) + "\n", "h1_underline")
        elif level == 2:
            self.text_widget.insert("end", "─" * min(len(content) + 3, 40) + "\n", "h2_underline")

    def _insert_formatted_text(self, text, base_tag="paragraph"):
        text = replace_emoji_shortcuts(text, self.emoji_map)
        
        patterns = [
            (r'\*\*\*(.+?)\*\*\*', 'bold_italic'),
            (r'___(.+?)___', 'bold_italic'),
            (r'\*\*(.+?)\*\*', 'bold'),
            (r'__(.+?)__', 'bold'),
            (r'\*(.+?)\*', 'italic'),
            (r'_([^_]+)_', 'italic'),
            (r'~~(.+?)~~', 'strikethrough'),
            (r'==(.+?)==', 'highlight'),
            (r'`([^`]+)`', 'code'),
            (r'\[\^(\w+)\]', 'footnote_ref'),
            (r'\[((?:!\[.*?\]\(.*?\)|[^\]]+))\]\((.+?)\)', 'link'),
            (r'!\[(.+?)\]\((.+?)\)', 'image'),
        ]
        
        pos = 0
        remaining = text
        while remaining:
            earliest_match = None
            earliest_pos = len(remaining)
            matched_pattern = None
            
            for pattern, tag in patterns:
                match = re.search(pattern, remaining)
                if match and match.start() < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start()
                    matched_pattern = (pattern, tag)
            
            if earliest_match and matched_pattern:
                if earliest_pos > 0:
                    self.text_widget.insert("end", remaining[:earliest_pos], base_tag)
                
                pattern, tag = matched_pattern
                if tag == 'link':
                    self._insert_link(earliest_match.group(1), earliest_match.group(2))
                elif tag == 'image':
                    self._insert_image(earliest_match.group(1), earliest_match.group(2))
                elif tag == 'footnote_ref':
                    ref_id = earliest_match.group(1)
                    self.text_widget.insert("end", f"[{ref_id}]", "footnote_ref")
                else:
                    self.text_widget.insert("end", earliest_match.group(1), tag)
                
                remaining = remaining[earliest_match.end():]
            else:
                self.text_widget.insert("end", remaining, base_tag)
                break

    def _insert_link(self, text, url):
        # Link içinde resim kontrolü (Rozet desteği)
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', text)
        if img_match:
            alt_text = img_match.group(1)
            img_url = img_match.group(2)
            self._insert_image(alt_text, img_url, link_url=url)
            return

        link_tag = f"url_{len(self.anchors)}_{hash(url)}" 
        
        self.text_widget.tag_configure(link_tag,
            foreground=self.styler.colors["link"],
            underline=True
        )
        self.text_widget.tag_bind(link_tag, "<Enter>", lambda e: self.text_widget.configure(cursor="hand2"))
        self.text_widget.tag_bind(link_tag, "<Leave>", lambda e: self.text_widget.configure(cursor="arrow"))
        self.text_widget.tag_bind(link_tag, "<Button-1>", lambda e, u=url: self._on_link_click(u))
        
        icon = "🔗 " if not url.startswith("#") else "⚓ "
        self.text_widget.insert("end", icon + text, ("link", link_tag))

    def _on_link_click(self, url):
        if url.startswith("#"):
            anchor_key = url[1:].lower().replace(" ", "-")
            if anchor_key in self.anchors:
                self.text_widget.see(self.anchors[anchor_key])
        else:
             try:
                 webbrowser.open(url)
             except:
                 pass

    def _insert_image(self, alt_text, url, link_url=None):
        if PIL_AVAILABLE:
            try:
                if url.startswith(('http://', 'https://')):
                     req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                     with urlopen(req, timeout=5) as response:
                        img_data = response.read()
                     img = Image.open(BytesIO(img_data))
                else:
                    path = url
                    if self.file_path:
                        base = os.path.dirname(self.file_path)
                        path = os.path.join(base, url)
                    img = Image.open(path)
                
                # Çok büyükse yeniden boyutlandır, ancak küçük simgeleri (rozetler) olduğu gibi bırak
                if img.height > 50: # Sadece makul derecede büyükse yeniden boyutlandır, rozetlerin bulanıklaşmasını önle
                    max_width = 400
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                self.images[url] = photo
                
                self.text_widget.image_create("end", image=photo)
                
                # Eğer link_url sağlandıysa tıklanabilir yap
                if link_url:
                    img_tag = f"img_link_{len(self.images)}"
                    self.text_widget.tag_add(img_tag, "end-1c")
                    self.text_widget.tag_bind(img_tag, "<Button-1>", lambda e, u=link_url: self._on_link_click(u))
                    self.text_widget.tag_bind(img_tag, "<Enter>", lambda e: self.text_widget.configure(cursor="hand2"))
                    self.text_widget.tag_bind(img_tag, "<Leave>", lambda e: self.text_widget.configure(cursor="arrow"))
                else:
                    # İsteğe bağlı: Sadece resimse basit boşluk ekle
                    pass


            except Exception as e:
                self.text_widget.insert("end", f"🖼️ [{alt_text}]", "image_placeholder")
        else:
            self.text_widget.insert("end", f"🖼️ [{alt_text}]", "image_placeholder")

    def _show_task_progress(self):
        total = self.task_stats["total"]
        completed = self.task_stats["completed"]
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        self.text_widget.insert("end", "\n")
        self.text_widget.insert("end", "─" * 50 + "\n", "hr")
        self.text_widget.insert("end", "📋 Görev İlerlemesi\n", "h4")
        
        bar_length = 30
        filled = int((percentage / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_text = f"{bar} {percentage}% ({completed}/{total})\n"
        self.text_widget.insert("end", progress_text, "task_progress")

    def _render_footnotes(self):
        self.text_widget.insert("end", "\n")
        self.text_widget.insert("end", "─" * 30 + "\n", "hr")
        self.text_widget.insert("end", "📝 Dipnotlar\n", "h4")
        
        for ref_id, content in self.footnotes.items():
            self.text_widget.insert("end", f"[{ref_id}] ", "footnote_ref")
            self.text_widget.insert("end", f"{content}\n", "footnote_content")
