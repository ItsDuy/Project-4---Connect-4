from __future__ import annotations
import sys
import os
from typing import Optional

import pygame

from SoundManager import SoundManager
import Human_vs_AI as HUAI
import AI_vs_AI as AIAI
import ConnectFour as CF
from ConnectFour import ConnectFour as C4
from MultiplayerLobby import Lobby
from button import Button


class DifficultySelectionScreen:
	def __init__(self, screen: pygame.Surface, sound: SoundManager, main_menu: MainMenu) -> None:
		self.screen = screen
		self.sound = sound
		self.width, self.height = self.screen.get_size()
		self.title_font = pygame.font.SysFont(None, 72)
		self.button_font = pygame.font.SysFont(None, 48)
		
		self.main_menu = main_menu
		# Buttons layout
		bw, bh = int(self.width * 0.5), 70
		bx = (self.width - bw) // 2
		base_y = C4.cell_size * 2
		gap = 20

		self.btn_easy = Button(
			pygame.Rect(bx, base_y, bw, bh),
			"Easy",
			self.button_font,
			(20, 20, 25),
			(230, 230, 240),
			(200, 220, 240),
		)
		self.btn_normal = Button(
			pygame.Rect(bx, base_y + (bh + gap), bw, bh),
			"Normal",
			self.button_font,
			(20, 20, 25),
			(230, 230, 240),
			(200, 220, 240),
		)
		self.btn_hard = Button(
			pygame.Rect(bx, base_y + 2 * (bh + gap), bw, bh),
			"Hard",
			self.button_font,
			(20, 20, 25),
			(230, 230, 240),
			(200, 220, 240),
		)

	def run(self) -> Optional[int]:
		"""Returns selected depth (1, 3, or 6), or None if cancelled"""
		clock = pygame.time.Clock()
		running = True
		selected_depth = None

		while running:
			mouse_pos = pygame.mouse.get_pos()
			mouse_down = False

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
						running = False
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse_down = True

			# Handle clicks
			if mouse_down:
				if self.btn_easy.is_clicked(mouse_pos, mouse_down):
					selected_depth = 1
					running = False
				elif self.btn_normal.is_clicked(mouse_pos, mouse_down):
					selected_depth = 3
					running = False
				elif self.btn_hard.is_clicked(mouse_pos, mouse_down):
					selected_depth = 6
					running = False

			# Background
			self.main_menu._draw_background()

			# Title
			title = self.title_font.render("Select Difficulty", True, C4.text_color)
			self.screen.blit(title, title.get_rect(center=(self.width // 2, C4.cell_size // 2)))

			# Buttons
			self.btn_easy.draw(self.screen, mouse_pos)
			self.btn_normal.draw(self.screen, mouse_pos)
			self.btn_hard.draw(self.screen, mouse_pos)

			# Footer hint
			hint = pygame.font.SysFont(None, 28).render("Esc/Backspace: Back", True, (180, 180, 180))
			self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 30)))

   
			pygame.display.flip()
			clock.tick(C4.fps)

		return selected_depth


class MusicSettingsScreen:
	def __init__(self, screen: pygame.Surface, sound: SoundManager) -> None:
		self.screen = screen
		self.sound = sound
		self.width, self.height = self.screen.get_size()
		self.title_font = pygame.font.SysFont(None, 72)
		self.ui_font = pygame.font.SysFont(None, 36)
		self.small_font = pygame.font.SysFont(None, 28)

		# Slider geometry
		self.slider_w = int(self.width * 0.5)
		self.slider_h = 8
		self.slider_x = (self.width - self.slider_w) // 2
		self.bgm_slider_y = C4.cell_size * 2
		self.sfx_slider_y = C4.cell_size * 3

		self.active: Optional[str] = None  # 'bgm' or 'sfx'

	def _draw_slider(self, y: int, value: float, label: str) -> pygame.Rect:
		# Track
		track_rect = pygame.Rect(self.slider_x, y, self.slider_w, self.slider_h)
		pygame.draw.rect(self.screen, (80, 80, 90), track_rect, border_radius=4)
		# Fill
		# value is 0..100 percent
		pct = max(0.0, min(100.0, value))
		fill_w = int(self.slider_w * (pct / 100.0))
		fill_rect = pygame.Rect(self.slider_x, y, fill_w, self.slider_h)
		pygame.draw.rect(self.screen, C4.highlight_color, fill_rect, border_radius=4)
		# Knob
		knob_x = self.slider_x + fill_w
		pygame.draw.circle(self.screen, (220, 220, 220), (knob_x, y + self.slider_h // 2), 10)
		# Label
		text = self.ui_font.render(f"{label}: {int(round(pct))}%", True, C4.text_color)
		self.screen.blit(text, text.get_rect(midbottom=(self.width // 2, y - 10)))

		return track_rect

	def _value_from_mouse(self, track: pygame.Rect, mx: int) -> float:
		# Return percent 0..100 based on mouse position over track
		rel = max(0, min(track.w, mx - track.x))
		if track.w <= 0:
			return 0.0
		return (rel / track.w) * 100.0

	def run(self) -> None:
		clock = pygame.time.Clock()
		running = True
		dragging: Optional[str] = None

		while running:
			mouse_pos = pygame.mouse.get_pos()
			mouse_down = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
						running = False
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse_down = True
					dragging = (
						'bgm' if self._bgm_track.collidepoint(mouse_pos)
						else ('sfx' if self._sfx_track.collidepoint(mouse_pos) else None)
					)
				elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					dragging = None

			# Background
			self.screen.fill(C4.bg_color)

			# Title
			title = self.title_font.render("Music Settings", True, C4.text_color)
			self.screen.blit(title, title.get_rect(center=(self.width // 2, C4.cell_size // 2)))

			# Sliders
			self._bgm_track = self._draw_slider(self.bgm_slider_y, self.sound.bgm_volume, "BGM Volume")
			self._sfx_track = self._draw_slider(self.sfx_slider_y, self.sound.sfx_volume, "SFX Volume")

			# Handle dragging to update values
			if dragging == 'bgm' and pygame.mouse.get_pressed()[0]:
				new_val = self._value_from_mouse(self._bgm_track, mouse_pos[0])  # 0..100
				self.sound.set_bgm_volume(new_val)
			elif dragging == 'sfx' and pygame.mouse.get_pressed()[0]:
				new_val = self._value_from_mouse(self._sfx_track, mouse_pos[0])  # 0..100
				self.sound.set_sfx_volume(new_val)

			# Footer hint
			hint = self.small_font.render("Esc/Backspace: Back", True, (180, 180, 180))
			self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 30)))

			pygame.display.flip()
			clock.tick(C4.fps)


class MainMenu:
	def __init__(self) -> None:
		pygame.init()
		pygame.display.set_caption("Connect 4 - Main Menu")
		self.width, self.height = C4.width, C4.height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.clock = pygame.time.Clock()

		self.lobby = Lobby(on_return=main)

		# Background image (optional)
		self.background: Optional[pygame.Surface] = None
		bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'bg.jpeg')
		if os.path.isfile(bg_path):
			try:
				img = pygame.image.load(bg_path)
				self.background = pygame.transform.scale(img, (self.width, self.height))
			except Exception as e:
				print(f"[MainMenu] Failed to load background: {e}")
				self.background = None

		# Fonts
		self.title_font = pygame.font.SysFont(None, 96)
		self.button_font = pygame.font.SysFont(None, 48)

		# Colors
		self.title_color = C4.text_color
		self.button_fg = (20, 20, 25)
		self.button_bg = (230, 230, 240)
		self.button_hover = (200, 220, 240)

		# Buttons layout
		bw, bh = int(self.width * 0.5), 70
		bx = (self.width - bw) // 2
		base_y = C4.cell_size * 2
		gap = 20
		self.btn_pvp = Button(
			pygame.Rect(bx, base_y, bw, bh),
			"Play PvP",
			self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
		)
		self.btn_ai = Button(
			pygame.Rect(bx, base_y + (bh + gap), bw, bh),
			"Play AI",
			self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
		)
		self.btn_ai_vs_ai = Button(
			pygame.Rect(bx, base_y + 2 * (bh + gap), bw, bh),
			"AI vs AI",
			self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
		)
		self.btn_music = Button(
			pygame.Rect(bx, base_y + 3 * (bh + gap), bw, bh),
			"Music Settings",
			self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
		)

		# Toast state
		self.toast_text: Optional[str] = None
		self.toast_until: int = 0

		# Sound
		self.sound = SoundManager()
		self.sound.play_bgm()

	def _draw_background(self) -> None:
		if self.background is not None:
			self.screen.blit(self.background, (0, 0))
		else:
			self.screen.fill(C4.bg_color)

		# Dim panel for board area feel (semi-transparent)
		overlay = pygame.Surface((self.width, self.height - C4.cell_size), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 60))
		self.screen.blit(overlay, (0, C4.cell_size))

	def _draw_title(self) -> None:
		title_surf = self.title_font.render("Connect 4", True, self.title_color)
		self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, C4.cell_size // 2)))

	def _draw_buttons(self) -> None:
		mouse_pos = pygame.mouse.get_pos()
		self.btn_pvp.draw(self.screen, mouse_pos)
		self.btn_ai.draw(self.screen, mouse_pos)
		self.btn_ai_vs_ai.draw(self.screen, mouse_pos)
		self.btn_music.draw(self.screen, mouse_pos)

	def _handle_clicks(self, mouse_down: bool) -> None:
		mouse_pos = pygame.mouse.get_pos()
		if self.btn_pvp.is_clicked(mouse_pos, mouse_down):
			# Stop menu BGM and jump to game loop
			try:
				self.sound.cleanup()
			except Exception:
				pass
			self.lobby.run()
			# Restart menu BGM when returning from game
			try:
				self.sound.play_bgm()
			except Exception:
				pass
		elif self.btn_ai.is_clicked(mouse_pos, mouse_down):
			# Show difficulty selection screen
			difficulty_screen = DifficultySelectionScreen(self.screen, self.sound, self)
			selected_depth = difficulty_screen.run()
			
			if selected_depth is not None:
				try:
					self.sound.cleanup()
				except Exception:
					pass
				# is_normal=True only for Normal mode (depth=3)
				is_normal = (selected_depth == 3)
				HUAI.game_loop_ai(depth=selected_depth, is_normal=is_normal)
				try:
					self.sound.play_bgm()
				except Exception:
					pass
		elif self.btn_ai_vs_ai.is_clicked(mouse_pos, mouse_down):
			# Stop menu BGM and start AI vs AI game loop
			try:
				self.sound.cleanup()
			except Exception:
				pass
			AIAI.game_loop_ai_vs_ai(ai1_depth=5, ai2_depth=6, delay_ms=500)
			# Restart menu BGM when returning from game
			try:
				self.sound.play_bgm()
			except Exception:
				pass
		elif self.btn_music.is_clicked(mouse_pos, mouse_down):
			MusicSettingsScreen(self.screen, self.sound).run()

	def _draw_toast(self) -> None:
		if self.toast_text and pygame.time.get_ticks() < self.toast_until:
			surf = pygame.font.SysFont(None, 36).render(self.toast_text, True, C4.text_color)
			bg_rect = surf.get_rect(center=(self.width // 2, self.height - 40)).inflate(20, 10)
			toast_overlay = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
			pygame.draw.rect(toast_overlay, (0, 0, 0, 160), toast_overlay.get_rect(), border_radius=8)
			self.screen.blit(toast_overlay, bg_rect.topleft)
			self.screen.blit(surf, surf.get_rect(center=bg_rect.center))
		else:
			self.toast_text = None

	def run(self) -> None:
		running = True
		while running:
			mouse_down = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse_down = True
				elif event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_ESCAPE, pygame.K_q):
						running = False

			# Draw
			self._draw_background()
			self._draw_title()
			self._draw_buttons()
			self._draw_toast()

			# Handle clicks after drawing to avoid visual lag
			if mouse_down:
				self._handle_clicks(mouse_down)

			pygame.display.flip()
			self.clock.tick(C4.fps)

		# Cleanup on exit
		try:
			self.sound.cleanup()
		finally:
			pygame.quit()
			sys.exit(0)


def main() -> None:
	menu = MainMenu()
	menu.run()


if __name__ == "__main__":
	main()

