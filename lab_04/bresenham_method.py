from math import sqrt
from draw import draw_dots_circle, draw_dots_ellipse

def bresenham_circle(canvas_win, dot_c, radius, color, history, draw):
    x_c = round(dot_c[0])
    y_c = round(dot_c[1])

    x = 0
    y = radius

    delta_i = 2 * (1 - radius)
    eps = 0

    step_history = []
    step_history.clear()
    while x <= y:

        if draw:
            draw_dots_circle(canvas_win, [x_c, y_c], [x, y], color, step_history)

        param = 1
        if delta_i <= 0:
            eps = 2 * delta_i + 2 * y - 1

            if eps < 0:
                param = 1
            else:
                param = 2
        elif delta_i > 0:  # никогдане будет для окружности
            eps = 2 * delta_i - 2 * x - 1

            if eps < 0:
                param = 2
            else:
                param = 3

        if param == 1:
            x = x + 1
            delta_i = delta_i + 2 * x + 1
        elif param == 2:
            x = x + 1
            y = y - 1
            delta_i = delta_i + 2 * x - 2 * y + 2
        else: # сюда тоже не попадем для окр
            y = y - 1
            delta_i = delta_i - 2 * y + 1

    history.append(step_history)


def bresenham_ellipse(canvas_win, dot_c, rad, color, history, draw):
    x_c = round(dot_c[0])
    y_c = round(dot_c[1])

    x = 0
    y = rad[1]

    r_a_2 = rad[0] * rad[0]
    r_b_2 = rad[1] * rad[1]

    delta_i = r_b_2 - r_a_2 * (2 * y + 1)

    eps = 0

    step_history = []
    step_history.clear()
    while y >= 0:
        if draw:
            draw_dots_ellipse(canvas_win, [x_c, y_c], [x, y], color, step_history)

        param = 1
        if delta_i <= 0:
            eps = 2 * delta_i + (2 * y + 2) * r_a_2

            if eps < 0:
                param = 1
            else:
                param = 2
        elif delta_i > 0:
            eps = 2 * delta_i + (- 2 * x + 2) * r_b_2

            if eps < 0:
                param = 2
            else:
                param = 3
        
        if param == 1:
            x = x + 1
            delta_i = delta_i + (2 * x) * r_b_2 + r_b_2
        elif param == 2:
            x = x + 1
            y = y - 1
            delta_i = delta_i + (2 * x) * r_b_2 - (2 * y) * r_a_2 + (r_a_2 + r_b_2)
        else:
            y = y - 1
            delta_i = delta_i - (2 * y) * r_a_2 + r_a_2

    history.append(step_history)
