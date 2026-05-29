import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.font as tkfont
import locale
import threading
import json
import os
import keyboard
import io

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import MAX_SLOTS, SLOTS_VISIBLE, TRANSLATIONS, STUDENTS_URLS, get_icon_path, ICON_SIZE
from utils import get_registry, set_registry, build_matcher, match_token, tokenize_line, dbg, search_students_by_name
from data_manager import (
    load_guides_json, save_guides_json, 
    load_custom_dict_local, save_custom_dict_local,
    load_all_students_local, save_all_students_local,
    fetch_students_remote, download_icon
)
from auto_tracker import AutoTracker
from ui_windows import open_settings_window, open_custom_dict_window

class AdvancedGuideTeleprompter:
    def __init__(self, root):
        self.root = root
        self.all_students_data = {}   # {"ko": [...], "en": [...], ...} — 모든 언어 통합
        self.custom_dict       = {}
        self.matcher           = []
        self.image_mode        = False

        self.guide_slots   = [""] * MAX_SLOTS
        self.current_slot  = 0
        self._slot_offset  = 0

        self._img_widgets = []
        self._img_cur     = 0
        self._photo_cache = {}
        self._raw_text    = ""
        
        self.auto_tracker = AutoTracker(
            should_run_auto_cb=self._should_run_auto,
            set_armed_cb=self._set_armed,
            on_cast_cb=self._on_cast
        )

        self.load_data()

        self.root.title(self.t["title"])
        self.root.geometry("480x560")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.config["opacity"] / 100.0)

        self.current_line     = 1
        self.hotkeys_active   = False
        self.real_total_lines = 1

        self.custom_font    = tkfont.Font(family="맑은 고딕", size=self.config["font_size"],   weight="bold")
        self.custom_hl_font = tkfont.Font(family="맑은 고딕", size=self.config["font_size"]+2, weight="bold")

        self.setup_ui()
        self.apply_ui_text()
        self._load_slot(self.current_slot, init=True)
        self.update_highlight()
        threading.Thread(target=self._init_students, daemon=True).start()

    # ── 데이터 로드/저장 ──────────────────────────
    def _get_current_raw_text(self):
        if self.image_mode: return getattr(self, "_raw_text", "")
        if self.hotkeys_active: return self.text_widget.get("1.0", f"{self.real_total_lines}.end")
        return self.text_widget.get("1.0", "end-1c")

    def _load_slot(self, idx, init=False):
        if not init:
            self.guide_slots[self.current_slot] = self._get_current_raw_text()
        self.current_slot = idx
        text = self.guide_slots[idx]
        if self.image_mode:
            self.image_mode = False
            self.apply_ui_text()
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text if text.strip() else self.t["placeholder"], "normal")
        self._raw_text = text
        self._img_widgets = []; self._img_cur = 0; self._photo_cache = {}
        self.current_line = 1
        if self.hotkeys_active:
            self.real_total_lines = int(self.text_widget.index('end-1c').split('.')[0])
            self.text_widget.config(state=tk.DISABLED)
        self.update_highlight()
        self._refresh_slot_buttons()

    def load_data(self):
        self.config = {"lang":"auto","prev_key":"q","next_key":"e",
                       "margin_top":2,"hl_color":"#00ff00","font_size":14,"opacity":100,"icon_size":36}
        val = get_registry("config")
        if val:
            try: self.config.update(json.loads(val))
            except Exception: pass
        
        cd = load_custom_dict_local()
        if cd is not None:
            self.custom_dict = cd
        else:
            val = get_registry("custom_dict")
            if val:
                try:
                    self.custom_dict = json.loads(val)
                    self._save_custom_dict()
                    dbg("custom_dict: migrated from registry")
                except Exception: pass
                
        all_local = load_all_students_local()
        if all_local:
            # _size_* 메타키 제거해서 순수 언어 데이터만
            self.all_students_data = {k: v for k, v in all_local.items()
                                      if not k.startswith("_") and isinstance(v, list)}
            self._rebuild_matcher()
            total = sum(len(v) for v in self.all_students_data.values())
            dbg(f"students: loaded {total} entries across {list(self.all_students_data.keys())}")
        else:
            val = get_registry("students_cache")
            if val:
                try:
                    self.all_students_data = {"ko": json.loads(val)}
                    self._rebuild_matcher()
                    dbg("students: migrated from registry cache")
                except Exception: pass
                
        self.current_slot, self.guide_slots = load_guides_json(self.current_slot, self.guide_slots)
        self.update_language()

    def _resolve_lang(self):
        cfg_lang = self.config.get("lang", "auto")
        if cfg_lang == "auto":
            try:
                lc = locale.getlocale()[0] or ""
                lp = lc[:2].lower() if lc else "en"
                return lp if lp in STUDENTS_URLS else "en"
            except Exception: return "en"
        return cfg_lang if cfg_lang in STUDENTS_URLS else "en"

    def save_data(self):
        set_registry("config", json.dumps(self.config))
        self._save_custom_dict()
        self.guide_slots[self.current_slot] = self._get_current_raw_text()
        save_guides_json(self.current_slot, self.guide_slots)

    def _save_custom_dict(self):
        save_custom_dict_local(self.custom_dict)

    def update_language(self):
        if self.config["lang"] == "auto":
            try:
                lc = locale.getlocale()[0] or ""
                lp = lc[:2].lower() if lc else "en"
                self.lang = lp if lp in TRANSLATIONS else "en"
            except Exception: self.lang = "en"
        else:
            self.lang = self.config["lang"]
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])
        # 언어가 바뀌어도 all_students_data 는 그대로 — 매처는 항상 전체 언어 기준
        # (별도 리로드 불필요)

    def _init_students(self):
        self.root.after(0, lambda: self._set_status(self.t.get("updating", "Updating...")))
        all_local = load_all_students_local() or {}
        any_updated = False
        all_students_for_icons = []

        for lang in STUDENTS_URLS:
            meta_key = f"_size_{lang}"
            local_size = all_local.get(meta_key, 0)
            students, remote_size = fetch_students_remote(lang, local_size)
            if students:
                all_local[lang] = students
                all_local[meta_key] = remote_size
                any_updated = True
                dbg(f"saved {len(students)} students for lang={lang}")
            all_students_for_icons.extend(all_local.get(lang, []))

        if any_updated:
            save_all_students_local(all_local)
            self.all_students_data = {k: v for k, v in all_local.items()
                                      if not k.startswith("_") and isinstance(v, list)}
            self._rebuild_matcher()
            self._download_missing_icons(all_students_for_icons)
        else:
            dbg("all language data unchanged")

        self.root.after(0, lambda: self._set_status(self.t.get("loading_done","OK")))

    def _download_missing_icons(self, students):
        missing = [s for s in students if not os.path.exists(get_icon_path(s["Id"]))]
        if not missing: return
        self.root.after(0, lambda: self._set_status(self.t.get("img_downloading","Downloading icons...")))
        ok = 0
        for s in missing:
            if download_icon(s["Id"]): ok += 1
        dbg(f"icon download done: {ok}/{len(missing)}")
        self.root.after(0, lambda: self._set_status(self.t.get("loading_done","OK")))

    def _rebuild_matcher(self):
        self.matcher = build_matcher(self.all_students_data, self.custom_dict)

    def _set_status(self, msg):
        self.root.title(f"{self.t['title']}  [{msg}]")
        self.root.after(3000, lambda: self.root.title(self.t["title"]))

    # ── UI ──────────────────────────────────────
    def setup_ui(self):
        ctrl = tk.Frame(self.root, bg="#2d2d2d", pady=4)
        ctrl.pack(fill=tk.X)
        for c in range(4): ctrl.columnconfigure(c, weight=1)

        self.btn_first = tk.Button(ctrl, text="", command=self.go_first, bg="#444444", fg="white", borderwidth=1)
        self.btn_first.grid(row=0, column=0, padx=3, sticky="ew")
        self.btn_last = tk.Button(ctrl, text="", command=self.go_last, bg="#444444", fg="white", borderwidth=1)
        self.btn_last.grid(row=0, column=1, padx=3, sticky="ew")
        self.btn_toggle_hotkey = tk.Button(ctrl, text="", bg="#ff5555", fg="white", font=("맑은 고딕",9,"bold"), command=self.toggle_hotkeys)
        self.btn_toggle_hotkey.grid(row=0, column=2, padx=3, sticky="ew")
        self.btn_img_mode = tk.Button(ctrl, text="", bg="#555588", fg="white", font=("맑은 고딕",9,"bold"), command=self.toggle_image_mode)
        self.btn_img_mode.grid(row=0, column=3, padx=3, sticky="ew")

        slot_row = tk.Frame(self.root, bg="#2d2d2d", pady=2)
        slot_row.pack(fill=tk.X)

        self.btn_slot_prev = tk.Button(slot_row, text="<", width=2, bg="#333333", fg="white", borderwidth=1, command=self._slot_offset_prev)
        self.btn_slot_prev.pack(side=tk.LEFT, padx=(3,1))

        self.slot_btn_frame = tk.Frame(slot_row, bg="#2d2d2d")
        self.slot_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_slot_next = tk.Button(slot_row, text=">", width=2, bg="#333333", fg="white", borderwidth=1, command=self._slot_offset_next)
        self.btn_slot_next.pack(side=tk.LEFT, padx=(1,3))

        self.btn_settings = tk.Button(slot_row, text="", command=self.open_settings, bg="#444444", fg="white", borderwidth=1)
        self.btn_settings.pack(side=tk.RIGHT, padx=3)

        self._slot_btns = []
        self._build_slot_buttons(SLOTS_VISIBLE)
        self.slot_btn_frame.bind("<Configure>", self._on_slot_frame_resize)

        self.text_widget = tk.Text(
            self.root, font=self.custom_font, bg="#1e1e1e", fg="#555555", insertbackground="white",
            borderwidth=0, highlightthickness=0, spacing1=5, spacing3=5, wrap=tk.WORD,
        )
        self.text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=8)
        self.text_widget.tag_configure("highlight", justify="left")
        self.text_widget.tag_configure("normal",    justify="left")
        self.text_widget.bind("<ButtonRelease-1>", self.on_text_click)
        self.text_widget.bind("<KeyRelease>",      self.on_text_edit)

    def _build_slot_buttons(self, count):
        for b in self._slot_btns: b.destroy()
        self._slot_btns = []
        for i in range(count):
            b = tk.Button(self.slot_btn_frame, text="", width=3, bg="#333355", fg="white", borderwidth=1, command=lambda i=i: self._on_slot_btn(i))
            b.pack(side=tk.LEFT, padx=1)
            self._slot_btns.append(b)

    def _on_slot_frame_resize(self, event):
        btn_w = 32
        available = max(0, event.width - 4)
        new_count = max(1, min(MAX_SLOTS, available // btn_w))
        if new_count != len(self._slot_btns):
            self._build_slot_buttons(new_count)
            max_offset = max(0, MAX_SLOTS - new_count)
            self._slot_offset = min(self._slot_offset, max_offset)
            self._refresh_slot_buttons()

    def _visible_count(self): return len(self._slot_btns)

    def _refresh_slot_buttons(self):
        n = self._visible_count()
        offset = self._slot_offset
        for i, btn in enumerate(self._slot_btns):
            slot_idx = offset + i
            if slot_idx < MAX_SLOTS:
                is_active = (slot_idx == self.current_slot)
                has_text  = bool(self.guide_slots[slot_idx].strip())
                if is_active:    bg, fg = "#5577cc", "white"
                elif has_text:   bg, fg = "#335533", "#aaffaa"
                else:            bg, fg = "#333355", "#888888"
                btn.config(text=str(slot_idx+1), bg=bg, fg=fg, state=tk.NORMAL)
            else:
                btn.config(text="", bg="#2d2d2d", state=tk.DISABLED)
        max_offset = max(0, MAX_SLOTS - n)
        self.btn_slot_prev.config(state=tk.NORMAL if offset > 0 else tk.DISABLED)
        self.btn_slot_next.config(state=tk.NORMAL if offset < max_offset else tk.DISABLED)

    def _on_slot_btn(self, btn_idx):
        slot_idx = self._slot_offset + btn_idx
        if slot_idx >= MAX_SLOTS or slot_idx == self.current_slot: return
        if self.hotkeys_active: self.toggle_hotkeys()
        self._load_slot(slot_idx)

    def _slot_offset_prev(self):
        if self._slot_offset > 0:
            self._slot_offset -= 1
            self._refresh_slot_buttons()

    def _slot_offset_next(self):
        max_offset = max(0, MAX_SLOTS - self._visible_count())
        if self._slot_offset < max_offset:
            self._slot_offset += 1
            self._refresh_slot_buttons()

    def apply_ui_text(self):
        self.root.title(self.t["title"])
        self.btn_first.config(text=self.t["first"])
        self.btn_last.config(text=self.t["last"])
        self.btn_settings.config(text=self.t["settings"])
        if self.hotkeys_active:
            self.btn_toggle_hotkey.config(text=self.t["hotkey_active"], bg="#55ff55", fg="black")
        else:
            self.btn_toggle_hotkey.config(text=self.t["hotkey_on"], bg="#ff5555", fg="white")
        if self.image_mode:
            self.btn_img_mode.config(text=self.t["img_toggle_on"],  bg="#3355cc")
        else:
            self.btn_img_mode.config(text=self.t["img_toggle_off"], bg="#555588")
        self.custom_font.configure(size=self.config["font_size"])
        self.custom_hl_font.configure(size=self.config["font_size"]+2)
        self.text_widget.tag_configure("highlight", foreground=self.config["hl_color"], font=self.custom_hl_font, justify="left")
        self.text_widget.tag_configure("normal", font=self.custom_font, justify="left")
        self._refresh_slot_buttons()

    def open_settings(self):
        open_settings_window(self)

    # ── 이미지 모드 ─────────────────────────────
    def toggle_image_mode(self):
        if not PIL_AVAILABLE:
            messagebox.showwarning(self.t["error_title"], "이미지 모드를 사용하려면 Pillow가 필요합니다.\ninstall.bat을 실행해 설치해주세요.")
            return
        self.image_mode = not self.image_mode
        self.apply_ui_text()
        if self.image_mode: self._render_image_mode(capture_text=True)
        else:               self._restore_text_mode()
        if self.hotkeys_active:
            keyboard.unhook_all()
            self._register_nav_hotkeys()
            if self.image_mode: self.auto_tracker.start_hooks()
            else:               self.auto_tracker.stop_hooks()

    def _render_image_mode(self, capture_text=False):
        if capture_text:
            self._raw_text = self.text_widget.get("1.0","end-1c")
        self._img_widgets = []
        self._img_cur     = 0
        self._photo_cache = {}
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        lines = self._raw_text.split("\n")
        for line_no, line in enumerate(lines):
            for tok_str, is_bracket in tokenize_line(line):
                if is_bracket: self.text_widget.insert(tk.END, tok_str, "normal")
                else:          self._insert_token_with_images(tok_str)
            if line_no < len(lines) - 1:
                self.text_widget.insert(tk.END, "\n", "normal")
        if self.hotkeys_active:
            self.real_total_lines = int(self.text_widget.index('end-1c').split('.')[0])
            self.text_widget.config(state=tk.DISABLED)
        self._img_cur = 0
        self._update_image_highlight()

    def _insert_token_with_images(self, token):
        if not token: return
        if not self.matcher:
            self.text_widget.insert(tk.END, token, "normal"); return
        m = match_token(token, self.matcher)
        if m is None:
            self.text_widget.insert(tk.END, token, "normal"); return
        prefix, sid, suffix = m
        if prefix: self.text_widget.insert(tk.END, prefix, "normal")
        ph = tk.Label(self.text_widget, text="[?]", bg="#1e1e1e", fg="#aaaaaa", font=self.custom_font, cursor="arrow")
        tw = self.text_widget
        ph.bind("<MouseWheel>",       lambda e: tw.event_generate("<MouseWheel>",       delta=e.delta))
        ph.bind("<Button-4>",         lambda e: tw.event_generate("<Button-4>"))
        ph.bind("<Button-5>",         lambda e: tw.event_generate("<Button-5>"))
        self.text_widget.window_create(tk.END, window=ph)
        self._img_widgets.append(ph)
        local_path = get_icon_path(sid)
        if os.path.exists(local_path):
            threading.Thread(target=self._load_icon_local, args=(sid, ph, local_path), daemon=True).start()
        else:
            threading.Thread(target=self._load_icon_remote, args=(sid, ph), daemon=True).start()
        if suffix: self._insert_token_with_images(suffix)

    def _icon_size(self):
        s = self.config.get("icon_size", 36)
        return (s, s)

    def _load_icon_local(self, student_id, label, path):
        try:
            img   = Image.open(path).convert("RGBA").resize(self._icon_size(), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.root.after(0, lambda: self._place_icon(student_id, photo, label))
        except Exception:
            threading.Thread(target=self._load_icon_remote, args=(student_id, label), daemon=True).start()

    def _load_icon_remote(self, student_id, label):
        try:
            data = download_icon(student_id)
            if data:
                img   = Image.open(io.BytesIO(data)).convert("RGBA").resize(self._icon_size(), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self._place_icon(student_id, photo, label))
        except Exception: pass

    def _place_icon(self, student_id, photo, label):
        self._photo_cache[student_id] = photo
        try: label.config(image=photo, text="", bg="#1e1e1e"); label.image = photo
        except Exception: pass
        self._update_image_highlight()

    def _restore_text_mode(self):
        raw = getattr(self, "_raw_text", "")
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, raw if raw.strip() else self.t["placeholder"], "normal")
        self._img_widgets = []; self._img_cur = 0; self._photo_cache = {}
        if self.hotkeys_active:
            self.real_total_lines = int(self.text_widget.index('end-1c').split('.')[0])
            self.text_widget.config(state=tk.DISABLED)
        self.update_highlight()

    def _update_image_highlight(self, armed=False):
        if not self._img_widgets: return
        self._img_cur = max(0, min(self._img_cur, len(self._img_widgets)-1))
        hl = "#ff3333" if armed else self.config["hl_color"]
        for i, w in enumerate(self._img_widgets):
            try:
                if i == self._img_cur: w.config(bg=hl, relief="solid", borderwidth=2)
                else:                  w.config(bg="#1e1e1e", relief="flat", borderwidth=0)
            except Exception: pass
        if not armed:
            self.root.after(1, self._scroll_to_current_img)

    def _scroll_to_current_img(self):
        if not self._img_widgets: return
        try:
            tw    = self.text_widget
            cur_w = self._img_widgets[self._img_cur]
            idx   = tw.index(str(cur_w))
            tw.see(idx); tw.update_idletasks()
            info = tw.dlineinfo(idx)
            if info is None: return
            wy        = info[1]
            line_h    = self.custom_font.metrics("linespace") + 10
            margin_px = self.config["margin_top"] * line_h
            delta     = wy - margin_px
            if abs(delta) < 2: return
            tw_h    = tw.winfo_height()
            yv      = tw.yview()
            span    = yv[1] - yv[0]
            total_h = tw_h / span if span > 0 else tw_h
            new_top = max(0.0, min(1.0, yv[0] + delta / total_h))
            tw.yview_moveto(new_top)
        except Exception: pass

    def _img_go_next(self, event=None):
        if self._img_widgets and self._img_cur < len(self._img_widgets)-1:
            self._img_cur += 1
            self._update_image_highlight()

    def _img_go_prev(self, event=None):
        if self._img_widgets and self._img_cur > 0:
            self._img_cur -= 1
            self._update_image_highlight()

    def _should_run_auto(self):
        return self.hotkeys_active and self.image_mode

    def _set_armed(self, armed: bool):
        self.root.after(0, lambda: self._update_image_highlight(armed=armed))

    def _on_cast(self):
        self._img_go_next()

    # ── 단축키 ──────────────────────────────
    def _register_nav_hotkeys(self):
        if self.image_mode:
            keyboard.add_hotkey(self.config["prev_key"], self._img_go_prev)
            keyboard.add_hotkey(self.config["next_key"], self._img_go_next)
        else:
            keyboard.add_hotkey(self.config["prev_key"], self.go_prev)
            keyboard.add_hotkey(self.config["next_key"], self.go_next)

    def toggle_hotkeys(self):
        if self.hotkeys_active:
            keyboard.unhook_all()
            self.auto_tracker.stop_hooks()
            self.btn_toggle_hotkey.config(text=self.t["hotkey_on"], bg="#ff5555", fg="white")
            self.text_widget.config(state=tk.NORMAL)
            self.hotkeys_active = False
            self.save_data()
        else:
            try:
                self._register_nav_hotkeys()
                self.btn_toggle_hotkey.config(text=self.t["hotkey_active"], bg="#55ff55", fg="black")
                self.real_total_lines = int(self.text_widget.index('end-1c').split('.')[0])
                self.text_widget.config(state=tk.DISABLED)
                self.hotkeys_active = True
                self.root.focus()
                self.update_highlight()
                self.save_data()
                if self.image_mode:
                    self.auto_tracker.start_hooks()
            except Exception:
                messagebox.showerror(self.t["error_title"], self.t["error_msg"])

    # ── 하이라이트 (텍스트 모드) ────────────────
    def update_highlight(self):
        if self.image_mode:
            self._update_image_highlight(); return
        tw = self.text_widget
        tw.tag_remove("highlight", "1.0", tk.END)
        tw.tag_add("normal", "1.0", tk.END)
        ls = f"{self.current_line}.0"
        ln = f"{self.current_line+1}.0"
        tw.tag_remove("normal", ls, ln)
        tw.tag_add("highlight", ls, ln)
        if self.hotkeys_active:
            total = int(tw.index('end-1c').split('.')[0])
            needed = self.current_line + 20
            if total < needed:
                tw.config(state=tk.NORMAL)
                tw.insert(tk.END, "\n"*(needed-total))
                tw.config(state=tk.DISABLED)
            tw.see(ls)
            self.root.after(1, lambda l=ls: self._scroll_to_line(l))
        else:
            tw.see(ls)

    def _scroll_to_line(self, line_start):
        try:
            tw = self.text_widget
            tw.update_idletasks()
            info = tw.dlineinfo(line_start)
            if info is None: return
            wy        = info[1]
            line_h    = self.custom_font.metrics("linespace") + 10
            margin_px = self.config["margin_top"] * line_h
            delta     = wy - margin_px
            if abs(delta) < 2: return
            tw_h    = tw.winfo_height()
            yv      = tw.yview()
            span    = yv[1] - yv[0]
            total_h = tw_h / span if span > 0 else tw_h
            new_top = max(0.0, min(1.0, yv[0] + delta / total_h))
            tw.yview_moveto(new_top)
        except Exception: pass

    def on_text_click(self, event):
        if self.image_mode: return
        self.current_line = int(self.text_widget.index(f"@{event.x},{event.y}").split('.')[0])
        self.update_highlight()

    def on_text_edit(self, event):
        if not self.hotkeys_active and not self.image_mode:
            self.current_line = int(self.text_widget.index(tk.INSERT).split('.')[0])
            self.update_highlight()

    def go_prev(self, event=None):
        if self.image_mode: self._img_go_prev(); return
        if self.current_line > 1: self.current_line -= 1; self.update_highlight()

    def go_next(self, event=None):
        if self.image_mode: self._img_go_next(); return
        limit = self.real_total_lines if self.hotkeys_active else int(self.text_widget.index('end-1c').split('.')[0])
        if self.current_line < limit: self.current_line += 1; self.update_highlight()

    def go_first(self):
        if self.image_mode:
            if self._img_widgets: self._img_cur = 0; self._update_image_highlight()
            return
        self.current_line = 1; self.update_highlight()

    def go_last(self):
        if self.image_mode:
            if self._img_widgets: self._img_cur = len(self._img_widgets)-1; self._update_image_highlight()
            return
        self.current_line = self.real_total_lines if self.hotkeys_active else int(self.text_widget.index('end-1c').split('.')[0])
        self.update_highlight()
