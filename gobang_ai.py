import random
import tkinter.messagebox as messagebox

class GobangAI:
    def __init__(self, game):
        self.game = game

    def computer_move(self):
        if not self.game.game_over and not self.game.animation_in_progress and self.game.current_player == 2:
            best_move = self.get_best_move()
            if best_move is None:
                messagebox.showinfo("平局", "棋盘已满！")
                self.game.animation_in_progress = False
                return
            if best_move:
                x, y = best_move
                self.game.make_move(x, y, 2)

    def get_available_moves(self):
        return [(i, j) for i in range(15) for j in range(15) if self.game.board[i][j] == 0]

    def evaluate_position(self, x, y, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        threat_weights = {
            'five': 1000000,
            'open4': 100000,
            'half4': 8000,
            'open3': 5000,
            'half3': 500,
            'open2': 100,
            'block_open4': 150000,
            'block_half4': 10000,
            'block_open3': 6000,
            'block_half3': 600,
            'center_bonus': [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],
                [0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 0],
                [0, 0, 1, 3, 5, 5, 5, 5, 5, 5, 5, 3, 1, 0, 0],
                [0, 0, 2, 3, 5, 8, 8, 8, 8, 8, 5, 3, 2, 0, 0],
                [0, 1, 2, 3, 5, 8, 10,10,10, 8, 5, 3, 2, 1, 0],
                [0, 1, 2, 3, 5, 8, 10,15,10, 8, 5, 3, 2, 1, 0],
                [0, 1, 2, 3, 5, 8, 10,10,10, 8, 5, 3, 2, 1, 0],
                [0, 0, 2, 3, 5, 8, 8, 8, 8, 8, 5, 3, 2, 0, 0],
                [0, 0, 1, 3, 5, 5, 5, 5, 5, 5, 5, 3, 1, 0, 0],
                [0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 0],
                [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ]
        }

        # 中心位置梯度得分
        score += threat_weights['center_bonus'][x][y] * 5

        for dx, dy in directions:
            line = []
            for step in range(-4, 5):
                nx, ny = x + dx * step, y + dy * step
                line.append(self.game.board[nx][ny] if 0 <= nx < 15 and 0 <= ny < 15 else -1)

            for i in range(5):
                segment = line[i:i + 5]
                player_count = segment.count(player)
                opponent_count = segment.count(3 - player)
                empty_count = segment.count(0)

                if opponent_count == 0:
                    if player_count == 5: return threat_weights['five']
                    if player_count == 4 and empty_count == 1: score += threat_weights['open4']
                    if player_count == 3 and empty_count == 2: score += threat_weights['open3']
                    if player_count == 2 and empty_count == 3: score += threat_weights['open2']
                elif player_count == 0:
                    if opponent_count == 4 and empty_count == 1: score += threat_weights['block_open4']
                    if opponent_count == 3 and empty_count == 2: score += threat_weights['block_open3']
                
                if player_count == 4 and empty_count == 1: score += threat_weights['half4']
                if opponent_count == 4 and empty_count == 1: score += threat_weights['block_half4']
                if player_count == 3 and empty_count == 1: score += threat_weights['half3']
                if opponent_count == 3 and empty_count == 1: score += threat_weights['block_half3']

        return score

    def get_best_move(self):
        best_score = -float('inf')
        best_moves = []
        search_radius = 5
        candidate_moves = []

        if self.game.move_history:
            last_x, last_y = self.game.move_history[-1][0], self.game.move_history[-1][1]
            for x in range(max(0, last_x - search_radius), min(15, last_x + search_radius + 1)):
                for y in range(max(0, last_y - search_radius), min(15, last_y + search_radius + 1)):
                    if self.game.board[x][y] == 0:
                        candidate_moves.append((x, y))
        else:
            candidate_moves = self.get_available_moves()

        if not candidate_moves:
            return None

        for x, y in candidate_moves:
            attack_score = self.evaluate_position(x, y, 2)
            defense_score = self.evaluate_position(x, y, 1)
            total_score = attack_score * 1.6 + defense_score * 1.5

            if total_score > best_score:
                best_score = total_score
                best_moves = [(x, y)]
            elif total_score == best_score:
                best_moves.append((x, y))

        if not self.game.move_history and (7, 7) in best_moves:
            return (7, 7)

        return random.choice(best_moves) if best_moves else None