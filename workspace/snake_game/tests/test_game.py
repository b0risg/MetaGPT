## game.py

import pygame
import random
from typing import List, Tuple

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen_width: int = 600
        self.screen_height: int = 400
        self.cell_size: int = 20
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Snake Game')
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.SysFont('Arial', 25)
        self.reset()

    def reset(self) -> None:
        self.score: int = 0
        self.speed: int = 10
        self.snake: List[Tuple[int, int]] = [(100, 100), (80, 100), (60, 100)]
        self.direction: Tuple[int, int] = (20, 0)
        self.food: Tuple[int, int] = self._place_food()
        self.game_over: bool = False

    def _place_food(self) -> Tuple[int, int]:
        return (random.randint(0, (self.screen_width // self.cell_size) - 1) * self.cell_size,
                random.randint(0, (self.screen_height // self.cell_size) - 1) * self.cell_size)

    def run(self) -> None:
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw(self.screen)
            self.clock.tick(self.speed)
        self._show_game_over()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, 20):
                    self.direction = (0, -20)
                elif event.key == pygame.K_DOWN and self.direction != (0, -20):
                    self.direction = (0, 20)
                elif event.key == pygame.K_LEFT and self.direction != (20, 0):
                    self.direction = (-20, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-20, 0):
                    self.direction = (20, 0)

    def update(self) -> None:
        if self.game_over:
            return

        new_head: Tuple[int, int] = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        if (new_head[0] < 0 or new_head[0] >= self.screen_width or
                new_head[1] < 0 or new_head[1] >= self.screen_height or
                new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self._place_food()
            self.speed += 1
        else:
            self.snake.pop()

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        for segment in self.snake:
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(segment[0], segment[1], self.cell_size, self.cell_size))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.food[0], self.food[1], self.cell_size, self.cell_size))
        score_text: pygame.Surface = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    def _show_game_over(self) -> None:
        game_over_text: pygame.Surface = self.font.render('Game Over! Press R to Restart', True, (255, 255, 255))
        self.screen.blit(game_over_text, (self.screen_width // 4, self.screen_height // 2))
        pygame.display.flip()
        self._wait_for_restart()

    def _wait_for_restart(self) -> None:
        waiting: bool = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.game_over = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset()
                    self.run()
                    waiting = False

## test_game.py

import unittest
from unittest.mock import patch, MagicMock
import pygame
import random
from game import Game

## TestGameInitialization
class TestGameInitialization(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_initial_screen_dimensions(self) -> None:
        self.assertEqual(self.game.screen_width, 600)
        self.assertEqual(self.game.screen_height, 400)

    def test_initial_cell_size(self) -> None:
        self.assertEqual(self.game.cell_size, 20)

    def test_initial_snake_position(self) -> None:
        self.assertEqual(self.game.snake, [(100, 100), (80, 100), (60, 100)])

    def test_initial_direction(self) -> None:
        self.assertEqual(self.game.direction, (20, 0))

    def test_initial_score(self) -> None:
        self.assertEqual(self.game.score, 0)

    def test_initial_speed(self) -> None:
        self.assertEqual(self.game.speed, 10)

    def test_initial_game_over(self) -> None:
        self.assertFalse(self.game.game_over)

## TestGameReset
class TestGameReset(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_reset(self) -> None:
        self.game.score = 5
        self.game.speed = 15
        self.game.snake = [(200, 200)]
        self.game.direction = (0, 20)
        self.game.food = (300, 300)
        self.game.game_over = True

        self.game.reset()

        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.speed, 10)
        self.assertEqual(self.game.snake, [(100, 100), (80, 100), (60, 100)])
        self.assertEqual(self.game.direction, (20, 0))
        self.assertFalse(self.game.game_over)

## TestGamePlaceFood
class TestGamePlaceFood(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    @patch('random.randint')
    def test_place_food(self, mock_randint: MagicMock) -> None:
        mock_randint.side_effect = [5, 10]
        food_position = self.game._place_food()
        self.assertEqual(food_position, (100, 200))

## TestGameHandleEvents
class TestGameHandleEvents(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_handle_quit_event(self) -> None:
        event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event)
        self.game.handle_events()
        self.assertTrue(self.game.game_over)

    def test_handle_keydown_up(self) -> None:
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        pygame.event.post(event)
        self.game.handle_events()
        self.assertEqual(self.game.direction, (0, -20))

    def test_handle_keydown_down(self) -> None:
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        pygame.event.post(event)
        self.game.handle_events()
        self.assertEqual(self.game.direction, (0, 20))

    def test_handle_keydown_left(self) -> None:
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        pygame.event.post(event)
        self.game.handle_events()
        self.assertEqual(self.game.direction, (-20, 0))

    def test_handle_keydown_right(self) -> None:
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        self.game.handle_events()
        self.assertEqual(self.game.direction, (20, 0))

## TestGameUpdate
class TestGameUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    def test_update_snake_movement(self) -> None:
        self.game.update()
        self.assertEqual(self.game.snake[0], (120, 100))

    def test_update_food_eaten(self) -> None:
        self.game.food = (120, 100)
        self.game.update()
        self.assertEqual(self.game.score, 1)
        self.assertEqual(len(self.game.snake), 4)

    def test_update_collision_with_wall(self) -> None:
        self.game.snake[0] = (580, 100)
        self.game.direction = (20, 0)
        self.game.update()
        self.assertTrue(self.game.game_over)

    def test_update_collision_with_self(self) -> None:
        self.game.snake = [(100, 100), (80, 100), (60, 100), (60, 120), (80, 120), (100, 120)]
        self.game.direction = (0, 20)
        self.game.update()
        self.assertTrue(self.game.game_over)

## TestGameDraw
class TestGameDraw(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    @patch('pygame.display.flip')
    @patch('pygame.draw.rect')
    @patch('pygame.Surface.fill')
    def test_draw(self, mock_fill: MagicMock, mock_rect: MagicMock, mock_flip: MagicMock) -> None:
        self.game.draw(self.game.screen)
        self.assertTrue(mock_fill.called)
        self.assertTrue(mock_rect.called)
        self.assertTrue(mock_flip.called)

## TestGameShowGameOver
class TestGameShowGameOver(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    @patch('pygame.display.flip')
    @patch('pygame.font.Font.render')
    def test_show_game_over(self, mock_render: MagicMock, mock_flip: MagicMock) -> None:
        self.game._show_game_over()
        self.assertTrue(mock_render.called)
        self.assertTrue(mock_flip.called)

## TestGameWaitForRestart
class TestGameWaitForRestart(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game()

    @patch('pygame.event.get')
    def test_wait_for_restart_quit(self, mock_event_get: MagicMock) -> None:
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]
        self.game._wait_for_restart()
        self.assertTrue(self.game.game_over)

    @patch('pygame.event.get')
    def test_wait_for_restart_keydown_r(self, mock_event_get: MagicMock) -> None:
        mock_event_get.return_value = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)]
        with patch.object(self.game, 'run') as mock_run:
            self.game._wait_for_restart()
            self.assertTrue(mock_run.called)

if __name__ == '__main__':
    unittest.main()
