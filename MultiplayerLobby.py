from network import Network
import pygame
from ConnectFour import ConnectFour as C4
import ConnectFour as CF
import socket
from button import Button

class Lobby:
    def __init__(self, on_return=None):
        pygame.init()

        self.WIDTH, self.HEIGHT = C4.width, C4.height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        pygame.display.set_caption("Connect 4")

        self.on_return = on_return

        self.text_color = C4.text_color
        self.bg_color = C4.bg_color
        self.input_color = (100, 150, 255)

        self.bw, self.bh = int(self.WIDTH * 0.5), 70
        self.bx = (self.WIDTH - self.bw) // 2
        self.base_y = C4.cell_size * 2
        self.gap = 20

        self.text_font = pygame.font.SysFont(None, 36)

        self.button_font = pygame.font.SysFont(None, 48)
        self.button_fg = (20, 20, 25)
        self.button_bg = (230, 230, 240)
        self.button_hover = (200, 220, 240)

        self.host_btn = Button(
            pygame.Rect(self.bx, self.base_y, self.bw, self.bh),
            "Host a room",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.join_btn = Button(
            pygame.Rect(self.bx, self.base_y + (self.bh + self.gap), self.bw, self.bh),
            "Join a room",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.leave_room_btn = Button(
            pygame.Rect(self.bx, self.base_y + 2 * (self.bh + self.gap), self.bw, self.bh),
            "Leave room",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.exit_btn = Button(
            pygame.Rect(self.bx, self.base_y + 2 * (self.bh + self.gap), self.bw, self.bh),
            "Exit multiplayer",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.ready_btn = Button(
            pygame.Rect(self.bx, self.base_y, self.bw, self.bh),
            "Ready",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.cancel_btn = Button(
            pygame.Rect(self.bx, self.base_y + 3 * (self.bh + self.gap), self.bw, self.bh),
            "Cancel",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.submit_btn = Button(
            pygame.Rect(self.bx, self.base_y + 2 * (self.bh + self.gap), self.bw, self.bh),
            "Join",
            self.button_font,
			self.button_fg,
			self.button_bg,
			self.button_hover,
        )
        self.input_rect = pygame.Rect(self.bx, self.base_y + 1 * (self.bh + self.gap), self.bw, self.bh)

        # Lobby state
        self.mode = ""
        self.input_active = False
        self.joining_code = ""
        self.room_code = ""
        self.waiting = False
        self.network = None
        self.connected = False
        self.connection_message = ""
        self.ready = False
        self.code_len = 5
        self.other_joined = False
        self.player_num = None

    def generate_code(self):
        from random import randrange
        num = randrange(1, 100000, 1)
        return str(num).zfill(self.code_len)
    
    def host_game(self):
        self.mode = "host"
        self.room_code = self.generate_code()

        try:
            self.network = Network()
            self.network.send(f"HOST:{self.room_code}")
            self.waiting = True
            self.connection_message = "Hosting..."
            print(f"[HOST] Room code: {self.room_code}")
        except socket.error as e:
            self.connection_message = f"Error: {e}"
            
    def leave_game(self):
        if self.network:
            try:
                self.network.send("LEAVE")
                self.network.client.close()
            except Exception:
                pass
            self.network.close()

        self.mode = ""
        self.joining_code = ""
        self.room_code = ""
        self.connection_message = ""
        self.network = None
        self.other_joined = False
        self.ready = False
        self.connected = False
        self.waiting = False

    def join_game(self):
        self.mode = "join"
        self.joining_code = ""
        self.input_active = True
        self.connection_message = ""

    def connect_to_game(self):
        try:
            self.network = Network()
            self.network.send(f"JOIN:{self.joining_code}")
            self.connected = True
            self.connection_message = "Connected!"
            self.other_joined = True
        except socket.error:
            self.connection_message = "Connection failed!"

    def toggle_ready(self):
        self.ready = not self.ready
        try:
            if self.ready:
                self.network.send("READY") if self.network else None
                self.connection_message = "Ready"
            else:
                self.network.send("CANCEL") if self.network else None
                self.connection_message = "Cancelled"
        except Exception as e:
            print("Error toggling ready:", e)
    
    def handle_join_input(self, event):
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.connect_to_game()
            elif event.key == pygame.K_BACKSPACE:
                self.joining_code = self.joining_code[:-1]
            else:
                if len(self.joining_code) < self.code_len and event.unicode.isdigit():
                    self.joining_code += str(event.unicode)
            
    
    def draw(self):
        self.screen.fill(self.bg_color)
        mouse = pygame.mouse.get_pos()

        if not self.mode:
            self.host_btn.draw(self.screen, mouse)
            self.join_btn.draw(self.screen, mouse)
            self.exit_btn.draw(self.screen, mouse)
        elif self.mode == "host":
            code_text = self.text_font.render(f"Room Code: {self.room_code}", True, self.text_color)
            self.screen.blit(code_text, (self.WIDTH // 2 - code_text.get_width() // 2, self.base_y - 40))

            msg = "Waiting for another player..." if not self.other_joined else "Another player joined!"
            status_text = self.text_font.render(msg, True, self.text_color)
            self.screen.blit(status_text, (self.WIDTH // 2 - status_text.get_width() // 2, self.base_y + self.bh // 2))

            if self.other_joined:
                self.ready_btn.text = "Ready" if not self.ready else "Cancel"
                self.ready_btn.draw(self.screen, mouse)

            self.leave_room_btn.draw(self.screen, mouse)
        elif self.mode == "join":
            if not self.other_joined: # Show input code stuff if not joined
                prompt = self.text_font.render("Enter room code: ", True, self.text_color)
                self.screen.blit(prompt, (self.WIDTH // 2 - prompt.get_width() // 2, self.base_y - 40))

                pygame.draw.rect(self.screen, self.button_bg, self.input_rect, border_radius=10)
                text_surface = self.text_font.render(self.joining_code, True, self.button_fg)
                self.screen.blit(text_surface, (self.input_rect.x + 10, self.input_rect.y + 10))

                
                self.submit_btn.draw(self.screen, mouse)
                self.cancel_btn.draw(self.screen, mouse)
            else:
                self.ready_btn.text = "Ready" if not self.ready else "Cancel"
                self.ready_btn.draw(self.screen, mouse)
                self.leave_room_btn.draw(self.screen, mouse)

            msg = self.text_font.render(self.connection_message, True, self.text_color)
            self.screen.blit(msg, (self.WIDTH // 2 - msg.get_width() // 2, self.base_y - 40))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                mouse_down = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

                if not self.mode:
                    if self.host_btn.is_clicked(mouse, mouse_down):
                        self.host_game()
                    elif self.join_btn.is_clicked(mouse, mouse_down):
                        self.join_game()
                    elif self.exit_btn.is_clicked(mouse, mouse_down):
                        running = False
                        if self.on_return:
                            self.on_return()
                        else:
                            print("No return callback; Staying in lobby.")
                elif self.mode == "host":
                    if self.leave_room_btn.is_clicked(mouse, mouse_down):
                        self.leave_game()
                    elif self.other_joined and self.ready_btn.is_clicked(mouse, mouse_down):
                        self.toggle_ready()
                elif self.mode == "join":
                    if not self.other_joined:
                        self.input_active = True
                        self.handle_join_input(event)
                        
                        if self.submit_btn.is_clicked(mouse, mouse_down):
                            if self.joining_code:
                                print("[CLI] Code entered: ", self.joining_code)
                                self.connect_to_game()
                    else:
                            
                        if self.leave_room_btn.is_clicked(mouse, mouse_down):
                            self.leave_game()
                        elif self.ready_btn.is_clicked(mouse, mouse_down):
                            self.toggle_ready()
            
            if self.network:
                msg: str = self.network.get_message() 
                if msg:
                    if msg.startswith("ROLE:"):
                        self.player_num = int(msg.split(":")[1])
                        self.connection_message = f"Role assigned: Player {self.player_num}"
                    if msg == "JOINED":
                        self.other_joined = True
                        self.connection_message = "A player has joined!"
                    elif msg == "START":
                        player_role = self.player_num
                        self.connection_message = "Starting game..."
                        CF.game_loop(self.network, player_role)
                        self.leave_game()
                    elif msg.startswith("ERR"):
                        self.connection_message = msg
                    elif msg == "LEFT":
                        self.connection_message = "Opponent left!"
                        self.other_joined = False

            self.draw()
            clock.tick(30)

        pygame.quit()

def lobby():
    lobby = Lobby()
    lobby.run()

if __name__ == "__main__":
    lobby()