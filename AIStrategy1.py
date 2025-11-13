"""
AI Strategy 1: Balanced offense/defense with center control
"""
import random
from typing import List, Optional, Tuple

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from AICore import Board, get_valid_locations, is_terminal_node, copy_board, simulate_drop, order_moves_by_heuristic


def evaluate_window(window: List[int], piece: int) -> int:
	"""Evaluate a 4-cell window"""
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
	"""Score the current board position"""
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


def minimax(board: Board, depth: int, alpha: int, beta: int, maximizing: bool, ai_piece: int) -> Tuple[int, Optional[int]]:
	"""Minimax algorithm with alpha-beta pruning"""
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
	"""AI Strategy 1: Choose the best column to play"""
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

