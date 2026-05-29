import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colorchooser
import webbrowser
from utils import search_students_by_name, _find_id_by_name


def open_settings_window(app):
    if app.hotkeys_active: app.toggle_hotkeys()
    app.temp_config = app.config.copy()
    sw = tk.Toplevel(app.root)
    sw.title(app.t["s_title"]); sw.geometry("400x540")
    sw.configure(bg="#2d2d2d"); sw.attributes('-topmost', True); sw.grab_set()
    bg, fg = "#2d2d2d", "white"
    lnm = {"auto": app.t["auto"], "ko": "한국어", "en": "English", "ja": "日本語", "zh": "中文(简体)"}
    lcm = {v: k for k, v in lnm.items()}

    _rerender_job = [None]

    def upv(*a):
        try:
            app.config["margin_top"] = int(em.get() or app.temp_config["margin_top"])
            app.config["font_size"]  = int(es.get() or app.temp_config["font_size"])
            app.config["icon_size"]  = int(si.get())
            app.config["icon_pad"]   = int(sp.get())
            app.config["opacity"]    = int(so.get())
            app.config["hl_color"]   = cv.get()
            app.config["fg_color"]   = fgv.get()
            app.config["bg_color"]   = bgv.get()
            app.config["lang"]       = lcm[lv.get()]
            app.config["debug"]      = bool(dv.get())
            app.root.attributes('-alpha', app.config["opacity"] / 100.0)
            app.update_language(); app.apply_ui_text(); app.update_highlight()
            app.apply_debug()
            if app.image_mode:
                if _rerender_job[0]: sw.after_cancel(_rerender_job[0])
                _rerender_job[0] = sw.after(150, app._render_image_mode)
        except ValueError: pass

    r = 0
    for lbl, key in [(app.t["s_prev"], "prev_key"), (app.t["s_next"], "next_key")]:
        tk.Label(sw, text=lbl, bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
        e = tk.Entry(sw, width=15); e.insert(0, app.config[key])
        e.grid(row=r, column=1); r += 1
        if key == "prev_key": ep = e
        else:                  en = e

    tk.Label(sw, text=app.t["s_margin"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    em = tk.Spinbox(sw, from_=0, to=10, width=13, command=upv)
    em.delete(0, tk.END); em.insert(0, app.config["margin_top"]); em.bind("<KeyRelease>", upv)
    em.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t["s_size"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    es = tk.Spinbox(sw, from_=10, to=40, width=13, command=upv)
    es.delete(0, tk.END); es.insert(0, app.config["font_size"]); es.bind("<KeyRelease>", upv)
    es.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t["s_icon_size"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    si = tk.Scale(sw, from_=20, to=80, orient=tk.HORIZONTAL, bg=bg, fg=fg, highlightthickness=0, command=upv)
    si.set(app.config.get("icon_size", 36)); si.grid(row=r, column=1, sticky="w"); r += 1

    tk.Label(sw, text=app.t.get("s_icon_pad", "Icon Padding:"), bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    sp = tk.Scale(sw, from_=0, to=20, orient=tk.HORIZONTAL, bg=bg, fg=fg, highlightthickness=0, command=upv)
    sp.set(app.config.get("icon_pad", 4)); sp.grid(row=r, column=1, sticky="w"); r += 1

    tk.Label(sw, text=app.t["s_color"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    cv = tk.StringVar(value=app.config["hl_color"])
    def pick():
        c = colorchooser.askcolor(title="Color", initialcolor=app.config["hl_color"])[1]
        if c: cv.set(c); bc.config(bg=c); upv()
    bc = tk.Button(sw, text="...", bg=app.config["hl_color"], command=pick, width=10)
    bc.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t.get("s_fg_color", "Text Color:"), bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    fgv = tk.StringVar(value=app.config.get("fg_color", "#ffffff"))
    def pick_fg():
        c = colorchooser.askcolor(title="Text Color", initialcolor=app.config.get("fg_color", "#ffffff"))[1]
        if c: fgv.set(c); bfg.config(bg=c); upv()
    bfg = tk.Button(sw, text="...", bg=app.config.get("fg_color", "#ffffff"), command=pick_fg, width=10)
    bfg.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t.get("s_bg_color", "Background Color:"), bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    bgv = tk.StringVar(value=app.config.get("bg_color", "#1e1e1e"))
    def pick_bg():
        c = colorchooser.askcolor(title="Background Color", initialcolor=app.config.get("bg_color", "#1e1e1e"))[1]
        if c: bgv.set(c); bbg.config(bg=c); upv()
    bbg = tk.Button(sw, text="...", bg=app.config.get("bg_color", "#1e1e1e"), command=pick_bg, width=10)
    bbg.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t["s_opacity"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    so = tk.Scale(sw, from_=20, to=100, orient=tk.HORIZONTAL, bg=bg, fg=fg, highlightthickness=0, command=upv)
    so.set(app.config["opacity"]); so.grid(row=r, column=1, sticky="w"); r += 1

    dv = tk.BooleanVar(value=bool(app.config.get("debug", False)))
    tk.Checkbutton(sw, text=app.t["s_debug"], variable=dv, command=upv,
                   bg=bg, fg=fg, selectcolor="#1e1e1e", activebackground=bg,
                   activeforeground=fg).grid(row=r, column=0, columnspan=2, pady=3, padx=10, sticky="w"); r += 1

    tk.Label(sw, text=app.t["s_lang"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    lv = tk.StringVar(value=lnm.get(app.config["lang"], "English"))
    om = tk.OptionMenu(sw, lv, *lnm.values(), command=upv)
    om.config(width=10); om.grid(row=r, column=1); r += 1

    tk.Button(sw, text=app.t["s_custom_dict"], bg="#446688", fg="white",
              command=lambda: open_custom_dict_window(app, sw)
              ).grid(row=r, column=0, columnspan=2, pady=8, padx=10, sticky="ew"); r += 1

    def save():
        app.config["prev_key"] = ep.get(); app.config["next_key"] = en.get()
        app.save_data(); sw.destroy()

    def cancel():
        app.config = app.temp_config.copy()
        app.root.attributes('-alpha', app.config["opacity"] / 100.0)
        cv.set(app.config["hl_color"]); bc.config(bg=app.config["hl_color"])
        fgv.set(app.config.get("fg_color", "#ffffff")); bfg.config(bg=app.config.get("fg_color", "#ffffff"))
        bgv.set(app.config.get("bg_color", "#1e1e1e")); bbg.config(bg=app.config.get("bg_color", "#1e1e1e"))
        app.update_language(); app.apply_ui_text(); app.update_highlight()
        app.apply_debug()
        if app.image_mode: app._render_image_mode()
        sw.destroy()

    sw.protocol("WM_DELETE_WINDOW", cancel)
    bf = tk.Frame(sw, bg=bg); bf.grid(row=r, column=0, columnspan=2, pady=10)
    tk.Button(bf, text=app.t["s_save"],   command=save,   bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT,  padx=10)
    tk.Button(bf, text=app.t["s_cancel"], command=cancel, bg="#f44336", fg="white", width=10).pack(side=tk.RIGHT, padx=10)
    r += 1

    # -- 하단 정보 --
    info = tk.Frame(sw, bg="#222222")
    info.grid(row=r, column=0, columnspan=2, sticky="ew")

    credit_row = tk.Frame(info, bg="#222222")
    credit_row.pack(pady=(6, 2))

    lnk_license = tk.Label(credit_row, text="License / Credits", bg="#222222", fg="#7799bb",
                            font=("Malgun Gothic", 8, "underline"), cursor="hand2")
    lnk_license.pack(side=tk.LEFT, padx=6)
    lnk_license.bind("<Button-1>", lambda e: open_license_window(sw))

    tk.Label(credit_row, text="|", bg="#222222", fg="#555555", font=("Malgun Gothic", 8)).pack(side=tk.LEFT)

    lnk_author = tk.Label(credit_row, text="Deckill", bg="#222222", fg="#7799bb",
                           font=("Malgun Gothic", 8, "underline"), cursor="hand2")
    lnk_author.pack(side=tk.LEFT, padx=6)
    lnk_author.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@ButterDeckill"))

    # notice = tk.Label(info,
    #                   text="Data: SchaleDB  |  Unofficial non-commercial fan tool for Blue Archive.\n"
    #                        "Copyright belongs to NEXON Korea Corp. & NEXON GAMES Co., Ltd. & YOSTAR, Inc.",
    #                   bg="#222222", fg="#666666", font=("Malgun Gothic", 7), justify="center", wraplength=380)
    # notice.pack(pady=(0, 6), padx=6)


def open_license_window(parent=None):
    lw = tk.Toplevel(parent)
    lw.title("License / Credits")
    lw.geometry("520x520")
    lw.configure(bg="#1e1e1e")
    lw.attributes('-topmost', True)
    if parent: lw.grab_set()

    bg       = "#1e1e1e"
    fg       = "#cccccc"
    link_fg  = "#7799bb"
    head_fg  = "#ffffff"
    font_h   = ("Malgun Gothic", 11, "bold")
    font_b   = ("Malgun Gothic",  9)
    font_lnk = ("Malgun Gothic",  9, "underline")

    outer = tk.Frame(lw, bg=bg)
    outer.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    sb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    inner = tk.Frame(canvas, bg=bg)
    wid = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    inner.bind("<MouseWheel>",  lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def section(title):
        tk.Label(inner, text=title, bg=bg, fg=head_fg, font=font_h,
                 anchor="w").pack(fill=tk.X, padx=16, pady=(14, 2))
        tk.Frame(inner, bg="#444444", height=1).pack(fill=tk.X, padx=16)

    def body(text):
        tk.Label(inner, text=text, bg=bg, fg=fg, font=font_b,
                 anchor="w", justify="left", wraplength=460).pack(fill=tk.X, padx=24, pady=2)

    def linkrow(label, url, note=""):
        row = tk.Frame(inner, bg=bg)
        row.pack(fill=tk.X, padx=24, pady=1)
        lbl = tk.Label(row, text=label, bg=bg, fg=link_fg, font=font_lnk, cursor="hand2")
        lbl.pack(side=tk.LEFT)
        lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        if note:
            tk.Label(row, text="  " + note, bg=bg, fg=fg, font=font_b).pack(side=tk.LEFT)

    # 데이터 출처
    section("데이터 출처 / Data Sources")
    linkrow("SchaleDB", "https://schaledb.com/", "— 학생 이미지")

    # 사용 라이브러리
    section("사용 라이브러리 / Libraries Used")
    linkrow("Pillow", "https://github.com/python-pillow/Pillow",
            "— HPND License  |  Image processing")
    linkrow("keyboard", "https://github.com/boppreh/keyboard",
            "— MIT License  |  Global hotkey support")
    linkrow("mouse", "https://github.com/boppreh/mouse",
            "— MIT License  |  Mouse event detection")
    linkrow("PyInstaller", "https://github.com/pyinstaller/pyinstaller",
            "— GPL-2.0 + bootloader exception  |  EXE packaging")

    # 면책 조항
    section("면책 조항 / Disclaimer")
    body("This is an unofficial and non-commercial fan tool for Blue Archive.")
    body("All copyright of Blue Archive belongs to:")

    row = tk.Frame(inner, bg=bg)
    row.pack(fill=tk.X, padx=24, pady=(2, 8))
    for label, url in [
        ("NEXON Korea Corp.", "https://www.nexon.com/"),
        ("NEXON GAMES Co., Ltd.", "https://www.nexongames.co.kr/"),
        ("YOSTAR, Inc.", "https://www.yo-star.com/"),
    ]:
        lbl = tk.Label(row, text=label, bg=bg, fg=link_fg, font=font_lnk, cursor="hand2")
        lbl.pack(side=tk.LEFT, padx=(0, 10))
        lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    tk.Frame(inner, bg="#333333", height=1).pack(fill=tk.X, padx=16, pady=(8, 4))
    tk.Button(inner, text="닫기", command=lw.destroy,
              bg="#555555", fg="white", font=font_b, width=10).pack(pady=(4, 14))


def open_custom_dict_window(app, parent=None):
    cw = tk.Toplevel(parent or app.root)
    cw.title(app.t["cd_title"]); cw.geometry("460x480")
    cw.configure(bg="#2d2d2d"); cw.attributes('-topmost', True)
    if parent: cw.grab_set()
    bg, fg = "#2d2d2d", "white"

    inp = tk.Frame(cw, bg=bg)
    inp.pack(fill=tk.X, padx=10, pady=(10, 0))

    tk.Label(inp, text=app.t["cd_alias"],   bg=bg, fg=fg, width=18, anchor="w").grid(row=0, column=0)
    tk.Label(inp, text=app.t["cd_student"], bg=bg, fg=fg, width=22, anchor="w").grid(row=0, column=1, columnspan=2)

    ea = tk.Entry(inp, width=18, bg="#1e1e1e", fg="white", insertbackground="white")
    ea.grid(row=1, column=0, padx=(0, 6), pady=(2, 0))

    es = tk.Entry(inp, width=20, bg="#1e1e1e", fg="white", insertbackground="white")
    es.grid(row=1, column=1, pady=(2, 0))

    status_var = tk.StringVar(value="")
    status_lbl = tk.Label(inp, textvariable=status_var, bg=bg, fg="#aaaaaa",
                          font=("Malgun Gothic", 9), anchor="w")
    status_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(3, 0))

    ac_frame = tk.Frame(cw, bg="#1a1a2e", relief="solid", borderwidth=1)
    ac_lb = tk.Listbox(ac_frame, bg="#1a1a2e", fg="white", selectbackground="#446688",
                       font=("Malgun Gothic", 10), height=6, activestyle="none",
                       borderwidth=0, highlightthickness=0)
    ac_lb.pack(fill=tk.BOTH, expand=True)
    ac_results = []

    def _show_dropdown(results):
        nonlocal ac_results
        ac_results = results
        ac_lb.delete(0, tk.END)
        for item in results:
            ac_lb.insert(tk.END, "  " + item["display"])
        if results:
            cw.update_idletasks()
            ex = es.winfo_rootx() - cw.winfo_rootx()
            ey = es.winfo_rooty() - cw.winfo_rooty() + es.winfo_height() + 2
            ew = es.winfo_width()
            eh = min(len(results), 6) * 22 + 4
            ac_frame.place(x=ex, y=ey, width=ew, height=eh)
            ac_frame.lift()
        else:
            ac_frame.place_forget()

    def _hide_dropdown(*_):
        ac_frame.place_forget()

    def _select_ac(idx):
        if 0 <= idx < len(ac_results):
            name = ac_results[idx]["Name"]
            es.delete(0, tk.END)
            es.insert(0, name)
            _update_status(name)
            _hide_dropdown()

    def _resolve_chain(raw):
        visited, cur = set(), raw
        while cur in app.custom_dict and cur not in visited:
            visited.add(cur)
            cur = app.custom_dict[cur]
        return cur

    def _update_status(text):
        if not text:
            status_var.set(""); return
        final = _resolve_chain(text)
        sid = _find_id_by_name(final, app.all_students_data)
        if sid is not None:
            if final != text:
                status_var.set("OK: " + text + " -> " + final + "  (Id " + str(sid) + ")")
            else:
                status_var.set("OK: " + final + "  (Id " + str(sid) + ")")
            status_lbl.config(fg="#88ff88")
        else:
            status_var.set("X: '" + final + "' 에 해당하는 학생 없음")
            status_lbl.config(fg="#ff8888")

    def _on_es_key(event):
        if event.keysym == "Down":
            if ac_results:
                cur = ac_lb.curselection()
                nxt = (cur[0] + 1) if cur else 0
                if nxt < len(ac_results):
                    ac_lb.selection_clear(0, tk.END)
                    ac_lb.selection_set(nxt); ac_lb.see(nxt)
            return "break"
        if event.keysym == "Up":
            if ac_results:
                cur = ac_lb.curselection()
                prv = (cur[0] - 1) if cur else len(ac_results) - 1
                if prv >= 0:
                    ac_lb.selection_clear(0, tk.END)
                    ac_lb.selection_set(prv); ac_lb.see(prv)
            return "break"
        if event.keysym in ("Return", "Tab"):
            sel = ac_lb.curselection()
            if sel:            _select_ac(sel[0])
            elif ac_results:   _select_ac(0)
            return "break"
        if event.keysym == "Escape":
            _hide_dropdown(); return "break"
        cw.after(50, _do_search)

    def _do_search():
        q = es.get().strip()
        _update_status(q)
        if len(q) < 1:
            _hide_dropdown(); return
        results = search_students_by_name(q, app.all_students_data, max_results=8)
        _show_dropdown(results)

    ac_lb.bind("<ButtonRelease-1>", lambda e: _select_ac(ac_lb.nearest(e.y)))
    es.bind("<KeyPress>",  _on_es_key)
    es.bind("<FocusOut>",  lambda e: cw.after(200, _hide_dropdown))
    es.bind("<FocusIn>",   lambda e: _do_search())

    lf = tk.Frame(cw, bg=bg)
    lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
    sb = tk.Scrollbar(lf); sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(lf, bg="#1e1e1e", fg=fg, selectbackground="#446688",
                    font=("Malgun Gothic", 11), yscrollcommand=sb.set)
    lb.pack(fill=tk.BOTH, expand=True); sb.config(command=lb.yview)

    def ref():
        lb.delete(0, tk.END)
        for a, s in sorted(app.custom_dict.items()):
            lb.insert(tk.END, a + "  ->  " + s)

    def add():
        a = ea.get().strip()
        s = es.get().strip()
        if not a or not s:
            messagebox.showwarning(app.t["error_title"], app.t["cd_err_empty"], parent=cw); return
        if a in app.custom_dict:
            messagebox.showwarning(app.t["error_title"], app.t["cd_err_dup"], parent=cw); return
        final = _resolve_chain(s)
        app.custom_dict[a] = final
        app._rebuild_matcher(); app._save_custom_dict()
        ea.delete(0, tk.END); es.delete(0, tk.END)
        status_var.set(""); _hide_dropdown(); ref()

    def delete():
        sel = lb.curselection()
        if not sel: return
        key = lb.get(sel[0]).split("  ->  ")[0].strip()
        app.custom_dict.pop(key, None)
        app._rebuild_matcher(); app._save_custom_dict(); ref()

    bf = tk.Frame(cw, bg=bg)
    bf.pack(fill=tk.X, padx=10, pady=6)
    tk.Button(bf, text=app.t["cd_add"],    command=add,        bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT,  padx=4)
    tk.Button(bf, text=app.t["cd_delete"], command=delete,     bg="#f44336", fg="white", width=12).pack(side=tk.LEFT,  padx=4)
    tk.Button(bf, text=app.t["cd_close"],  command=cw.destroy, bg="#555555", fg="white", width=8 ).pack(side=tk.RIGHT, padx=4)
    ref()
