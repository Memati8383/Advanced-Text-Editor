from text_editor.config import APP_NAME, SUPPORTED_FILES
from text_editor.utils.performance_monitor import PerformanceMonitor
from text_editor.utils.language_manager import LanguageManager
import time
import platform

class HelpContentProvider:
    """
    HelpContentProvider sınıfı, Yardım Merkezi için gerekli olan tüm metin içeriklerini sağlar.
    Statik ve dinamik içerikler burada ayrıştırılmıştır.
    """

    @staticmethod
    def get_quick_start():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.quick_start")

    @staticmethod
    def get_shortcuts():
        from text_editor.utils.shortcut_manager import ShortcutManager
        shortcuts = ShortcutManager.get_instance()
        fmt = shortcuts.get_display_string
        lang = LanguageManager.get_instance()
        
        template = lang.get("help_content.shortcuts")
        
        # Prepare formatting dictionary with current shortcuts
        format_map = {
            "new_tab": fmt(shortcuts.get("new_tab")),
            "open_file": fmt(shortcuts.get("open_file")),
            "open_folder": fmt(shortcuts.get("open_folder")),
            "save_file": fmt(shortcuts.get("save_file")),
            "save_as": fmt(shortcuts.get("save_as")),
            "close_tab": fmt(shortcuts.get("close_tab")),
            
            "undo": fmt(shortcuts.get("undo")),
            "redo": fmt(shortcuts.get("redo")),
            "cut": fmt(shortcuts.get("cut")),
            "copy": fmt(shortcuts.get("copy")),
            "paste": fmt(shortcuts.get("paste")),
            "select_all": fmt(shortcuts.get("select_all")),
            "find": fmt(shortcuts.get("find")),
            "goto_line": fmt(shortcuts.get("goto_line")),
            "duplicate_line": fmt(shortcuts.get("duplicate_line")),
            "move_line_up": fmt(shortcuts.get("move_line_up")),
            "move_line_down": fmt(shortcuts.get("move_line_down")),
            
            "zoom_reset": fmt(shortcuts.get("zoom_reset")),
            "toggle_fullscreen": fmt(shortcuts.get("toggle_fullscreen")),
            "toggle_file_explorer": fmt(shortcuts.get("toggle_file_explorer")),
            "toggle_minimap": fmt(shortcuts.get("toggle_minimap")),
            "toggle_line_numbers": fmt(shortcuts.get("toggle_line_numbers")),
            "toggle_word_wrap": fmt(shortcuts.get("toggle_word_wrap")),
            "toggle_terminal": fmt(shortcuts.get("toggle_terminal")),
            "preview_markdown": fmt(shortcuts.get("preview_markdown")),
            "toggle_zen_mode": fmt(shortcuts.get("toggle_zen_mode")),
            
            "copy_path": fmt(shortcuts.get("copy_path")),
            "copy_relative_path": fmt(shortcuts.get("copy_relative_path"))
        }

        try:
            return template.format(**format_map)
        except KeyError:
            return template # Fallback in case of missing keys in template

    @staticmethod
    def get_multi_cursor_guide():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.multi_cursor")

    @staticmethod
    def get_theme_guide():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.theme_guide")

    @staticmethod
    def get_tips_and_tricks():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.tips")

    @staticmethod
    def get_supported_formats():
        lang = LanguageManager.get_instance()
        template = lang.get("help_content.supported_formats")
        
        from text_editor.config import SUPPORTED_FILES
        # Format the list of files
        formats_list = []
        for name, ext in SUPPORTED_FILES:
             formats_list.append(f"   • {name}: {ext}")
        
        return template.format(formats="\n".join(formats_list))

    @staticmethod
    def get_faq():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.faq")

    @staticmethod
    def get_performance_report(app_instance):
        """Performans verilerini dinamik olarak çeker."""
        lang = LanguageManager.get_instance()
        
        # 1. Veril Toplama (Separation of Concerns)
        sys_info = PerformanceMonitor.get_system_info()
        py_ver = PerformanceMonitor.get_python_version()
        memory_usage = PerformanceMonitor.get_memory_usage()
        cpu_usage = PerformanceMonitor.get_cpu_usage()
        thread_count = PerformanceMonitor.get_thread_count()
        uptime_str = PerformanceMonitor.get_uptime_str()
        
        stats = PerformanceMonitor.get_editor_stats(app_instance)
        
        # 2. Öneriler Logic
        suggestions = []
        
        if stats["tab_count"] > 10:
            suggestions.append(lang.get("help_content.performance_suggestions.high_tab_count"))
        if stats["total_lines"] > 20000:
            suggestions.append(lang.get("help_content.performance_suggestions.high_line_count"))
            
        unknown_msg = lang.get("messages.unknown")
        # Hafıza kontrolü
        if not memory_usage.startswith(unknown_msg):
            try:
                # "23.5 MB" -> 23.5
                mem_val = float(memory_usage.split()[0])
                if mem_val > 500:
                    suggestions.append(lang.get("help_content.performance_suggestions.high_memory"))
            except ValueError:
                pass

        unknown_psutil_msg = lang.get("messages.unknown_psutil")
        if unknown_psutil_msg in cpu_usage:
             suggestions.append(lang.get("help_content.performance_suggestions.install_psutil"))

        if not suggestions:
            suggestions.append(lang.get("help_content.performance_suggestions.all_good"))
            
        suggestions_text = "\n".join(suggestions)
        current_theme = app_instance.settings.get("theme", "Dark")
        active_str = lang.get("messages.active")
        passive_str = lang.get("messages.passive")
        gpu_status = active_str if app_instance.settings.get("use_gpu", True) else passive_str

        # 3. View (Presentation) -> Use localized template
        template = lang.get("help_content.performance_report")
        
        return template.format(
            sys_info=sys_info,
            py_ver=py_ver,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            thread_count=thread_count,
            uptime_str=uptime_str,
            tab_count=stats['tab_count'],
            total_lines=f"{stats['total_lines']:,}",
            total_chars=f"{stats['total_chars']:,}",
            current_theme=current_theme,
            languages_str=stats['languages_str'],
            gpu_status=gpu_status,
            suggestions_text=suggestions_text,
            node=platform.node(),
            time=time.strftime('%Y-%m-%d %H:%M:%S')
        )

    @staticmethod
    def get_report_bug():
         lang = LanguageManager.get_instance()
         return lang.get("help_content.report_bug")

    @staticmethod
    def get_about():
        lang = LanguageManager.get_instance()
        template = lang.get("help_content.about")
        from text_editor.config import APP_NAME
        return template.format(app_name=APP_NAME)

    @staticmethod
    def get_markdown_guide():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.markdown_guide")

    @staticmethod
    def get_image_viewer_guide():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.image_viewer")

    @staticmethod
    def get_goto_line_guide():
        lang = LanguageManager.get_instance()
        return lang.get("help_content.goto_line")
