import pygame
from collections import Counter
import copy
import time

# Initialize pygame
pygame.init()

# Set up the display
width, height = 750, 750 # Increased size for padding
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Giftwrap!")

# Define colors
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (120, 120, 120)
DARKER_GRAY = (80, 80, 80)
BLUE = (0, 0, 255)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 150, 0)
DARK_BLUE = (0, 0, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Calculate square size and board dimensions
square_size = 60
board_width = 8 * square_size
board_height = 8 * square_size
board_x = (width - board_width) // 2
board_y = (height - board_height) // 2

# Assets

p1_gift = pygame.transform.scale(pygame.image.load(("p1_present.png")).convert(), (square_size, square_size))
p2_gift = pygame.transform.scale(pygame.image.load(("p2_present.png")).convert(), (square_size, square_size))
ice_block = pygame.transform.scale(pygame.image.load(("ice_block.png")).convert_alpha(), (square_size, square_size))

logo = pygame.transform.scale(pygame.image.load("logo.png").convert_alpha(), (240, 240))
logo_rect = logo.get_rect(center=(width // 2, (height // 2)-150))
pygame.display.set_icon(logo)

guide = pygame.transform.scale(pygame.image.load("guide.png").convert_alpha(), (1350/2, 450/2))
guide_rect = guide.get_rect(center=(width // 2, (height // 2)-250))

# Sounds
select = pygame.mixer.Sound(("select.wav"))
place = pygame.mixer.Sound(("place.wav"))
win = pygame.mixer.Sound(("win.wav"))

# Create a 2D list to represent the board
board = [['.' for _ in range(8)] for _ in range(8)]
board[3][3] = 'X'
board[4][4] = 'X'
board[3][4] = 'O'
board[4][3] = 'O'

# Game state
p1_turn = True
p2_human = True
current_screen = "title"  # Track the current screen
selected_square = None
running = True
player_input = True
p1_score = 2
p2_score = 2
winner = None

# Buttons
play_2p_button = pygame.Rect(width // 2, height // 2, 400, 50)
play_ai_button = pygame.Rect(width // 2, height // 2, 400, 50)
ice_block_button = pygame.Rect(width // 2, height // 2, 400, 50)
no_ice_block_button = pygame.Rect(width // 2, height // 2, 400, 50)
menu_button = pygame.Rect(width // 2, height // 2, 400, 50)

#Minimax functions
def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm for Giftwrap!

    Args:
        board: The current game board.
        depth: The current depth of the search.
        alpha: The alpha value for alpha-beta pruning.
        beta: The beta value for alpha-beta pruning.
        maximizing_player: True if the current player is maximizing, False otherwise.

    Returns:
        The best score for the current player, and the best move (row, col).
    """

    # Base case: terminal state (no more moves or game over)
    if depth == 0 or is_terminal_node(board):
        return evaluate_board(board), None

    if maximizing_player:
        max_eval = -float('inf')
        best_move = None

        for row in range(8):
            for col in range(8):
                if is_valid_move(board, row, col):
                    # Make a copy of the board to avoid modifying the original
                    temp_board = copy.deepcopy(board)
                    make_move(temp_board, row, col, maximizing_player)
                    eval, _ = minimax(temp_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    if max_eval == eval:
                        best_move = (row, col)

                    if beta <= alpha:
                        break  # Beta cutoff

        return max_eval, best_move

    else:  # Minimizing player
        min_eval = float('inf')
        best_move = None

        for row in range(8):
            for col in range(8):
                if is_valid_move(board, row, col):
                    # Make a copy of the board to avoid modifying the original
                    temp_board = copy.deepcopy(board)
                    make_move(temp_board, row, col, maximizing_player)
                    eval, _ = minimax(temp_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    if min_eval == eval:
                        best_move = (row, col)

                    if beta <= alpha:
                        break  # Alpha cutoff

        return min_eval, best_move

# Helper functions

def is_terminal_node(board):
    """
    Checks if the game is over (no more moves or a winner).
    """
    for row in board:
        if '.' in row:
            return False
    return True

def evaluate_board(board):
    """
    Evaluates the current board state for the maximizing player.
    """
    score = 0
    for row in board:
        count = Counter(row)
        score += count['O']
        score -= count['X']

    return score

def is_valid_move(board, row, col):
    """
    Checks if a move is valid on the board.
    """
    
    adjacent = False

      # Define directions for orthogonal and diagonal checks
    directions = [
      (-1, 0),  # Up
      (1, 0),   # Down
      (0, -1),  # Left
      (0, 1),   # Right
      (-1, -1),  # Top-Left Diagonal
      (-1, 1),   # Top-Right Diagonal
      (1, -1),   # Bottom-Left Diagonal
      (1, 1)    # Bottom-Right Diagonal
    ]
    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        # Check if the new position is within the array bounds
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            if board[new_row][new_col] in ['X', 'O']:
                adjacent = True

    return (board[row][col] == '.' and adjacent)

def make_move(board, row, col, maximizing_player):
    """
    Makes a move on the board.
    """
    board[row][col] = 'O' if maximizing_player else 'X'

    for i in range(max(0, row - 1), min(8, row + 2)):
        for j in range(max(0, col - 1), min(8, col + 2)):
            if i == row and j == col: 
                continue  # Skip the given element itself

            if board[i][j] == 'X':
                board[i][j] = 'O'
            elif board[i][j] == 'O':
                board[i][j] = 'X'


# Function to draw the checkerboard
def draw_board():
    mouse_pos = pygame.mouse.get_pos()

    # Draw "Escape: Menu" text
    font = pygame.font.Font(None, 24)
    text = font.render("Escape: Menu", True, BLACK)
    text_rect = text.get_rect(topleft=(10, height - 30))  # Position at bottom left
    screen.blit(text, text_rect)

    for row in range(8):
        for col in range(8):
            color = LIGHT_GRAY if (row + col) % 2 == 0 else DARK_GRAY
            if row == ((mouse_pos[1] - board_y) // square_size) and col == ((mouse_pos[0] - board_x) // square_size): color = DARKER_GRAY 

            pygame.draw.rect(screen, color, (board_x + col * square_size, board_y + row * square_size, square_size, square_size))
            
            if board[row][col] == 'X':
                screen.blit(p1_gift, (board_x + col * square_size, board_y + row * square_size))

            if board[row][col] == 'O':
                screen.blit(p2_gift, (board_x + col * square_size, board_y + row * square_size))
            
            if board[row][col] == 'B':
                screen.blit(ice_block, (board_x + col * square_size, board_y + row * square_size))
    
    font = pygame.font.Font(None, 36)
    
    text = font.render("Player 1 - Gift Score: " + str(p1_score), True, BLACK)
    text_rect = text.get_rect(center=(width//2, (height//2) - 300))
    screen.blit(text, text_rect)

    text = font.render("Player 2 - Gift Score: " + str(p2_score), True, BLACK)
    text_rect = text.get_rect(center=(width//2, (height//2) + 300))
    screen.blit(text, text_rect)

    if p1_turn:
        text = font.render("Player 1's Turn.", True, DARK_RED)
        text_rect = text.get_rect(center=(width//2, (height//2) - 325))
        screen.blit(text, text_rect)
    elif p2_human:
        text = font.render("Player 2's Turn.", True, DARK_GREEN)
        text_rect = text.get_rect(center=(width//2, (height//2) + 325))
        screen.blit(text, text_rect)
    else:
        text = font.render("Opponent is thinking...", True, DARK_GREEN)
        text_rect = text.get_rect(center=(width//2, (height//2) + 325))
        screen.blit(text, text_rect)

    
    if winner != None:
        win_rect = pygame.Rect(width // 2, height // 2, 800, 50)
        win_rect.center = (width // 2, height // 2)
        pygame.draw.rect(screen, BLACK, win_rect)
        if winner == 1:
            text = font.render("Player 1 Wins! Click to continue.", True, WHITE)
            text_rect = text.get_rect(center=(width//2, height//2))
            screen.blit(text, text_rect)
        elif winner == 2:
            text = font.render("Player 2 Wins! Click to continue.", True, WHITE)
            text_rect = text.get_rect(center=(width//2, height//2))
            screen.blit(text, text_rect)
        elif winner == 3:
            text = font.render("Tie! Click to continue.", True, WHITE)
            text_rect = text.get_rect(center=(width//2, height//2))
            screen.blit(text, text_rect)

def place_gift(row, col):
    global p1_turn, player_input, p1_score, p2_score, winner

    place.play()

    if is_valid_move(board, row, col):
        board[row][col] = 'X' if p1_turn else 'O'

        for i in range(max(0, row - 1), min(8, row + 2)):
            for j in range(max(0, col - 1), min(8, col + 2)):
                if i == row and j == col: 
                    continue  # Skip the given element itself

                if board[i][j] == 'X':
                    board[i][j] = 'O'
                elif board[i][j] == 'O':
                    board[i][j] = 'X'

        p1_turn = not p1_turn
        player_input = False
        p1_score = 0
        p2_score = 0

        for row in board:
            if '.' in row:
                player_input = True
            for space in row:
                if space == 'X': p1_score += 1
                if space == 'O': p2_score += 1

        if not player_input:
            win.play()
            if p1_score > p2_score:
                winner = 1
            elif p1_score < p2_score:
                winner = 2
            else:
                winner = 3

        if not p1_turn and not p2_human:
            player_input = False
            screen.fill(WHITE)
            screen.fill((180, 180, 200))  # Fill background with light gray
            draw_board()
            pygame.display.update() 
            p2_move = minimax(board, 5, -float('inf'), float('inf'), True)
            time.sleep(0.5)
            place.play()
            row = p2_move[1][0]
            col = p2_move[1][1]
            board[row][col] = 'O'

            for i in range(max(0, row - 1), min(8, row + 2)):
                for j in range(max(0, col - 1), min(8, col + 2)):
                    if i == row and j == col: 
                        continue  # Skip the given element itself

                    if board[i][j] == 'X':
                        board[i][j] = 'O'
                    elif board[i][j] == 'O':
                        board[i][j] = 'X'

            p1_score = 0
            p2_score = 0

            for row in board:
                if '.' in row:
                    player_input = True
                for space in row:
                    if space == 'X': p1_score += 1
                    if space == 'O': p2_score += 1

                if not player_input:
                    win.play()
                    if p1_score > p2_score:
                        winner = 1
                    elif p1_score < p2_score:
                        winner = 2
                    else:
                        winner = 3
            
            p1_turn = not p1_turn


def handle_menu_input():
    global current_screen, p2_human
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_2p_button.collidepoint(pygame.mouse.get_pos()):
                current_screen = "howto"
                p2_human = True
                select.play()
            elif play_ai_button.collidepoint(pygame.mouse.get_pos()):
                current_screen = "howto"
                p2_human = False
                select.play()
        
def handle_howto_input():
    global current_screen, p1_turn, p1_score, p2_score, board, winner, player_input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ice_block_button.collidepoint(pygame.mouse.get_pos()):
                current_screen = "game"
                # Create a 2D list to represent the board
                board = [['.' for _ in range(8)] for _ in range(8)]
                board[3][3] = 'X'
                board[4][4] = 'X'
                board[3][4] = 'O'
                board[4][3] = 'O'
                board[1][1] = 'B'
                board[6][6] = 'B'
                board[1][6] = 'B'
                board[6][1] = 'B'
                player_input = True
                p1_turn = True
                p1_score = 0
                p2_score = 0
                winner = None
                select.play()
            elif no_ice_block_button.collidepoint(pygame.mouse.get_pos()):
                current_screen = "game"
                # Create a 2D list to represent the board
                board = [['.' for _ in range(8)] for _ in range(8)]
                board[3][3] = 'X'
                board[4][4] = 'X'
                board[3][4] = 'O'
                board[4][3] = 'O'
                player_input = True
                winner = None
                select.play()
            elif menu_button.collidepoint(pygame.mouse.get_pos()):
                current_screen = "title"
                select.play()
                
# Function to handle player input
def handle_game_input():
    global selected_square, current_screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if player_input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                row = (mouse_pos[1] - board_y) // square_size
                col = (mouse_pos[0] - board_x) // square_size
                if 0 <= row < 8 and 0 <= col < 8:  # Check if click is within board
                    place_gift(row, col)
            elif event.type == pygame.KEYDOWN:
                if selected_square:
                    row, col = selected_square
                    if event.key == pygame.K_UP:
                        row = max(0, row - 1)
                    elif event.key == pygame.K_DOWN:
                        row = min(7, row + 1)
                    elif event.key == pygame.K_LEFT:
                        col = max(0, col - 1)
                    elif event.key == pygame.K_RIGHT:
                        col = min(7, col + 1)
                    if event.key == pygame.K_RETURN:
                        place_gift(selected_square[0], selected_square[1])
                    if event.key == pygame.K_ESCAPE:
                        current_screen = "title"
                    selected_square = (row, col)
                else:
                    selected_square = (0, 0)
        else:     
            if event.type == pygame.MOUSEBUTTONDOWN and winner != None:
                current_screen = "title"

# Function to highlight the selected square
def highlight_selected():
    if selected_square:
        row, col = selected_square
        pygame.draw.rect(screen, BLUE, (board_x + col * square_size, board_y + row * square_size, square_size, square_size), 4)

# Function to display title screen
def draw_title_screen():
    screen.blit(logo, logo_rect)

    font = pygame.font.Font(None, 24)
    text = font.render("Made by r3sgame", True, BLACK)
    text_rect = text.get_rect(topleft=(10, height - 30))  # Position at bottom left
    screen.blit(text, text_rect)

    font = pygame.font.Font(None, 72)
    text = font.render("Giftwrap!", True, BLACK)
    text_rect = text.get_rect(center=(width//2, height//2))
    screen.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    play_2p_button.center = (width // 2, (height // 2)+75)
    pygame.draw.rect(screen, BLACK, play_2p_button)
    text = font.render("Play with a Friend", True, WHITE)
    text_rect = text.get_rect(center=play_2p_button.center)
    screen.blit(text, text_rect)

    play_ai_button.center = (width // 2, (height // 2)+150)
    pygame.draw.rect(screen, BLACK, play_ai_button)
    text = font.render("Play with Insane AI Santa", True, WHITE)
    text_rect = text.get_rect(center=play_ai_button.center)
    screen.blit(text, text_rect)

# Function to display how-to-play screen
def draw_how_to_play_screen():
    screen.blit(guide, guide_rect)

    font = pygame.font.Font(None, 36)
    instructions = [
        "How to Play:",
        "1. Take turns placing gifts on the board; CLICK on a space to place gifts.",
        "2. You can also place gifts with the ARROW KEYS and ENTER.",
        "3. Gifts must be placed adjacent to an existing gift.",
        "4. When a gift is placed, all adjacent gifts switch player possession.",
        "5. Gifts cannot be placed on ice blocks, and ice blocks cannot switch.",
        "6. The player with the most gifts on the board at the end wins!"
    ]
    for i, line in enumerate(instructions):
        text = font.render(line, True, BLACK)
        text_rect = text.get_rect(center=(width//2, height//2 -100 + i*30))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 30)
    
    ice_block_button.center = (width // 2, (height // 2)+150)
    pygame.draw.rect(screen, BLACK, ice_block_button)
    text = font.render("Play with Ice Blocks", True, WHITE)
    text_rect = text.get_rect(center=ice_block_button.center)
    screen.blit(text, text_rect)

    no_ice_block_button.center = (width // 2, (height // 2)+225)
    pygame.draw.rect(screen, BLACK, no_ice_block_button)
    text = font.render("Play without Ice Blocks", True, WHITE)
    text_rect = text.get_rect(center=no_ice_block_button.center)
    screen.blit(text, text_rect)

    menu_button.center = (width // 2, (height // 2)+300)
    pygame.draw.rect(screen, BLACK, menu_button)
    text = font.render("Menu", True, WHITE)
    text_rect = text.get_rect(center=menu_button.center)
    screen.blit(text, text_rect)

while running:
    pygame.event.get()
    screen.fill((180, 180, 200))  # Fill background with light gray
    if current_screen == "title":
        draw_title_screen()
        handle_menu_input()
    elif current_screen == "howto":
        draw_how_to_play_screen()
        handle_howto_input()
    elif current_screen == "game":
        draw_board()
        handle_game_input()
        highlight_selected()
    pygame.display.update()