from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ui import View, Button

class MiniBoardView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game
        self.create_buttons()
        # self.totalboardswon=0

    def create_buttons(self):
        for i in range(3):
            for j in range(3):
                board_idx = 3 * i + j
                is_won = self.game.global_board[board_idx] != ' '  # Check if the board is won
                button = Button(
                    label=f"Board {board_idx + 1}",
                    style=discord.ButtonStyle.primary if not is_won else discord.ButtonStyle.secondary,
                    row=i,
                    custom_id=f"board-{board_idx}",
                    disabled=is_won,  # Disable button if the board is won
                )
                if is_won:
                    button.callback = self.board_won_message  # Assign a callback for won boards
                else:
                    button.callback = self.board_button_callback
                self.add_item(button)
    async def board_won_message(self, interaction: discord.Interaction):
        # Show a message when a user clicks on a won board
        await interaction.response.send_message("This board is already won. Please choose another board.", ephemeral=True)

    async def board_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
        custom_id = interaction.data["custom_id"]
        board_idx = int(custom_id.split("-")[1])
        self.game.board.save_board(filename="board.png", active_board_idx=board_idx)
        # Switch to CellView for the selected mini-board
        await interaction.response.edit_message(
            content=f"Mini-board {board_idx + 1} {self.game.current_player.mention}'s turn",
            view=CellView(self.game, board_idx),
            attachments=[discord.File("board.png")],
        )

class CellView(View):
    def __init__(self, game, board_idx):
        super().__init__(timeout=None)
        self.game = game
        self.board_idx = board_idx
        self.create_buttons()

    def create_buttons(self):
        for i in range(3):
            for j in range(3):
                button = Button(label="-", style=discord.ButtonStyle.secondary, row=i, custom_id=f"cell-{self.board_idx}-{3*i+j}")
                button.callback = self.cell_button_callback
                self.add_item(button)

    async def cell_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
        custom_id = interaction.data["custom_id"]
        # print(f'custom id {custom_id}')
        _, board_idx, cell_idx = custom_id.split("-")
        board_idx, cell_idx = int(board_idx), int(cell_idx)
        # print(f"{board_idx}  {cell_idx} line 44")
        move=self.game.make_move(board_idx,cell_idx)

        if move>=0:
            # self.clear_items
            await interaction.response.edit_message(content=f"Mini-board {move+1} {self.game.current_player.mention}'s turn ", view=CellView(self.game, move),attachments=[discord.File("board.png")])
            return
        if move==-2:
            # self.clear_items
            await interaction.response.send_message("Cell occupied, choose another.",ephemeral=True)
            await interaction.response.edit_message(content=f"Mini-board {board_idx+1} {self.game.current_player.mention}'s turn", view=CellView(self.game, board_idx),attachments=[discord.File("board.png")])
            return
        if move==-3:
            self.clear_items()
            await interaction.response.edit_message(content=f"{self.game.current_player.mention} wins!", attachments=[discord.File("board.png")],view=self)
            return
        if move==-4:
            self.clear_items()
            await interaction.response.edit_message(content=f"It's a draw!",attachments=[discord.File("board.png")],view=self)
            return
        if not move:
            await interaction.response.send_message("Invalid move!", ephemeral=True)
            return
        # Update button label
        player_symbol = "X" if self.game.current_player == self.game.player1 else "O"
        for child in self.children:
            if child.custom_id == custom_id:
                child.label = player_symbol
                child.disabled = True
                break

        # Save updated board image and return to mini-board view
        await interaction.response.edit_message(
            content=f"Back to mini-board selection {self.game.current_player.mention}'s turn", 
            attachments=[discord.File("board.png")], 
            view=MiniBoardView(self.game)
        )

class UltimateTicTacToeImage:
    def __init__(self):
        self.cell_size = 50  # Size of each cell
        self.board_size = self.cell_size * 9  # Total size of the board
        self.line_width = 3  # Line width for grid
        self.board = [[" " for _ in range(9)] for _ in range(9)]  # Empty board
        self.base_image=self.initialize_board()
        self.image = self.base_image.copy()
        # self.mini_boards = [" " for _ in range(9)]
    
    def initialize_board(self):
        self.base_image = Image.new("RGB", (self.board_size, self.board_size), "black")
        draw = ImageDraw.Draw(self.base_image)
    
        # Draw the grid
        for i in range(1, 9):
            line_width = self.line_width if i % 3 == 0 else 1  # Thicker lines for larger grid
            # Vertical lines
            draw.line(
                [(i * self.cell_size, 0), (i * self.cell_size, self.board_size)],
                fill="white",
                width=line_width,
            )
            # Horizontal lines
            draw.line(
                [(0, i * self.cell_size), (self.board_size, i * self.cell_size)],
                fill="white",
                width=line_width,
            )
        return self.base_image
    def update_symbol(self, row, col, symbol):
    # Copy the base image
        # self.image = self.base_image.copy()
        draw = ImageDraw.Draw(self.base_image)
    
        # font = ImageFont.load_default(size=self.cell_size//2)
        font = ImageFont.truetype("toe/ldfcomicsans-font/Ldfcomicsansbold-zgma.ttf", self.cell_size//2)
        text_x = col * self.cell_size + self.cell_size // 3
        text_y = row * self.cell_size + self.cell_size // 4
        fill = "red" if symbol == "X" else "blue"
    
    # Draw the symbol
        offsets = [(-1 , -1), (1, -1), (-1, 1), (1, 1)]  # Top-left, top-right, etc.
        for dx, dy in offsets:
            draw.text((text_x + dx, text_y + dy), symbol, fill, font=font)
        return self.base_image
    
    def highlight_active_board(self, active_board_idx):
        self.image = self.base_image.copy()
        draw = ImageDraw.Draw(self.image)

        if active_board_idx is not None:
            # Calculate row and column of the mini-board
            board_row, board_col = divmod(active_board_idx, 3)
        
            # Calculate the coordinates of the highlight box
            highlight_x1 = board_col * self.cell_size * 3
            highlight_y1 = board_row * self.cell_size * 3
            highlight_x2 = highlight_x1 + self.cell_size * 3
            highlight_y2 = highlight_y1 + self.cell_size * 3
        
        # Draw the highlight rectangle
            draw.rectangle(
                [(highlight_x1, highlight_y1), (highlight_x2, highlight_y2)],
                outline="yellow", width=5
            )
        return self.image
    def markboardwon(self,won_board_row,won_board_col,symbol):
        draw = ImageDraw.Draw(self.base_image)
        font = ImageFont.truetype("toe/ldfcomicsans-font/Ldfcomicsansbold-zgma.ttf", (self.cell_size)*2.2)
        if symbol=="X":
            fill = "red"
            x_offset=self.cell_size*3//4
            y_offset=self.cell_size//4
        elif symbol=="O":
            fill ="blue"
            x_offset=self.cell_size*3//4
            y_offset=self.cell_size//4
        else:
            fill="green"
            x_offset=self.cell_size*3//4
            y_offset=self.cell_size//4
        text_x = won_board_col * 3 * self.cell_size + x_offset
        text_y = won_board_row * 3 * self.cell_size + y_offset
        
    
    # Draw the symbol
        offsets = [(-1 , -1), (1, -1), (-1, 1), (1, 1)]  # Top-left, top-right, etc.
        for dx, dy in offsets:
            draw.text((text_x + dx, text_y + dy), symbol, fill, font=font)
        return self.base_image

    def dim_mini_board(self,mini_board_idx, dim_color=(0, 0, 0, 200)):
        draw = ImageDraw.Draw(self.base_image, "RGBA")  # Use RGBA mode for transparency
        cell_size = 50
        mini_board_size = cell_size * 3

        # Calculate coordinates of the mini-board
        board_row, board_col = divmod(mini_board_idx, 3)
        x1 = board_col * mini_board_size+2
        y1 = board_row * mini_board_size+2
        x2 = x1 + mini_board_size-4
        y2 = y1 + mini_board_size-4

        # Overlay a semi-transparent rectangle
        draw.rectangle([(x1, y1), (x2, y2)], fill=dim_color)

    def update_cell(self, x, y, symbol):
        # Update the board with a symbol at (x, y)
        if self.board[x][y] == " ":
            self.board[x][y] = symbol
            self.update_symbol(x,y,symbol)
        else:
            raise ValueError("Cell is already occupied!")
    def save_board(self, filename="board.png", active_board_idx=None):
        # Save the current board as an image with the active board highlighted
        if self.image:
            self.highlight_active_board(active_board_idx)
            self.image.save(filename)

class UltimateTicTacToe:
    def __init__(self,player1,player2):
        # Initialize a 3x3 board of 3x3 boards
        self.boards = [[[' ' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.global_board = [' ' for _ in range(9)]  # Tracks the status of each sub-board
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        # self.current_player = 'X'
        self.next_board = None  # Determines which board the player must play on
        self.board = UltimateTicTacToeImage()
        self.board.save_board(filename="board.png", active_board_idx=self.next_board)

    def is_cell_occupied(self, board_idx, cell_idx):
        """Check if a cell in a specific board is occupied."""
        return self.boards[board_idx][cell_idx // 3][cell_idx % 3] != " "
    
    def check_winner(self, board,boardtype):
        """Check if a player has won a local or global board."""
        # Check rows, columns, and diagonals
        for i in range(3):
            if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] != ' ' and board[i * 3] != 'D':  # Rows
                return board[i * 3]
            if board[i] == board[i + 3] == board[i + 6] != ' ' and board[i] != 'D':  # Columns
                return board[i]
    
        # Check diagonals
        if board[0] == board[4] == board[8] != ' ' and board[0] != 'D':  # Diagonal
            return board[0]
        if board[2] == board[4] == board[6] != ' ' and board[2] != 'D':  # Anti-diagonal
            return board[2]
        if boardtype == 'global' and all(cell != ' ' for cell in board):
            x_count = board.count('X')
            o_count = board.count('O')
            if x_count > o_count:
                return 'X'  # Player 'X' wins based on more filled cells
            elif o_count > x_count:
                return 'O'  # Player 'O' wins based on more filled cells
            else:
                return 'D'  # It's a draw if both have equal filled cells
        # If there are no valid winner lines (and no 'D' in rows or columns), check for draw condition
        if all(cell != ' ' for cell in board):
            return 'D'  # 'D' stands for Draw
    
        return None
    

    def make_move(self, board_idx, cell_idx):
        """Attempt to make a move on the specified board and cell."""
        board_row, board_col = divmod(board_idx, 3)
        cell_row, cell_col = divmod(cell_idx, 3)

        if self.global_board[board_idx] != ' ':
            print("This board has already been won. Choose another!")
            return -3

        if self.boards[board_idx][cell_idx // 3][cell_idx % 3] != ' ':
            print("Cell already occupied. Choose another!")
            return -2

        # Make the move
        if self.current_player==self.player1:
            char='X'
        else:
            char='O'
        self.boards[board_idx][cell_idx // 3][cell_idx % 3] = char
        self.board.update_cell(board_row * 3 + cell_row, board_col * 3 + cell_col, char)

        # Save updated board

        # Check if this sub-board is now won
        flat_board = [cell for row in self.boards[board_idx] for cell in row]
        winner = self.check_winner(flat_board,'miniboard')
        if winner:
            self.global_board[board_idx] = winner
            self.board.dim_mini_board(board_idx)
            self.board.markboardwon(board_row,board_col,winner)
        # Check if the global board is won
        global_winner = self.check_winner(self.global_board,'global')
        
        if global_winner:
            self.board.save_board(filename="board.png", active_board_idx=self.next_board)
            if global_winner=='X':
                self.current_player=self.player1
            elif global_winner=='D':
                return -4
            else:
                self.current_player=self.player2
            return -3

        # Switch players
        self.current_player = self.player2 if self.current_player ==self.player1 else self.player1
        # Update the next board
        if self.global_board[cell_idx] == ' ':  # If the next board is still active
            self.next_board = cell_idx
        else:
            self.next_board = -1  # Player can choose any board
        
        self.board.save_board(filename="board.png", active_board_idx=self.next_board)
        return self.next_board
