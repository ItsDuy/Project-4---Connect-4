import sys
import random
from typing import List, Optional, Tuple

import pygame

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from SoundManager import SoundManager


Board = List[List[int]]


# ---- AI evaluation helpers ----
def get_valid_locations(board: Board) -> List[int]:
	return [c for c in range(C4.cols) if board[0][c] == C4.empty_cell]


def is_terminal_node(board: Board) -> bool:
	return CF.winning_move(board, C4.player1) or CF.winning_move(board, C4.player2) or CF.is_draw(board)


def evaluate_window(window: List[int], piece: int) -> int:
	opp_piece = C4.player1 if piece == C4.player2 else C4.player2
	score = 0

	count_piece = window.count(piece)
	count_opp = window.count(opp_piece)
	count_empty = window.count(C4.empty_cell)

	# Winning/forcing patterns
	if count_piece == 4:
		score += 100000
	elif count_piece == 3 and count_empty == 1:
		score += 100
	elif count_piece == 2 and count_empty == 2:
		score += 12

	# Defensive urgency: block opponent 3
	if count_opp == 3 and count_empty == 1:
		score -= 120
	elif count_opp == 2 and count_empty == 2:
		score -= 10

	return score


def score_position(board: Board, piece: int) -> int:
	score = 0

	# Center column priority
	center_col = C4.cols // 2
	center_array = [board[r][center_col] for r in range(C4.rows)]
	score += center_array.count(piece) * 6

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
	# Prefer center columns to improve pruning and strategy
	center = C4.cols // 2
	return sorted(valid_cols, key=lambda c: abs(c - center))


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


def ai_choose_column(board: Board, ai_piece: int, depth: int = 5) -> int:
	# If first move or easy pick, try quick wins/blocks before full search
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

	# 3) Search deeper with alpha-beta
	_, best_col = minimax(board, depth, -10**9, 10**9, True, ai_piece)
	if best_col is None:
		# Fallback to center preference
		ordered = order_moves_by_heuristic(get_valid_locations(board))
		return ordered[0] if ordered else 0
	return best_col


# ---- Game loop (Human vs AI) ----
def game_loop_ai(depth: int = 5) -> None:
	pygame.init()
	pygame.display.set_caption("Connect Four - vs AI")
	screen = pygame.display.set_mode((C4.width, C4.height))
	clock = pygame.time.Clock()

	sound = SoundManager()
	sound.play_bgm()

	board = CF.create_board()

	# Randomize who starts
	human_piece, ai_piece = (C4.player1, C4.player2) if random.choice([True, False]) else (C4.player2, C4.player1)
	turn = human_piece if random.choice([True, False]) else ai_piece

	game_over = False
	winner: Optional[int] = None

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				try:
					sound.cleanup()
				finally:
					pygame.quit()
					sys.exit(0)
			if event.type == pygame.KEYDOWN and game_over:
				if event.key == pygame.K_r:
					# Restart and re-randomize
					board = CF.create_board()
					human_piece, ai_piece = (C4.player1, C4.player2) if random.choice([True, False]) else (C4.player2, C4.player1)
					turn = human_piece if random.choice([True, False]) else ai_piece
					game_over = False
					winner = None
				elif event.key in (pygame.K_ESCAPE, pygame.K_q):
					try:
						sound.cleanup()
					finally:
						pygame.quit()
						sys.exit(0)

			# Human move
			if event.type == pygame.MOUSEBUTTONDOWN and not game_over and turn == human_piece:
				col = CF.get_col_from_mouse(event.pos[0])
				row = CF.get_next_open_row(board, col)
				if row is not None:
					CF.drop_piece(board, row, col, human_piece)
					sound.play_sfx()
					if CF.winning_move(board, human_piece):
						game_over = True
						winner = human_piece
					elif CF.is_draw(board):
						game_over = True
						winner = None
					else:
						turn = ai_piece

		# AI move (outside event loop to allow thinking without extra click)
		if not game_over and turn == ai_piece:
			# Optional: brief pump to keep window responsive
			pygame.event.pump()
			col = ai_choose_column(board, ai_piece, depth=depth)
			row = CF.get_next_open_row(board, col)
			if row is not None:
				CF.drop_piece(board, row, col, ai_piece)
				sound.play_sfx()
				if CF.winning_move(board, ai_piece):
					game_over = True
					winner = ai_piece
				elif CF.is_draw(board):
					game_over = True
					winner = None
				else:
					turn = human_piece

		# Draw
		CF.draw_board(screen, board)
		if game_over:
			if winner is None:
				CF.render_text(screen, "Draw! Press R to restart", C4.text_color, C4.cell_size // 2)
			else:
				color = C4.player1_color if winner == C4.player1 else C4.player2_color
				label = "AI wins!" if winner == ai_piece else "You win!"
				CF.render_text(screen, f"{label} Press R", color, C4.cell_size // 2)
		else:
			if turn == human_piece:
				color = C4.player1_color if human_piece == C4.player1 else C4.player2_color
				CF.render_text(screen, "Your turn", color, C4.cell_size // 2)
			else:
				color = C4.player1_color if ai_piece == C4.player1 else C4.player2_color
				CF.render_text(screen, "AI thinking...", color, C4.cell_size // 2)

		pygame.display.flip()
		clock.tick(C4.fps)


def main() -> None:
	game_loop_ai(depth=5)


if __name__ == "__main__":
	main()

