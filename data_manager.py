import json
import os
from urllib.request import urlopen, Request
from config import STUDENTS_URLS, get_students_path, get_custom_dict_path, get_save_path, get_icon_path, get_config_path, ICON_URL_TEMPLATE, MAX_SLOTS
from utils import dbg

def load_config_json():
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            dbg(f"load_config_json error: {e}")
    return None

def save_config_json(config):
    try:
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        dbg(f"save_config_json error: {e}")

def load_guides_json(current_slot, guide_slots):
    try:
        with open(get_save_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        for i, text in enumerate(data.get("slots", [])[:MAX_SLOTS]):
            guide_slots[i] = text or ""
        slot = int(data.get("current_slot", 0))
        if 0 <= slot < MAX_SLOTS:
            current_slot = slot
    except Exception: pass
    return current_slot, guide_slots

def save_guides_json(current_slot, guide_slots):
    try:
        with open(get_save_path(), "w", encoding="utf-8") as f:
            json.dump({"slots": list(guide_slots), "current_slot": current_slot},
                      f, ensure_ascii=False, indent=2)
    except Exception as e:
        dbg(f"save_guides_json error: {e}")

def load_custom_dict_local():
    path = get_custom_dict_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cd = json.load(f)
            dbg(f"custom_dict: loaded {len(cd)} entries")
            return cd
        except Exception as e:
            dbg(f"load_custom_dict error: {e}")
    return None

def save_custom_dict_local(custom_dict):
    try:
        with open(get_custom_dict_path(), "w", encoding="utf-8") as f:
            json.dump(custom_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        dbg(f"save_custom_dict error: {e}")

def load_all_students_local():
    path = get_students_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        if "students" in all_data and isinstance(all_data["students"], list):
            dbg("migrating old ba_students.json format to multi-lang")
            all_data = {"ko": all_data["students"]}
        return all_data
    except Exception as e:
        dbg(f"load_all_students_local error: {e}")
        return None

def save_all_students_local(all_local):
    try:
        with open(get_students_path(), "w", encoding="utf-8") as f:
            json.dump(all_local, f, ensure_ascii=False, indent=2)
    except Exception as e:
        dbg(f"save ba_students.json error: {e}")

def fetch_students_remote(lang, current_size):
    url = STUDENTS_URLS.get(lang)
    if not url: return None, current_size
    try:
        req = Request(url, headers={"User-Agent":"BATacticHelper/2"})
        with urlopen(req, timeout=10) as resp:
            remote_bytes = resp.read()
        remote_size = len(remote_bytes)
        if remote_size != current_size:
            raw = json.loads(remote_bytes.decode("utf-8"))
            students = [
                {"Id": v.get("Id"), "Name": v.get("Name",""), "SearchTags": v.get("SearchTags") or []}
                for v in raw.values()
            ]
            return students, remote_size
    except Exception as e:
        dbg(f"fetch_students_remote[{lang}] error: {e}")
    return None, current_size

def download_icon(student_id):
    try:
        url = ICON_URL_TEMPLATE.format(student_id)
        req = Request(url, headers={"User-Agent":"BATacticHelper/2"})
        with urlopen(req, timeout=8) as resp: data = resp.read()
        with open(get_icon_path(student_id), "wb") as f:
            f.write(data)
        return data
    except Exception as e:
        dbg(f"icon dl fail sid={student_id}: {e}")
        return None
