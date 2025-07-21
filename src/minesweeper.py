import discord
from discord import ui
import random

class MineButton(ui.Button):
    def __init__(self, x, y, board, minesweeper_view):
        super().__init__(style=discord.ButtonStyle.secondary, label="_", row=y)
        self.x = x
        self.y = y
        self.board = board
        self.minesweeper_view = minesweeper_view

    async def callback(self, interaction: discord.Interaction):
        if self.minesweeper_view.game_over:
            await interaction.response.send_message("ゲームは終了しています。", ephemeral=True)
            return

        if self.minesweeper_view.revealed[self.y][self.x]:
            await interaction.response.defer()
            return

        self.minesweeper_view.revealed[self.y][self.x] = True

        if self.board[self.y][self.x] == -1:
            self.style = discord.ButtonStyle.danger
            self.label = "💣"
            self.minesweeper_view.game_over = True
            await interaction.response.edit_message(view=self.minesweeper_view)
            await interaction.followup.send("💥 爆弾を踏みました！ゲームオーバー！", ephemeral=False)
            self.minesweeper_view.disable_all_buttons()
            await interaction.edit_original_response(view=self.minesweeper_view)
            return
        else:
            count = self.minesweeper_view.count_adjacent_mines(self.x, self.y)
            self.style = discord.ButtonStyle.success if count == 0 else discord.ButtonStyle.secondary
            self.label = "・" if count == 0 else str(count)  # 空白の代わりに「・」
            if self.minesweeper_view.check_victory():
                self.minesweeper_view.game_over = True
                self.minesweeper_view.disable_all_buttons()
                await interaction.response.edit_message(view=self.minesweeper_view)
                await interaction.followup.send("🎉 おめでとうございます！クリアしました！", ephemeral=False)
                return
            await interaction.response.edit_message(view=self.minesweeper_view)

class MinesweeperView(ui.View):
    def __init__(self, size=5, mines=5):
        super().__init__(timeout=None)
        self.size = size
        self.mines = mines
        self.game_over = False
        self.board = self.create_board()
        self.revealed = [[False]*size for _ in range(size)]

        for y in range(size):
            for x in range(size):
                self.add_item(MineButton(x, y, self.board, self))

    def create_board(self):
        board = [[0]*self.size for _ in range(self.size)]
        mines_placed = 0
        while mines_placed < self.mines:
            rx = random.randint(0, self.size-1)
            ry = random.randint(0, self.size-1)
            if board[ry][rx] == -1:
                continue
            board[ry][rx] = -1
            mines_placed += 1
        return board

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.board[ny][nx] == -1:
                        count += 1
        if self.board[y][x] == -1:
            count -= 1
        return count

    def disable_all_buttons(self):
        for child in self.children:
            child.disabled = True

    def check_victory(self):
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] != -1 and not self.revealed[y][x]:
                    return False
        return True
