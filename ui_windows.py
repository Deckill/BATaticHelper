import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.colorchooser as colorchooser
from utils import search_students_by_name, _find_id_by_name


def open_settings_window(app):
    if app.hotkeys_active: app.toggle_hotkeys()
    app.temp_config = app.config.copy()
    sw = tk.Toplevel(app.root)
    sw.title(app.t["s_title"]); sw.geometry("400x440")
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
            app.config["opacity"]    = int(so.get())
            app.config["hl_color"]   = cv.get()
            app.config["lang"]       = lcm[lv.get()]
            app.root.attributes('-alpha', app.config["opacity"] / 100.0)
            app.update_language(); app.apply_ui_text(); app.update_highlight()
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

    tk.Label(sw, text=app.t["s_color"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    cv = tk.StringVar(value=app.config["hl_color"])
    def pick():
        c = colorchooser.askcolor(title="Color", initialcolor=app.config["hl_color"])[1]
        if c: cv.set(c); bc.config(bg=c); upv()
    bc = tk.Button(sw, text="...", bg=app.config["hl_color"], command=pick, width=10)
    bc.grid(row=r, column=1); r += 1

    tk.Label(sw, text=app.t["s_opacity"], bg=bg, fg=fg).grid(row=r, column=0, pady=5, padx=10, sticky="e")
    so = tk.Scale(sw, from_=20, to=100, orient=tk.HORIZONTAL, bg=bg, fg=fg, highlightthickness=0, command=upv)
    so.set(app.config["opacity"]); so.grid(row=r, column=1, sticky="w"); r += 1

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
        app.update_language(); app.apply_ui_text(); app.update_highlight()
        if app.image_mode: app._render_image_mode()
        sw.destroy()

    sw.protocol("WM_DELETE_WINDOW", cancel)
    bf = tk.Frame(sw, bg=bg); bf.grid(row=r, column=0, columnspan=2, pady=10)
    tk.Button(bf, text=app.t["s_save"],   command=save,   bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT,  padx=10)
    tk.Button(bf, text=app.t["s_cancel"], command=cancel, bg="#f44336", fg="white", width=10).pack(side=tk.RIGHT, padx=10)


def open_custom_dict_window(app, parent=None):
    """
    통상 명칭 사전 관리 창.
    타겟 학생 입력 시 모든 언어 학생 데이터에서 실시간 검색 -> 드롭다운 추천.
    커스텀 사전 체인 지원: 입력 이름이 기존 커스텀 사전 value이면 체인 따라가 최종 Name 저장.
    """
    cw = tk.Toplevel(parent or app.root)
    cw.title(app.t["cd_title"]); cw.geometry("460x480")
    cw.configure(bg="#2d2d2d"); cw.attributes('-topmost', True)
    if parent: cw.grab_set()
    bg, fg = "#2d2d2d", "white"

    # -- 입력 영역 --
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

    # -- 자동완성 드롭다운 --
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
        """커스텀 사전 체인 따라가 최종 Name 반환 (순환 방지)"""
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

    # -- 등록 목록 --
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
