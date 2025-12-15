import platform
import sys
import time
import threading

class PerformanceMonitor:
    """
    Sistem ve uygulama performans metriklerini toplayan yardımcı sınıf.
    Psutil kütüphanesini opsiyonel olarak kullanır.
    """
    
    @staticmethod
    def get_editor_stats(app_instance):
        """Editör istatistiklerini hesaplar."""
        from collections import Counter
        
        tab_count = len(app_instance.tab_manager.editors)
        total_lines = 0
        total_chars = 0
        file_types = Counter()
        
        for name, editor in app_instance.tab_manager.editors.items():
            try:
                # Satır ve karakter sayıları
                # Text widget'tan index alma
                index = editor.text_area.index("end-1c")
                if index:
                    lines = int(index.split('.')[0])
                    total_lines += lines
                    total_chars += len(editor.text_area.get("1.0", "end-1c"))
                
                # Dosya türü analizi
                ext = name.split('.')[-1] if '.' in name else 'txt'
                file_types[ext] += 1
            except Exception:
                pass
                
        top_languages = file_types.most_common(3)
        languages_str = ", ".join([f".{ext} ({count})" for ext, count in top_languages]) if top_languages else "Bilinmiyor"

        return {
            "tab_count": tab_count,
            "total_lines": total_lines,
            "total_chars": total_chars,
            "languages_str": languages_str,
            "file_types": file_types # Raw counter if needed
        }

    @staticmethod
    def get_system_info():
        return f"{platform.system()} {platform.release()} ({platform.machine()})"

    @staticmethod
    def get_python_version():
        return sys.version.split()[0]

    @staticmethod
    def get_memory_usage():
        """Bellek kullanımını MB cinsinden döndürür (varsa psutil, yoksa native fallback)."""
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        try:
            import psutil
            process = psutil.Process()
            mem = process.memory_info()
            return f"{mem.rss / 1024 / 1024:.1f} MB"
        except ImportError:
            return PerformanceMonitor._get_memory_usage_fallback()
        except Exception:
            return lang.get("messages.unknown")

    @staticmethod
    def _get_memory_usage_fallback():
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        if platform.system() == "Windows":
            try:
                import ctypes
                from ctypes import wintypes
                import os
                
                class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
                    _fields_ = [
                        ('cb', wintypes.DWORD),
                        ('PageFaultCount', wintypes.DWORD),
                        ('PeakWorkingSetSize', ctypes.c_size_t),
                        ('WorkingSetSize', ctypes.c_size_t),
                        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                        ('QuotaPagedPoolUsage', ctypes.c_size_t),
                        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                        ('PagefileUsage', ctypes.c_size_t),
                        ('PeakPagefileUsage', ctypes.c_size_t),
                        ('PrivateUsage', ctypes.c_size_t),
                    ]
                
                # PROCESS_QUERY_LIMITED_INFORMATION (0x1000) | PROCESS_VM_READ (0x0010)
                hProcess = ctypes.windll.kernel32.OpenProcess(0x1010, False, os.getpid())
                
                if hProcess:
                    counters = PROCESS_MEMORY_COUNTERS_EX()
                    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
                    
                    if ctypes.windll.psapi.GetProcessMemoryInfo(hProcess, ctypes.byref(counters), ctypes.sizeof(counters)):
                        val = f"{counters.WorkingSetSize / 1024 / 1024:.1f} MB"
                        ctypes.windll.kernel32.CloseHandle(hProcess)
                        return val
                    ctypes.windll.kernel32.CloseHandle(hProcess)
            except Exception:
                pass
        return lang.get("messages.unknown")

    @staticmethod
    def get_cpu_usage():
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        try:
            import psutil
            process = psutil.Process()
            # interval=None non-blocking çağrıdır, ilk çağrı 0 dönebilir veya son çağrıdan farkı.
            cpu_val = process.cpu_percent(interval=None)
            return f"%{cpu_val:.1f}"
        except Exception:
            return lang.get("messages.unknown_psutil")

    @staticmethod
    def get_thread_count():
        try:
            import psutil
            process = psutil.Process()
            return str(process.num_threads())
        except (ImportError, Exception):
            return str(threading.active_count())

    @staticmethod
    def get_uptime_str():
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        try:
            import psutil
            process = psutil.Process()
            create_time = process.create_time()
            uptime_seconds = time.time() - create_time
        except (ImportError, Exception):
            # Fallback: Bunu tam olarak bilmemiz zor eğer app başlangıcını kaydetmediysek.
            # Ancak basitlik için burada "Hesaplanamadı" diyoruz.
            return lang.get("messages.calculation_failed")
            
        return PerformanceMonitor._format_duration(uptime_seconds)

    @staticmethod
    def _format_duration(seconds):
        from text_editor.utils.language_manager import LanguageManager
        lang = LanguageManager.get_instance()
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        h_str = lang.get("messages.time_h")
        m_str = lang.get("messages.time_m")
        s_str = lang.get("messages.time_s")
        return f"{int(h)}{h_str} {int(m)}{m_str} {int(s)}{s_str}"
