"""
Common AI utility functions for Connect Four
"""
from typing import List, Optional

import ConnectFour as CF
from ConnectFour import ConnectFour as C4


Board = List[List[int]]


def get_valid_locations(board: Board) -> List[int]:
	"""Get list of columns that are not full"""
	return [c for c in range(C4.cols) if board[0][c] == C4.empty_cell]


def is_terminal_node(board: Board) -> bool:
	"""Check if the game is over (win or draw)"""
	return CF.winning_move(board, C4.player1) or CF.winning_move(board, C4.player2) or CF.is_draw(board)


def copy_board(board: Board) -> Board:
	"""Create a deep copy of the board"""
	return [row[:] for row in board]


def simulate_drop(board: Board, col: int, piece: int) -> Optional[Board]:
	"""Simulate dropping a piece in a column, return new board or None if invalid"""
	row = CF.get_next_open_row(board, col)
	if row is None:
		return None
	nb = copy_board(board)
	CF.drop_piece(nb, row, col, piece)
	return nb


def order_moves_by_heuristic(valid_cols: List[int], prefer_center: bool = True) -> List[int]:
	"""Order moves by heuristic - prefer center columns by default"""
	if prefer_center:
		center = C4.cols // 2
		return sorted(valid_cols, key=lambda c: abs(c - center))
	return valid_cols

