from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class FileMonitor:
    def __init__(self, callback):
        self.observer = Observer()
        self.callback = callback
        self.watched_files = {} # yol -> izleyici
        self.observer.start()

    def add_file(self, file_path):
        directory = os.path.dirname(file_path)
        if not directory: return 

        # Dizin izlemeyi kontrol et?
        # Watchdog dizinleri izler.
        # Biz sadece olay içeriğini işleyebiliriz.
        
        # Basit yaklaşım: Dizini recursive=False izle
        if directory not in self.watched_files:
            handler = FileChangeHandler(self.on_file_changed)
            watch = self.observer.schedule(handler, directory, recursive=False)
            self.watched_files[directory] = watch
    
    def on_file_changed(self, src_path):
        # Ana geri çağrıya ilet
        self.callback(src_path)

    def stop(self):
        self.observer.stop()
        self.observer.join()
