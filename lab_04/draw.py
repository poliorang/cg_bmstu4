from tkinter import *
from tkinter import messagebox

coord_center = [400, 400]
m_board = 1
SIZE = 800
CENTER = [400, 400]


# оси координат и сетка
def draw_axes(canvas_win, xy_current, size):
    canvas_win.create_line(0, size / 2, size - 2, size / 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")
    canvas_win.create_line(size / 2, size, size / 2, 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")

    s = int(size)
    j = 0
    for i in range(0, s, s // 16):
        canvas_win.create_line(i, s / 2 - 5, i, s / 2 + 5, fill='pink', width=2)
        canvas_win.create_line(i, 0, i, s, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(i, s // 2 + 20, text=f'{"%.2f" % xy_current[j]}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

        canvas_win.create_line(s / 2 - 5, i, s / 2 + 5, i, fill='pink', width=2)
        canvas_win.create_line(0, i, s, i, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(s // 2 - 20, i, text=f'{"%.2f" % xy_current[16 - j]}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

        j += 1

    canvas_win.create_text(s - 20, s // 2 + 20, text='X', font="AvantGardeC 14", fill='grey')
    canvas_win.create_text(s // 2 + 20, 20, text='Y', font="AvantGardeC 14", fill='grey')

# из канвасовских координат в фактические
def to_coords(dot):
    x = (dot[0] - coord_center[0]) * m_board
    y = (-dot[1] + coord_center[1]) * m_board

    return [x, y]

# из фактических координат в реальные
def to_canva(dot):
    x = coord_center[0] + dot[0] / m_board
    y = coord_center[1] - dot[1] / m_board

    return [x, y]


def draw_pixel(canvas_win, dot, step_history):
    x, y = dot[0], dot[1]
    canvas_win.create_polygon([x, y], [x, y + 1],
                   [x + 1, y + 1], [x + 1, y],
                   fill=dot[2].hex, tag='pixel')
    step_history.append(dot)


def draw_dots_circle(canvas_win, center, dot_dif, color, step_history):
    x_c, y_c = to_canva([center[0], center[1]])
    x = dot_dif[0]
    y = dot_dif[1]

    draw_pixel(canvas_win, [x_c + x, y_c + y, color], step_history)
    draw_pixel(canvas_win, [x_c - x, y_c + y, color], step_history)
    draw_pixel(canvas_win, [x_c + x, y_c - y, color], step_history)
    draw_pixel(canvas_win, [x_c - x, y_c - y, color], step_history)

    draw_pixel(canvas_win, [x_c + y, y_c + x, color], step_history)
    draw_pixel(canvas_win, [x_c - y, y_c + x, color], step_history)
    draw_pixel(canvas_win, [x_c + y, y_c - x, color], step_history)
    draw_pixel(canvas_win, [x_c - y, y_c - x, color], step_history)


def draw_dots_ellipse(canvas_win, center, dot_dif, color, step_history):
    x_c, y_c = to_canva([center[0], center[1]])

    x = dot_dif[0]
    y = dot_dif[1]

    draw_pixel(canvas_win, [x_c + x, y_c + y, color], step_history)
    draw_pixel(canvas_win, [x_c - x, y_c + y, color], step_history)
    draw_pixel(canvas_win, [x_c + x, y_c - y, color], step_history)
    draw_pixel(canvas_win, [x_c - x, y_c - y, color], step_history)


# отрисовать отрезов без сохранения в историю
def draw_without_history(canvas_win, dots):
    for dot in dots:
        x, y = dot[0:2]
        point = [x, y, dot[2]]
        canvas_win.create_polygon([x, y], [x, y + 1],
                                  [x + 1, y + 1], [x + 1, y],
                                  fill=point[2].hex, tag='pixel')


def draw_all_figures(canvas_win, array_dots):
    for dots in array_dots:
        if isinstance(dots[0][0], float):
            draw_without_history(canvas_win, dots)
        else:
            draw_all_figures(canvas_win, dots)


# откат
def undo(canvas_win, figure_history):
    if len(figure_history) == 0:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    canvas_win.delete('pixel')

    figure_history.pop()
    draw_all_figures(canvas_win, figure_history)
