import threading
import os
from customtkinter import *
from rules_utils import load_rules, save_rules
from threading import Thread
from watcher_start import start_watchers

set_appearance_mode("System")  # Modes: system (default), light, dark
set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = CTk()  # create CTk window like you do with the Tk window
app.title("DirWiz")
app.geometry("660x480")
app.wm_minsize(720, 480)

rules_frame = CTkFrame(master=app)
rules_frame.pack(padx=20, pady=20, fill="both", expand=True)

def is_valid_directory(path):
    return os.path.isdir(path)

def quit_window(widget):
    file_queue.put(None)  # Sentinel to tell move_matching_files to exit
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

def add_rule(rule_type, rule, destination, directory):
    rule = rule.get()
    directory = directory.get()
    destination = destination.get()
    print(f"Rule: {rule}, Destination: {destination} Directory: {directory}")
    rule_id = f"Rule {len(rules) + 1}"
    rules[rule_id] = {
        "rule_type": rule_type,
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

from file_mover import find_matching_files, move_matching_files, file_queue

def start_finding():
    rules = load_rules()
    for rule in rules.values():
        base_dir = rule['directory']
        user_input = rule['rule']
        rule_type = rule['rule_type']
        thread = threading.Thread(target=find_matching_files, args=(base_dir, rule_type, user_input), daemon=True)
        thread.start()

def start_moving():
    thread = threading.Thread(target=move_matching_files, daemon=True)
    thread.start()

# Adding rules window
def popup():
    add_rule_app = CTkToplevel(app)
    add_rule_app.geometry("660x480")
    add_rule_app.title("Rule Creation")
    add_rule_app.lift()
    add_rule_app.focus_force()
    add_rule_app.grab_set()

    desc1 = CTkLabel(master=add_rule_app, text="Where should DirWiz search ?")
    directory_entry = CTkEntry(master=add_rule_app, placeholder_text="ex : C:/, C:/Users/user/Downloads ...")

    desc2 = CTkLabel(master=add_rule_app, text="What rule type do you want?")
    rule_type_entry = CTkComboBox(master=add_rule_app, state="readonly",values=[
        "contains", "creation date", "modification date",
        "file length (music/video)", "longer than", "shorter than",
        "file size", "file resolution (image/video)"
    ])

    dynamic_frame = CTkFrame(master=add_rule_app)

    desc4 = CTkLabel(master=add_rule_app, text="Where Should DirWiz move your file(s)")
    destination_entry = CTkEntry(master=add_rule_app, placeholder_text="C:/Users/user/Images")

    # Dynamic Update Function 
    def rule_type_change():
        for widget in dynamic_frame.winfo_children():
            widget.destroy()

        rule_type = rule_type_entry.get()

        # Logic map
        placeholder_map = {
            "contains": ("What should DirWiz search for?", "ex : .exe, .gif, .png"),
            "creation date": ("When was the file created? (YYYY-MM-DD)", "ex : 2022-01-01"),
            "modification date": ("When was the file modified? (YYYY-MM-DD)", "ex : 2022-01-01"),
            "file length (music/video)": ("How long should the file be (in seconds)?", "ex : 100000"),
            "longer than": ("Minimum length (in seconds)", "ex : 100000"),
            "shorter than": ("Maximum length (in seconds)", "ex : 100000"),
            "file size": ("File size (in ko)", "ex : 10000"),
            "file resolution (image/video)": ("Resolution (pixels)", "ex : 1920x1080")
        }

        desc_text, placeholder = placeholder_map.get(rule_type, ("Enter rule parameter:", ""))

        desc3 = CTkLabel(master=dynamic_frame, text=desc_text)
        rule_entry = CTkEntry(master=dynamic_frame, placeholder_text=placeholder)

        desc3.pack()
        rule_entry.pack()

        # Store for use in Validate
        dynamic_frame.rule_entry = rule_entry

    error_msg = None

    def on_validate():
        nonlocal error_msg  # Access the outer variable

        rule_type = rule_type_entry.get()
        rule_value = dynamic_frame.rule_entry.get()
        directory = directory_entry.get()
        destination = destination_entry.get()

        # Show error if any field is empty
        if not rule_type or not rule_value or not directory or not destination:
            if error_msg is None or not error_msg.winfo_exists():
                error_msg = CTkLabel(master=add_rule_app, text="All fields are required", text_color="red")
                error_msg.pack(pady=5)

        elif not is_valid_directory(directory) and not is_valid_directory(destination):
            if error_msg is None or not error_msg.winfo_exists():
                error_msg = CTkLabel(master=add_rule_app, text="Directories are not valid", text_color="red")
                error_msg.pack(pady=5)

        else:
            # Use your existing add_rule logic
            rule_entry_mock = CTkEntry(master=add_rule_app)
            rule_entry_mock.insert(0, f"{rule_value}")
            directory_entry_mock = CTkEntry(master=add_rule_app)
            directory_entry_mock.insert(0, directory)
            destination_entry_mock = CTkEntry(master=add_rule_app)
            destination_entry_mock.insert(0, destination)

            add_rule(rule_type, rule_entry_mock, destination_entry_mock, directory_entry_mock)
            add_rule_app.destroy()

    # Layout
    desc1.pack(pady=5)
    directory_entry.pack(pady=5)
    desc2.pack(pady=5)
    rule_type_entry.pack(pady=5)
    dynamic_frame.pack(pady=10, fill="x", expand=True)
    desc4.pack(pady=5)
    destination_entry.pack(pady=5)

    rule_type_entry.configure(command=rule_type_change)

    rule_type_entry.set("contains")
    rule_type_change()  # Call initially to set up the dynamic frame

    add_btn = CTkButton(master=add_rule_app, text="Validate", command=on_validate)
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