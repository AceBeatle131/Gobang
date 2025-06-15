# gobang_main.py
import ttkbootstrap as ttk
from gobang_ui import GobangUI

if __name__ == "__main__":
    root = ttk.Window()
    app = GobangUI(root)
    root.mainloop()