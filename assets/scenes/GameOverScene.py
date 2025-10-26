import pygame
from .Scene import Scene

class GameOverScene(Scene):
    def __init__(self, screen, winner_message="No winner"):
        super().__init__(screen)
        self.winner_message = winner_message
        self.font = pygame.font.Font(None, 74)
    def draw(self):
        self.screen.fill((128, 128, 192))
        font = pygame.font.Font(None, 74)
        text = self.font.render(self.winner_message, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)
        
        # Instruction for the user
        small_font = pygame.font.Font(None, 36)
        instruction_text = small_font.render("Press SPACE to return to Main Menu", True, (0, 0, 0))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_rect().centerx, self.screen.get_rect().centery + 100))
        self.screen.blit(instruction_text, instruction_rect)