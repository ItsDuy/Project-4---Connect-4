"""
Game loop for Human vs AI1 (using AIStrategy1)
"""
import sys
import random
from typing import Optional

import pygame

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from SoundManager import SoundManager
from AIStrategy1 import ai_choose_column
from AICore import get_valid_locations


# ---- Game loop (Human vs AI) ----
def game_loop_ai(depth: int = 6, is_normal: bool = False) -> None:
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

	# Back to menu button
	button_width, button_height = 150, 40
	button_x = C4.width - button_width - 10
	button_y = 10
	menu_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

	while True:
		mouse_pos = pygame.mouse.get_pos()
		
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
					board = CF.create_board()
					human_piece, ai_piece = (C4.player1, C4.player2) if random.choice([True, False]) else (C4.player2, C4.player1)
					turn = human_piece if random.choice([True, False]) else ai_piece
					game_over = False
					winner = None

			# Human move
			if event.type == pygame.MOUSEBUTTONDOWN:
				if menu_button_rect.collidepoint(event.pos):
					sound.cleanup()
					screen.fill(C4.bg_color)
					pygame.display.flip()
					return  
				if not game_over and turn == human_piece:
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

		# AI move
		if not game_over and turn == ai_piece:
			pygame.event.pump()
			
			if is_normal and random.random() < 0.25:
				valid_cols = get_valid_locations(board)
				if valid_cols:
					col = random.choice(valid_cols)
				else:
					col = ai_choose_column(board, ai_piece, depth=depth)
			else:
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
		
		# Draw back to menu button
		CF.draw_button(screen, "Back to Menu", menu_button_rect, mouse_pos)
		
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
