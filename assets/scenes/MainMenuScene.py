import pygame
from .Scene import Scene

class MainMenuScene(Scene):
    def draw(self):
        self.screen.fill((0, 0, 255)) # Blue background
        font = pygame.font.Font(None, 74)
        text = font.render("Main Menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)
        
        # Instruction for the user
        small_font = pygame.font.Font(None, 36)
        instruction_text = small_font.render("Press SPACE to Start Game", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(self.screen.get_rect().centerx, self.screen.get_rect().centery + 100))
        self.screen.blit(instruction_text, instruction_rect)