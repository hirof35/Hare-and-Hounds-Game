import tkinter as tk
from tkinter import messagebox
import random

class HaresAndHoundsStable:
    def __init__(self, root):
        self.root = root
        self.root.title("ウサギと猟犬 - 安定版")
        
        # ボード接続定義
        self.adj = {
            0: [1, 2, 3], 1: [0, 2, 4, 5], 2: [0, 1, 3, 5],
            3: [0, 2, 5, 6], 4: [1, 5, 7], 5: [1, 2, 3, 4, 6, 7, 8, 9],
            6: [3, 5, 9], 7: [4, 5, 8, 10], 8: [5, 7, 9, 10],
            9: [5, 6, 8, 10], 10: [7, 8, 9]
        }
        self.pos = {
            0: (50, 150), 1: (150, 50), 2: (150, 150), 3: (150, 250),
            4: (250, 50), 5: (250, 150), 6: (250, 250), 7: (350, 50),
            8: (350, 150), 9: (350, 250), 10: (450, 150)
        }

        self.player_role = tk.StringVar(value="Hare")
        self.is_running = False
        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # 設定エリア
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="あなたの役割:").pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="ウサギ (赤)", variable=self.player_role, value="Hare").pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="猟犬 (青)", variable=self.player_role, value="Hound").pack(side=tk.LEFT)
        
        self.start_btn = tk.Button(control_frame, text="ゲーム開始/リセット", command=self.reset_game, bg="lightgreen")
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # 盤面
        self.canvas = tk.Canvas(self.root, width=500, height=300, bg="white")
        self.canvas.pack()

        self.label = tk.Label(self.root, text="陣営を選んで開始してください", font=("MS Gothic", 12))
        self.label.pack(pady=5)

        self.buttons = {}
        # ボタンの作成（一度だけ）
        for i, (x, y) in self.pos.items():
            btn = tk.Button(self.root, text=str(i), command=lambda idx=i: self.on_click(idx), width=4)
            self.buttons[i] = btn
            self.canvas.create_window(x, y, window=btn)

    def reset_game(self):
        self.hounds = [0, 1, 3]
        self.hare = 10
        self.turn = "Hound"  # ルール上、猟犬が先手
        self.selected_hound = None
        self.is_running = True
        
        # 線の描画（リセット時に再描画）
        self.canvas.delete("line")
        for start, neighbors in self.adj.items():
            for end in neighbors:
                x1, y1 = self.pos[start]
                x2, y2 = self.pos[end]
                self.canvas.create_line(x1, y1, x2, y2, fill="#ccc", tags="line")

        self.update_display()
        
        # もしプレイヤーがウサギなら、最初のAI（猟犬）の手番を起動
        if self.player_role.get() == "Hare":
            self.label.config(text="AI(猟犬)が考え中...")
            self.root.after(800, self.ai_move)
        else:
            self.label.config(text="あなたの番です（猟犬を1匹選んでください）")

    def update_display(self):
        for i, btn in self.buttons.items():
            if i in self.hounds:
                bg = "#00FFFF" if i == self.selected_hound else "#4169E1"
                btn.config(bg=bg, fg="white", text="犬")
            elif i == self.hare:
                btn.config(bg="#FF4500", fg="white", text="兎")
            else:
                btn.config(bg="#F0F0F0", fg="#AAA", text=str(i))

    def on_click(self, idx):
        if not self.is_running or self.turn != self.player_role.get():
            return

        if self.turn == "Hare":
            # ウサギの移動
            if idx in self.adj[self.hare] and idx not in self.hounds:
                self.hare = idx
                self.end_turn()
        else:
            # 猟犬の移動
            if idx in self.hounds:
                self.selected_hound = idx
                self.update_display()
            elif self.selected_hound is not None:
                if idx in self.adj[self.selected_hound] and idx not in self.hounds and idx != self.hare:
                    # 戻り制限（x座標が減る移動は不可）
                    if self.pos[idx][0] >= self.pos[self.selected_hound][0]:
                        self.hounds[self.hounds.index(self.selected_hound)] = idx
                        self.selected_hound = None
                        self.end_turn()
                    else:
                        self.label.config(text="【不可】猟犬は左には戻れません！")

    def end_turn(self):
        self.update_display()
        if self.check_winner():
            self.is_running = False
            return

        self.turn = "Hare" if self.turn == "Hound" else "Hound"
        
        if self.turn != self.player_role.get():
            self.label.config(text="AIが考え中...")
            self.root.after(800, self.ai_move)
        else:
            msg = "あなたの番（ウサギ）" if self.turn == "Hare" else "あなたの番（猟犬を選択）"
            self.label.config(text=msg)

    def ai_move(self):
        if not self.is_running: return

        if self.turn == "Hare":
            # ウサギAI: 左へ逃げる
            moves = [m for m in self.adj[self.hare] if m not in self.hounds]
            if moves:
                moves.sort(key=lambda m: self.pos[m][0]) # x座標最小を狙う
                self.hare = moves[0]
        else:
            # 猟犬AI: 追い詰める
            best = self.get_best_hound_move()
            if best:
                h_idx, target = best
                self.hounds[h_idx] = target
        
        self.end_turn()

    def get_best_hound_move(self):
        choices = []
        for i, h_pos in enumerate(self.hounds):
            for target in self.adj[h_pos]:
                if self.pos[target][0] >= self.pos[h_pos][0] and \
                   target not in self.hounds and target != self.hare:
                    choices.append((i, target))
        if not choices: return None
        # ウサギに一番近い手を選ぶ
        choices.sort(key=lambda c: abs(self.pos[c[1]][0] - self.pos[self.hare][0]))
        return choices[0]

    def check_winner(self):
        # ウサギ勝利
        if self.pos[self.hare][0] < min(self.pos[h][0] for h in self.hounds):
            messagebox.showinfo("勝利", "ウサギが逃げ切りました！")
            return True
        # 猟犬勝利
        if not [m for m in self.adj[self.hare] if m not in self.hounds]:
            messagebox.showinfo("勝利", "猟犬がウサギを包囲しました！")
            return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = HaresAndHoundsStable(root)
    root.mainloop()
