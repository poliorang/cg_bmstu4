from math import sqrt, pi, cos, sin
from draw import draw_dots_circle, draw_dots_ellipse


def parametric_circle(canvas_win, dot_c, radius, color, history, draw):
    step = 1 / radius
    alpha = 0

    step_history = []
    step_history.clear()
    while alpha < pi / 4 + step:
        x = round(radius * cos(alpha))
        y = round(radius * sin(alpha))

        if draw:
            draw_dots_circle(canvas_win, dot_c, [x, y], color, step_history)

        alpha += step
    history.append(step_history)


def parametric_ellipse(canvas_win, dot_c, rad, color, history, draw):
    if rad[0] > rad[1]:
        step = 1 / rad[0]
    else:
        step = 1 / rad[1]

    alpha = 0

    step_history = []
    step_history.clear()
    while alpha < pi / 2 + step:
        x = round(rad[0] * cos(alpha))
        y = round(rad[1] * sin(alpha))

        if draw:
            draw_dots_ellipse(canvas_win, dot_c, [x, y], color, step_history)

        alpha += step

    history.append(step_history)