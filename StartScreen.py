import pygame
import sys

pygame.init()


pygame.display.set_caption("Checkers - Main Menu")

screen = pygame.display.set_mode((500, 500))
font = pygame.font.Font(None, 36)


start_button = pygame.Rect(180, 320, 150, 50)

radio1_pos = (150, 100)   
radio2_pos = (150, 150)   
radio_radius = 10


radio1_rect = pygame.Rect(radio1_pos[0]-radio_radius, radio1_pos[1]-radio_radius,
                          radio_radius*2, radio_radius*2)
radio2_rect = pygame.Rect(radio2_pos[0]-radio_radius, radio2_pos[1]-radio_radius,
                          radio_radius*2, radio_radius*2)

selected = None


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if radio1_rect.collidepoint(event.pos):
                selected = "PVP"
            if radio2_rect.collidepoint(event.pos):
                selected = "AI"
            if start_button.collidepoint(event.pos):
                if selected is None:
                    print("Start clicked but no mode selected yet!")
                else:
                    print("Start clicked with mode:", selected)

 
    screen.fill((200, 200, 200))

    mouse_pos = pygame.mouse.get_pos()
    
    start_color = (255, 0, 0)

    if start_button.collidepoint(mouse_pos):
        start_color = (200, 0, 0)

  
    pygame.draw.rect(screen, start_color, start_button)

  
    label = font.render("Start", True, (255, 255, 255))  


    label_rect = label.get_rect(center=start_button.center)


    screen.blit(label, label_rect)


    pygame.draw.circle(screen, (0, 0, 0), radio1_pos, 10, 2)  

   
    pygame.draw.circle(screen, (0, 0, 0), radio2_pos, 10, 2)


    if selected == "PVP":
        pygame.draw.circle(screen, (0, 0, 0), radio1_pos, 5)  
    elif selected == "AI":
        pygame.draw.circle(screen, (0, 0, 0), radio2_pos, 5)
  

    screen.blit(font.render("Player vs Player", True, (0, 0, 0)), (180, 90)) 
    screen.blit(font.render("Player vs AI", True, (0, 0, 0)), (180, 140))

   
    pygame.display.flip()  
