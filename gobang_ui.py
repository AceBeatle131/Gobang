import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from gobang_game import GobangGame
from gobang_ai import GobangAI

class GobangUI:
    def __init__(self, master):
        self.master = master
        self.master.title("五子棋")
        try:
            self.master.iconbitmap('gobang.ico')
        except:
            pass
        self.master.resizable(False, False)

        # 设置样式
        style = ttk.Style()
        style.theme_use('flatly')

        # 先初始化游戏实例
        self.init_game()

        # 然后创建菜单栏
        self.create_menu()

        # 最后创建界面元素
        self.create_ui()

        # 初始绘制
        self.game.draw_board()
        
        # 绑定键盘事件
        self.master.bind('<Key>', self.handle_key_press)
        
    def handle_key_press(self, event):
        """处理键盘快捷键"""
        if event.char.lower() == 'a':  # 按a显示关于页面
            self.show_about()
        elif event.char.lower() == 'r' and not event.state:  # 按r悔棋
            if self.regret_button['state'] == tk.NORMAL:
                self.game.regret()
        elif event.char.lower() == 's':  # 按s认输
            if self.surrender_button['state'] == tk.NORMAL:
                self.game.surrender()
        elif event.keysym == 'Escape':  # 按ESC退出
            self.master.quit()
        elif event.state & 0x0004 and event.keysym.lower() == 'r':  # Ctrl+R重新开始
            self.game.restart()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.master)
        
        # 创建"游戏"菜单
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="新游戏", command=self.game.restart, accelerator="(Ctrl+R)")
        game_menu.add_command(label="退出", command=self.master.quit, accelerator="(Esc)")
        menubar.add_cascade(label="游戏", menu=game_menu)
        
        # 创建"帮助"菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about, accelerator="(A)")
        help_menu.add_command(label="如何玩", command=self.show_help, accelerator="(H)")
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.master.config(menu=menubar)

    def show_about(self):
        """显示关于信息"""
        about_text = """五子棋
- 版本: 2.0.1
- Powered by Python"""
        messagebox.showinfo("关于", about_text)
        
    def show_help(self):
        help_text = """操作指南
- A 显示关于页面
- H 显示此帮助信息
- Ctrl+R 重新开始（新游戏）
- Esc 退出游戏
- R 悔棋
- S 认输"""
        messagebox.showinfo("如何玩", help_text)
        
    def init_game(self):
        """初始化游戏实例"""
        self.game = GobangGame(self)
        self.ai = GobangAI(self.game)
        
        # 更新按钮的命令绑定
        if hasattr(self, 'regret_button'):
            self.regret_button.config(command=self.game.regret)
            self.surrender_button.config(command=self.game.surrender)
            self.restart_button.config(command=self.game.restart)

    def create_ui(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(pady=5)

        # 画布
        self.canvas = tk.Canvas(main_frame, width=450, height=450, bg='#D2B48C', bd=0, highlightthickness=0)
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_click)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="当前下棋方：玩家", font=('Microsoft YaHei', 12))
        self.status_label.pack(pady=2)

        # 按钮框架
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.pack(pady=5)

        # 按钮 - 初始状态
        self.regret_button = ttk.Button(self.button_frame, text="悔棋(R)", 
                                      style='secondary.TButton',
                                      state=tk.DISABLED,
                                      command=self.game.regret)
        self.regret_button.pack(side=tk.LEFT, padx=5)

        self.surrender_button = ttk.Button(self.button_frame, text="认输(S)", 
                                         style='danger.TButton',
                                         state=tk.DISABLED,
                                         command=self.game.surrender)
        self.surrender_button.pack(side=tk.LEFT, padx=5)

        self.restart_button = ttk.Button(self.button_frame, text="再来一局(Ctrl+R)", 
                                       style='success.TButton',
                                       command=self.game.restart)
        self.restart_button.pack(side=tk.LEFT, padx=5)

    def on_click(self, event):
        if self.game is None or self.game.animation_in_progress or self.game.game_over:
            return
        
        # 确保是玩家回合才能下棋
        if self.game.current_player != 1:
            return

        y = event.x // self.game.cell_size  # 列坐标
        x = event.y // self.game.cell_size  # 行坐标

        if 0 <= x < 15 and 0 <= y < 15 and self.game.board[x][y] == 0:
            self.game.make_move(x, y, 1)