import sys
import argparse
from typing import List, Optional, Tuple

import pygame
from pygame import Rect
from SoundManager import SoundManager


class ConnectFour:
    rows = 6
    cols = 7
    empty_cell = 0
    player1 = 1
    player2 = 2
    cell_size = 100

    # Colors (RGB)
    bg_color = (25, 25, 30)
    board_color = (0, 102, 204)
    hole_color = (10, 10, 15)
    player1_color = (255, 66, 66)       # red
    player2_color = (255, 221, 87)      # yellow
    highlight_color = (55, 200, 120)
    text_color = (240, 240, 240)

    winning_length = 4
    title = "Connect Four"
    fps = 60

    # Derived sizes
    top_bar_rows = 1  # one extra row height for status text (no hover indicator)
    width = cols * cell_size
    height = (rows + top_bar_rows) * cell_size
    board_rect = Rect(0, cell_size, width, rows * cell_size)


Board = List[List[int]]


def create_board() -> Board:
    return [[ConnectFour.empty_cell for _ in range(ConnectFour.cols)] for _ in range(ConnectFour.rows)]


def get_next_open_row(board: Board, col: int) -> Optional[int]:
    if not 0 <= col < ConnectFour.cols:
        return None
    for r in range(ConnectFour.rows - 1, -1, -1):
        if board[r][col] == ConnectFour.empty_cell:
            return r
    return None


def drop_piece(board: Board, row: int, col: int, piece: int) -> None:
    board[row][col] = piece


def winning_move(board: Board, piece: int) -> bool:
    R, C, W = ConnectFour.rows, ConnectFour.cols, ConnectFour.winning_length

    # Horizontal
    for r in range(R):
        count = 0
        for c in range(C):
            count = count + 1 if board[r][c] == piece else 0
            if count >= W:
                return True

    # Vertical
    for c in range(C):
        count = 0
        for r in range(R):
            count = count + 1 if board[r][c] == piece else 0
            if count >= W:
                return True

    # Diagonals (\)
    for r in range(R):
        for c in range(C):
            if all(
                0 <= r + i < R
                and 0 <= c + i < C
                and board[r + i][c + i] == piece
                for i in range(W)
            ):
                return True

    # Diagonals (/)
    for r in range(R):
        for c in range(C):
            if all(
                0 <= r - i < R
                and 0 <= c + i < C
                and board[r - i][c + i] == piece
                for i in range(W)
            ):
                return True

    return False


def is_draw(board: Board) -> bool:
    return all(board[0][c] != ConnectFour.empty_cell for c in range(ConnectFour.cols))


def draw_board(screen: pygame.Surface, board: Board) -> None:
    screen.fill(ConnectFour.bg_color)

    # Board background
    pygame.draw.rect(screen, ConnectFour.board_color, ConnectFour.board_rect, border_radius=8)

    # Cells
    for r in range(ConnectFour.rows):
        for c in range(ConnectFour.cols):
            cx = c * ConnectFour.cell_size + ConnectFour.cell_size // 2
            cy = (r + 1) * ConnectFour.cell_size + ConnectFour.cell_size // 2
            center = (cx, cy)
            # Holes
            pygame.draw.circle(screen, ConnectFour.hole_color, center, ConnectFour.cell_size // 2 - 8)
            # Pieces
            if board[r][c] == ConnectFour.player1:
                pygame.draw.circle(screen, ConnectFour.player1_color, center, ConnectFour.cell_size // 2 - 12)
            elif board[r][c] == ConnectFour.player2:
                pygame.draw.circle(screen, ConnectFour.player2_color, center, ConnectFour.cell_size // 2 - 12)


def render_text(screen: pygame.Surface, text: str, color: Tuple[int, int, int], y: int) -> None:
    font = pygame.font.SysFont(None, 48)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(ConnectFour.width // 2, y))
    screen.blit(surf, rect)


def draw_button(screen: pygame.Surface, text: str, rect: Rect, mouse_pos: Tuple[int, int]) -> Rect:
    """Draw a button and return its rect. Returns the same rect for convenience."""
    is_hover = rect.collidepoint(mouse_pos)
    bg_color = ConnectFour.highlight_color if is_hover else (60, 60, 70)
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    font = pygame.font.SysFont(None, 32)
    label = font.render(text, True, ConnectFour.text_color)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


def get_col_from_mouse(x: int) -> int:
    return min(max(x // ConnectFour.cell_size, 0), ConnectFour.cols - 1)


def game_loop() -> None:
    pygame.init()
    pygame.display.set_caption(ConnectFour.title)
    screen = pygame.display.set_mode((ConnectFour.width, ConnectFour.height))
    clock = pygame.time.Clock()

    # Initialize and start background music
    sound = SoundManager()
    sound.play_bgm()

    board = create_board()
    turn = ConnectFour.player1
    game_over = False
    winner: Optional[int] = None

    # Back to menu button
    button_width, button_height = 150, 40
    button_x = ConnectFour.width - button_width - 10
    button_y = 10
    menu_button_rect = Rect(button_x, button_y, button_width, button_height)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    sound.cleanup()
                finally:
                    pygame.quit()
                    sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                # Check if menu button was clicked
                if menu_button_rect.collidepoint(event.pos):
                    sound.cleanup()
                    # Clear screen before returning to avoid game screen showing through
                    screen.fill(ConnectFour.bg_color)
                    pygame.display.flip()
                    return  # Return to main menu
                # Handle game move (only if not clicking button and game not over)
                if not game_over:
                    col = get_col_from_mouse(event.pos[0])
                    row = get_next_open_row(board, col)
                    if row is not None:
                        drop_piece(board, row, col, turn)
                        # Play move sound for every valid move
                        sound.play_sfx()
                        if winning_move(board, turn):
                            game_over = True
                            winner = turn
                        elif is_draw(board):
                            game_over = True
                            winner = None
                        else:
                            turn = ConnectFour.player2 if turn == ConnectFour.player1 else ConnectFour.player1
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    # Return to main menu
                    sound.cleanup()
                    # Clear screen before returning to avoid game screen showing through
                    screen.fill(ConnectFour.bg_color)
                    pygame.display.flip()
                    return
                if game_over and event.key == pygame.K_r:
                    # Restart
                    board = create_board()
                    game_over = False
                    winner = None
                    turn = ConnectFour.player1

        draw_board(screen, board)
        
        # Draw back to menu button
        draw_button(screen, "Back to Menu", menu_button_rect, mouse_pos)
        
        if game_over:
            if winner is None:
                render_text(screen, "Draw! Press R to restart", ConnectFour.text_color, ConnectFour.cell_size // 2)
            else:
                color = ConnectFour.player1_color if winner == ConnectFour.player1 else ConnectFour.player2_color
                render_text(screen, f"Player {winner} wins! Press R", color, ConnectFour.cell_size // 2)
        else:
            turn_text = f"Turn: Player {turn}"
            color = ConnectFour.player1_color if turn == ConnectFour.player1 else ConnectFour.player2_color
            render_text(screen, turn_text, color, ConnectFour.cell_size // 2)

        pygame.display.flip()
        clock.tick(ConnectFour.fps)


def self_test() -> None:
    # Horizontal win
    b = create_board()
    for c in range(4):
        b[5][c] = ConnectFour.player1
    assert winning_move(b, ConnectFour.player1)

    # Vertical win
    b = create_board()
    for r in range(3, -1, -1):
        b[r][2] = ConnectFour.player2
    assert winning_move(b, ConnectFour.player2)

    # Diagonal \
    b = create_board()
    b[5][0] = b[4][1] = b[3][2] = b[2][3] = ConnectFour.player1
    assert winning_move(b, ConnectFour.player1)

    # Diagonal /
    b = create_board()
    b[2][0] = b[3][1] = b[4][2] = b[5][3] = ConnectFour.player2
    assert winning_move(b, ConnectFour.player2)

    # No win draw check
    b = create_board()
    assert not is_draw(b)

    print("Self-tests passed.")


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(description="Connect Four Game")
    parser.add_argument("--test", action="store_true", help="run logic self-tests and exit")
    args = parser.parse_args(argv)

    if args.test:
        self_test()
        return

    game_loop()


if __name__ == "__main__":
    main()

