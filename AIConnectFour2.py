import sys
import random
from typing import List, Optional, Tuple

import pygame

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from SoundManager import SoundManager


Board = List[List[int]]


# ---- AI evaluation helpers (Different strategy: More aggressive) ----
def get_valid_locations(board: Board) -> List[int]:
	return [c for c in range(C4.cols) if board[0][c] == C4.empty_cell]


def is_terminal_node(board: Board) -> bool:
	return CF.winning_move(board, C4.player1) or CF.winning_move(board, C4.player2) or CF.is_draw(board)


def evaluate_window(window: List[int], piece: int) -> int:
	"""More aggressive evaluation - prioritizes offense over defense"""
	opp_piece = C4.player1 if piece == C4.player2 else C4.player2
	score = 0

	count_piece = window.count(piece)
	count_opp = window.count(opp_piece)
	count_empty = window.count(C4.empty_cell)

	# Winning/forcing patterns (more aggressive scoring)
	if count_piece == 4:
		score += 100000
	elif count_piece == 3 and count_empty == 1:
		score += 150  # Higher than AI1 (was 100)
	elif count_piece == 2 and count_empty == 2:
		score += 20   # Higher than AI1 (was 12)
	elif count_piece == 1 and count_empty == 3:
		score += 3    # Bonus for potential threats

	# Defensive (less urgent than AI1)
	if count_opp == 3 and count_empty == 1:
		score -= 100  # Less urgent than AI1 (was -120)
	elif count_opp == 2 and count_empty == 2:
		score -= 8    # Less urgent than AI1 (was -10)

	return score


def score_position(board: Board, piece: int) -> int:
	"""More aggressive position scoring"""
	score = 0

	# Center column priority (stronger than AI1)
	center_col = C4.cols // 2
	center_array = [board[r][center_col] for r in range(C4.rows)]
	score += center_array.count(piece) * 10  # Higher than AI1 (was 6)

	# Also favor columns adjacent to center
	for offset in [1, -1]:
		adj_col = center_col + offset
		if 0 <= adj_col < C4.cols:
			adj_array = [board[r][adj_col] for r in range(C4.rows)]
			score += adj_array.count(piece) * 4

	# Horizontal
	for r in range(C4.rows):
		row_array = [board[r][c] for c in range(C4.cols)]
		for c in range(C4.cols - 3):
			window = row_array[c : c + 4]
			score += evaluate_window(window, piece)

	# Vertical
	for c in range(C4.cols):
		col_array = [board[r][c] for r in range(C4.rows)]
		for r in range(C4.rows - 3):
			window = col_array[r : r + 4]
			score += evaluate_window(window, piece)

	# Diagonal /
	for r in range(3, C4.rows):
		for c in range(C4.cols - 3):
			window = [board[r - i][c + i] for i in range(4)]
			score += evaluate_window(window, piece)

	# Diagonal \
	for r in range(C4.rows - 3):
		for c in range(C4.cols - 3):
			window = [board[r + i][c + i] for i in range(4)]
			score += evaluate_window(window, piece)

	return score


def copy_board(board: Board) -> Board:
	return [row[:] for row in board]


def order_moves_by_heuristic(valid_cols: List[int]) -> List[int]:
	"""Different move ordering: prefer center but also consider edge columns"""
	center = C4.cols // 2
	# Prefer center, then adjacent, then edges
	return sorted(valid_cols, key=lambda c: (
		abs(c - center),  # Distance from center
		abs(c - center) > 2  # Prefer center region
	))


def simulate_drop(board: Board, col: int, piece: int) -> Optional[Board]:
	row = CF.get_next_open_row(board, col)
	if row is None:
		return None
	nb = copy_board(board)
	CF.drop_piece(nb, row, col, piece)
	return nb


def minimax(board: Board, depth: int, alpha: int, beta: int, maximizing: bool, ai_piece: int) -> Tuple[int, Optional[int]]:
	opp_piece = C4.player1 if ai_piece == C4.player2 else C4.player2

	terminal = is_terminal_node(board)
	if depth == 0 or terminal:
		if terminal:
			if CF.winning_move(board, ai_piece):
				return 1_000_000, None
			elif CF.winning_move(board, opp_piece):
				return -1_000_000, None
			else:
				return 0, None  # draw
		else:
			return score_position(board, ai_piece), None

	valid_cols = get_valid_locations(board)
	if not valid_cols:
		return 0, None

	best_col: Optional[int] = None

	if maximizing:
		value = -10**9
		for col in order_moves_by_heuristic(valid_cols):
			child = simulate_drop(board, col, ai_piece)
			if child is None:
				continue
			new_score, _ = minimax(child, depth - 1, alpha, beta, False, ai_piece)
			if new_score > value:
				value = new_score
				best_col = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return value, best_col
	else:
		value = 10**9
		for col in order_moves_by_heuristic(valid_cols):
			child = simulate_drop(board, col, opp_piece)
			if child is None:
				continue
			new_score, _ = minimax(child, depth - 1, alpha, beta, True, ai_piece)
			if new_score < value:
				value = new_score
				best_col = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return value, best_col


def ai_choose_column(board: Board, ai_piece: int, depth: int = 6) -> int:
	"""AI2: More aggressive, deeper search (default depth 6 vs AI1's 5)"""
	valid_cols = get_valid_locations(board)
	random.shuffle(valid_cols)

	# 1) Can we win in one move?
	for col in valid_cols:
		child = simulate_drop(board, col, ai_piece)
		if child is not None and CF.winning_move(child, ai_piece):
			return col

	# 2) Can opponent win next? Block it
	opp = C4.player1 if ai_piece == C4.player2 else C4.player2
	for col in valid_cols:
		child = simulate_drop(board, col, opp)
		if child is not None and CF.winning_move(child, opp):
			return col

	# 3) Search deeper with alpha-beta (deeper than AI1)
	_, best_col = minimax(board, depth, -10**9, 10**9, True, ai_piece)
	if best_col is None:
		# Fallback to center preference
		ordered = order_moves_by_heuristic(get_valid_locations(board))
		return ordered[0] if ordered else 0
	return best_col


# ---- AI vs AI Game loop ----
def game_loop_ai_vs_ai(ai1_depth: int = 5, ai2_depth: int = 6, delay_ms: int = 500) -> None:
	"""Watch two AIs compete against each other"""
	import AIConnectFour1 as AI1
	
	pygame.init()
	pygame.display.set_caption("Connect Four - AI vs AI")
	screen = pygame.display.set_mode((C4.width, C4.height))
	clock = pygame.time.Clock()

	sound = SoundManager()
	sound.play_bgm()

	board = CF.create_board()

	# AI1 uses player1, AI2 uses player2
	ai1_piece = C4.player1
	ai2_piece = C4.player2
	turn = ai1_piece  # AI1 starts

	game_over = False
	winner: Optional[int] = None

	# Back to menu button
	button_width, button_height = 150, 40
	button_x = C4.width - button_width - 10
	button_y = 10
	menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

	# Timer for AI moves (to make it watchable)
	last_move_time = 0

	while True:
		mouse_pos = pygame.mouse.get_pos()
		current_time = pygame.time.get_ticks()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				try:
					sound.cleanup()
				finally:
					pygame.quit()
					sys.exit(0)
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
					sound.cleanup()
					screen.fill(C4.bg_color)
					pygame.display.flip()
					return
				if game_over and event.key == pygame.K_r:
					# Restart
					board = CF.create_board()
					turn = ai1_piece
					game_over = False
					winner = None
					last_move_time = current_time
			if event.type == pygame.MOUSEBUTTONDOWN:
				if menu_button_rect.collidepoint(event.pos):
					sound.cleanup()
					screen.fill(C4.bg_color)
					pygame.display.flip()
					return

		# AI moves (with delay to make it watchable)
		if not game_over and current_time - last_move_time >= delay_ms:
			pygame.event.pump()
			
			if turn == ai1_piece:
				col = AI1.ai_choose_column(board, ai1_piece, depth=ai1_depth)
				ai_name = "AI1"
			else:
				col = ai_choose_column(board, ai2_piece, depth=ai2_depth)
				ai_name = "AI2"
			
			row = CF.get_next_open_row(board, col)
			if row is not None:
				CF.drop_piece(board, row, col, turn)
				sound.play_sfx()
				last_move_time = current_time
				
				if CF.winning_move(board, turn):
					game_over = True
					winner = turn
				elif CF.is_draw(board):
					game_over = True
					winner = None
				else:
					turn = ai2_piece if turn == ai1_piece else ai1_piece

		# Draw
		CF.draw_board(screen, board)
		CF.draw_button(screen, "Back to Menu", menu_button_rect, mouse_pos)

		if game_over:
			if winner is None:
				CF.render_text(screen, "Draw! Press R to restart", C4.text_color, C4.cell_size // 2)
			else:
				color = C4.player1_color if winner == C4.player1 else C4.player2_color
				winner_name = "AI1" if winner == ai1_piece else "AI2"
				CF.render_text(screen, f"{winner_name} wins! Press R", color, C4.cell_size // 2)
		else:
			current_ai = "AI1" if turn == ai1_piece else "AI2"
			color = C4.player1_color if turn == C4.player1 else C4.player2_color
			CF.render_text(screen, f"{current_ai} thinking...", color, C4.cell_size // 2)

		pygame.display.flip()
		clock.tick(C4.fps)


def main() -> None:
	game_loop_ai_vs_ai(ai1_depth=5, ai2_depth=6, delay_ms=500)


if __name__ == "__main__":
	main()

