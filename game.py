import pygame

from assets.scenes.Scene import Scene
# --- Scene Classes ---
from assets.scenes.GameScene import GameScene
from assets.scenes.GameOverScene import GameOverScene
from assets.scenes.MainMenuScene import MainMenuScene


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

# Initialize scenes
main_menu_scene = MainMenuScene(screen)
game_scene = GameScene(screen)
game_over_scene = GameOverScene(screen)
game_state_manager = GameStateManager(main_menu_scene)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Let the current scene handle the event and check for a scene change signal
        scene_signal = game_state_manager.current_scene.handle_event(event)

        if scene_signal == 'main_menu':
            game_state_manager.set_scene(main_menu_scene)
            
        # Handle scene switching with SPACE key (original logic)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if isinstance(game_state_manager.current_scene, MainMenuScene):
                    game_state_manager.set_scene(game_scene)
                elif isinstance(game_state_manager.current_scene, GameScene):
                    game_state_manager.set_scene(game_over_scene)
                elif isinstance(game_state_manager.current_scene, GameOverScene):
                    game_state_manager.set_scene(main_menu_scene)

    game_state_manager.current_scene.update()
    game_state_manager.current_scene.draw()
    pygame.display.flip()

pygame.quit()