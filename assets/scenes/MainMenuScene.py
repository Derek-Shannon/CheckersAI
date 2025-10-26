import pygame
from .Scene import Scene

class MainMenuScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 48)
        
        # --- Title Setup ---
        self.title_text = self.font_large.render("Pygame Checkers", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        
        # --- Button Setup ---
        BUTTON_WIDTH = 280
        BUTTON_HEIGHT = 70
        CENTER_X = self.SCREEN_WIDTH // 2
        
        # PvP Button
        self.pvp_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.pvp_rect.center = (CENTER_X, self.SCREEN_HEIGHT // 2 - 50)
        self.pvp_text = self.font_medium.render("Player vs Player", True, (255, 255, 255))
        self.pvp_text_rect = self.pvp_text.get_rect(center=self.pvp_rect.center)
        
        # PvAI Button
        self.pvai_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.pvai_rect.center = (CENTER_X, self.SCREEN_HEIGHT // 2 + 50)
        self.pvai_text = self.font_medium.render("Player vs AI", True, (255, 255, 255))
        self.pvai_text_rect = self.pvai_text.get_rect(center=self.pvai_rect.center)
        
        # Colors for visual feedback
        self.button_color = (0, 100, 200) # Default Blue
        self.hover_color = (0, 150, 250) # Highlight Blue
        self.pvp_current_color = self.button_color
        self.pvai_current_color = self.button_color

    def handle_event(self, event):
        # Update hover state
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.pvp_current_color = self.hover_color if self.pvp_rect.collidepoint(mouse_pos) else self.button_color
            self.pvai_current_color = self.hover_color if self.pvai_rect.collidepoint(mouse_pos) else self.button_color
            
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.pvp_rect.collidepoint(mouse_pos):
                # Signal to start PvP game mode
                return 'start_pvp' 
            elif self.pvai_rect.collidepoint(mouse_pos):
                # Signal to start PvAI game mode
                return 'start_pvai'
        
        return None

    def draw(self):
        # Background: Gradient dark blue/purple
        self.screen.fill((128, 128, 192))
        
        # Title
        self.screen.blit(self.title_text, self.title_rect)
        
        # Draw PvP Button
        pygame.draw.rect(self.screen, self.pvp_current_color, self.pvp_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pvp_rect, 4, border_radius=15) # White Border
        self.screen.blit(self.pvp_text, self.pvp_text_rect)

        # Draw PvAI Button
        pygame.draw.rect(self.screen, self.pvai_current_color, self.pvai_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pvai_rect, 4, border_radius=15) # White Border
        self.screen.blit(self.pvai_text, self.pvai_text_rect)
        
        # Instructions
        small_font = pygame.font.Font(None, 30)
        instruction_text = small_font.render("Select a mode to begin playing Checkers.", True, (180, 180, 255))
        instruction_rect = instruction_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
        self.screen.blit(instruction_text, instruction_rect)

    def update(self):
        # Menu state is static, no update logic needed here
        pass
