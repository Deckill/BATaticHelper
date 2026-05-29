import tkinter as tk
import keyboard
import mouse
from main_app import AdvancedGuideTeleprompter

if __name__ == "__main__":
    root = tk.Tk()
    app  = AdvancedGuideTeleprompter(root)
    
    def on_closing():
        app.save_data()
        try: keyboard.unhook_all()
        except Exception: pass
        try: mouse.unhook_all()
        except Exception: pass
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
