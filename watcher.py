from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import shutil

from file_mover import move_matching_files


class RuleWatcher(FileSystemEventHandler):
    def __init__(self, rule_data):
        self.rule = rule_data['rule'].lower()
        self.dest = Path(rule_data['destination'])
        self.dest.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if not event.is_directory:
            path = Path(event.src_path)
            if self.rule in path.name.lower():
                shutil.move(str(path), str(self.dest / path.name))
                print(f"[Watcher] Moved {path.name} → {self.dest}")