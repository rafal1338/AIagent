import pygame
import sys
import random
from pygame.locals import *

# Inicjalizacja Pygame
pygame.init()

# Stałe
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Kolory
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Klasa Snake
class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = head
        if self.direction == UP:
            y = (y - 1) % GRID_HEIGHT
        elif self.direction == DOWN:
            y = (y + 1) % GRID_HEIGHT
        elif self.direction == LEFT:
            x = (x - 1) % GRID_WIDTH
        elif self.direction == RIGHT:
            x = (x + 1) % GRID_WIDTH

        new_position = (x, y)
        if new_position in self.positions[1:]:
            return False  # Game over
        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True  # Game continues

    def render(self, surface):
        for p in self.positions:
            rect = pygame.Rect(p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GREEN, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

# Klasa Food
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def render(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)

# Kierunki
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Funkcja główna
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()

    font = pygame.font.SysFont(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT

        # Aktualizacja stanu gry
        if not snake.update():
            # Game over
            screen.fill(BLACK)
            text = font.render("Game Over! Press R to restart or Q to quit", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_r:
                            main()  # Restart game
                        elif event.key == K_q:
                            pygame.quit()
                            sys.exit()
        else:
            # Sprawdzenie czy snake zjadł jedzenie
            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 10
                food.randomize_position()
                # Upewnij się, że jedzenie nie pojawia się na snake
                while food.position in snake.positions:
                    food.randomize_position()

        # Rysowanie
        screen.fill(BLACK)
        snake.render(screen)
        food.render(screen)
        score_text = font.render(f"Score: {snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.update()
        clock.tick(10)  # 10 klatek na sekundę

if __name__ == "__main__":
    main()