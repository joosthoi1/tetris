import pygame

from .grid import TetrisGrid, GriddedShape, Point
from .shape import Shape
from .helpers import get_font

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


def valid_space(shape, grid):
    for point in shape.positions:
        if point not in grid.available_points:
            if point.y > -1:
                return False
    return True


def get_shape(grid_width):
    return GriddedShape(Point(grid_width // 2, 0), Shape.new_shape())


def draw_text_middle(surface, text, size, color):
    font = get_font("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2),
            top_left_y + play_height / 2 - label.get_height() / 2,
        ),
    )


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(grid.height):
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (sx, sy + i * block_size),
            (sx + play_width, sy + i * block_size),
        )
        for j in range(grid.width):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (sx + j * block_size, sy),
                (sx + j * block_size, sy + play_height),
            )


def clear_rows(grid, locked):
    inc = 0
    for y in range(grid.height - 1, -1, -1):
        row = grid[y]
        if (0, 0, 0) not in row:
            inc += 1
            ind = y
            for x in range(grid.width):
                try:
                    del locked[Point(x, y)]
                except KeyError:
                    continue

    if inc > 0:
        for point in sorted(list(locked), key=lambda point: point.y)[::-1]:
            if point.y < ind:
                newpoint = Point(point.x, point.y + inc)
                locked[newpoint] = locked.pop(point)

    return inc


def draw_next_shape(shape, surface):
    font = get_font("comicsans", 30)
    label = font.render("Next Shape", 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    # format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(shape.shape.shape):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                pygame.draw.rect(
                    surface,
                    shape.color,
                    (
                        sx + j * block_size,
                        sy + i * block_size,
                        block_size,
                        block_size
                    ),
                    0,
                )

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open("scores.txt", "w") as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open("scores.txt", "r") as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))

    font = get_font("comicsans", 60)
    label = font.render("Tetris", 1, (255, 255, 255))

    surface.blit(
        label,
        (top_left_x + play_width / 2 - (label.get_width() / 2), 30)
    )

    # current score
    font = get_font("comicsans", 30)
    label = font.render("Score: " + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render("High Score: " + last_score, 1, (255, 255, 255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(grid.height):
        for j in range(grid.width):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (
                    top_left_x + j * block_size,
                    top_left_y + i * block_size,
                    block_size,
                    block_size,
                ),
                0,
            )

    pygame.draw.rect(
        surface,
        (255, 0, 0),
        (top_left_x, top_left_y, play_width, play_height),
        5
    )

    draw_grid(surface, grid)


def run(win):  # *
    last_score = max_score()
    locked_points = {}
    GRID_WIDTH = 10
    GRID_HEIGHT = 20

    change_piece = False
    locked_points_set = False
    running = True
    current_piece = get_shape(GRID_WIDTH)
    next_piece = get_shape(GRID_WIDTH)
    clock = pygame.time.Clock()
    fall_time1 = 0
    one_point_fall_time = 0.27
    # level_time = 0
    score = 0

    grid = TetrisGrid(GRID_WIDTH, GRID_HEIGHT, locked_points)
    while running:
        fall_time1 += clock.get_rawtime()
        # level_time += clock.get_rawtime()
        clock.tick()

        # if level_time / 1000 > 5:
        #     level_time = 0
        #     if level_time > 0.12:
        #         level_time -= 0.005

        # 30 pixels per 0.27 secs
        if fall_time1 / 1000 > one_point_fall_time:
            fall_time1 = 0
            current_piece.go_down(1)
            if not (valid_space(current_piece, grid)) \
                    and current_piece.point.y > 0:
                current_piece.go_up(1)
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.go_left(1)
                    if not (valid_space(current_piece, grid)):
                        current_piece.go_right(1)
                if event.key == pygame.K_RIGHT:
                    current_piece.go_right(1)
                    if not (valid_space(current_piece, grid)):
                        current_piece.go_left(1)
                if event.key == pygame.K_DOWN:
                    current_piece.go_down(1)
                    if not (valid_space(current_piece, grid)):
                        current_piece.go_up(1)
                if event.key == pygame.K_UP:
                    current_piece.shape.rotate_right()
                    if not (valid_space(current_piece, grid)):
                        current_piece.shape.rotate_left()

        tmp_points = dict(locked_points)
        for point in current_piece.positions:
            if point.y > -1:
                tmp_points[point] = current_piece.color
        grid.update(tmp_points)

        if change_piece:
            for point in current_piece.positions:
                locked_points[point] = current_piece.color
            locked_points_set = True
            current_piece = next_piece
            next_piece = get_shape(grid.width)
            change_piece = False
            score += clear_rows(grid, locked_points) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        grid.update(locked_points, locked_points_set)
        locked_points_set = False

        if grid.check_lost():
            draw_text_middle(win, "YOU LOST!", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            running = False
            update_score(score)
            pygame.event.clear()


def draw_main_menu(win):
    win.fill((0, 0, 0))
    draw_text_middle(win, "Press Any Key To Play", 60, (255, 255, 255))
    pygame.display.update()


def main_menu(win):
    while True:
        draw_main_menu(win)
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN and event.mod == pygame.KMOD_NONE:
            run(win)

    pygame.display.quit()


def main():
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption("Tetris")
    pygame.font.init()
    main_menu(win)


if __name__ == '__main__':
    main()
