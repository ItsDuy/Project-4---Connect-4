import sys
import argparse
from typing import List, Optional, Tuple

import pygame
from pygame import Rect
from SoundManager import SoundManager
from network import Network


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
    player1_color = (255, 66, 66)  # red
    player2_color = (255, 221, 87)  # yellow
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


def get_col_from_mouse(x: int) -> int:
    return min(max(x // ConnectFour.cell_size, 0), ConnectFour.cols - 1)


def game_loop(net: 'Network', my_player: int) -> None:
    pygame.init()
    pygame.display.set_caption(ConnectFour.title)
    screen = pygame.display.set_mode((ConnectFour.width, ConnectFour.height))
    clock = pygame.time.Clock()

    # Initialize and start background music
    sound = SoundManager()
    sound.play_bgm()

    board = create_board()
    game_over = False
    winner: Optional[int] = None
    turn = ConnectFour.player1
    started = False

    # If player 2, wait for player 1’s first move
    if my_player == ConnectFour.player2:
        turn = ConnectFour.player1
    
    def send_move(col):
        try:
            net.send(f"MOVE:{col}")
        except Exception as e:
            print(f"Failed to send move: {e}")

    

    while True:
        msg = net.get_message()
        if msg:
            if msg.startswith("MOVE:"):
                col = int(msg.split(":")[1])
                opp_piece = ConnectFour.player1 if my_player == ConnectFour.player2 else ConnectFour.player2
                row = get_next_open_row(board, col)
                if row is not None:
                    drop_piece(board, row, col, opp_piece)
                    sound.play_sfx()
                    if winning_move(board, opp_piece):
                        game_over = True
                        winner = opp_piece
                    elif is_draw(board):
                        game_over = True
                    else:
                        turn = my_player
            
            elif msg == "LEFT":
                quit_msgs = ["Opponent disconnected.", "Opponent chickened out.", "Opponent lost their wifi.", "You scared them to disconnection!"]
                from random import randrange
                print(quit_msgs[randrange(0, len(quit_msgs), 1)])
            elif msg == "RESET":
                board = create_board()
                game_over = False
                winner = None
                turn = ConnectFour.player1
            elif msg == "QUIT":
                break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    sound.cleanup()
                finally:
                    net.send("QUIT")
                    net.close()
                    pygame.quit()
                    sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                col = get_col_from_mouse(event.pos[0])
                if turn == my_player:
                    row = get_next_open_row(board, col)
                    if row is not None:
                        drop_piece(board, row, col, my_player)
                        # Play move sound for every valid move
                        sound.play_sfx()
                        send_move(col)
                        if winning_move(board, my_player):
                            game_over = True
                            winner = my_player
                        elif is_draw(board):
                            game_over = True
                            winner = None
                        else:
                            turn = ConnectFour.player2 if my_player == 1 else ConnectFour.player1
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Restart
                    board = create_board()
                    game_over = False
                    winner = None
                    turn = randrange(1, 3, 1)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    try:
                        sound.cleanup()
                    finally:
                        net.send("QUIT")
                        net.close()
                        pygame.quit()
                        sys.exit(0)

        draw_board(screen, board)
        if game_over:
            if winner is None:
                render_text(screen, "Draw! Press R to restart", ConnectFour.text_color, ConnectFour.cell_size // 2)
            elif winner == my_player:
                color = ConnectFour.player1_color if winner == ConnectFour.player1 else ConnectFour.player2_color
                render_text(screen, "You win!", color, ConnectFour.cell_size // 2)
            else:
                color = ConnectFour.player1_color if winner == ConnectFour.player1 else ConnectFour.player2_color
                render_text(screen, "You lost!", color, ConnectFour.cell_size // 2)
        else:
            color = ConnectFour.player1_color if turn == ConnectFour.player1 else ConnectFour.player2_color
            if turn == my_player:
                render_text(screen, "Your turn. Select a column to drop", color, ConnectFour.cell_size // 2)
            else:
                render_text(screen, "Opponent's turn. Be patient.", color, ConnectFour.cell_size // 2)
        
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

