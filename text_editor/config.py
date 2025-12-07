
# Metin Editörü Yapılandırması

APP_NAME = "Memati Editör"
APP_SIZE = "1200x800"

# Yazı Tipleri
FONT_FAMILY = "Consolas"  # Kod için eşaralıklı yazı tipi
FONT_SIZE = 14

# Sözdizimi Vurgulama Stilleri (Yedek/Özel)
# Öncelikle Pygments stillerini kullanacağız, ancak burada geçersiz kılmalar tanımlanabilir.
THEME_MODE = "Dark"  # "System" (Sistem), "Dark" (Koyu), "Light" (Açık)
DEFAULT_THEME_COLOR = "blue"  # Temalar: "blue" (standart), "green" (yeşil), "dark-blue" (koyu mavi)

# Dosya Türleri
SUPPORTED_FILES = [
    ("All Files", "*.*"),
    ("Python", "*.py"),
    ("Text", "*.txt"),
    ("HTML", "*.html"),
    ("CSS", "*.css"),
    ("JavaScript", "*.js"),
    ("JSON", "*.json"),
    ("XML", "*.xml"),
    ("Markdown", "*.md"),
]
