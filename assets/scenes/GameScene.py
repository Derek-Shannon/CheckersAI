import pygame
from .Scene import Scene

class GameScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        try:
            self.board_image = pygame.image.load('assets/images/board.jpg').convert_alpha()
            self.board_image = pygame.transform.scale(self.board_image, (500, 500))

            self.red_piece_image = pygame.image.load('assets/images/red.png').convert_alpha()
            self.black_piece_image = pygame.image.load('assets/images/black.png').convert_alpha()
            
            # Scale pieces to fit the squares
            piece_size = 60
            self.red_piece_image = pygame.transform.scale(self.red_piece_image, (piece_size, piece_size))
            self.black_piece_image = pygame.transform.scale(self.black_piece_image, (piece_size, piece_size))

            self.images_loaded = True
        except pygame.error as e:
            print(f"Error loading images: {e}. Using placeholders.")
        
        # Back Button Setup (Top Left)
        self.button_rect = pygame.Rect(10, 10, 120, 40) # x, y, width, height
        self.font = pygame.font.Font(None, 36)
        self.button_text = self.font.render("<< Back", True, (255, 255, 255))
        self.text_rect = self.button_text.get_rect(center=self.button_rect.center)
        
        # Taken Pieces Counter Setup
        self.taken_pieces = {'Red': 0, 'Black': 0}
        self.big_font = pygame.font.Font(None, 74) 
        self.small_font = pygame.font.Font(None, 36)

    def handle_event(self, event):
        # Check for mouse click (used for the back button)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                if self.button_rect.collidepoint(event.pos):
                    return 'main_menu' # Signal to the main loop to switch to scenes

    def draw_back_button(self):
        # Draw the button background
        pygame.draw.rect(self.screen, (100, 100, 100), self.button_rect, border_radius=5)
        # Draw the text on the button
        self.screen.blit(self.button_text, self.text_rect)

    def draw_checkers_board_and_pieces(self):
        
        # Draw a central rectangle for the game board
        board_size = 500
        board_rect = pygame.Rect(0, 0, board_size, board_size)
        board_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        pygame.draw.rect(self.screen, (139, 69, 19), board_rect) # Brown background
        self.screen.blit(self.board_image, board_rect.topleft)
        
        square_size = board_size / 8
        example_x = board_rect.left + (1 * square_size) # Column 1
        example_y = board_rect.top + (2 * square_size) # Row 2
        
        # Draw the piece
        piece_offset = (square_size - self.red_piece_image.get_width()) // 2
        self.screen.blit(self.red_piece_image, (example_x + piece_offset, example_y + piece_offset))
        
        # Example: Draw one black piece
        example_x_black = board_rect.left + (5 * square_size) # Column 5
        example_y_black = board_rect.top + (4 * square_size) # Row 4
        
        piece_offset_black = (square_size - self.black_piece_image.get_width()) // 2
        self.screen.blit(self.black_piece_image, (example_x_black + piece_offset_black, example_y_black + piece_offset_black))

    def draw_taken_pieces_counter(self):
        # Position the counter on the right side
        counter_x = self.screen.get_width() - 150
        counter_y_start = 230
        
        # Title
        title_text = self.small_font.render("Pieces Taken:", True, (0, 0, 0))
        self.screen.blit(title_text, (counter_x, counter_y_start))
        
        # Red Pieces Counter
        red_text = self.small_font.render(f"{self.taken_pieces['Red']}", True, (200, 0, 0))
        self.screen.blit(red_text, (counter_x + 20, counter_y_start + 40))
        
        # Black Pieces Counter
        black_text = self.small_font.render(f"{self.taken_pieces['Black']}", True, (50, 50, 50))
        self.screen.blit(black_text, (counter_x + 20, counter_y_start + 80))


    def draw(self):
        self.screen.fill((255, 255, 0)) # background
        
        self.draw_checkers_board_and_pieces()
        self.draw_taken_pieces_counter()
        self.draw_back_button()