import re
import os
import webbrowser
import tempfile
import tkinter.filedialog as filedialog

class MarkdownExporter:
    """Markdown dışa aktarım işlemlerini yönetir."""
    
    def __init__(self, editor, styler):
        self.editor = editor
        self.styler = styler
        
    def export_as_html(self, parent_window=None):
        """Markdown içeriğini HTML olarak render edip kaydeder."""
        if not self.editor:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Dosyası", "*.html"), ("Tüm Dosyalar", "*.*")],
            title="HTML Olarak Kaydet",
            parent=parent_window
        )
        
        if not file_path:
            return
            
        html_content = self.generate_html(with_styles=True)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return file_path
        except Exception as e:
            print(f"Export Error: {e}")
            return None

    def print_preview(self):
        """Önizlemeyi yazdırmak için tarayıcıda açar."""
        if not self.editor:
            return
            
        try:
            fd, path = tempfile.mkstemp(suffix=".html")
            
            raw_markdown = self.editor.text_area.get("1.0", "end-1c")
            content_html = self.convert_to_html(raw_markdown)
            
            # Print-friendly CSS
            print_css = """
                @media print {
                    body { margin: 2cm; }
                    .no-print { display: none; }
                }
            """
            
            html = self._create_html_document(content_html, extra_css=print_css, show_print_button=True)
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)
                
            webbrowser.open(f'file://{path}')
            return True
        except Exception as e:
            print(f"Print error: {e}")
            return False

    def open_in_browser(self):
        """Mevcut önizlemeyi tarayıcıda açar."""
        if not self.editor:
            return
            
        try:
            fd, path = tempfile.mkstemp(suffix=".html")
            html = self.generate_html(with_styles=True)
            
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)
                
            webbrowser.open(f'file://{path}')
            return True
        except Exception as e:
            print(f"Browser open error: {e}")
            return False

    def generate_html(self, with_styles=True):
        """Tam HTML dokümanını oluşturur."""
        raw_markdown = self.editor.text_area.get("1.0", "end-1c")
        content_html = self.convert_to_html(raw_markdown)
        return self._create_html_document(content_html, with_styles=with_styles)

    def _create_html_document(self, content, with_styles=True, extra_css="", show_print_button=False):
        colors = self.styler.colors
        
        styles = ""
        if with_styles:
            styles = f"""
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                color: {colors.get("fg", "#333")};
                background-color: {colors.get("bg", "#fff")};
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            pre {{
                background-color: {colors.get("code_bg", "#f5f5f5")};
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            code {{
                font-family: Consolas, 'Courier New', monospace;
                font-size: 0.9em;
                color: {colors.get("code_fg", "#d63384")};
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {colors.get("h1", "#000")};
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
            }}
            h1 {{ border-bottom: 1px solid {colors.get("hr", "#ccc")}; padding-bottom: 0.3em; }}
            blockquote {{
                border-left: 4px solid {colors.get("quote_border", "#ccc")};
                margin: 0;
                padding-left: 1em;
                color: {colors.get("quote_fg", "#666")};
                background-color: {colors.get("quote_bg", "#f9f9f9")};
            }}
            a {{ color: {colors.get("link", "#007bff")}; text-decoration: none; }}
            table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
            th, td {{ border: 1px solid {colors.get("table_border", "#ccc")}; padding: 6px 13px; }}
            th {{ background-color: {colors.get("table_header_bg", "#eee")}; }}
            img {{ max-width: 100%; }}
            {extra_css}
            """
            
        print_btn = ""
        if show_print_button:
            print_btn = """
            <div class="no-print" style="text-align: center; margin-bottom: 20px;">
                <button onclick="window.print()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                    🖨️ Yazdır
                </button>
            </div>
            """
            
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown</title>
    <style>{styles}</style>
</head>
<body>
    {print_btn}
    {content}
</body>
</html>"""

    def convert_to_html(self, text):
        """Basit Markdown -> HTML dönüştürücü."""
        lines = text.split('\n')
        html = []
        in_code = False
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Kod Blokları
            if stripped.startswith('```'):
                if in_code:
                    html.append("</pre>")
                    in_code = False
                else:
                    html.append("<pre><code>")
                    in_code = True
                i += 1
                continue
            
            if in_code:
                html.append(line.replace("<", "&lt;").replace(">", "&gt;"))
                i += 1
                continue
                
            # Başlıklar
            if stripped.startswith('#'):
                level = len(stripped.split()[0])
                content = stripped[level:].strip()
                html.append(f"<h{level}>{content}</h{level}>")
                i += 1
                continue
                
            # Yatay Çizgi
            if set(stripped) <= set('-*_') and len(stripped) >= 3:
                html.append("<hr>")
                i += 1
                continue
                
            # Alıntılar
            if stripped.startswith('>'):
                content = stripped[1:].strip()
                html.append(f"<blockquote>{content}</blockquote>")
                i += 1
                continue
                
            # Listeler
            if stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('+ '):
                content = stripped[2:].strip()
                html.append(f"<li>{content}</li>")
                i += 1
                continue
                
            # Tablolar
            if '|' in stripped and len(stripped) > 2:
                if not in_table:
                    html.append("<table>")
                    in_table = True
                
                cells = [c.strip() for c in stripped.split('|') if c.strip()]
                row_html = "<tr>"
                tag = "th" if i == 0 else "td" # Simple heuristic
                
                # Skip separator
                if '---' in stripped:
                    i += 1
                    continue
                    
                for cell in cells:
                    row_html += f"<{tag}>{cell}</{tag}>"
                row_html += "</tr>"
                html.append(row_html)
                
                if i + 1 >= len(lines) or '|' not in lines[i+1]:
                    html.append("</table>")
                    in_table = False
                i += 1
                continue
                
            # Paragraf
            if stripped:
                content = line
                content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
                content = re.sub(r'\*(.+?)\*', r'<i>\1</i>', content)
                content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
                content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
                html.append(f"<p>{content}</p>")
            else:
                html.append("<br>")
                
            i += 1
            
        return "\n".join(html)
