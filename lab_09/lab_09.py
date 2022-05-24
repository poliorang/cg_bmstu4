from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
import colorutils as cu
import copy
from itertools import combinations

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

CLIPPER = 1
FIGURE = 0

X_MIN = 0
X_MAX = 1
Y_MIN = 2
Y_MAX = 3

X_DOT = 0
Y_DOT = 1

TASK = "Реализация (и исследование) " \
       "отсечения многоугольника нерегулярным отсекателем " \
       "методом Сазерленда-Ходжмена"

AUTHOR = "\n\nЕгорова Полина ИУ7-44Б"


# координаты точки из канвасовских в фактические
def to_coords(dot):
    x = (dot[0] - coord_center[0]) * m_board
    y = (-dot[1] + coord_center[1]) * m_board

    return [x, y]


# координаты точки из фактических в канвасовские
def to_canva(dot):
    x = coord_center[0] + dot[0] / m_board
    y = coord_center[1] - dot[1] / m_board

    return [x, y]


# добаление точки по координатам (не через канвас)
def add_dot():
    try:
        x = int(x_entry.get())
        y = int(y_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    draw_point(x, y, 0)


# рисовать отсекатель
def draw_line_clipper(new_dot):
    global clipper_coords
    color = cu.Color(clipper_color[1])

    if len(clipper_coords) > 0:
        previous_dot = clipper_coords[-1]
        canvas_win.create_line(previous_dot, new_dot, fill=color, tag='clipper')
        canvas_win.delete('clipper_dot')

    clipper_coords.append(new_dot)
    cur = copy.deepcopy(clipper_coords)
    history.append([cur, 'rectangle'])


def draw_line_rectangle(new_dot):
    global figure_coords
    color = cu.Color(rectangle_color[1])

    if len(figure_coords[-1]) > 0:
        previous_dot = figure_coords[-1][-1]
        canvas_win.create_line(previous_dot, new_dot, fill=color, tag='figure')

    figure_coords[-1].append(new_dot)
    cur = copy.deepcopy(figure_coords)
    history.append([cur, 'figure'])


# замкнуть фигуру
def make_figure():
    global is_close_clipper, is_close_figure, option_line, click_clipper, start_clipper

    if option_line.get() == FIGURE:
        if len(figure_coords[-1]) < 3:
            messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
            return

        is_close_figure = 1
        draw_point(figure_coords[-1][0][0], figure_coords[-1][0][1], 1)

    elif option_line.get() == CLIPPER:
        if len(clipper_coords) < 3:
            messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
            return

        draw_point(clipper_coords[0][0], clipper_coords[0][1], 1)
        is_close_clipper = 1
        if click_clipper == 0:
            click_clipper = 1
        start_clipper = []


# отрисовка и вставка в листбокс добавленной точки
def draw_point(ev_x, ev_y, click_):
    global option_line, figure_coords, clipper_coords, start_clipper, \
        is_close_clipper, is_close_figure, \
        start_rectangle,\
        click_rectangle, click_clipper

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canva([ev_x, ev_y])

    x_y = to_coords([x, y])

    if option_line.get() == 0:
        if click_rectangle == 0:
            click_rectangle = 1
        start_rectangle = [x, y]
        dot_str = "  (%-d; %-d)" % (x_y[0], x_y[1])
        figures_block.insert(END, dot_str)
        draw_line_rectangle([x, y])
        canvas_win.delete('figure_dot', 'lineHelper')
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='pink', fill='pink', activeoutline='lightgreen', width=2, tag='figure_dot')
        if is_close_figure:
            click_rectangle = 0
            start_rectangle = []
            figures_block.insert(END, 50*'-')
            figure_coords.append([])
            is_close_figure = 0

    elif option_line.get() == 1:
        start_clipper = [x, y]
        print(start_clipper)
        if is_close_clipper:
            for _ in range(len(clipper_coords)):
                clipper_block.delete(END)
            click_clipper = 0
            clipper_coords = []
            is_close_clipper = 0
            canvas_win.delete('clipper_dot', 'clipper')

        dot_str = "  (%-d; %-d)" % (x_y[0], x_y[1])
        clipper_block.insert(END, dot_str)
        canvas_win.delete('lineHelper')
        draw_line_clipper([x, y])

        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='pink', fill='pink', activeoutline='lightgreen', width=2, tag='clipper_dot')


def get_vector(dot1, dot2):
    return [dot2[X_DOT] - dot1[X_DOT], dot2[Y_DOT] - dot1[Y_DOT]]


def vector_mul(vec1, vec2):
    return (vec1[0] * vec2[1] - vec1[1] * vec2[0])


def scalar_mul(vec1, vec2):
    return (vec1[0] * vec2[0] + vec1[1] * vec2[1])


def line_koefs(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1 * y2 - x2 * y1

    return a, b, c


def solve_lines_intersection(a1, b1, c1, a2, b2, c2):
    opr = a1 * b2 - a2 * b1
    opr1 = (-c1) * b2 - b1 * (-c2)
    opr2 = a1 * (-c2) - (-c1) * a2

    if (opr == 0):
        return -5, -5  # прямые параллельны

    x = opr1 / opr
    y = opr2 / opr

    return x, y


def is_coord_between(left_coord, right_coord, dot_coord):
    return (min(left_coord, right_coord) <= dot_coord) \
           and (max(left_coord, right_coord) >= dot_coord)


def is_dot_between(dot_left, dot_right, dot_intersec):
    return is_coord_between(dot_left[X_DOT], dot_right[X_DOT], dot_intersec[X_DOT]) \
           and is_coord_between(dot_left[Y_DOT], dot_right[Y_DOT], dot_intersec[Y_DOT])


def are_connected_sides(line1, line2):
    if ((line1[0][X_DOT] == line2[0][X_DOT]) and (line1[0][Y_DOT] == line2[0][Y_DOT])) \
            or ((line1[1][X_DOT] == line2[1][X_DOT]) and (line1[1][Y_DOT] == line2[1][Y_DOT])) \
            or ((line1[0][X_DOT] == line2[1][X_DOT]) and (line1[0][Y_DOT] == line2[1][Y_DOT])) \
            or ((line1[1][X_DOT] == line2[0][X_DOT]) and (line1[1][Y_DOT] == line2[0][Y_DOT])):
        return True

    return False


def extra_check(object):  # чтобы не было пересечений

    lines = []

    for i in range(len(object) - 1):
        lines.append([object[i], object[i + 1]])  # разбиваю многоугольник на линии

    combs_lines = list(combinations(lines, 2))  # все возможные комбинации сторон

    for i in range(len(combs_lines)):
        line1 = combs_lines[i][0]
        line2 = combs_lines[i][1]

        if are_connected_sides(line1, line2):
            continue

        a1, b1, c1 = line_koefs(line1[0][X_DOT], line1[0][Y_DOT], line1[1][X_DOT], line1[1][Y_DOT])
        a2, b2, c2 = line_koefs(line2[0][X_DOT], line2[0][Y_DOT], line2[1][X_DOT], line2[1][Y_DOT])

        dot_intersec = solve_lines_intersection(a1, b1, c1, a2, b2, c2)

        if (is_dot_between(line1[0], line1[1], dot_intersec)) \
                and (is_dot_between(line2[0], line2[1], dot_intersec)):
            return True

    return False


def check_polygon():  # через проход по всем точкам, поворот которых должен быть все время в одну сторону
    if len(clipper_coords) < 3:
        return False

    sign = 0

    if vector_mul(get_vector(clipper_coords[1], clipper_coords[2]),
                  get_vector(clipper_coords[0], clipper_coords[1])) > 0:
        sign = 1
    else:
        sign = -1

    for i in range(3, len(clipper_coords)):
        if sign * vector_mul(get_vector(clipper_coords[i - 1], clipper_coords[i]),
                             get_vector(clipper_coords[i - 2], clipper_coords[i - 1])) < 0:
            return False

    check = extra_check(clipper_coords)

    if check:
        return False

    if sign < 0:
        clipper_coords.reverse()

    return True


def get_normal(dot1, dot2, pos):
    f_vect = get_vector(dot1, dot2)
    pos_vect = get_vector(dot2, pos)

    if f_vect[1]:
        normal = [1, -f_vect[0] / f_vect[1]]
    else:
        normal = [0, 1]

    if scalar_mul(pos_vect, normal) < 0:
        normal[0] = -normal[0]
        normal[1] = -normal[1]

    return normal


def is_visible(dot, f_dot, s_dot):
    vec1 = get_vector(f_dot, s_dot)
    vec2 = get_vector(f_dot, dot)

    if vector_mul(vec1, vec2) <= 0:
        return True
    else:
        return False


def get_lines_parametric_intersec(line1, line2, normal):
    d = get_vector(line1[0], line1[1])
    w = get_vector(line2[0], line1[0])

    d_scalar = scalar_mul(d, normal)
    w_scalar = scalar_mul(w, normal)

    t = -w_scalar / d_scalar

    dot_intersec = [line1[0][X_DOT] + d[0] * t, line1[0][Y_DOT] + d[1] * t]

    return dot_intersec


def sutherland_hodgman_algorythm(cutter_line, position, prev_result):
    cur_result = []

    dot1 = cutter_line[0]
    dot2 = cutter_line[1]

    normal = get_normal(dot1, dot2, position)

    prev_vision = is_visible(prev_result[-2], dot1, dot2)

    for cur_dot_index in range(-1, len(prev_result)):
        cur_vision = is_visible(prev_result[cur_dot_index], dot1, dot2)

        if prev_vision:
            if cur_vision:
                cur_result.append(prev_result[cur_dot_index])
            else:
                figure_line = [prev_result[cur_dot_index - 1], prev_result[cur_dot_index]]

                cur_result.append(get_lines_parametric_intersec(figure_line, cutter_line, normal))
        else:
            if cur_vision:
                figure_line = [prev_result[cur_dot_index - 1], prev_result[cur_dot_index]]

                cur_result.append(get_lines_parametric_intersec(figure_line, cutter_line, normal))

                cur_result.append(prev_result[cur_dot_index])

        prev_vision = cur_vision

    return cur_result


def cut_area():

    if not is_close_clipper:
        messagebox.showinfo("Ошибка", "Отсекатель не замкнут")
        return

    if is_close_figure:
        messagebox.showinfo("Ошибка", "Отекаемый многоугольник не замкнут")
        return


    if len(clipper_coords) < 3:
        messagebox.showinfo("Ошибка", "Не задан отсекатель")
        return

    if not check_polygon():
        messagebox.showinfo("Ошибка", "Отсекатель должен быть выпуклым многоугольником")
        return

    canvas_win.delete('result')
    for figure in figure_coords:

        if len(figure) == 0:
            continue

        if extra_check(figure):
            messagebox.showinfo("Ошибка", "Неверно задан отсекаемый многоугольник")
            return

        result = copy.deepcopy(figure)

        for cur_dot_ind in range(-1, len(clipper_coords) - 1):
            line = [clipper_coords[cur_dot_ind], clipper_coords[cur_dot_ind + 1]]

            position_dot = clipper_coords[cur_dot_ind + 1]

            result = sutherland_hodgman_algorythm(line, position_dot, result)

            if len(result) <= 2:
                return

        draw_result_figure(result)


def make_unique(sides):

    for side in sides:
        side.sort()

    return list(filter(lambda x: (sides.count(x) % 2) == 1, sides))


def is_dot_in_side(dot, side):
    if abs(vector_mul(get_vector(dot, side[0]), get_vector(side[1], side[0]))) <= 1e-6:
        if side[0] < dot < side[1] or side[1] < dot < side[0]:
            return True
    return False


def get_sides(side, rest_dots):
    dots_list = [side[0], side[1]]

    for dot in rest_dots:
        if is_dot_in_side(dot, side):
            dots_list.append(dot)

    dots_list.sort()

    sections_list = list()

    for i in range(len(dots_list) - 1):
        sections_list.append([dots_list[i], dots_list[i + 1]])

    return sections_list


def remove_odd_sides(figure_dots):
    all_sides = list()
    rest_dots = figure_dots[2:]

    for i in range(len(figure_dots)):
        cur_side = [figure_dots[i], figure_dots[(i + 1) % len(figure_dots)]]

        all_sides.extend(get_sides(cur_side, rest_dots))

        rest_dots.pop(0)
        rest_dots.append(figure_dots[i])

    return make_unique(all_sides)


def draw_result_figure(figure_dots):
    global history
    fixed_figure = remove_odd_sides(figure_dots)

    res_color = cu.Color(result_color[1])

    result_figure = [[]]
    for line in fixed_figure:
        canvas_win.create_line(line[0], line[1], fill = res_color, tag='result')
        result_figure[0].append(line)
    result_figure.append('result')
    history.append(result_figure)



# предварительный просмотр линии
def motion(event):
    global click_clipper, click_rectangle, start_clipper, start_rectangle
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    if option_line.get() == 0:
        if click_rectangle == 1:
            canvas_win.delete("lineHelper")
            canvas_win.create_line(start_rectangle[0], start_rectangle[1], event.x, event.y,
                                   fill='grey', width=1, dash=(7, 9), tag='lineHelper')
    if option_line.get() == 1:
        if click_clipper == 1:
            canvas_win.delete("lineHelper")
            print(start_clipper)
            canvas_win.create_line(start_clipper[0], start_clipper[1], event.x, event.y,
                                   fill='grey', width=1, dash=(7, 9), tag='lineHelper')


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    draw_point(event.x, event.y, 1)


# изменение цвета фона
def change_bg_color():
    global canvas_color
    canvas_color = colorchooser.askcolor()
    canvas_win.configure(bg=cu.Color(canvas_color[1]))


# изменение цвета отрезка, результата или отсекателя
def choose_color_rectangle():
    global rectangle_color
    rectangle_color = colorchooser.askcolor()


def choose_color_result():
    global result_color
    result_color = colorchooser.askcolor()


def choose_color_clipper():
    global clipper_color
    clipper_color = colorchooser.askcolor()


# при нажатии буквы w / s будет переключать радиобаттон (для быстрого задания концов отрезка или отсекателя)
def change_option_click_down(event):
    global option_line

    current_position = option_line.get()
    option_line.set((current_position + 1) % 2)


def change_option_click_up(event):
    global option_line

    current_position = option_line.get()
    option_line.set((current_position - 1) % 2)


# отрисовка по нажатию энтера
def draw_with_enter(event):
    make_figure()


# определить крайний отсекатель для ундо
def find_rectangle(history):
    for i in range(len(history) - 1, -1, -1):
        if history[i][1] == 'rectangle':
            return history[i][0]

    return []


# заполнить листбокс при ундо
def fill_listbox():
    global clipper_coords, figure_coords

    clipper_block.delete('0', 'end')
    figures_block.delete('0', 'end')

    for dot in clipper_coords:
        dot = to_coords(dot)
        dot_str = "  (%-d; %-d)" % (dot[0], dot[1])
        clipper_block.insert(END, dot_str)

    for figure in figure_coords:
        for dot in figure:
            dot = to_coords(dot)
            dot_str = "  (%-d; %-d)" % (dot[0], dot[1])
            figures_block.insert(END, dot_str)
        if len(figure) != 0:
            figures_block.insert(END, 50*"-")


def draw_figure():
    color_line = cu.Color(rectangle_color[1])

    for figures in history:
        if figures[1] == 'figure':
            for figure in figures[0]:
                for i in range(len(figure) - 1):
                    if len(figure) > 1:
                        canvas_win.create_line(figure[i], figure[i + 1], fill=color_line, tag='figure')


# для ундо
def draw_all():
    global clipper_coords, figure_coords

    draw_figure()

    clipper_coords = find_rectangle(history)
    if len(clipper_coords) != 0:
        check_is_close()
        draw_clipper()

    fill_listbox()


def check_is_close():
    global is_close_clipper, clipper_coords

    if clipper_coords[0][0] == clipper_coords[-1][0] and clipper_coords[0][1] == clipper_coords[-1][1]:
        is_close_clipper = 1
    else:
        is_close_clipper = 0


def draw_clipper():
    color_clipper = cu.Color(clipper_color[1])

    for i in range(len(clipper_coords) - 1):
        canvas_win.create_line(clipper_coords[i], clipper_coords[i + 1], fill=color_clipper, tag='clipper')


# откат
def undo():
    global history, clipper_coords, figure_coords, lines

    if len(history) == 0:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    canvas_win.delete('figure', 'dot1', 'dot2', 'clipper', 'clipper_dot', 'result', 'figure_dot')


    deleted = history.pop()
    if deleted[1] == 'figure':
        if len(figure_coords[-1]) == 0:
            figure_coords = figure_coords[:-1]
        figure_coords[-1].pop()

    draw_all()


#  отчистака канваса
def clean_canvas():
    global canvas_color, history, lines, clipper_coords, figure_coords

    history = []
    lines = []
    clipper_coords = []
    figure_coords = [[]]

    figures_block.delete('0', 'end')
    figures_block.delete('0', 'end')

    clipper_block.delete('0', 'end')
    clipper_block.delete('0', 'end')

    canvas_win.delete('figure', 'dot1', 'dot2', 'clipper', 'clipper_dot', 'figure_dot', 'result', 'lineHelper')
    canvas_color = ((255, 255, 255), "#ffffff")
    canvas_win.configure(bg=cu.Color(canvas_color[1]))


# оси координат и сетка
def draw_axes():
    s = int(size)
    j = 0

    canvas_win.create_line(0, s // 2, s - 2, s // 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")
    canvas_win.create_line(s // 2, s, s // 2, 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")

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


# модификация окна
def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size, coord_center

        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)

        size = SIZE * win_k
        m = size / (2 * border + ten_percent)
        coord_center = [size / 2, size / 2]

        canvas_win.place(x=300 * win_x, y=0 * win_y, width=size, height=size)
        canvas_win.create_image((WIN_WIDTH / 2, WIN_HEIGHT / 2), image=image_canvas, state="normal")

        info_lbl.place(x=30 * win_x, y=20 * win_y, width=237 * win_x, height=65 * win_y)

        # координаты отрезка
        line_lbl.place(x=30 * win_x, y=108 * win_y, width=237 * win_x, height=24 * win_y)
        figures_block.place(x=30 * win_x, y=133 * win_y, width=237 * win_x, height=135 * win_y)
        point1_radio.place(x=3 * win_x, y=108 * win_y)


        # координаты отсекателя
        clipper_lbl.place(x=30 * win_x, y=275 * win_y, width=237 * win_x, height=24 * win_y)
        clipper_block.place(x=30 * win_x, y=300 * win_y, width=237 * win_x, height=135 * win_y)

        clipper_radio.place(x=3 * win_x, y=275 * win_y)
        x_lbl.place(x=30 * win_x, y=442 * win_y, width=30 * win_x, height=18 * win_y)
        y_lbl.place(x=156 * win_x, y=442 * win_y, width=30 * win_x, height=18 * win_y)
        x_entry.place(x=62 * win_x, y=442 * win_y, width=80 * win_x, height=20 * win_y)
        y_entry.place(x=188 * win_x, y=442 * win_y, width=80 * win_x, height=20 * win_y)

        add_btn.place(x=30 * win_x, y=465 * win_y, width=237 * win_x, height=25 * win_y)
        add_clipper.place(x=30 * win_x, y=493 * win_y, width=237 * win_x, height=25 * win_y)


        # цвет фона, отсекателя, отрезка и результата
        color_lbl.place(x=30 * win_x, y=540 * win_y, width=237 * win_x, height=24 * win_y)

        bg_clr.place(x=30 * win_x, y=567 * win_y, width=111 * win_x, height=25 * win_y)
        clipper_clr.place(x=155 * win_x, y=567 * win_y, width=111 * win_x, height=25 * win_y)
        line_clr.place(x=30 * win_x, y=593 * win_y, width=111 * win_x, height=25 * win_y)
        result_clr.place(x=155 * win_x, y=593 * win_y, width=111 * win_x, height=25 * win_y)

        # отсечь
        bld.place(x=30 * win_x, y=630 * win_y, width=235 * win_x, height=30 * win_y)

        # условие
        con.place(x=30 * win_x, y=670 * win_y, width=235 * win_x, height=28 * win_y)
        # откат
        und.place(x=30 * win_x, y=700 * win_y, width=109 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=157 * win_x, y=700 * win_y, width=109 * win_x, height=28 * win_y)


        canvas_win.delete('all')
        draw_axes()


# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #9")


# Цвета
color_lbl = Label(text="Цвет", bg='pink', font="AvantGardeC 14", fg='black')
bg_clr = Button(text="фона", font="AvantGardeC 14",
                borderwidth=0, command=lambda: change_bg_color())
clipper_clr = Button(text="отсекателя", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: choose_color_clipper())
line_clr = Button(text="фигуры", font="AvantGardeC 14",
                  borderwidth=0, command=lambda: choose_color_rectangle())
result_clr = Button(text="результата", font="AvantGardeC 14",
                    borderwidth=0, command=lambda: choose_color_result())

clipper_color = ((0, 0, 0), "#000000")  # черный
rectangle_color = ((253, 189, 186), "#fdbdba")  # розовый
canvas_color = ((255, 255, 255), "#ffffff")  # белый
result_color = ((147, 236, 148), "#93ec94")  # светло-зеленый


# Канвас
canvas_win = Canvas(win, bg=cu.Color(canvas_color[1]))
image_canvas = PhotoImage(width = WIN_WIDTH, height = WIN_HEIGHT)
win.bind("<Configure>", config)
win.bind("<Motion>", motion)
canvas_win.bind('<1>', click)
win.bind("s", change_option_click_down)
win.bind("w", change_option_click_up)
win.bind("<Return>", draw_with_enter)


# выбор поля, куда вводятся координаты точки, которую тыкнули
option_line = IntVar()
option_line.set(0)


# информация о клавишах
INFO = "w - движение вверх по радиобаттону\n" \
       "s - движение вниз по радиобаттону\n" \
       "Enter - построить многоугольник\n" \
       "        или отсекатель"
info_lbl = Label(text=INFO, font="AvantGardeC 12", fg='grey', bg='lightgrey')

# отрезок
line_lbl = Label(text="Координаты многоугольников", bg='pink', font="AvantGardeC 14", fg='black')
figures_block = Listbox(bg="#ffffff")
figures_block.configure(font="AvantGardeC 14", fg='black')

point1_radio = Radiobutton(variable=option_line, value=0, bg="grey",
                           activebackground="grey", highlightbackground="grey")


# отсекатель
clipper_lbl = Label(text="Координаты отсекателя", bg='pink', font="AvantGardeC 14", fg='black')

x_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
y_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
x_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
y_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')

clipper_block = Listbox(bg="#ffffff")
clipper_block.configure(font="AvantGardeC 14", fg='black')

add_btn = Button(text="Добавить точку", font="AvantGardeC 14",
                 borderwidth=0, command=lambda: add_dot())
add_clipper = Button(text="Замкнуть", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: make_figure())

clipper_radio = Radiobutton(variable=option_line, value=1, bg="grey",
                            activebackground="grey", highlightbackground="grey")


figure_coords = [[]]
clipper_coords = []
history = []

lines = []
clippers = []

click_rectangle = 0  # был ли клик
click_clipper = 0  # был ли клик

start_rectangle = []
start_clipper = []

is_close_clipper = 0  # был ли замкнут отсекатель
is_close_figure = 0  # была ли замкнута фигура


# Кнопки
bld = Button(text="Отсечь", font="AvantGardeC 14",
             borderwidth=0, command=lambda : cut_area())
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK + AUTHOR))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: clean_canvas())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())


win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
coord_center = [400, 400]  # центр координат (в координатах канваса)
m_board = 1  # коэффициент масштабирования при изменении масштаба канваса
xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
              0, 50, 100, 150, 200, 250, 300, 350, 400]


# Меню
menu = Menu(win)
add_menu = Menu(menu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', TASK + AUTHOR))
add_menu.add_command(label='Выход', command=exit)
menu.add_cascade(label='Help', menu=add_menu)
win.config(menu=menu)

win.mainloop()
