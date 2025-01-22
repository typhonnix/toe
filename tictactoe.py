# # tictactoe.py
import discord
from discord.ui import Button, View

class TicTacToeButton(Button):
    def __init__(self, x, y, game):
        super().__init__(label="-", style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        symbol = "X" if self.game.current_player == self.game.player1 else "O"
        self.label = symbol
        self.disabled = True
        self.style = discord.ButtonStyle.success if symbol == "X" else discord.ButtonStyle.danger
        self.game.board[self.x][self.y] = symbol

        if self.game.check_winner(symbol):
            if self.view is not None:
                for child in self.view.children:
                    child.disabled = True
                await interaction.response.edit_message(content=f"{self.game.current_player.mention} wins!", view=self.view)
            return

        if self.game.is_draw():
            if self.view is not None:
                for child in self.view.children:
                    child.disabled = True
                await interaction.response.edit_message(content="It's a draw!", view=self.view)
            return

        self.game.switch_player()
        await interaction.response.edit_message(content=f"It's {self.game.current_player.mention}'s turn.", view=self.view)


class TicTacToeGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[" " for _ in range(3)] for _ in range(3)]

    def check_winner(self, symbol):
        for row in self.board:
            if all(cell == symbol for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == symbol for row in range(3)):
                return True
        if all(self.board[i][i] == symbol for i in range(3)) or all(self.board[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def is_draw(self):
        return all(cell != " " for row in self.board for cell in row)

    def switch_player(self):
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2


class TicTacToeView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, game))

# class TicTacToe:
#     def __init__(self, player1, player2):
#         self.board = [" " for _ in range(9)]
#         self.current_player = player1
#         self.other_player = player2
#         self.player1 = player1  # Store player1 explicitly
#         self.player2 = player2  # Store player2 explicitly
#         self.winner = None

#     def make_move(self, position):
#         if self.board[position] == " ":
#             # Use self.player1 for comparison
#             self.board[position] = "X" if self.current_player == self.player1 else "O"
#             self.check_winner()
#             self.switch_player()
#             return True
#         return False

#     def check_winner(self):
#         win_positions = [
#             (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
#             (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
#             (0, 4, 8), (2, 4, 6)              # Diagonals
#         ]
#         for a, b, c in win_positions:
#             if self.board[a] == self.board[b] == self.board[c] and self.board[a] != " ":
#                 self.winner = self.current_player
#                 return

#     def switch_player(self):
#         self.current_player, self.other_player = self.other_player, self.current_player

#     def render_board(self):
#         return f"""
#         {self.board[0]} | {self.board[1]} | {self.board[2]}
#         ---------
#         {self.board[3]} | {self.board[4]} | {self.board[5]}
#         ---------
#         {self.board[6]} | {self.board[7]} | {self.board[8]}
#         """
