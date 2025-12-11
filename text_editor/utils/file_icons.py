"""
Dosya türleri için emoji ikonları ve renk şemaları.
Kapsamlı dosya uzantısı desteği.
"""

class FileIcons:
    """
    Dosya türlerine göre emoji ikonları ve bilgileri sağlar.
    """
    
    # Dosya türü kategorileri ve ikonları
    ICONS = {
        # Programlama Dilleri
        ".py": {"icon": "🐍", "type": "Python", "color": "#3776ab"},
        ".pyw": {"icon": "🐍", "type": "Python", "color": "#3776ab"},
        ".pyi": {"icon": "🐍", "type": "Python Interface", "color": "#3776ab"},
        
        ".js": {"icon": "📜", "type": "JavaScript", "color": "#f7df1e"},
        ".jsx": {"icon": "⚛️", "type": "React JSX", "color": "#61dafb"},
        ".mjs": {"icon": "📜", "type": "JavaScript Module", "color": "#f7df1e"},
        
        ".ts": {"icon": "🔷", "type": "TypeScript", "color": "#3178c6"},
        ".tsx": {"icon": "⚛️", "type": "React TSX", "color": "#3178c6"},
        
        ".java": {"icon": "☕", "type": "Java", "color": "#007396"},
        ".class": {"icon": "☕", "type": "Java Class", "color": "#007396"},
        ".jar": {"icon": "📦", "type": "Java Archive", "color": "#007396"},
        
        ".cpp": {"icon": "⚙️", "type": "C++", "color": "#00599c"},
        ".cc": {"icon": "⚙️", "type": "C++", "color": "#00599c"},
        ".cxx": {"icon": "⚙️", "type": "C++", "color": "#00599c"},
        ".c": {"icon": "©️", "type": "C", "color": "#555555"},
        ".h": {"icon": "📋", "type": "C/C++ Header", "color": "#555555"},
        ".hpp": {"icon": "📋", "type": "C++ Header", "color": "#00599c"},
        
        ".cs": {"icon": "#️⃣", "type": "C#", "color": "#239120"},
        
        ".php": {"icon": "🐘", "type": "PHP", "color": "#777bb4"},
        
        ".rb": {"icon": "💎", "type": "Ruby", "color": "#cc342d"},
        
        ".go": {"icon": "🦫", "type": "Go", "color": "#00add8"},
        
        ".rs": {"icon": "🦀", "type": "Rust", "color": "#ce422b"},
        
        ".swift": {"icon": "🕊️", "type": "Swift", "color": "#fa7343"},
        
        ".kt": {"icon": "🅺", "type": "Kotlin", "color": "#7f52ff"},
        ".kts": {"icon": "🅺", "type": "Kotlin Script", "color": "#7f52ff"},
        
        ".scala": {"icon": "🔺", "type": "Scala", "color": "#dc322f"},
        
        ".r": {"icon": "📊", "type": "R", "color": "#276dc3"},
        
        ".lua": {"icon": "🌙", "type": "Lua", "color": "#000080"},
        
        ".pl": {"icon": "🐪", "type": "Perl", "color": "#39457e"},
        ".pm": {"icon": "🐪", "type": "Perl Module", "color": "#39457e"},
        
        ".sh": {"icon": "🐚", "type": "Shell Script", "color": "#89e051"},
        ".bash": {"icon": "🐚", "type": "Bash Script", "color": "#89e051"},
        ".zsh": {"icon": "🐚", "type": "Zsh Script", "color": "#89e051"},
        
        ".bat": {"icon": "⚡", "type": "Batch File", "color": "#c1c1c1"},
        ".cmd": {"icon": "⚡", "type": "Command File", "color": "#c1c1c1"},
        
        ".ps1": {"icon": "💠", "type": "PowerShell", "color": "#012456"},
        
        # Web Teknolojileri
        ".html": {"icon": "🌐", "type": "HTML", "color": "#e34c26"},
        ".htm": {"icon": "🌐", "type": "HTML", "color": "#e34c26"},
        
        ".css": {"icon": "🎨", "type": "CSS", "color": "#1572b6"},
        ".scss": {"icon": "🎨", "type": "SCSS", "color": "#cc6699"},
        ".sass": {"icon": "🎨", "type": "Sass", "color": "#cc6699"},
        ".less": {"icon": "🎨", "type": "Less", "color": "#1d365d"},
        
        ".vue": {"icon": "💚", "type": "Vue", "color": "#42b883"},
        
        ".svelte": {"icon": "🔥", "type": "Svelte", "color": "#ff3e00"},
        
        # Veri Formatları
        ".json": {"icon": "📋", "type": "JSON", "color": "#000000"},
        ".jsonc": {"icon": "📋", "type": "JSON with Comments", "color": "#000000"},
        
        ".xml": {"icon": "📰", "type": "XML", "color": "#0060ac"},
        
        ".yaml": {"icon": "📄", "type": "YAML", "color": "#cb171e"},
        ".yml": {"icon": "📄", "type": "YAML", "color": "#cb171e"},
        
        ".toml": {"icon": "⚙️", "type": "TOML", "color": "#9c4121"},
        
        ".ini": {"icon": "🔧", "type": "INI Config", "color": "#6d6d6d"},
        ".cfg": {"icon": "🔧", "type": "Config", "color": "#6d6d6d"},
        ".conf": {"icon": "🔧", "type": "Config", "color": "#6d6d6d"},
        
        ".env": {"icon": "🌍", "type": "Environment", "color": "#ecd53f"},
        
        # Dokümantasyon
        ".md": {"icon": "📝", "type": "Markdown", "color": "#083fa1"},
        ".markdown": {"icon": "📝", "type": "Markdown", "color": "#083fa1"},
        
        ".txt": {"icon": "📄", "type": "Text", "color": "#89e051"},
        
        ".pdf": {"icon": "📕", "type": "PDF", "color": "#f40f02"},
        
        ".doc": {"icon": "📘", "type": "Word Document", "color": "#2b579a"},
        ".docx": {"icon": "📘", "type": "Word Document", "color": "#2b579a"},
        
        ".rtf": {"icon": "📃", "type": "Rich Text", "color": "#6d6d6d"},
        
        # Veritabanı
        ".sql": {"icon": "🗄️", "type": "SQL", "color": "#e38c00"},
        ".db": {"icon": "🗄️", "type": "Database", "color": "#003b57"},
        ".sqlite": {"icon": "🗄️", "type": "SQLite", "color": "#003b57"},
        ".sqlite3": {"icon": "🗄️", "type": "SQLite3", "color": "#003b57"},
        
        # Görsel Dosyalar
        ".png": {"icon": "🖼️", "type": "PNG Image", "color": "#8bc34a"},
        ".jpg": {"icon": "🖼️", "type": "JPEG Image", "color": "#8bc34a"},
        ".jpeg": {"icon": "🖼️", "type": "JPEG Image", "color": "#8bc34a"},
        ".gif": {"icon": "🎞️", "type": "GIF Image", "color": "#8bc34a"},
        ".svg": {"icon": "🎨", "type": "SVG", "color": "#ffb13b"},
        ".ico": {"icon": "🔷", "type": "Icon", "color": "#cbcb41"},
        ".webp": {"icon": "🖼️", "type": "WebP Image", "color": "#8bc34a"},
        ".bmp": {"icon": "🖼️", "type": "Bitmap", "color": "#8bc34a"},
        
        # Arşiv Dosyaları
        ".zip": {"icon": "📦", "type": "ZIP Archive", "color": "#9c5c2b"},
        ".rar": {"icon": "📦", "type": "RAR Archive", "color": "#9c5c2b"},
        ".7z": {"icon": "📦", "type": "7-Zip Archive", "color": "#9c5c2b"},
        ".tar": {"icon": "📦", "type": "TAR Archive", "color": "#9c5c2b"},
        ".gz": {"icon": "📦", "type": "GZip Archive", "color": "#9c5c2b"},
        ".bz2": {"icon": "📦", "type": "BZip2 Archive", "color": "#9c5c2b"},
        
        # Git
        ".gitignore": {"icon": "🚫", "type": "Git Ignore", "color": "#f05032"},
        ".gitattributes": {"icon": "📝", "type": "Git Attributes", "color": "#f05032"},
        
        # Paket Yöneticisi
        "package.json": {"icon": "📦", "type": "NPM Package", "color": "#cb3837"},
        "package-lock.json": {"icon": "🔒", "type": "NPM Lock", "color": "#cb3837"},
        "yarn.lock": {"icon": "🔒", "type": "Yarn Lock", "color": "#2c8ebb"},
        "requirements.txt": {"icon": "📋", "type": "Python Requirements", "color": "#3776ab"},
        "Pipfile": {"icon": "📋", "type": "Pipenv File", "color": "#3776ab"},
        "Gemfile": {"icon": "💎", "type": "Ruby Gemfile", "color": "#cc342d"},
        "Cargo.toml": {"icon": "📦", "type": "Rust Cargo", "color": "#ce422b"},
        "go.mod": {"icon": "📦", "type": "Go Module", "color": "#00add8"},
        
        # Derleme & Yapılandırma
        "Makefile": {"icon": "🔨", "type": "Makefile", "color": "#6d6d6d"},
        "CMakeLists.txt": {"icon": "🔨", "type": "CMake", "color": "#064f8d"},
        ".dockerfile": {"icon": "🐳", "type": "Dockerfile", "color": "#2496ed"},
        "Dockerfile": {"icon": "🐳", "type": "Dockerfile", "color": "#2496ed"},
        "docker-compose.yml": {"icon": "🐳", "type": "Docker Compose", "color": "#2496ed"},
        ".eslintrc": {"icon": "🔍", "type": "ESLint Config", "color": "#4b32c3"},
        ".prettierrc": {"icon": "✨", "type": "Prettier Config", "color": "#f7b93e"},
        "tsconfig.json": {"icon": "🔷", "type": "TypeScript Config", "color": "#3178c6"},
        
        # README & Lisans
        "README.md": {"icon": "📖", "type": "README", "color": "#083fa1"},
        "LICENSE": {"icon": "⚖️", "type": "License", "color": "#6d6d6d"},
        "LICENSE.md": {"icon": "⚖️", "type": "License", "color": "#6d6d6d"},
        
        # Günlük (Log) Dosyaları
        ".log": {"icon": "📊", "type": "Log File", "color": "#6d6d6d"},
        
        # Video & Ses
        ".mp4": {"icon": "🎬", "type": "MP4 Video", "color": "#ff6b6b"},
        ".avi": {"icon": "🎬", "type": "AVI Video", "color": "#ff6b6b"},
        ".mov": {"icon": "🎬", "type": "MOV Video", "color": "#ff6b6b"},
        ".mp3": {"icon": "🎵", "type": "MP3 Audio", "color": "#4ecdc4"},
        ".wav": {"icon": "🎵", "type": "WAV Audio", "color": "#4ecdc4"},
        ".flac": {"icon": "🎵", "type": "FLAC Audio", "color": "#4ecdc4"},
    }
    
    # Varsayılan ikonlar
    DEFAULT_FILE = {"icon": "📄", "type": "File", "color": "#6d6d6d"}
    DEFAULT_FOLDER = {"icon": "📁", "type": "Folder", "color": "#90a4ae"}
    DEFAULT_CODE = {"icon": "💻", "type": "Code", "color": "#89e051"}
    
    @classmethod
    def get_icon(cls, filename):
        """
        Dosya adından emoji ikonunu döndürür.
        
        Args:
            filename: Dosya adı veya yolu
            
        Returns:
            str: Emoji ikonu
        """
        if not filename:
            return cls.DEFAULT_FILE["icon"]
        
        # Tam dosya adı kontrolü (örn: package.json, Dockerfile)
        if filename in cls.ICONS:
            return cls.ICONS[filename]["icon"]
        
        # Uzantı kontrolü
        import os
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in cls.ICONS:
            return cls.ICONS[ext]["icon"]
        
        # Varsayılan
        return cls.DEFAULT_FILE["icon"]
    
    @classmethod
    def get_type(cls, filename):
        """
        Dosya adından tür açıklamasını döndürür.
        
        Args:
            filename: Dosya adı veya yolu
            
        Returns:
            str: Dosya türü açıklaması
        """
        if not filename:
            return cls.DEFAULT_FILE["type"]
        
        # Tam dosya adı kontrolü
        if filename in cls.ICONS:
            return cls.ICONS[filename]["type"]
        
        # Uzantı kontrolü
        import os
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in cls.ICONS:
            return cls.ICONS[ext]["type"]
        
        # Varsayılan
        return cls.DEFAULT_FILE["type"]
    
    @classmethod
    def get_color(cls, filename):
        """
        Dosya adından renk kodunu döndürür.
        
        Args:
            filename: Dosya adı veya yolu
            
        Returns:
            str: Hex renk kodu
        """
        if not filename:
            return cls.DEFAULT_FILE["color"]
        
        # Tam dosya adı kontrolü
        if filename in cls.ICONS:
            return cls.ICONS[filename]["color"]
        
        # Uzantı kontrolü
        import os
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in cls.ICONS:
            return cls.ICONS[ext]["color"]
        
        # Varsayılan
        return cls.DEFAULT_FILE["color"]
    
    @classmethod
    def get_info(cls, filename):
        """
        Dosya adından tüm bilgileri döndürür.
        
        Args:
            filename: Dosya adı veya yolu
            
        Returns:
            dict: {"icon": str, "type": str, "color": str}
        """
        if not filename:
            return cls.DEFAULT_FILE.copy()
        
        # Tam dosya adı kontrolü
        if filename in cls.ICONS:
            return cls.ICONS[filename].copy()
        
        # Uzantı kontrolü
        import os
        ext = os.path.splitext(filename.lower())[1]
        
        if ext in cls.ICONS:
            return cls.ICONS[ext].copy()
        
        # Varsayılan
        return cls.DEFAULT_FILE.copy()
    
    @classmethod
    def is_image(cls, filename):
        """Dosya bir görsel mi?"""
        ext = os.path.splitext(filename.lower())[1] if filename else ""
        return ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp"]
    
    @classmethod
    def is_video(cls, filename):
        """Dosya bir video mu?"""
        ext = os.path.splitext(filename.lower())[1] if filename else ""
        return ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    
    @classmethod
    def is_audio(cls, filename):
        """Dosya bir ses dosyası mı?"""
        ext = os.path.splitext(filename.lower())[1] if filename else ""
        return ext in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
    
    @classmethod
    def is_archive(cls, filename):
        """Dosya bir arşiv mi?"""
        ext = os.path.splitext(filename.lower())[1] if filename else ""
        return ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]


import os
