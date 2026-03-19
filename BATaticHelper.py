import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colorchooser
import tkinter.font as tkfont
import keyboard
import locale
import json
import winreg 

REG_PATH = r"Software\BATacticHelper"

TRANSLATIONS = {
    "ko": {
        "title": "블아 택틱 도우미", "hotkey_on": "단축키 켜기", "hotkey_active": "단축키 켜짐 (수정불가)",
        "first": "⏪ 처음", "last": "마지막 ⏩", "settings": "⚙️ 설정",
        "placeholder": "여기에 공략을 복사해서 붙여넣으세요.\n(Ctrl+V)\n\n클릭하면 해당 순서로 이동합니다.",
        "error_title": "오류", "error_msg": "잘못된 단축키 형식입니다.",
        "s_title": "설정", "s_prev": "이전 단축키:", "s_next": "다음 단축키:",
        "s_margin": "상단 고정 (몇 번째 줄):", "s_color": "하이라이트 색상:",
        "s_size": "글자 크기:", "s_lang": "언어 (Language):", "s_opacity": "배경 투명도 (%):",
        "s_save": "저장", "s_cancel": "취소", "auto": "자동 감지 (Auto)"
    },
    "en": {
        "title": "BA Tactic Helper", "hotkey_on": "Hotkeys OFF", "hotkey_active": "Hotkeys ON (Read-Only)",
        "first": "⏪ First", "last": "Last ⏩", "settings": "⚙️ Settings",
        "placeholder": "Paste your guide here.\n(Ctrl+V)\n\nClick to move.",
        "error_title": "Error", "error_msg": "Invalid hotkey format.",
        "s_title": "Settings", "s_prev": "Prev Hotkey:", "s_next": "Next Hotkey:",
        "s_margin": "Top Margin (Lines):", "s_color": "Highlight Color:",
        "s_size": "Font Size:", "s_lang": "Language:", "s_opacity": "Opacity (%):",
        "s_save": "Save", "s_cancel": "Cancel", "auto": "Auto Detect"
    },
    "ja": {
        "title": "ブルアカ タクティクス 補助", "hotkey_on": "ショートカット OFF", "hotkey_active": "ショートカット ON (読取専用)",
        "first": "⏪ 最初", "last": "最後 ⏩", "settings": "⚙️ 設定",
        "placeholder": "ここに攻略を貼り付けてください。\n(Ctrl+V)\n\nクリックで移動します。",
        "error_title": "エラー", "error_msg": "無効なショートカット形式です。",
        "s_title": "設定", "s_prev": "前のショートカット:", "s_next": "次のショートカット:",
        "s_margin": "上部固定 (行数):", "s_color": "ハイライト色:",
        "s_size": "文字サイズ:", "s_lang": "言語 (Language):", "s_opacity": "背景の不透明度 (%):",
        "s_save": "保存", "s_cancel": "キャンセル", "auto": "自動検出 (Auto)"
    },
    "zh": {
        "title": "蔚蓝档案排刀助手", "hotkey_on": "开启快捷键", "hotkey_active": "快捷键已开启 (只读)",
        "first": "⏪ 最前", "last": "最后 ⏩", "settings": "⚙️ 设置",
        "placeholder": "请在此处粘贴攻略。\n(Ctrl+V)\n\n点击跳转。",
        "error_title": "错误", "error_msg": "无效的快捷键格式。",
        "s_title": "设置", "s_prev": "上一步快捷键:", "s_next": "下一步快捷键:",
        "s_margin": "顶部固定 (行数):", "s_color": "高亮颜色:",
        "s_size": "字体大小:", "s_lang": "语言 (Language):", "s_opacity": "背景不透明度 (%):",
        "s_save": "保存", "s_cancel": "取消", "auto": "自动检测 (Auto)"
    }
}

class AdvancedGuideTeleprompter:
    def __init__(self, root):
        self.root = root
        
        self.saved_guide_text = ""
        self.load_data()
        
        self.root.title(self.t["title"])
        self.root.geometry("450x500")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', self.config["opacity"] / 100.0)

        self.current_line = 1
        self.hotkeys_active = False
        self.real_total_lines = 1

        self.custom_font = tkfont.Font(family="맑은 고딕", size=self.config["font_size"], weight="bold")
        self.custom_hl_font = tkfont.Font(family="맑은 고딕", size=self.config["font_size"]+2, weight="bold")

        self.setup_ui()
        self.apply_ui_text()
        self.update_highlight()

    # --- 윈도우 레지스트리 제어 ---
    def set_registry(self, name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
        except Exception:
            pass

    def get_registry(self, name):
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except OSError:
            return None

    def load_data(self):
        # 기본 투명도 100으로 변경
        self.config = {
            "lang": "auto", "prev_key": "q", "next_key": "e",
            "margin_top": 2, "hl_color": "#00ff00", "font_size": 14, "opacity": 100
        }
        
        saved_config = self.get_registry("config")
        if saved_config:
            try:
                self.config.update(json.loads(saved_config))
            except Exception:
                pass

        saved_text = self.get_registry("guide_text")
        if saved_text:
            self.saved_guide_text = saved_text
            
        self.update_language()

    def save_data(self):
        self.set_registry("config", json.dumps(self.config))
        
        if self.hotkeys_active:
            real_text = self.text_widget.get("1.0", f"{self.real_total_lines}.end")
        else:
            real_text = self.text_widget.get("1.0", "end-1c")
            
        self.set_registry("guide_text", real_text)

    def update_language(self):
        if self.config["lang"] == "auto":
            try:
                lang_code, _ = locale.getdefaultlocale()
                lang_prefix = lang_code[:2].lower() if lang_code else "en"
                self.lang = lang_prefix if lang_prefix in TRANSLATIONS else "en"
            except:
                self.lang = "en"
        else:
            self.lang = self.config["lang"]
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])

    def setup_ui(self):
        control_frame = tk.Frame(self.root, bg="#2d2d2d", pady=5)
        control_frame.pack(fill=tk.X)

        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        control_frame.columnconfigure(3, weight=1)

        self.btn_first = tk.Button(control_frame, text="", command=self.go_first, bg="#444444", fg="white", borderwidth=1)
        self.btn_first.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_last = tk.Button(control_frame, text="", command=self.go_last, bg="#444444", fg="white", borderwidth=1)
        self.btn_last.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_toggle_hotkey = tk.Button(control_frame, text="", bg="#ff5555", fg="white", font=("맑은 고딕", 10, "bold"), command=self.toggle_hotkeys)
        self.btn_toggle_hotkey.grid(row=0, column=2, padx=5, sticky="ew")

        self.btn_settings = tk.Button(control_frame, text="", command=self.open_settings, bg="#444444", fg="white", borderwidth=1)
        self.btn_settings.grid(row=0, column=3, padx=5, sticky="ew")

        self.text_widget = tk.Text(
            self.root, font=self.custom_font, 
            bg="#1e1e1e", fg="#555555", insertbackground="white",
            borderwidth=0, highlightthickness=0, spacing1=5, spacing3=5
        )
        self.text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.text_widget.tag_configure("highlight", justify='center')
        self.text_widget.tag_configure("normal", justify='center')

        self.text_widget.bind("<ButtonRelease-1>", self.on_text_click)
        self.text_widget.bind("<KeyRelease>", self.on_text_edit)

        if self.saved_guide_text.strip():
            self.text_widget.insert(tk.END, self.saved_guide_text, "normal")
        else:
            self.text_widget.insert(tk.END, self.t["placeholder"], "normal")

    def apply_ui_text(self):
        self.root.title(self.t["title"])
        self.btn_first.config(text=self.t["first"])
        self.btn_last.config(text=self.t["last"])
        self.btn_settings.config(text=self.t["settings"])
        
        if self.hotkeys_active:
            self.btn_toggle_hotkey.config(text=self.t["hotkey_active"], bg="#55ff55", fg="black")
        else:
            self.btn_toggle_hotkey.config(text=self.t["hotkey_on"], bg="#ff5555", fg="white")

        self.custom_font.configure(size=self.config["font_size"])
        self.custom_hl_font.configure(size=self.config["font_size"]+2)
        
        self.text_widget.tag_configure("highlight", foreground=self.config["hl_color"], font=self.custom_hl_font)
        self.text_widget.tag_configure("normal", font=self.custom_font)

    def open_settings(self):
        if self.hotkeys_active:
            self.toggle_hotkeys()

        # 취소를 대비해 현재 설정을 백업해 둡니다.
        self.temp_config = self.config.copy()

        set_win = tk.Toplevel(self.root)
        set_win.title(self.t["s_title"])
        set_win.geometry("380x350")
        set_win.configure(bg="#2d2d2d")
        set_win.attributes('-topmost', True)
        set_win.grab_set() 

        labels_color = "white"
        bg_color = "#2d2d2d"

        lang_name_map = {
            "auto": self.t["auto"],
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文(简体)"
        }
        lang_code_map = {v: k for k, v in lang_name_map.items()}

        # 실시간 미리보기 적용 함수
        def update_preview(*args):
            try:
                # 숫자나 문자가 지워지는 과정에서 발생하는 오류를 막기 위해 try-except 적용
                self.config["margin_top"] = int(ent_margin.get() or self.temp_config["margin_top"])
                self.config["font_size"] = int(ent_size.get() or self.temp_config["font_size"])
                self.config["opacity"] = int(scale_opacity.get())
                self.config["hl_color"] = color_var.get()
                self.config["lang"] = lang_code_map[lang_var.get()]
                
                # 즉시 화면에 렌더링
                self.root.attributes('-alpha', self.config["opacity"] / 100.0)
                self.update_language()
                self.apply_ui_text()
                self.update_highlight()
            except ValueError:
                pass

        tk.Label(set_win, text=self.t["s_prev"], bg=bg_color, fg=labels_color).grid(row=0, column=0, pady=5, padx=10, sticky="e")
        ent_prev = tk.Entry(set_win, width=15); ent_prev.insert(0, self.config["prev_key"])
        ent_prev.grid(row=0, column=1)

        tk.Label(set_win, text=self.t["s_next"], bg=bg_color, fg=labels_color).grid(row=1, column=0, pady=5, padx=10, sticky="e")
        ent_next = tk.Entry(set_win, width=15); ent_next.insert(0, self.config["next_key"])
        ent_next.grid(row=1, column=1)

        tk.Label(set_win, text=self.t["s_margin"], bg=bg_color, fg=labels_color).grid(row=2, column=0, pady=5, padx=10, sticky="e")
        ent_margin = tk.Spinbox(set_win, from_=0, to=10, width=13, command=update_preview)
        ent_margin.delete(0, tk.END); ent_margin.insert(0, self.config["margin_top"])
        ent_margin.bind("<KeyRelease>", update_preview)
        ent_margin.grid(row=2, column=1)

        tk.Label(set_win, text=self.t["s_size"], bg=bg_color, fg=labels_color).grid(row=3, column=0, pady=5, padx=10, sticky="e")
        ent_size = tk.Spinbox(set_win, from_=10, to=40, width=13, command=update_preview)
        ent_size.delete(0, tk.END); ent_size.insert(0, self.config["font_size"])
        ent_size.bind("<KeyRelease>", update_preview)
        ent_size.grid(row=3, column=1)

        tk.Label(set_win, text=self.t["s_color"], bg=bg_color, fg=labels_color).grid(row=4, column=0, pady=5, padx=10, sticky="e")
        color_var = tk.StringVar(value=self.config["hl_color"])
        def choose_color():
            color_code = colorchooser.askcolor(title="Choose Color", initialcolor=self.config["hl_color"])[1]
            if color_code:
                color_var.set(color_code)
                btn_color.config(bg=color_code)
                update_preview() # 색상 변경 즉시 렌더링
        btn_color = tk.Button(set_win, text="■■■", bg=self.config["hl_color"], command=choose_color, width=10)
        btn_color.grid(row=4, column=1)

        tk.Label(set_win, text=self.t["s_opacity"], bg=bg_color, fg=labels_color).grid(row=5, column=0, pady=5, padx=10, sticky="e")
        scale_opacity = tk.Scale(set_win, from_=20, to=100, orient=tk.HORIZONTAL, bg=bg_color, fg=labels_color, highlightthickness=0, command=update_preview)
        scale_opacity.set(self.config["opacity"])
        scale_opacity.grid(row=5, column=1, sticky="w")

        tk.Label(set_win, text=self.t["s_lang"], bg=bg_color, fg=labels_color).grid(row=6, column=0, pady=5, padx=10, sticky="e")
        lang_var = tk.StringVar(value=lang_name_map.get(self.config["lang"], "English"))
        lang_menu = tk.OptionMenu(set_win, lang_var, *lang_name_map.values(), command=update_preview)
        lang_menu.config(width=10)
        lang_menu.grid(row=6, column=1)

        def save_and_close():
            self.config["prev_key"] = ent_prev.get()
            self.config["next_key"] = ent_next.get()
            # 텍스트 박스(단축키) 설정만 추가로 확정하고 저장
            self.save_data() 
            set_win.destroy()

        def cancel_and_close():
            # 백업본으로 원상복구
            self.config = self.temp_config.copy()
            self.root.attributes('-alpha', self.config["opacity"] / 100.0)
            self.update_language()
            self.apply_ui_text()
            self.update_highlight()
            set_win.destroy()

        # X 버튼을 누를 때도 취소와 똑같이 동작하도록 연결
        set_win.protocol("WM_DELETE_WINDOW", cancel_and_close)

        btn_frame = tk.Frame(set_win, bg=bg_color)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text=self.t["s_save"], command=save_and_close, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text=self.t["s_cancel"], command=cancel_and_close, bg="#f44336", fg="white", width=10).pack(side=tk.RIGHT, padx=10)

    def toggle_hotkeys(self):
        if self.hotkeys_active:
            keyboard.unhook_all()
            self.btn_toggle_hotkey.config(text=self.t["hotkey_on"], bg="#ff5555", fg="white")
            self.text_widget.config(state=tk.NORMAL) 
            self.hotkeys_active = False
            self.save_data() 
        else:
            try:
                keyboard.add_hotkey(self.config["prev_key"], self.go_prev)
                keyboard.add_hotkey(self.config["next_key"], self.go_next)
                self.btn_toggle_hotkey.config(text=self.t["hotkey_active"], bg="#55ff55", fg="black")
                
                self.real_total_lines = int(self.text_widget.index('end-1c').split('.')[0])
                
                self.text_widget.config(state=tk.DISABLED) 
                self.hotkeys_active = True
                self.root.focus() 
                self.update_highlight() 
                self.save_data() 
            except Exception as e:
                messagebox.showerror(self.t["error_title"], self.t["error_msg"])

    def update_highlight(self):
        self.text_widget.tag_remove("highlight", "1.0", tk.END)
        self.text_widget.tag_add("normal", "1.0", tk.END)

        line_start = f"{self.current_line}.0"
        line_next = f"{self.current_line + 1}.0"
        self.text_widget.tag_remove("normal", line_start, line_next)
        self.text_widget.tag_add("highlight", line_start, line_next)

        if self.hotkeys_active:
            margin = self.config["margin_top"]
            total_lines = int(self.text_widget.index('end-1c').split('.')[0])
            needed_lines = self.current_line + 20 
            
            if total_lines < needed_lines:
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, "\n" * (needed_lines - total_lines))
                self.text_widget.config(state=tk.DISABLED)

            self.text_widget.yview(line_start)
            if margin > 0:
                self.text_widget.yview_scroll(-margin, "units")
        else:
            self.text_widget.see(line_start)

    def on_text_click(self, event):
        cursor_pos = self.text_widget.index(f"@{event.x},{event.y}")
        self.current_line = int(cursor_pos.split('.')[0])
        self.update_highlight()

    def on_text_edit(self, event):
        if not self.hotkeys_active:
            cursor_pos = self.text_widget.index(tk.INSERT)
            self.current_line = int(cursor_pos.split('.')[0])
            self.update_highlight()

    def go_prev(self, event=None):
        if self.current_line > 1:
            self.current_line -= 1
            self.update_highlight()

    def go_next(self, event=None):
        limit = self.real_total_lines if self.hotkeys_active else int(self.text_widget.index('end-1c').split('.')[0])
        if self.current_line < limit:
            self.current_line += 1
            self.update_highlight()

    def go_first(self):
        self.current_line = 1
        self.update_highlight()

    def go_last(self):
        self.current_line = self.real_total_lines if self.hotkeys_active else int(self.text_widget.index('end-1c').split('.')[0])
        self.update_highlight()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedGuideTeleprompter(root)
    
    def on_closing():
        app.save_data()
        keyboard.unhook_all()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
