from pathlib import Path
import pygame
from util import EventHandler


class WeaponState:
    name = "RAPIDA"
    interval = 0.18
    damage = 1
    stun = 0
    color = (249, 218, 105)

    def fire(self, player, target):
        direction = pygame.Vector2(target) - player.pos
        if direction.length_squared():
            EventHandler().notify("Shoot", (player.pos.copy(), direction.normalize(), self))


class Cannon(WeaponState):
    name = "CANHAO"
    interval = 0.7
    damage = 4
    color = (255, 151, 107)


class Electric(WeaponState):
    name = "ELETRICA"
    interval = 0.48
    stun = 1.2
    color = (107, 225, 246)


class Defender:
    weapons = (WeaponState, Cannon, Electric)

    def __init__(self):
        self.pos = pygame.Vector2(500, 365)
        self.hp = 10
        self.state = WeaponState()
        self.cooldown = self.invincible = self.power = 0
        self.target = self.pos + pygame.Vector2(1, 0)
        path = Path(__file__).parent / "images/duck/base.png"
        self.sprite = pygame.transform.scale(pygame.image.load(str(path)).convert_alpha(), (64, 64))

    def change_state(self, index):
        self.state = self.weapons[index]()

    def update(self, dt, target, firing):
        self.target = pygame.Vector2(target)
        self.invincible = max(0, self.invincible - dt)
        self.power = max(0, self.power - dt)
        self.cooldown = max(0, self.cooldown - dt)
        if firing and self.cooldown == 0:
            self.state.fire(self, target)
            self.cooldown = self.state.interval * (0.5 if self.power else 1)

    def hit(self, damage):
        if self.invincible or self.hp <= 0:
            return
        self.hp = max(0, self.hp - damage)
        self.invincible = 1
        EventHandler().notify("PlayerDamaged", self.pos.copy())

    def draw(self, screen):
        pygame.draw.circle(screen, (66, 85, 80), self.pos, 42)
        pygame.draw.circle(screen, self.state.color, self.pos, 42, 3)
        direction = self.target - self.pos
        if direction.length_squared():
            pygame.draw.line(screen, self.state.color, self.pos, self.pos + direction.normalize() * 56, 9)
        if not self.invincible or int(self.invincible * 12) % 2:
            screen.blit(self.sprite, self.sprite.get_rect(center=self.pos))
        if self.power:
            pygame.draw.circle(screen, (249, 218, 105), self.pos, 49, 2)


class Approaching:
    def update(self, enemy, dt):
        delta = enemy.target - enemy.pos
        if delta.length() <= 85:
            enemy.state = Aiming()
        else:
            enemy.pos += delta.normalize() * min(enemy.speed * dt, delta.length() - 85)


class Aiming:
    def __init__(self):
        self.timer = 0.9

    def update(self, enemy, dt):
        self.timer -= dt
        if self.timer <= 0:
            EventHandler().notify("AttackPlayer", 1)
            enemy.state = Aiming()


class Stunned:
    def __init__(self, duration):
        self.timer = duration

    def update(self, enemy, dt):
        self.timer -= dt
        if self.timer <= 0:
            enemy.state = Approaching()


class Enemy:
    def __init__(self, pos, target, wave, armored=False):
        self.pos = pygame.Vector2(pos)
        self.target = pygame.Vector2(target)
        self.armored = armored
        self.max_hp = (7 if armored else 3) + wave // 2
        self.hp = self.max_hp
        self.speed = (35 if armored else 57) + wave * 3
        self.radius = 23 if armored else 17
        self.state = Approaching()
        self.alive = True

    def update(self, dt):
        self.state.update(self, dt)

    def hit(self, bullet):
        if not self.alive:
            return
        self.hp -= bullet.damage
        if self.hp <= 0:
            self.alive = False
            EventHandler().notify("EnemyKilled", self)
            EventHandler().notify("DestroyObj", self)
        elif bullet.stun:
            self.state = Stunned(bullet.stun)

    def draw(self, screen):
        color = (107, 225, 246) if isinstance(self.state, Stunned) else (224, 103, 127)
        if isinstance(self.state, Aiming):
            pygame.draw.line(screen, (128, 67, 79), self.pos, self.target, 2)
        pygame.draw.circle(screen, (15, 25, 29), self.pos + pygame.Vector2(3, 5), self.radius + 2)
        pygame.draw.circle(screen, color, self.pos, self.radius)
        if self.armored:
            pygame.draw.circle(screen, (245, 202, 130), self.pos, self.radius, 4)
        for offset in (-6, 6):
            pygame.draw.circle(screen, (26, 34, 39), self.pos + pygame.Vector2(offset, -3), 3)
        pygame.draw.rect(screen, (45, 52, 56), (self.pos.x - 20, self.pos.y - 33, 40, 4))
        pygame.draw.rect(screen, color, (self.pos.x - 20, self.pos.y - 33, 40 * self.hp / self.max_hp, 4))


class Projectile:
    def __init__(self, pos, direction, weapon):
        self.pos = pygame.Vector2(pos)
        self.previous = self.pos.copy()
        self.velocity = direction * 650
        self.damage, self.stun, self.color = weapon.damage, weapon.stun, weapon.color
        self.radius = 5 if self.damage == 1 else 9
        self.alive = True
        self.life = 2

    def update(self, dt):
        self.previous = self.pos.copy()
        self.pos += self.velocity * dt
        self.life -= dt
        if self.life <= 0:
            self.destroy()

    def destroy(self):
        if self.alive:
            self.alive = False
            EventHandler().notify("DestroyObj", self)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.pos - self.velocity * 0.025, self.pos, 3)
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
