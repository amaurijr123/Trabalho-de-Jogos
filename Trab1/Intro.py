# Inicialização
import pygame 
import random
pygame.init()
pygame.font.init()



font = font = pygame.font.Font(None, 50)
Nome = "Amauri"

random.seed(Nome)
x, y =  random.randint(0, 500), random.randint(0, 400)

text_surface = font.render(Nome, True, (0,0,0))
rect = text_surface.get_rect(topleft=(x, y))

print(y)

# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

#loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        # Desenha
        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (255,255,255), rect)
        screen.blit(text_surface, (x, y))
        pygame.display.flip()
