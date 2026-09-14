import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from main import Game, pygame
from entities import Aiming, Approaching, Electric, Enemy, Projectile, Stunned


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1000, 700))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game = Game()

    def test_damage_has_temporary_invincibility(self):
        player = self.game.player
        self.game.events.notify("AttackPlayer", 1)
        self.game.events.notify("AttackPlayer", 1)
        self.assertEqual(player.hp, 9)
        player.update(1.1, (0, 0), False)
        self.game.events.notify("AttackPlayer", 1)
        self.assertEqual(player.hp, 8)

    def test_enemy_aims_stuns_and_recovers(self):
        enemy = Enemy((580, 365), self.game.player.pos, 1)
        enemy.update(0.1)
        self.assertIsInstance(enemy.state, Aiming)
        enemy.hit(Projectile((0, 0), pygame.Vector2(1, 0), Electric()))
        self.assertIsInstance(enemy.state, Stunned)
        enemy.update(1)
        self.assertEqual(self.game.player.hp, 10)
        enemy.update(0.3)
        self.assertIsInstance(enemy.state, Approaching)
        enemy.update(0.1)
        enemy.update(1)
        self.assertEqual(self.game.player.hp, 9)

    def test_collision_removes_objects_and_awards_score(self):
        game = self.game
        enemy = Enemy((570, 365), game.player.pos, 1)
        game.events.notify("SpawnEnemy", enemy)
        game.player.change_state(1)
        game.update(0.15, enemy.pos, True)
        self.assertFalse(game.enemies)
        self.assertFalse(game.bullets)
        self.assertEqual(game.score, 10)

    def test_power_up_and_restart_subscriptions(self):
        game = self.game
        for _ in range(8):
            game.killed(Enemy((0, 0), game.player.pos, 1))
        self.assertEqual(game.player.power, 5)
        replacement = Game()
        replacement.events.notify("AttackPlayer", 1)
        self.assertEqual(replacement.player.hp, 9)
        self.assertEqual(game.player.hp, 10)

    def test_pause_and_victory(self):
        game = self.game
        game.paused = True
        game.update(4, (0, 0), True)
        self.assertEqual(game.wave, 0)
        self.assertFalse(game.bullets)
        game.paused = False
        game.update(3, (0, 0), False)
        self.assertEqual(game.wave, 1)
        self.assertTrue(game.enemies)
        game.enemies.clear()
        game.remaining = 0
        game.wave = 8
        game.update(4, (0, 0), False)
        self.assertTrue(game.victory)


if __name__ == "__main__":
    unittest.main()
