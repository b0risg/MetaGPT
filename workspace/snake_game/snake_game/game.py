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
