import re

def auto_link_urls(text):
    """Metindeki URL'leri otomatik olarak linkleştirir."""
    # Zaten markdown link formatında olanları atla
    if re.search(r'\[.+?\]\(.+?\)', text):
        return text
    
    # URL pattern
    url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
    
    def replace_url(match):
        url = match.group(1)
        # www ile başlıyorsa http ekle
        full_url = url if url.startswith('http') else f'http://{url}'
        return f'[{url}]({full_url})'
    
    return re.sub(url_pattern, replace_url, text)

def load_emoji_map():
    """Yaygın emoji kısayollarını yükler."""
    return {
        ":smile:": "😊", ":heart:": "❤️", ":thumbsup:": "👍", ":fire:": "🔥",
        ":star:": "⭐", ":check:": "✅", ":x:": "❌", ":warning:": "⚠️",
        ":info:": "ℹ️", ":rocket:": "🚀", ":tada:": "🎉", ":sparkles:": "✨",
        ":bulb:": "💡", ":book:": "📚", ":memo:": "📝", ":link:": "🔗",
        ":lock:": "🔒", ":key:": "🔑", ":mag:": "🔍", ":bell:": "🔔",
        ":eyes:": "👀", ":thinking:": "🤔", ":wave:": "👋", ":clap:": "👏",
    }

def replace_emoji_shortcuts(text, emoji_map):
    """Metindeki emoji kısayollarını gerçek emoji'lerle değiştirir."""
    for shortcut, emoji in emoji_map.items():
        text = text.replace(shortcut, emoji)
    return text
