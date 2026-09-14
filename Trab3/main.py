import argparse
import math
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".deps"))
import pygame
from entities import Defender, Enemy, Projectile
from util import EventHandler

WIDTH, HEIGHT = 1000, 700


class Game:
    def __init__(self):
        self.events = EventHandler()
        self.events.observers.clear()
        self.player = Defender()
        self.enemies, self.bullets, self.effects = [], [], []
        self.wave = self.score = self.kills = self.remaining = 0
        self.spawn_timer = 0
        self.break_timer = 2
        self.paused = self.victory = False
        self.events.subscribe("Shoot", self.shoot)
        self.events.subscribe("SpawnEnemy", self.enemies.append)
        self.events.subscribe("DestroyObj", self.remove)
        self.events.subscribe("Collision", self.collide)
        self.events.subscribe("AttackPlayer", self.player.hit)
        self.events.subscribe("EnemyKilled", self.killed)
        self.events.subscribe("PowerUp", self.power_up)
        self.events.subscribe("PlayerDamaged", lambda pos: self.effects.append([pos, 0.4, (255, 110, 100)]))

    def shoot(self, data):
        self.bullets.append(Projectile(*data))

    def remove(self, obj):
        collection = self.bullets if isinstance(obj, Projectile) else self.enemies
        if obj in collection:
            collection.remove(obj)

    def collide(self, data):
        bullet, enemy = data
        enemy.hit(bullet)
        bullet.destroy()
        self.effects.append([enemy.pos.copy(), 0.25, bullet.color])

    def killed(self, enemy):
        self.score += 25 if enemy.armored else 10
        self.kills += 1
        if self.kills % 8 == 0:
            self.events.notify("PowerUp", 5)

    def power_up(self, duration):
        self.player.power = duration

    def update(self, dt, target, firing):
        if self.paused or self.player.hp <= 0 or self.victory:
            return
        self.player.update(dt, target, firing)
        if not self.remaining and not self.enemies:
            self.break_timer -= dt
            if self.break_timer <= 0:
                if self.wave == 8:
                    self.victory = True
                    return
                self.wave += 1
                self.remaining = 5 + self.wave * 2
                self.break_timer = 3
        if self.remaining:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                angle = random.uniform(0, math.tau)
                pos = self.player.pos + pygame.Vector2(math.cos(angle) * 560, math.sin(angle) * 380)
                self.events.notify("SpawnEnemy", Enemy(pos, self.player.pos, self.wave, self.remaining % 4 == 0))
                self.remaining -= 1
                self.spawn_timer = max(0.35, 1.1 - self.wave * 0.08)
        for enemy in self.enemies[:]:
            enemy.update(dt)
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.alive:
                continue
            # Test the traveled segment so fast bullets cannot skip a target.
            segment = bullet.pos - bullet.previous
            for enemy in self.enemies[:]:
                t = max(0, min(1, (enemy.pos - bullet.previous).dot(segment) / segment.length_squared())) if segment.length_squared() else 0
                if (bullet.previous + segment * t).distance_to(enemy.pos) <= enemy.radius + bullet.radius:
                    self.events.notify("Collision", (bullet, enemy))
                    break
        for effect in self.effects:
            effect[1] -= dt
        self.effects = [effect for effect in self.effects if effect[1] > 0]

    def draw(self, screen, fonts):
        small, medium, large = fonts
        screen.fill((23, 38, 40))
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, (29, 46, 47), (x, 82), (x, 625))
        for y in range(100, 625, 50):
            pygame.draw.line(screen, (29, 46, 47), (0, y), (WIDTH, y))
        for radius in (100, 200, 300):
            pygame.draw.circle(screen, (38, 57, 57), self.player.pos, radius, 1)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.player.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for pos, life, color in self.effects:
            pygame.draw.circle(screen, color, pos, max(1, int((0.5 - life) * 75)), 2)
        pygame.draw.rect(screen, (15, 24, 29), (0, 0, WIDTH, 82))
        pygame.draw.rect(screen, (15, 24, 29), (0, 625, WIDTH, 75))

        def label(text, pos, font=small, color=(226, 236, 230)):
            screen.blit(font.render(text, True, color), pos)

        label("PATO SENTINELA", (25, 16), medium)
        label("DEFESA DO NINHO", (26, 49), color=(130, 168, 156))
        label(f"ONDA {self.wave}/8", (390, 25), medium)
        label(f"PONTOS {self.score:05}", (565, 25), medium)
        label(f"VIDA {self.player.hp}/10", (815, 25), medium, (124, 223, 175))
        for index, weapon in enumerate(self.player.weapons):
            x = 25 + index * 185
            active = type(self.player.state) is weapon
            pygame.draw.line(screen, weapon.color if active else (56, 72, 77), (x, 638), (x + 162, 638), 3)
            label(f"{index + 1}  {weapon.name}", (x, 650), color=weapon.color if active else (139, 159, 160))
        label("P  PAUSA     R  REINICIAR", (660, 650))
        if self.player.power:
            label(f"CADENCIA 2X: {self.player.power:.1f}s", (25, 100), color=(249, 218, 105))
        if not self.enemies and not self.remaining and not self.victory:
            label(f"Proxima onda em {max(0, math.ceil(self.break_timer))}", (390, 112))
        if self.paused or self.player.hp <= 0 or self.victory:
            overlay = pygame.Surface((WIDTH, 543), pygame.SRCALPHA)
            overlay.fill((10, 17, 23, 215))
            screen.blit(overlay, (0, 82))
            title = "NINHO PROTEGIDO!" if self.victory else "FIM DE JOGO" if self.player.hp <= 0 else "PAUSADO"
            rendered = large.render(title, True, (236, 239, 222))
            screen.blit(rendered, rendered.get_rect(center=(500, 325)))
            rendered = medium.render(f"{self.score} pontos", True, (124, 223, 175))
            screen.blit(rendered, rendered.get_rect(center=(500, 380)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=0)
    args = parser.parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pato Sentinela - Trab3")
    fonts = [pygame.font.SysFont("consolas", size) for size in (17, 23, 44)]
    clock = pygame.time.Clock()
    game = Game()
    running = True
    frames = 0
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game = Game()
                elif event.key == pygame.K_p:
                    game.paused = not game.paused
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    game.player.change_state(event.key - pygame.K_1)
        game.update(dt, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE])
        game.draw(screen, fonts)
        pygame.display.flip()
        frames += 1
        if args.frames and frames >= args.frames:
            running = False
    pygame.quit()


if __name__ == "__main__":
    main()
