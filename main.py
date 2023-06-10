import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

FPS = 60

WHITE = (245, 245, 245)
BLACK = (0, 0, 0)
green = (0, 128, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 30, 200
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("times new roman", 50)
WINNING_SCORE = 5

# Sound effects
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
hit_sound = pygame.mixer.Sound("hit.wav")


class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    MAX_VEL = 5
    COLOR = green

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel *= -1


def draw(win, left_paddle, right_paddle, ball, left_score, right_score, game_over):
    win.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
    win.blit(right_score_text, (WIDTH * (3 / 4) - right_score_text.get_width() // 2, 20))

    left_paddle.draw(win)
    right_paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT // 20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH // 2 - 5, i, 2, HEIGHT // 20))

    ball.draw(win)

    if game_over:
        game_over_text = SCORE_FONT.render("Game Over", 1, WHITE)
        play_again_text = SCORE_FONT.render("Play Again", 1, WHITE)
        win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        win.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2 + game_over_text.get_height()))

    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT or ball.y - ball.radius <= 0:
        ball.y_vel *= -1
        pygame.mixer.Sound.play(hit_sound)

    if ball.x_vel < 0:
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_vel *= -1
                pygame.mixer.Sound.play(hit_sound)

                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel

    else:
        if right_paddle.y <= ball.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1
                pygame.mixer.Sound.play(hit_sound)

                middle_y = right_paddle.y + right_paddle.height / 3
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel


def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
        left_paddle.move(up=False)

    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)


def main():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    pygame.mixer.music.play(-1)  # Play background music

    game_over = False

    while run:
        clock.tick(FPS)
        draw(WIN, left_paddle, right_paddle, ball, left_score, right_score, game_over)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    game_over = False
                    left_score = 0
                    right_score = 0
                    ball.reset()

        if game_over:
            continue

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x + ball.radius >= WIDTH:
            left_score += 1
            ball.reset()

        if ball.x - ball.radius <= 0:
            right_score += 1
            ball.reset()

        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            game_over = True

    pygame.quit()


if __name__ == "__main__":
    main()
