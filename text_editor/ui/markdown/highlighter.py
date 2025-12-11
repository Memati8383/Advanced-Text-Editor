import re

class MarkdownHighlighter:
    """Markdown kod blokları için basit sözdizimi renklendirme."""
    
    def __init__(self, text_widget, styler):
        self.text_widget = text_widget
        self.styler = styler
        self.keywords = {
            'python': ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 
                      'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'lambda',
                      'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False', 'self'],
            'javascript': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                          'return', 'class', 'extends', 'import', 'export', 'default', 'async',
                          'await', 'try', 'catch', 'finally', 'new', 'this', 'null', 'undefined',
                          'true', 'false'],
            'java': ['public', 'private', 'protected', 'class', 'interface', 'extends', 'implements',
                    'static', 'final', 'void', 'int', 'String', 'boolean', 'if', 'else', 'for',
                    'while', 'return', 'new', 'this', 'null', 'true', 'false'],
            'c': ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
                  'return', 'void', 'int', 'char', 'float', 'double', 'struct', 'typedef',
                  'const', 'static', 'extern', 'sizeof', 'NULL'],
            'cpp': ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
                   'return', 'void', 'int', 'char', 'float', 'double', 'class', 'public',
                   'private', 'protected', 'virtual', 'override', 'const', 'static', 'new',
                   'delete', 'nullptr', 'true', 'false', 'template', 'typename', 'namespace',
                   'using', 'std'],
            'html': ['html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'br', 'hr', 'a', 'img', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'script',
                    'style', 'link', 'meta', 'title', 'button', 'input', 'form', 'label'],
            'css': ['color', 'background', 'margin', 'padding', 'border', 'font', 'text', 'display',
                   'position', 'width', 'height', 'top', 'left', 'right', 'bottom', 'z-index',
                   'flex', 'grid', 'align', 'justify', 'media', 'import', 'important'],
            'sql': ['select', 'from', 'where', 'insert', 'update', 'delete', 'into', 'values',
                   'create', 'table', 'drop', 'alter', 'index', 'join', 'inner', 'left', 'right',
                   'on', 'group', 'by', 'order', 'limit', 'offset', 'having', 'as', 'distinct',
                   'count', 'sum', 'avg', 'max', 'min', 'null', 'not', 'and', 'or', 'like']
        }

    def highlight_line(self, line, lang):
        """Tek bir satıra sözdizimi renklendirmesi uygular."""
        lang_lower = lang.lower()
        if lang_lower in ['js', 'jsx', 'ts', 'tsx']:
            lang_lower = 'javascript'
        elif lang_lower in ['py', 'py3']:
            lang_lower = 'python'
            
        lang_keywords = self.keywords.get(lang_lower, self.keywords.get('python', []))
        
        remaining = line
        
        while remaining:
            # Yorum kontrolü
            comment_match = re.match(r'(#.*|//.*|/\*.*\*/)', remaining)
            if comment_match:
                self.text_widget.insert("end", comment_match.group(0), "code_comment")
                remaining = remaining[comment_match.end():]
                continue
            
            # String kontrolü
            string_match = re.match(r'(["\'])(?:(?!\1)[^\\]|\\.)*\1', remaining)
            if string_match:
                self.text_widget.insert("end", string_match.group(0), "code_string")
                remaining = remaining[string_match.end():]
                continue
            
            # Sayı kontrolü
            number_match = re.match(r'\b\d+\.?\d*\b', remaining)
            if number_match:
                self.text_widget.insert("end", number_match.group(0), "code_number")
                remaining = remaining[number_match.end():]
                continue
            
            # Fonksiyon kontrolü
            func_match = re.match(r'\b(\w+)\s*\(', remaining)
            if func_match:
                func_name = func_match.group(1)
                if func_name not in lang_keywords:
                    self.text_widget.insert("end", func_name, "code_function")
                    remaining = remaining[len(func_name):]
                    continue
            
            # Keyword kontrolü
            keyword_match = re.match(r'\b(' + '|'.join(map(re.escape, lang_keywords)) + r')\b', remaining)
            if keyword_match:
                self.text_widget.insert("end", keyword_match.group(0), "code_keyword")
                remaining = remaining[keyword_match.end():]
                continue
            
            # Sınıf isimleri (büyük harfle başlayan)
            class_match = re.match(r'\b([A-Z]\w*)\b', remaining)
            if class_match and class_match.group(1) not in lang_keywords:
                self.text_widget.insert("end", class_match.group(0), "code_class")
                remaining = remaining[class_match.end():]
                continue
            
            # Normal karakter
            self.text_widget.insert("end", remaining[0], "code_block")
            remaining = remaining[1:]
