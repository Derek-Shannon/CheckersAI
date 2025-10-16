import pygame
from .Scene import Scene

class GameOverScene(Scene):
    def draw(self):
        self.screen.fill((255, 0, 0)) # Red background
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over, The winner is: ", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)
        
        # Instruction for the user
        small_font = pygame.font.Font(None, 36)
        instruction_text = small_font.render("Press SPACE to return to Main Menu", True, (0, 0, 0))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_rect().centerx, self.screen.get_rect().centery + 100))
        self.screen.blit(instruction_text, instruction_rect)