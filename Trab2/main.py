"""Sokopato: Sokoban pequeno com teclado, mouse e animações."""

import sys

import pygame

from grid import Grid


WIDTH, HEIGHT = 800, 650
CELL_SIZE = 64
FPS = 60

LEVELS = [
    (
        "########",
        "#      #",
        "#  .   #",
        "#  $   #",
        "#  @   #",
        "#      #",
        "########",
    ),
    (
        "########",
        "# .  . #",
        "# $  $ #",
        "#   @  #",
        "#      #",
        "#      #",
        "########",
    ),
]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sokopato")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 29)
        self.small_font = pygame.font.Font(None, 22)
        self.level_index = 0
        self.grid = None
        self.restart_rect = pygame.Rect(0, 0, 0, 0)
        self.undo_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index % len(LEVELS)
        level = LEVELS[self.level_index]
        grid_width = max(map(len, level)) * CELL_SIZE
        self.grid = Grid((WIDTH - grid_width) // 2, 145, CELL_SIZE, level)

    def handle_key(self, key):
        directions = {
            pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
            pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0),
            pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
            pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1),
        }
        if key in directions:
            self.grid.move(*directions[key])
        elif key == pygame.K_r:
            self.grid.reset()
        elif key in (pygame.K_u, pygame.K_BACKSPACE):
            self.grid.undo()
        elif key in (pygame.K_n, pygame.K_RETURN) and self.grid.completed:
            self.load_level(self.level_index + 1)

    def draw_button(self, text, rect):
        mouse_over = rect.collidepoint(pygame.mouse.get_pos())
        color = (243, 190, 63) if mouse_over else (232, 238, 226)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (54, 78, 82), rect, 2, border_radius=10)
        label = self.small_font.render(text, True, (35, 52, 55))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill((248, 244, 225))
        title = self.title_font.render("SOKOPATO", True, (45, 75, 78))
        self.screen.blit(title, (38, 23))
        subtitle = self.small_font.render("Empurre todas as caixas para os ninhos", True,
                                          (83, 106, 102))
        self.screen.blit(subtitle, (40, 70))

        stats = f"Nível {self.level_index + 1}/{len(LEVELS)}    Movimentos: {self.grid.moves}    Empurrões: {self.grid.pushes}"
        stat_text = self.font.render(stats, True, (45, 75, 78))
        self.screen.blit(stat_text, (40, 105))

        self.grid.draw(self.screen)
        y = HEIGHT - 42
        self.restart_rect = pygame.Rect(39, y - 2, 112, 30)
        self.undo_rect = pygame.Rect(160, y - 2, 112, 30)
        self.draw_button("Reiniciar (R)", self.restart_rect)
        self.draw_button("Desfazer (U)", self.undo_rect)
        help_text = self.small_font.render("Setas/WASD ou clique numa célula vizinha", True,
                                           (74, 92, 90))
        self.screen.blit(help_text, (295, y + 4))

        if self.grid.completed:
            panel = pygame.Rect(195, 288, 410, 110)
            shade = pygame.Surface(panel.size, pygame.SRCALPHA)
            shade.fill((30, 61, 65, 232))
            self.screen.blit(shade, panel)
            pygame.draw.rect(self.screen, (255, 210, 74), panel, 3, border_radius=12)
            won = self.title_font.render("NÍVEL COMPLETO!", True, (255, 224, 109))
            tip = self.small_font.render("Enter/N ou clique para continuar", True, (246, 248, 235))
            self.screen.blit(won, won.get_rect(center=(WIDTH // 2, 325)))
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, 370)))
            self.next_rect = panel
        else:
            self.next_rect = pygame.Rect(0, 0, 0, 0)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.restart_rect.collidepoint(event.pos):
                        self.grid.reset()
                    elif self.undo_rect.collidepoint(event.pos):
                        self.grid.undo()
                    elif self.grid.completed and self.next_rect.collidepoint(event.pos):
                        self.load_level(self.level_index + 1)
                    else:
                        self.grid.click(event.pos)

            self.grid.update(dt)
            self.draw()

        pygame.quit()
        return 0


if __name__ == "__main__":
    sys.exit(Game().run())

