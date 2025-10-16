import pygame

class Scene:
    def __init__(self, screen):
        self.screen = screen

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class MainMenuScene(Scene):
    def draw(self):
        self.screen.fill((0, 0, 255)) # Blue background
        font = pygame.font.Font(None, 74)
        text = font.render("Main Menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)

class GameScene(Scene):
    def draw(self):
        self.screen.fill((0, 255, 0)) # Green background
        font = pygame.font.Font(None, 74)
        text = font.render("Playing Game", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)

class GameOverScene(Scene):
    def draw(self):
        self.screen.fill((255, 0, 0)) # Green background
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over, The winner is: ", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, text_rect)

class GameStateManager:
    def __init__(self, initial_scene):
        self.current_scene = initial_scene

    def set_scene(self, new_scene):
        self.current_scene = new_scene

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Multiple Screens Example")

main_menu_scene = MainMenuScene(screen)
game_scene = GameScene(screen)
game_over_scene = GameOverScene(screen)
game_state_manager = GameStateManager(main_menu_scene)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if isinstance(game_state_manager.current_scene, MainMenuScene):
                    game_state_manager.set_scene(game_scene)
                elif isinstance(game_state_manager.current_scene, GameScene):
                    game_state_manager.set_scene(game_over_scene)
                else:
                    game_state_manager.set_scene(main_menu_scene)
        game_state_manager.current_scene.handle_event(event)

    game_state_manager.current_scene.update()
    game_state_manager.current_scene.draw()
    pygame.display.flip()

pygame.quit()