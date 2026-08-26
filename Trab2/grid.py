"""Grade e regras de um Sokoban pequeno."""

from pathlib import Path

import pygame


FLOOR = " "
WALL = "#"
GOAL = "."
BOX = "$"
PLAYER = "@"
BOX_ON_GOAL = "*"
PLAYER_ON_GOAL = "+"


class Cell:
    """Uma célula desenhável da grade."""

    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size

    @property
    def rect(self):
        return pygame.Rect(self.col * self.size, self.row * self.size,
                           self.size, self.size)


class Grid:
    """Mantém o mapa, movimentação, histórico e animação visual."""

    def __init__(self, x, y, cell_size, level):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.level = tuple(level)
        self.rows = len(level)
        self.cols = max(len(line) for line in level)
        self.elapsed = 0.0
        self.walk_timer = 0.0
        self.bump_timer = 0.0
        self.won_timer = 0.0
        self.facing_left = False
        self.moves = 0
        self.pushes = 0
        self.history = []
        self._load_images()
        self.reset()

    def _load_images(self):
        image_dir = Path(__file__).resolve().parent / "images" / "duck"
        names = ("base", "blink", "step", "wing", "quack", "crouch")
        self.duck = {}
        target = int(self.cell_size * 0.78)
        for name in names:
            image = pygame.image.load(str(image_dir / f"{name}.png")).convert_alpha()
            self.duck[name] = pygame.transform.scale(image, (target, target))

    def reset(self):
        self.walls = set()
        self.goals = set()
        self.boxes = set()
        self.player = (0, 0)
        for row, line in enumerate(self.level):
            for col, char in enumerate(line):
                pos = (row, col)
                if char == WALL:
                    self.walls.add(pos)
                elif char in (GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL):
                    self.goals.add(pos)
                if char in (BOX, BOX_ON_GOAL):
                    self.boxes.add(pos)
                elif char in (PLAYER, PLAYER_ON_GOAL):
                    self.player = pos
        self.moves = 0
        self.pushes = 0
        self.history.clear()
        self.walk_timer = self.bump_timer = self.won_timer = 0.0

    @property
    def completed(self):
        return bool(self.boxes) and self.boxes <= self.goals

    def move(self, dr, dc):
        """Tenta mover o pato e retorna True quando o mapa mudou."""
        if self.completed:
            return False
        self.facing_left = dc < 0 if dc else self.facing_left
        target = (self.player[0] + dr, self.player[1] + dc)
        if target in self.walls:
            self.bump_timer = 0.22
            return False

        pushed = None
        if target in self.boxes:
            beyond = (target[0] + dr, target[1] + dc)
            if beyond in self.walls or beyond in self.boxes:
                self.bump_timer = 0.22
                return False
            pushed = (target, beyond)

        self.history.append((self.player, set(self.boxes), self.moves, self.pushes))
        self.player = target
        self.moves += 1
        if pushed:
            old, new = pushed
            self.boxes.remove(old)
            self.boxes.add(new)
            self.pushes += 1
        self.walk_timer = 0.18
        return True

    def undo(self):
        if not self.history:
            return False
        self.player, self.boxes, self.moves, self.pushes = self.history.pop()
        self.won_timer = 0.0
        return True

    def click(self, mouse_pos):
        """Clique em uma célula vizinha equivale a uma tecla direcional."""
        col = (mouse_pos[0] - self.x) // self.cell_size
        row = (mouse_pos[1] - self.y) // self.cell_size
        dr, dc = row - self.player[0], col - self.player[1]
        if abs(dr) + abs(dc) == 1:
            return self.move(dr, dc)
        return False

    def update(self, dt):
        self.elapsed += dt
        self.walk_timer = max(0.0, self.walk_timer - dt)
        self.bump_timer = max(0.0, self.bump_timer - dt)
        if self.completed:
            self.won_timer += dt

    def _tile_rect(self, row, col):
        return pygame.Rect(self.x + col * self.cell_size,
                           self.y + row * self.cell_size,
                           self.cell_size, self.cell_size)

    def _draw_floor(self, screen, rect, row, col):
        color = (213, 231, 197) if (row + col) % 2 == 0 else (202, 222, 183)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, (178, 199, 160), rect, 1, border_radius=5)

    def _draw_wall(self, screen, rect):
        pygame.draw.rect(screen, (73, 102, 112), rect, border_radius=6)
        pygame.draw.rect(screen, (108, 140, 146), rect.inflate(-6, -6), 3,
                         border_radius=4)
        pygame.draw.line(screen, (52, 77, 87), rect.midleft, rect.midright, 2)

    def _draw_goal(self, screen, rect):
        pygame.draw.circle(screen, (245, 191, 66), rect.center, self.cell_size // 4)
        pygame.draw.circle(screen, (255, 230, 142), rect.center, self.cell_size // 7)
        pygame.draw.circle(screen, (178, 121, 35), rect.center, self.cell_size // 4, 3)

    def _draw_box(self, screen, rect, on_goal):
        box_rect = rect.inflate(-12, -12)
        color = (89, 176, 102) if on_goal else (188, 123, 67)
        edge = (45, 120, 62) if on_goal else (127, 76, 41)
        pygame.draw.rect(screen, color, box_rect, border_radius=7)
        pygame.draw.rect(screen, edge, box_rect, 4, border_radius=7)
        pygame.draw.line(screen, edge, box_rect.topleft, box_rect.bottomright, 3)
        pygame.draw.line(screen, edge, box_rect.topright, box_rect.bottomleft, 3)

    def _duck_frame(self):
        if self.completed:
            return "quack" if int(self.won_timer * 5) % 2 == 0 else "wing"
        if self.bump_timer > 0:
            return "crouch"
        if self.walk_timer > 0:
            return "step" if int(self.elapsed * 18) % 2 == 0 else "base"
        return "blink" if int(self.elapsed) % 5 == 4 else "base"

    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = self._tile_rect(row, col)
                self._draw_floor(screen, rect, row, col)
                if (row, col) in self.goals:
                    self._draw_goal(screen, rect)
                if (row, col) in self.walls:
                    self._draw_wall(screen, rect)

        for row, col in self.boxes:
            self._draw_box(screen, self._tile_rect(row, col), (row, col) in self.goals)

        frame = self.duck[self._duck_frame()]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        player_rect = frame.get_rect(center=self._tile_rect(*self.player).center)
        if self.completed:
            player_rect.y -= int(abs(pygame.math.Vector2(0, 3).rotate(self.won_timer * 400).y))
        screen.blit(frame, player_rect)

