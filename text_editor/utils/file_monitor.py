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
        self.watched_files = {} # path -> watch
        self.observer.start()

    def add_file(self, file_path):
        directory = os.path.dirname(file_path)
        if not directory: return 

        # We watch the directory because watching a single file is tricky in some OSs or editors that use swap files
        # However, watching the whole dir might be noisy. 
        # We will filter in the handler (which we are not doing robustly yet, but handler receives the path)
        
        # Check if we already watch this directory?
        # Watchdog watches directories.
        # We can just handle the event content.
        
        # Simple approach: Watch the directory recursively=False
        if directory not in self.watched_files:
            handler = FileChangeHandler(self.on_file_changed)
            watch = self.observer.schedule(handler, directory, recursive=False)
            self.watched_files[directory] = watch
    
    def on_file_changed(self, src_path):
        # Pass to main callback
        self.callback(src_path)

    def stop(self):
        self.observer.stop()
        self.observer.join()
