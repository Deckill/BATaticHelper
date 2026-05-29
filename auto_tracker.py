import threading
import keyboard
import mouse
from utils import dbg

class AutoTracker:
    def __init__(self, should_run_auto_cb, set_armed_cb, on_cast_cb):
        self.should_run_auto_cb = should_run_auto_cb
        self.set_armed_cb = set_armed_cb
        self.on_cast_cb = on_cast_cb
        
        self._auto_state      = "idle"
        self._auto_key_num    = None
        self._auto_mouse_down = False
        self._auto_lock       = threading.Lock()
        self._kb_hook_handle    = None
        self._mouse_hook_handle = None

    def start_hooks(self):
        with self._auto_lock:
            self._auto_state      = "idle"
            self._auto_key_num    = None
            self._auto_mouse_down = False
        dbg("game hooks START")
        self._kb_hook_handle    = keyboard.hook(self._on_kb_hook, suppress=False)
        self._mouse_hook_handle = mouse.hook(self._on_mouse_hook)

    def stop_hooks(self):
        dbg("game hooks STOP")
        if self._kb_hook_handle:
            try: keyboard.unhook(self._kb_hook_handle)
            except Exception: pass
            self._kb_hook_handle = None
        if self._mouse_hook_handle:
            try: mouse.unhook(self._mouse_hook_handle)
            except Exception: pass
            self._mouse_hook_handle = None
        with self._auto_lock:
            self._auto_state = "idle"
        self.set_armed_cb(False)

    def _on_kb_hook(self, event):
        etype = event.event_type
        name  = event.name
        if etype != "down": return

        dbg(f"key_down: {repr(name)}")
        if not self.should_run_auto_cb(): return

        if name in ("esc", "escape"):
            with self._auto_lock:
                prev = self._auto_state
                if prev != "idle":
                    self._auto_state      = "idle"
                    self._auto_key_num    = None
                    self._auto_mouse_down = False
                    cancelled = True
                else:
                    cancelled = False
            if cancelled:
                dbg(f"ESC → cancel (was {prev})")
                self.set_armed_cb(False)
            return

        if name not in ("1","2","3","4","5","6","7","8","9","0"): return
        num = int(name)

        with self._auto_lock:
            state = self._auto_state
            if state == "idle":
                self._auto_key_num    = num
                self._auto_state      = "armed"
                self._auto_mouse_down = False
                do_arm   = True
                do_rearm = False
            elif state == "armed":
                if self._auto_key_num == num:
                    do_arm = do_rearm = False   # key repeat
                else:
                    self._auto_key_num = num    # 다른 번호로 교체
                    do_arm = do_rearm = False
            elif state == "armed_mouse_down":
                # 마우스 누른 상태에서 키 입력 → 마우스 down 취소, armed 복귀
                self._auto_state      = "armed"
                self._auto_mouse_down = False
                self._auto_key_num    = num
                do_arm   = False
                do_rearm = True
            else:
                do_arm = do_rearm = False

        if do_arm:
            dbg(f"key_down({num}) → armed")
            self.set_armed_cb(True)
        elif do_rearm:
            dbg(f"key_down({num}) during mouse_down → back to armed (key={num})")
            self.set_armed_cb(True)
        elif state in ("armed", "armed_mouse_down"):
            dbg(f"key_down({num}) → change key (state={state})")

    def _on_mouse_hook(self, event):
        if not isinstance(event, mouse.ButtonEvent): return
        if event.button != mouse.LEFT: return
        if not self.should_run_auto_cb(): return

        btn = event.event_type

        with self._auto_lock:
            state = self._auto_state

        dbg(f"mouse {btn}  state={state}")

        if state == "armed":
            if btn == "down":
                with self._auto_lock:
                    self._auto_state      = "armed_mouse_down"
                    self._auto_mouse_down = True
                dbg("→ armed_mouse_down")

        elif state == "armed_mouse_down":
            if btn == "up":
                with self._auto_lock:
                    if not self._auto_mouse_down: return
                    self._auto_mouse_down = False
                    self._auto_state      = "idle"
                    self._auto_key_num    = None
                dbg("→ CAST")
                self.on_cast_cb()
