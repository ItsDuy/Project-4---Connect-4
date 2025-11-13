"""
AI Strategy 2: More aggressive offense-focused strategy
"""
import random
from typing import List, Optional, Tuple

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from AICore import Board, get_valid_locations, is_terminal_node, copy_board, simulate_drop, order_moves_by_heuristic


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


def order_moves_by_heuristic_custom(valid_cols: List[int]) -> List[int]:
	"""Different move ordering: prefer center but also consider edge columns"""
	center = C4.cols // 2
	# Prefer center, then adjacent, then edges
	return sorted(valid_cols, key=lambda c: (
		abs(c - center),  # Distance from center
		abs(c - center) > 2  # Prefer center region
	))


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
		for col in order_moves_by_heuristic_custom(valid_cols):
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
		for col in order_moves_by_heuristic_custom(valid_cols):
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
	"""AI Strategy 2: More aggressive, deeper search (default depth 6 vs AI1's 5)"""
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
		ordered = order_moves_by_heuristic_custom(get_valid_locations(board))
		return ordered[0] if ordered else 0
	return best_col

