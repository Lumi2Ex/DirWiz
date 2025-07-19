import json, os

# Save and load rules from a JSON file
RULES_FILE = "rules.json"

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

def load_rules():
    if os.path.exists(RULES_FILE) and os.path.getsize(RULES_FILE) > 0:
        with open(RULES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Invalid JSON. Starting with empty rules.")
                # Reset the file and return empty dict
                with open(RULES_FILE, "w") as reset_f:
                    json.dump({}, reset_f)
                return {}
    else:
        # Create an empty rules file if it doesn't exist
        with open(RULES_FILE, "w") as f:
            json.dump({}, f)
        return {}