"""
Game loop for AI vs AI (using AIStrategy1 and AIStrategy2)
"""
import sys
from typing import Optional

import pygame

import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from SoundManager import SoundManager
from AIStrategy1 import ai_choose_column as ai1_choose_column
from AIStrategy2 import ai_choose_column as ai2_choose_column


# ---- AI vs AI Game loop ----
def game_loop_ai_vs_ai(ai1_depth: int = 5, ai2_depth: int = 6, delay_ms: int = 500) -> None:
	"""Watch two AIs compete against each other"""
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
				col = ai1_choose_column(board, ai1_piece, depth=ai1_depth)
			else:
				col = ai2_choose_column(board, ai2_piece, depth=ai2_depth)
			
			row = CF.get_next_open_row(board, col)
			if row is not None:
				# Animate the falling piece for the current AI
				def _extra_draw_ai(surf: pygame.Surface) -> None:
					CF.draw_button(surf, "Back to Menu", menu_button_rect, pygame.mouse.get_pos())
				status_color = C4.player1_color if turn == C4.player1 else C4.player2_color
				ai_label = "AI1 moving..." if turn == ai1_piece else "AI2 moving..."
				CF.animate_falling_piece(
					screen,
					board,
					col,
					row,
					turn,
					clock,
					sfx=sound,
					extra_draw=_extra_draw_ai,
					status_text=(ai_label, status_color),
					speed_px_per_frame=30,
					easing="ease_out",
				)
				last_move_time = pygame.time.get_ticks()
				
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
