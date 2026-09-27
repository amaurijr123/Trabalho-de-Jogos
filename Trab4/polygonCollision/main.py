"""Jogo de Breakout com obstáculos poligonais. Execute: python main.py"""

import math
import random
import pygame
from game_physics import circle_polygon_contact, entered_region, reflect

W, H, R = 800, 600, 9


def new_bricks():
    return [[(x + (8 if (row + col) % 2 else 0), y),
             (x + (61 if (row + col) % 2 else 69), y),
             (x + (69 if (row + col) % 2 else 61), y + 30),
             (x + (0 if (row + col) % 2 else 8), y + 30)]
            for row in range(3) for col in range(8)
            for x, y in [(58 + col * 87, 86 + row * 47)]]


def new_ball(x):
    return [float(x), 520.0], [random.choice((-180.0, 180.0)), -310.0]


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Breakout Poligonal')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 27)
    paddle_x = W / 2
    ball, velocity = new_ball(paddle_x)
    bricks, points, lives, launched = new_bricks(), 0, 3, False
    boost = [(320, 285), (480, 285), (510, 315), (290, 315)]
    bonus = [(352, 365), (448, 365), (470, 390), (330, 390)]
    bumpers = [[(130, 340), (220, 395), (125, 410)],
               [(670, 340), (580, 395), (675, 410)]]

    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 1 / 30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if lives <= 0 or not bricks:
                        bricks, points, lives = new_bricks(), 0, 3
                        ball, velocity = new_ball(paddle_x)
                        launched = False
                    else:
                        launched = True

        keys = pygame.key.get_pressed()
        if pygame.mouse.get_focused():
            paddle_x = pygame.mouse.get_pos()[0]
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle_x -= 480 * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle_x += 480 * dt
        paddle_x = max(53, min(W - 53, paddle_x))
        paddle = [(paddle_x - 51, 550), (paddle_x + 51, 550),
                  (paddle_x + 40, 566), (paddle_x - 40, 566)]

        if lives > 0 and bricks:
            if not launched:
                ball[0] = paddle_x
            else:
                # Subpassos evitam atravessar peças estreitas.
                for _ in range(4):
                    previous = ball.copy()
                    ball[0] += velocity[0] * dt / 4
                    ball[1] += velocity[1] * dt / 4
                    if ball[0] < R or ball[0] > W - R:
                        ball[0] = max(R, min(W - R, ball[0]))
                        velocity[0] *= -1
                    if ball[1] < 55 + R:
                        ball[1] = 55 + R
                        velocity[1] = abs(velocity[1])
                    if ball[1] > H + R:
                        lives -= 1
                        ball, velocity = new_ball(paddle_x)
                        launched = False
                        break

                    if entered_region(previous, ball, boost):
                        factor = min(1.18, 650 / math.hypot(*velocity))
                        velocity = [v * factor for v in velocity]
                    if entered_region(previous, ball, bonus):
                        points += 25

                    obstacles = [(paddle, 'paddle')]
                    obstacles += [(b, 'bumper') for b in bumpers]
                    obstacles += [(b, 'brick') for b in bricks]
                    for polygon, kind in obstacles:
                        contact = circle_polygon_contact(ball, R, polygon)
                        if contact is None:
                            continue
                        normal, depth = contact
                        ball[0] += normal[0] * (depth + 0.1)
                        ball[1] += normal[1] * (depth + 0.1)
                        velocity = list(reflect(velocity, normal))
                        if kind == 'paddle' and normal[1] < -0.5:
                            velocity[0] += (ball[0] - paddle_x) * 3.2
                            velocity[1] = -abs(velocity[1])
                        elif kind == 'brick':
                            bricks.remove(polygon)
                            points += 10
                        break

        screen.fill((16, 22, 39))
        pygame.draw.rect(screen, (38, 51, 76), (0, 0, W, 55))
        screen.blit(font.render(f'Pontos: {points}', True, 'white'), (20, 17))
        screen.blit(font.render(f'Vidas: {lives}', True, 'white'), (665, 17))
        for brick in bricks:
            pygame.draw.polygon(screen, (80, 192, 219), brick)
            pygame.draw.polygon(screen, 'white', brick, 2)
        for bumper in bumpers:
            pygame.draw.polygon(screen, (249, 138, 86), bumper)
            pygame.draw.polygon(screen, 'white', bumper, 2)
        pygame.draw.polygon(screen, (112, 212, 122), boost, 2)
        screen.blit(font.render('VELOCIDADE', True, (112, 212, 122)), (326, 289))
        pygame.draw.polygon(screen, (248, 213, 93), bonus, 2)
        screen.blit(font.render('+25', True, (248, 213, 93)), (380, 366))
        pygame.draw.polygon(screen, (180, 133, 238), paddle)
        pygame.draw.circle(screen, 'white', (round(ball[0]), round(ball[1])), R)
        if not launched or not bricks:
            message = ('Vitória! ESPAÇO para reiniciar' if not bricks else
                       'Fim de jogo! ESPAÇO para reiniciar' if lives <= 0 else
                       'ESPAÇO para lançar | Mouse ou setas para mover')
            label = font.render(message, True, 'white')
            screen.blit(label, label.get_rect(center=(W / 2, 455)))
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
