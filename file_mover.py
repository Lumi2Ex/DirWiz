from pathlib import Path
import shutil
from rules_utils import load_rules
from queue import Queue
from moviepy import VideoFileClip, AudioFileClip
from PIL import Image

def get_image_resolution(filepath):
    with Image.open(filepath) as img:
        return img.width, img.height

def get_video_resolution(filepath):
    clip = VideoFileClip(filepath)
    width, height = clip.size  # tuple (width, height)
    clip.close()
    return width, height

def get_file_type(filepath):
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.mpeg'}

    ext = filepath.lower().rsplit('.', 1)[-1]
    ext = '.' + ext if not ext.startswith('.') else ext

    if ext in image_exts:
        return "image"
    elif ext in video_exts:
        return "video"
    else:
        return "unknown"

def get_media_length(filepath):
    try:
        if filepath.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            clip = VideoFileClip(filepath)
            duration = clip.duration  # duration in seconds (float)
            clip.close()
        elif filepath.lower().endswith(('.mp3', '.wav', '.aac', '.flac')):
            clip = AudioFileClip(filepath)
            duration = clip.duration  # duration in seconds (float)
            clip.close()
        else:
            duration = None
        return duration
    except Exception:
        return None


file_queue = Queue()
def find_matching_files(base_dir: str, rule_type: str, user_input: str):
    base = Path(base_dir)
    rule_type = rule_type.lower()
    user_input = user_input.strip().lower()

    for file_s in base.rglob("*"):
        if rule_type == "contains":
            if file_s.is_file() and user_input in file_s.name.lower():
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "creation date":
            if file_s.is_file() and file_s.stat().st_ctime >= user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "modification date":
            if file_s.is_file() and file_s.stat().st_mtime >= user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "file size":
            if file_s.is_file() and file_s.stat().st_size == user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "longer than":
            duration = get_media_length(file_s)
            if duration is not None and duration >= user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "shorter than":
            duration = get_media_length(file_s)
            if duration is not None and duration <= user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")
        elif rule_type == "file resolution":
            resolution = get_image_resolution(file_s)
            file_type = get_file_type(file_s)
            if file_type == "image" or file_type == "video" and resolution == user_input:
                file_queue.put(file_s)
                print(f"Queued: {file_s}")




def move_matching_files():
    rules = load_rules()
    if not rules:
        print("No rules found")
        return

    while True:
        file = file_queue.get()
        if file is None:
            break  # Sentinel value to exit

        if not file.exists():
            print(f"File no longer exists: {file}")
            continue

        for rule_id, rule_data in rules.items():
            if rule_data['rule'].lower() in file.name.lower():
                destination = Path(rule_data['destination'])
                destination.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(destination / file.name))
                print(f"Moved {file.name} to {destination}")
                break

        file_queue.task_done()