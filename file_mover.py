from pathlib import Path
import shutil
from rules_utils import load_rules

results = []

def find_matching_files(base_dir: str, user_input: str):
    while True:
        base = Path(base_dir)
        user_input = user_input.strip().lower()

        for file_s in base.rglob("*"):
            if file_s.is_file() and user_input in file_s.name.lower():
                results.append(file_s)

def move_matching_files():
    while True:
        rules = load_rules()
        if not rules:
            print("No rules found")
            return

        for file in results:
            for rule_id, rule_data in rules.items():
                if rule_data['rule'].lower() in file.name.lower():
                    destination = Path(rule_data['destination'])
                    destination.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(destination / file.name))
                    print(f"Moved {file.name} to {destination}")
                    break
        results.clear()
