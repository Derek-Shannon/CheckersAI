# checkers/scenes/game_scene.py
import pygame
import math, random, copy # math/random might not be needed if Board and AI are separated
import sys

from .Scene import Scene
from utility.Board import Board # Assuming Board class is implemented in ..game.board
from utility.MinMaxAgent import MinMaxAgent # Assuming MinMax algorithm is implemented in ..ai.minmax
from utility.Timer import Timer # Assuming Timer is available (or utility.Timer from original)

class GameScene(Scene):
    def __init__(self, screen, mode='PvP'):
        super().__init__(screen)
        self.mode = mode
        self.board_manager = Board() # Instantiate the Board Model
        self.AITimer = Timer(500) # 500ms delay for AI
        print(f"Starting GameScene in {self.mode} mode.")

        # --- Image Loading (View) ---
        try:
            self.board_image = pygame.image.load('assets/images/board.jpg').convert_alpha()
            self.board_image = pygame.transform.scale(self.board_image, (560, 560))

            self.red_piece_image = pygame.image.load('assets/images/red.png').convert_alpha()
            self.black_piece_image = pygame.image.load('assets/images/black.png').convert_alpha()

            self.red_king_image = pygame.image.load('assets/images/redKing.png').convert_alpha()
            self.black_king_image = pygame.image.load('assets/images/blackKing.png').convert_alpha()
            
            # Scale pieces to fit the squares
            piece_size = 60
            self.red_piece_image = pygame.transform.scale(self.red_piece_image, (piece_size, piece_size))
            self.black_piece_image = pygame.transform.scale(self.black_piece_image, (piece_size, piece_size))
            self.red_king_image = pygame.transform.scale(self.red_king_image, (piece_size, piece_size))
            self.black_king_image = pygame.transform.scale(self.black_king_image, (piece_size, piece_size))

            self.images_loaded = True
        except pygame.error as e:
            print(f"Error loading images: {e}. Using placeholders.")
            self.images_loaded = False

        # --- Pygame Setup Constants (View) ---
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.BOARD_SIZE = 560
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.OFFSET_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 4
        self.OFFSET_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2 + 30

        self.MOVE_HIGHLIGHT = (0, 255, 0, 100) # Green transparent for valid moves
        self.SELECTION_HIGHLIGHT = (0, 0, 255) # Blue for selected piece

        # Back Button Setup
        self.button_rect = pygame.Rect(10, 10, 120, 40)
        self.font = pygame.font.Font(None, 36)
        self.button_text = self.font.render("<< Back", True, (255, 255, 255))
        self.text_rect = self.button_text.get_rect(center=self.button_rect.center)
        
        # Game State (now references the Board object)
        self.selected_piece = None # Stores the (row, col) of the selected piece
        self.valid_moves = {}      # Maps valid move (row, col) to captured piece (or None)
        
        # Text/UI
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.status_message = f"It's {self.board_manager.current_turn}'s turn. Select a piece."
        self.game_over = False

        #AI
        self.ai_agent = MinMaxAgent("Black", 7)

    # --- Coordinate Conversion (Stays here as it's screen-dependent) ---
    def _get_board_coords(self, pos):
        """Converts screen pixel coordinates to board (row, col)."""
        x, y = pos
        # Adjust for board offset
        x -= self.OFFSET_X
        y -= self.OFFSET_Y
        
        # Check if the click is within the board area
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            col = int(x // self.SQUARE_SIZE)
            row = int(y // self.SQUARE_SIZE)
            return row, col
        return None, None

    def _get_pixel_coords(self, row, col):
        """Converts board (row, col) to screen pixel center coordinates."""
        center_x = self.OFFSET_X + (col * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)
        center_y = self.OFFSET_Y + (row * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)
        return center_x, center_y

    # --- AI Control (Controller) ---
    def finalize_ai_move(self):
        """Executes the MinMax algorithm for the AI (Black) turn."""
        if self.board_manager.current_turn == "Black" and not self.game_over:
            depth = 5 
            # Pass the board's internal state (2D list of Pieces) to the MinMax algorithm
            # The minmax function should return (best_val, (piece_rc, target_rc, captured_piece))
            best_val, best_move = self.ai_agent.get_best_move()

            print(f"AI Best Move Value: {best_val}")
            
            if best_move:
                piece_rc, target_rc, captured_piece = best_move
                
                # Execute the move on the board manager
                must_multijump, status_msg = self.board_manager.move_piece(piece_rc, target_rc, captured_piece)
                self.status_message = status_msg
                
                # Check for mandatory multi-jump (which is handled slightly differently for AI)
                if must_multijump:
                    # In a fully autonomous AI, a forced multi-jump is just another move
                    # The minmax function should ideally handle multi-jumps recursively
                    # For simplicity, we assume the initial minmax call returns the *first* move 
                    # of a potential multi-jump chain, and the next 'update' cycle will call runAI again.
                    # Or, the minmax function is structured to return the entire best chain.
                    # Given the original code's structure, we'll re-run AI on the next update loop 
                    # if a multi-jump is mandatory. The board_manager's move_piece should 
                    # NOT switch the turn if a multi-jump is mandatory.

                    # Re-check the game state after the move
                    msg, is_over = self.board_manager.get_game_state()
                    if is_over:
                        self.game_over = True
                        self.status_message = msg
                else:
                    # End of turn
                    self.board_manager.current_turn = self.board_manager.current_turn
                    msg, is_over = self.board_manager.get_game_state()
                    if is_over:
                        self.game_over = True
                        self.status_message = msg
                    elif not self.status_message.endswith("Kinged!"): # Preserve kinging message
                        self.status_message = f"It's {self.board_manager.current_turn}'s turn."
            else:
                self.status_message = "uh oh! no valid AI moves :()"
                self.board_manager.get_game_state() # Will set game_over

    # --- Event Handling (Controller) ---
    def handle_event(self, event):
        # 1. Handle back button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return 'main_menu'

        if self.game_over:
            return 'game_over' # Ignore clicks if game is over or it's the AI's turn

        # 2. Handle game board click (Human turn)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r, c = self._get_board_coords(event.pos)

            if r is not None:
                clicked_piece = self.board_manager.get_piece_at(r, c)
                target_rc = (r, c)
                
                if self.selected_piece:
                    # A piece is already selected, check if click is a valid move
                    if target_rc in self.valid_moves:
                        piece_rc = self.selected_piece
                        captured_piece = self.valid_moves[target_rc]
                        
                        # Delegate movement to the Board Model
                        must_multijump, status_msg = self.board_manager.move_piece(piece_rc, target_rc, captured_piece)
                        self.status_message = status_msg
                        
                        if must_multijump:
                            # Re-select the piece and calculate new jumps
                            piece = self.board_manager.get_piece_at(target_rc[0], target_rc[1])
                            self.selected_piece = target_rc
                            self.valid_moves = self.board_manager._check_jump_moves(piece)
                        else:
                            # End of player's turn
                            self.selected_piece = None
                            self.valid_moves = {}
                            self.board_manager.current_turn = self.board_manager.current_turn
                        
                        # Check for game over
                        msg, is_over = self.board_manager.get_game_state()
                        if is_over:
                            self.game_over = True
                            self.status_message = msg

                    # Clicked the selected piece again to deselect
                    elif target_rc == self.selected_piece:
                        self.selected_piece = None
                        self.valid_moves = {}
                        self.status_message = f"It's {self.board_manager.current_turn}'s turn."
                    
                    # Clicked another piece (only allow selection change if no mandatory jump is active)
                    elif clicked_piece and clicked_piece.color == self.board_manager.current_turn and not self.valid_moves:
                        self.selected_piece = target_rc
                        self.valid_moves = self.board_manager.get_valid_moves(clicked_piece)
                        
                        if not self.valid_moves:
                            self.status_message = f"{self.board_manager.current_turn}'s piece at ({r},{c}) has no moves."
                        elif any(self.valid_moves.values()): # Check if any move is a jump
                            self.status_message = f"{self.board_manager.current_turn} must jump!"
                        else:
                            self.status_message = f"Piece selected: ({r},{c})"

                else:
                    # No piece selected, try to select one
                    if clicked_piece and clicked_piece.color == self.board_manager.current_turn:
                        self.selected_piece = target_rc
                        self.valid_moves = self.board_manager.get_valid_moves(clicked_piece)
                        
                        # Check for mandatory jump
                        if not self.valid_moves:
                            self.status_message = f"{self.board_manager.current_turn}'s piece at ({r},{c}) has no moves."
                        elif any(self.valid_moves.values()): # Check if any move is a jump
                            self.status_message = f"{self.board_manager.current_turn} must jump!"
                        else:
                            self.status_message = f"Piece selected: ({r},{c})"
                    else:
                        self.status_message = f"It's {self.board_manager.current_turn}'s turn. Select a piece."
    
    # --- Update/Draw Methods (View) ---
    def update(self):
        """Handles AI turn delay and execution."""
        if self.mode == "PvAI" and self.board_manager.current_turn == "Black":
            if not self.AITimer.running:
                self.AITimer.start()
            else:
                self.ai_agent.runAI(self.board_manager)
            if self.AITimer.is_finished():
                self.AITimer.stop()
                self.finalize_ai_move()

    def draw_board(self):
        """Draws the checkered pattern of the board."""
        board_rect = pygame.Rect(self.OFFSET_X, self.OFFSET_Y, self.BOARD_SIZE, self.BOARD_SIZE)
        self.screen.blit(self.board_image, board_rect.topleft)

    def draw_pieces(self):
        """Draws all pieces currently on the board using images."""
        if not self.images_loaded:
            return

        piece_size = self.red_piece_image.get_width() # Use the scaled size
        
        for r in range(8):
            for c in range(8):
                piece = self.board_manager.board[r][c]
                if piece:
                    center_x, center_y = self._get_pixel_coords(r, c)
                    
                    if piece.color == 'Red':
                        piece_image = self.red_king_image if piece.king else self.red_piece_image
                    else: # Black
                        piece_image = self.black_king_image if piece.king else self.black_piece_image
                        
                    # Calculate the top-left corner for blitting
                    top_left_x = center_x - (piece_size // 2)
                    top_left_y = center_y - (piece_size // 2)

                    # Blit the image onto the screen
                    self.screen.blit(piece_image, (top_left_x, top_left_y))

    def draw_indicators(self):
        """Draws selection highlight and valid move indicators."""
        
        # Draw selected piece highlight
        if self.selected_piece:
            r, c = self.selected_piece
            # Highlight the square
            rect = pygame.Rect(
                self.OFFSET_X + c * self.SQUARE_SIZE,
                self.OFFSET_Y + r * self.SQUARE_SIZE,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )
            pygame.draw.rect(self.screen, self.SELECTION_HIGHLIGHT, rect, 5) # Draw blue border

        # Draw valid move indicators
        if self.valid_moves:
            # Create a surface for semi-transparency
            s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, self.MOVE_HIGHLIGHT, (self.SQUARE_SIZE // 2, self.SQUARE_SIZE // 2), self.SQUARE_SIZE // 4)

            for r, c in self.valid_moves.keys():
                top_left_x = self.OFFSET_X + c * self.SQUARE_SIZE
                top_left_y = self.OFFSET_Y + r * self.SQUARE_SIZE
                self.screen.blit(s, (top_left_x, top_left_y))

    def draw_ui_elements(self):
        """Draws the status message, turn indicator, and taken pieces counter."""
        
        # --- Back Button ---
        pygame.draw.rect(self.screen, (60, 60, 60), self.button_rect, border_radius=8)
        self.screen.blit(self.button_text, self.text_rect)
        
        # --- Status / Turn Indicator ---
        status_y = self.OFFSET_Y - 30
        turn_color = (200, 0, 0) if self.board_manager.current_turn == 'Red' else (50, 50, 50)
        
        # Draw a bold turn message
        turn_message = f"Turn: {self.board_manager.current_turn}"
        turn_render = self.big_font.render(turn_message, True, turn_color)
        turn_rect = turn_render.get_rect(center=(self.OFFSET_X + (self.BOARD_SIZE//2), status_y))
        self.screen.blit(turn_render, turn_rect)

        # Draw the main game status message (below the turn)
        msg_render = self.small_font.render(self.status_message, True, (0, 0, 0))
        msg_rect = msg_render.get_rect(center=(self.OFFSET_X + (self.BOARD_SIZE//2), status_y + 20))
        self.screen.blit(msg_render, msg_rect)

        # --- Taken Pieces Counter (Circles) ---
        counter_x_start = self.OFFSET_X + self.BOARD_SIZE + 10
        counter_y_start = self.OFFSET_Y + self.BOARD_SIZE/2 - 100
        circle_radius = 25
        padding = 70
        
        # Title
        title_render = self.small_font.render("Pieces Taken:", True, (0, 0, 0))
        self.screen.blit(title_render, (counter_x_start, counter_y_start))
        
        # --- Draw Red Taken Circle ---
        red_center = (counter_x_start + circle_radius, counter_y_start + padding)
        pygame.draw.circle(self.screen, (200, 0, 0), red_center, circle_radius) 
        red_count_text = self.big_font.render(str(self.board_manager.taken_pieces['Red']), True, (255, 255, 255))
        red_count_rect = red_count_text.get_rect(center=red_center)
        self.screen.blit(red_count_text, red_count_rect)

        red_label = self.small_font.render("Red", True, (0, 0, 0))
        self.screen.blit(red_label, (red_center[0] + circle_radius + 10, red_center[1] - red_label.get_height() // 2))

        # --- Draw Black Taken Circle ---
        black_center = (counter_x_start + circle_radius, counter_y_start + padding + 2 * circle_radius + 10)
        pygame.draw.circle(self.screen, (50, 50, 50), black_center, circle_radius)
        black_count_text = self.big_font.render(str(self.board_manager.taken_pieces['Black']), True, (255, 255, 255))
        black_count_rect = black_count_text.get_rect(center=black_center)
        self.screen.blit(black_count_text, black_count_rect)
        
        black_label = self.small_font.render("Black", True, (0, 0, 0))
        self.screen.blit(black_label, (black_center[0] + circle_radius + 10, black_center[1] - black_label.get_height() // 2))

    def draw(self):
        """Draws all game elements to the screen."""
        self.screen.fill((128, 128, 192))
        
        # Game Elements
        self.draw_board()
        self.draw_pieces()
        self.draw_indicators()
        
        # UI Elements
        self.draw_ui_elements()