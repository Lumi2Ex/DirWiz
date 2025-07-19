# watcher_start.py
from watchdog.observers import Observer
from rules_utils import load_rules
from watcher import RuleWatcher
import time


def start_watchers():
    rules = load_rules()
    observers = []

    for rule_data in rules.values():
        directory = rule_data['directory']
        handler = RuleWatcher(rule_data)
        obs = Observer()
        obs.schedule(handler, path=directory, recursive=True)
        obs.start()
        observers.append(obs)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()