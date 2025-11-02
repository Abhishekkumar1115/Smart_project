import sys
import random
import pygame

# --- Config ---
CELL_SIZE = 24
GRID_WIDTH = 24
GRID_HEIGHT = 24
MARGIN = 16  # top margin for HUD

WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = MARGIN + CELL_SIZE * GRID_HEIGHT

BG_COLOR = (18, 18, 18)
GRID_COLOR = (30, 30, 30)
SNAKE_HEAD_COLOR = (0, 200, 120)
SNAKE_BODY_COLOR = (0, 150, 90)
FOOD_COLOR = (220, 50, 50)
TEXT_COLOR = (230, 230, 230)
GAME_OVER_COLOR = (250, 80, 80)

# Movement timing (milliseconds per step) — decreases as score grows
MOVE_DELAY_START = 140
MOVE_DELAY_MIN = 70
SPEEDUP_EVERY = 4  # apples per speedup step
SPEEDUP_DELTA = 8  # reduce delay by this many ms each step

# Controls mapping
KEY_TO_DIR = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}

MOVE_EVENT = pygame.USEREVENT + 1


def clamp_move_delay(score: int) -> int:
    steps = max(0, score // SPEEDUP_EVERY)
    delay = MOVE_DELAY_START - steps * SPEEDUP_DELTA
    return max(MOVE_DELAY_MIN, delay)


def new_food(snake):
    body_set = set(snake)
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in body_set:
            return (x, y)


def draw_grid(surface):
    for x in range(GRID_WIDTH + 1):
        px = x * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (px, MARGIN), (px, MARGIN + GRID_HEIGHT * CELL_SIZE), 1)
    for y in range(GRID_HEIGHT + 1):
        py = MARGIN + y * CELL_SIZE
        pygame.draw.line(surface, GRID_COLOR, (0, py), (GRID_WIDTH * CELL_SIZE, py), 1)


def draw_cell(surface, pos, color):
    x, y = pos
    rect = pygame.Rect(x * CELL_SIZE + 1, MARGIN + y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
    pygame.draw.rect(surface, color, rect, border_radius=4)


def render_text(surface, font, text, color, pos, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(img, rect)


def main():
    pygame.init()
    pygame.display.set_caption("Snake — Pygame")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 26)
    big_font = pygame.font.SysFont(None, 48)

    def reset_game():
        mid = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        snake = [mid, (mid[0] - 1, mid[1]), (mid[0] - 2, mid[1])]
        direction = (1, 0)
        pending_dir = direction
        food = new_food(snake)
        score = 0
        move_delay = clamp_move_delay(score)
        pygame.time.set_timer(MOVE_EVENT, move_delay)
        return snake, direction, pending_dir, food, score

    snake, direction, pending_dir, food, score = reset_game()
    paused = False
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key in KEY_TO_DIR and not game_over:
                    ndx, ndy = KEY_TO_DIR[event.key]
                    # prevent reversing directly
                    if (ndx, ndy) != (-direction[0], -direction[1]):
                        pending_dir = (ndx, ndy)
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    snake, direction, pending_dir, food, score = reset_game()
                    paused = False
                    game_over = False
            if event.type == MOVE_EVENT and not paused and not game_over:
                direction = pending_dir
                head_x, head_y = snake[0]
                dx, dy = direction
                nx, ny = head_x + dx, head_y + dy

                # wall collision ends game
                if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT:
                    game_over = True
                else:
                    new_head = (nx, ny)
                    if new_head in snake:
                        game_over = True
                    else:
                        snake.insert(0, new_head)
                        if new_head == food:
                            score += 1
                            food = new_food(snake)
                            # speed up
                            pygame.time.set_timer(MOVE_EVENT, clamp_move_delay(score))
                        else:
                            snake.pop()

        # draw
        screen.fill(BG_COLOR)
        # HUD
        render_text(screen, font, f"Score: {score}", TEXT_COLOR, (8, 8))
        render_text(screen, font, "P: Pause  R: Restart  ESC: Quit", (160, 160, 160), (150, 8))

        # grid and entities
        draw_grid(screen)
        # food
        draw_cell(screen, food, FOOD_COLOR)
        # snake
        if snake:
            draw_cell(screen, snake[0], SNAKE_HEAD_COLOR)
        for seg in snake[1:]:
            draw_cell(screen, seg, SNAKE_BODY_COLOR)

        if paused and not game_over:
            render_text(screen, big_font, "Paused", TEXT_COLOR, (WINDOW_WIDTH // 2, MARGIN + WINDOW_HEIGHT // 2 - MARGIN), center=True)

        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            render_text(screen, big_font, "Game Over", GAME_OVER_COLOR, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 32), center=True)
            render_text(screen, font, f"Final Score: {score}", TEXT_COLOR, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 8), center=True)
            render_text(screen, font, "Press R to restart or ESC to quit", (200, 200, 200), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40), center=True)

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()
