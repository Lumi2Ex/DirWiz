import threading

from customtkinter import *
from file_mover import move_matching_files, find_matching_files
from rules_utils import load_rules, save_rules
from threading import Thread
from watcher_start import start_watchers

set_appearance_mode("System")  # Modes: system (default), light, dark
set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = CTk()  # create CTk window like you do with the Tk window
app.geometry("660x480")
app.wm_minsize(720, 480)

rules_frame = CTkFrame(master=app)
rules_frame.pack(padx=20, pady=20, fill="both", expand=True)

def quit_window(widget):
    toplevel = widget.winfo_toplevel()
    toplevel.destroy()

def display_rules():
    for widget in rules_frame.winfo_children():
        widget.destroy()  # clear previous labels if updating

    for i, (rule_name, rule_data) in enumerate(rules.items(), start=1):
        text = f"{rule_name}: Search for '{rule_data['rule']}' in '{rule_data['directory']}' and move it to {rule_data['destination']}"
        row = CTkFrame(master=rules_frame)
        row.pack(fill="x", padx=10, pady=5)
        label = CTkLabel(master=row, text=text, anchor="w")
        label.pack(side="left", fill="x", expand=True)
        #deletion handler
        delete_btn = CTkButton(master=row, text="Delete", width=60, command=lambda r=rule_name: delete_rule(r))
        delete_btn.pack(side="right", padx=5)

def add_rule(rule, destination, directory):
    rule = rule.get()
    directory = directory.get()
    destination = destination.get()
    print(f"Rule: {rule}, Destination: {destination} Directory: {directory}")
    rule_id = f"Rule {len(rules) + 1}"
    rules[rule_id] = {
        "rule": rule,
        "destination": destination,
        "directory": directory
    }
    save_rules(rules)
    display_rules()

    return {}
def delete_rule(rule_id):
    if rule_id in rules:
        del rules[rule_id]
        save_rules(rules)
        display_rules()

rules = load_rules()

def start_finding():
    thread = threading.Thread(target=find_matching_files, daemon=True)
    thread.start()
def start_moving():
    thread = threading.Thread(target=move_matching_files, daemon=True)
    thread.start()

# Adding rules window
def popup():
    add_rule_app = CTkToplevel(app)
    add_rule_app.geometry("660x480")
    add_rule_app.title("Rule Creation")
    # Entries for the rule
    desc1 = CTkLabel(master=add_rule_app, text="Where should DirWiz search ?")
    directory_entry = CTkEntry(master=add_rule_app, placeholder_text="ex : C:/, C:/Users/user/Downloads ...")
    desc2 = CTkLabel(master=add_rule_app, text="What should DirWiz search for ?")
    rule_entry = CTkEntry(master=add_rule_app, placeholder_text="ex : .exe, .jpg ...")
    desc3 = CTkLabel(master=add_rule_app, text="Where Should DirWiz move your file(s)")
    destination_entry = CTkEntry(master=add_rule_app, placeholder_text="C:/Users/user/Images")
    desc1.pack()
    directory_entry.pack()
    desc2.pack()
    rule_entry.pack()
    desc3.pack()
    destination_entry.pack()

    # add rule button
    add_btn = CTkButton(master=add_rule_app, text="Validate", command=lambda: add_rule(rule_entry, destination_entry, directory_entry))
    add_btn.pack(pady=20)

# Main window
button = CTkButton(master=app, text="Add Rule", command=popup)
button.pack(pady=20)
display_rules()
start_finding()
start_moving()

watcher_thread = Thread(target=start_watchers, daemon=True)
watcher_thread.start()
app.mainloop()