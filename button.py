from typing import Tuple
import pygame

class Button:
	def __init__(
		self,
		rect: pygame.Rect,
		text: str,
		font: pygame.font.Font,
		fg: Tuple[int, int, int],
		bg: Tuple[int, int, int],
		hover: Tuple[int, int, int],
	) -> None:
		self.rect = rect
		self.text = text
		self.font = font
		self.fg = fg
		self.bg = bg
		self.hover = hover

	def draw(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]) -> None:
		is_hover = self.rect.collidepoint(mouse_pos)
		color = self.hover if is_hover else self.bg
		pygame.draw.rect(screen, color, self.rect, border_radius=10)
		label = self.font.render(self.text, True, self.fg)
		screen.blit(label, label.get_rect(center=self.rect.center))

	def is_clicked(self, mouse_pos: Tuple[int, int], mouse_down: bool) -> bool:
		return mouse_down and self.rect.collidepoint(mouse_pos)
