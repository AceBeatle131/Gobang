import tkinter as tk
import tkinter.messagebox as messagebox
import time

class GobangGame:
    def __init__(self, ui):
        self.ui = ui
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1  # 1:玩家(黑子) 2:AI(白子)
        self.game_over = False
        self.winner = None
        self.cell_size = 30
        self.move_history = []
        self.win_line = None
        self.regret_used = False
        self.animation_in_progress = False

    def draw_board(self):
        self.ui.canvas.delete("all")
        for i in range(15):
            for j in range(15):
                self.ui.canvas.create_rectangle(j * self.cell_size, i * self.cell_size,
                                             (j + 1) * self.cell_size, (i + 1) * self.cell_size,
                                             outline='black', fill='#D2B48C')

        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 1:
                    self.draw_piece(i, j, 'black')
                elif self.board[i][j] == 2:
                    self.draw_piece(i, j, 'white')

        if self.win_line:
            x1, y1, x2, y2 = self.win_line
            self.ui.canvas.create_line(y1 * self.cell_size + self.cell_size // 2,
                                    x1 * self.cell_size + self.cell_size // 2,
                                    y2 * self.cell_size + self.cell_size // 2,
                                    x2 * self.cell_size + self.cell_size // 2,
                                    fill='red', width=2)

    def draw_piece(self, x, y, color):
        center_x = y * self.cell_size + self.cell_size // 2
        center_y = x * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 5
        self.ui.canvas.create_oval(center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius,
                                fill=color, outline='black')

    def animate_piece(self, x, y, color, callback=None):
        center_x = y * self.cell_size + self.cell_size // 2
        center_y = x * self.cell_size + self.cell_size // 2
        max_radius = self.cell_size // 2 - 5
        min_radius = 5

        for i in range(5):
            current_y = center_y - (4 - i) * 5
            radius = min_radius + (max_radius - min_radius) * i / 4
            self.ui.canvas.delete("temp_piece")
            self.ui.canvas.create_oval(center_x - radius, current_y - radius,
                                    center_x + radius, current_y + radius,
                                    fill=color, outline='black', tags="temp_piece")
            self.ui.master.update()
            time.sleep(0.02)

        for i in range(3):
            factor = 1.1 - i * 0.05
            self.ui.canvas.delete("temp_piece")
            self.ui.canvas.create_oval(center_x - max_radius * factor, center_y - max_radius * factor,
                                    center_x + max_radius * factor, center_y + max_radius * factor,
                                    fill=color, outline='black', tags="temp_piece")
            self.ui.master.update()
            time.sleep(0.03)

        self.ui.canvas.delete("temp_piece")
        self.draw_piece(x, y, color)

        if callback:
            callback()

    def make_move(self, x, y, player):
        if self.board[x][y] != 0 or self.game_over:
            return
            
        self.animation_in_progress = True
        self.board[x][y] = player
        self.move_history.append((x, y, player))
        
        # 下第一颗子后启用悔棋和认输按钮
        if len(self.move_history) == 1:
            self.ui.regret_button.config(state=tk.NORMAL)
            self.ui.surrender_button.config(state=tk.NORMAL)
        
        self.ui.status_label.config(text="当前下棋方：电脑" if player == 1 else "当前下棋方：玩家")

        def after_animation():
            self.animation_in_progress = False
            if self.check_win(x, y, player):
                self.game_over = True
                self.winner = player
                winner_text = "恭喜你获胜了！" if player == 1 else "电脑获胜！"
                messagebox.showinfo("游戏结束", winner_text)
                self.ui.restart_button.config(state=tk.NORMAL)
                self.ui.regret_button.config(state=tk.DISABLED)
                self.ui.surrender_button.config(state=tk.DISABLED)
            else:
                # 切换玩家
                self.current_player = 3 - player
                self.ui.status_label.config(text="当前下棋方：电脑" if self.current_player == 2 else "当前下棋方：玩家")
                
                # 如果是AI回合，让AI下棋
                if self.current_player == 2 and not self.game_over:
                    self.ui.ai.computer_move()

        color = 'black' if player == 1 else 'white'
        self.animate_piece(x, y, color, after_animation)

    def check_win(self, x, y, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            start_x, start_y = x, y
            end_x, end_y = x, y

            for step in [-1, 1]:
                nx, ny = x + dx * step, y + dy * step
                while 0 <= nx < 15 and 0 <= ny < 15 and self.board[nx][ny] == player:
                    count += 1
                    nx += dx * step
                    ny += dy * step
                    if step == -1:
                        start_x, start_y = nx - dx * step, ny - dy * step
                    else:
                        end_x, end_y = nx - dx * step, ny - dy * step

            if count >= 5:
                self.win_line = (start_x, start_y, end_x, end_y)
                self.draw_board()
                return True
        return False

    def regret(self):
        """悔棋功能，每次移除最后两个棋子（AI和玩家各一个）"""
        if not self.game_over and len(self.move_history) >= 2:
            # 移除AI的最后一步
            ai_move = self.move_history.pop()
            self.board[ai_move[0]][ai_move[1]] = 0
            
            # 移除玩家的最后一步
            player_move = self.move_history.pop()
            self.board[player_move[0]][player_move[1]] = 0
            
            # 重置游戏状态
            self.current_player = 1  # 总是回到玩家回合
            self.win_line = None
            self.game_over = False
            self.winner = None
            
            # 更新UI
            self.draw_board()
            self.ui.status_label.config(text="当前下棋方：玩家")
            
            # 如果悔棋后没有棋子了，禁用悔棋和认输按钮
            if not self.move_history:
                self.ui.regret_button.config(state=tk.DISABLED)
                self.ui.surrender_button.config(state=tk.DISABLED)
        elif len(self.move_history) == 1:
            # 只有一步棋的情况（玩家先手时）
            player_move = self.move_history.pop()
            self.board[player_move[0]][player_move[1]] = 0
            self.ui.regret_button.config(state=tk.DISABLED)
            self.ui.surrender_button.config(state=tk.DISABLED)
            self.draw_board()

    def surrender(self):
        if not self.game_over:
            self.game_over = True
            self.winner = 2 if self.current_player == 1 else 1
            winner_text = "电脑获胜！" if self.current_player == 1 else "恭喜你获胜了！"
            messagebox.showinfo("认输", winner_text)
            self.ui.restart_button.config(state=tk.NORMAL)
            self.ui.regret_button.config(state=tk.DISABLED)
            self.ui.surrender_button.config(state=tk.DISABLED)

    def restart(self):
        self.board = [[0] * 15 for _ in range(15)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.win_line = None
        self.regret_used = False
        self.draw_board()
        self.ui.status_label.config(text="当前下棋方：玩家")
        self.ui.regret_button.config(state=tk.DISABLED)
        self.ui.surrender_button.config(state=tk.DISABLED)
        self.ui.restart_button.config(state=tk.NORMAL)