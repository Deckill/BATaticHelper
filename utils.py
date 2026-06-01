import winreg
import re
from config import REG_PATH

DEBUG_ENABLED = False

def dbg(msg):
    if DEBUG_ENABLED:
        print(f"[DBG] {msg}", flush=True)

# -- 레지스트리 --
def set_registry(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
        winreg.CloseKey(key)
    except Exception: pass

def get_registry(name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key); return value
    except OSError: return None

# -- 파싱 유틸리티 --
def tokenize_line(line):
    tokens, i, current = [], 0, ""
    while i < len(line):
        ch = line[i]
        if ch in "([":
            close = ")" if ch == "(" else "]"
            if current:
                for part in _split_normal(current): tokens.append(part)
                current = ""
            j = i + 1
            while j < len(line) and line[j] != close: j += 1
            tokens.append((line[i:j+1], True))
            i = j + 1
        else:
            current += ch; i += 1
    if current:
        for part in _split_normal(current): tokens.append(part)
    return tokens

def _split_normal(text):
    return [(p, False) for p in re.split(r"(\s+)", text) if p]


# -- 학생 검색/매처 --

def _find_id_by_name(name, langs_data):
    for students in langs_data.values():
        for s in students:
            if s.get("Name") == name:
                return s.get("Id")
    return None


def build_matcher(all_students_by_lang, custom_dict, custom_skills=None):
    if isinstance(all_students_by_lang, list):
        langs_data = {"_compat": all_students_by_lang}
    else:
        langs_data = all_students_by_lang

    def resolve_name(name, depth=0):
        if depth > 5: return name
        if name in custom_dict:
            return resolve_name(custom_dict[name], depth + 1)
        return name

    entries = []

    if custom_skills:
        for sk in custom_skills:
            if sk: entries.append((sk, f"CUSTOM_SKILL:{sk}", -1))

    for alias, raw_target in custom_dict.items():
        final_name = resolve_name(raw_target)
        sid = _find_id_by_name(final_name, langs_data)
        if sid is not None:
            entries.append((alias, sid, 0))

    for students in langs_data.values():
        for s in students:
            sid  = s.get("Id")
            name = s.get("Name", "")
            tags = s.get("SearchTags") or []
            if isinstance(tags, str): tags = [tags]
            for tag in tags:
                if tag: entries.append((tag, sid, 1))
            if name: entries.append((name, sid, 2))

    seen = {}
    for kw, sid, pri in entries:
        if kw not in seen or pri < seen[kw][1]:
            seen[kw] = (sid, pri)

    result = [(kw, sid, pri) for kw, (sid, pri) in seen.items()]
    result.sort(key=lambda x: (-len(x[0]), x[2]))
    total = sum(len(v) for v in langs_data.values())
    dbg("build_matcher: " + str(len(result)) + " entries from " + str(total) + " students across " + str(len(langs_data)) + " lang(s)")
    return result


def search_students_by_name(query, all_students_by_lang, max_results=8):
    query_lower = query.lower()
    seen_ids = set()
    results = []
    for lang, students in all_students_by_lang.items():
        for s in students:
            sid  = s.get("Id")
            name = s.get("Name", "")
            tags = s.get("SearchTags") or []
            if isinstance(tags, str): tags = [tags]
            matched = (query_lower in name.lower() or
                       any(query_lower in t.lower() for t in tags if t))
            if matched and sid not in seen_ids:
                seen_ids.add(sid)
                results.append({"Id": sid, "Name": name, "display": name, "lang": lang})
                if len(results) >= max_results:
                    return results
    return results


def match_token(token, matcher):
    for kw, sid, _ in matcher:
        idx = token.find(kw)
        if idx != -1:
            return (token[:idx], sid, token[idx+len(kw):])
    return None
