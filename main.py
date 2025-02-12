import pygame
import pymunk
import pymunk.pygame_util
import math
import random
import sys

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM_PANEL = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pool")

space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)

clock = pygame.time.Clock()
FPS = 120

current_level = 1
lives = 3
dia = 36
pocket_dia = 66
force = 0
max_force = 10000
force_direction = 1
game_running = True
cue_ball_potted = False
taking_shot = True
powering_up = False
potted_balls = []
available_balls = []

BG = (50, 50, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

cue_image = pygame.image.load("assets/images/cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table.png").convert_alpha()
ball_images = []
for i in range(1, 17):
    ball_image = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def create_ball(radius, pos, ball_number):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8
    shape.ball_number = ball_number  # Assign a number to the ball
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000
    space.add(body, shape, pivot)
    return shape


def setup_level(level):
    global balls, available_balls, lives, potted_balls

    if 'balls' in globals():
        for ball in balls[:-1]:
            for constraint in ball.body.constraints:
                space.remove(constraint)
            space.remove(ball.body, ball)
        balls = [balls[-1]]
    else:
        balls = []
        pos = (888, SCREEN_HEIGHT / 2)
        cue_ball = create_ball(dia / 2, pos, -1)
        balls.append(cue_ball)

    balls[-1].body.position = (888, SCREEN_HEIGHT / 2)
    balls[-1].body.velocity = (0.0, 0.0)

    potted_balls.clear()

    num_available = 6 - level
    all_ball_numbers = list(range(15))
    random.shuffle(all_ball_numbers)
    available_balls = all_ball_numbers[:num_available]

    rows = 5
    ball_count = 0
    for col in range(5):
        for row in range(rows):
            if ball_count < 16:
                pos = (250 + (col * (dia + 1)), 267 + (row * (dia + 1)) + (col * dia / 2))
                new_ball = create_ball(dia / 2, pos, ball_count)
                balls.insert(-1, new_ball)
                ball_count += 1
        rows -= 1

    lives = 3

pockets = [
    (55, 63),
    (592, 48),
    (1134, 64),
    (55, 616),
    (592, 629),
    (1134, 616)
]

cushions = [
    [(88, 56), (109, 77), (555, 77), (564, 56)],
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],
    [(89, 621), (110, 600), (556, 600), (564, 621)],
    [(622, 621), (630, 600), (1081, 600), (1102, 621)],
    [(56, 96), (77, 117), (77, 560), (56, 581)],
    [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]


def create_cushion(poly_dims):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = ((0, 0))
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = 0.8
    space.add(body, shape)


for c in cushions:
    create_cushion(c)


class Cue():
    def __init__(self, pos):
        self.original_image = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image,
                     (self.rect.centerx - self.image.get_width() / 2,
                      self.rect.centery - self.image.get_height() / 2)
                     )


setup_level(current_level)
cue = Cue(balls[-1].body.position)

power_bar = pygame.Surface((10, 20))
power_bar.fill(RED)

run = True
while run:
    clock.tick(FPS)
    space.step(1 / FPS)

    screen.fill(BG)
    screen.blit(table_image, (0, 0))

    for ball in balls[:-1]:
        for pocket in pockets:
            ball_x_dist = abs(ball.body.position[0] - pocket[0])
            ball_y_dist = abs(ball.body.position[1] - pocket[1])
            ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
            if ball_dist <= pocket_dia / 2:
                ball_number = ball.ball_number
                if ball_number in available_balls:
                    available_balls.remove(ball_number)
                    potted_balls.append(ball_number)
                else:
                    lives -= 1
                space.remove(ball.body)
                balls.remove(ball)
                break

    for pocket in pockets:
        ball_x_dist = abs(balls[-1].body.position[0] - pocket[0])
        ball_y_dist = abs(balls[-1].body.position[1] - pocket[1])
        ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
        if ball_dist <= pocket_dia / 2:
            lives -= 1
            cue_ball_potted = True
            balls[-1].body.position = (-100, -100)
            balls[-1].body.velocity = (0.0, 0.0)

    for ball in balls[:-1]:
        ball_number = ball.ball_number
        screen.blit(ball_images[ball_number], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))
    screen.blit(ball_images[-1],
                (balls[-1].body.position[0] - balls[-1].radius, balls[-1].body.position[1] - balls[-1].radius))

    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    if taking_shot and game_running:
        if cue_ball_potted:
            balls[-1].body.position = (888, SCREEN_HEIGHT / 2)
            cue_ball_potted = False
        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1])
        cue_angle = math.degrees(math.atan2(y_dist, x_dist))
        cue.update(cue_angle)
        cue.draw(screen)

    if powering_up and game_running:
        force += 100 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1
        for b in range(math.ceil(force / 2000)):
            screen.blit(power_bar,
                        (balls[-1].body.position[0] - 30 + (b * 15),
                         balls[-1].body.position[1] + 30))
    elif not powering_up and taking_shot:
        x_impulse = math.cos(math.radians(cue_angle))
        y_impulse = math.sin(math.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((force * -x_impulse, force * y_impulse), (0, 0))
        force = 0
        force_direction = 1

    pygame.draw.rect(screen, BG, (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))
    draw_text(f"LEVEL: {current_level}", font, WHITE, 10, SCREEN_HEIGHT + 10)
    draw_text("LIVES: " + str(lives), font, WHITE, SCREEN_WIDTH - 200, SCREEN_HEIGHT + 10)

    draw_text("Available Balls:", font, WHITE, 200, SCREEN_HEIGHT + 10)
    for i, ball_num in enumerate(available_balls):
        screen.blit(ball_images[ball_num], (400 + (i * 40), SCREEN_HEIGHT + 10))

    if lives <= 0:
        draw_text("GAME OVER", large_font, WHITE, SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 2 - 100)
        game_running = False

        play_again_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        exit_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 70, 200, 50)
        pygame.draw.rect(screen, GREEN, play_again_button)
        pygame.draw.rect(screen, RED, exit_button)
        draw_text("Play Again", font, WHITE, play_again_button.x + 50, play_again_button.y + 15)
        draw_text("Exit", font, WHITE, exit_button.x + 80, exit_button.y + 15)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if mouse_click[0]:
            if play_again_button.collidepoint(mouse_pos):
                current_level = 1
                lives = 3
                potted_balls.clear()
                available_balls.clear()
                setup_level(current_level)
                game_running = True
            elif exit_button.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

    if len(available_balls) == 0:
        if current_level < 5:
            current_level += 1
            setup_level(current_level)
        else:
            draw_text("YOU WIN!", large_font, WHITE, SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 2 - 100)
            game_running = False

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot:
            powering_up = True
        if event.type == pygame.MOUSEBUTTONUP and taking_shot:
            powering_up = False
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()