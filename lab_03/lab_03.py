import copy
from tkinter import messagebox, ttk
from tkinter import *
from math import radians, cos, sin
import colorutils as cu
from math import fabs, floor

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

PLUS = 1
MINUS = 0

TASK = "Геометрические преобразования.\n\n" \
       "Нарисовать исходный рисунок. " \
       "Осуществить возможность его перемещения, " \
       "масштабирования и поворота."

MAIN_POINT = "Ключевая точка - точка, относительно которой "\
             "будет производиться поворот, масштабирование."

AUTHOR = "\n\nЕгорова Полина ИУ7-44Б"


# связывает кнопку смещения и функцию
def sft_go():
    try:
        shx = float(shift_x.get())
        shy = float(shift_y.get())
        save_state()
        shift_car([shx, shy])
    except ValueError:
        messagebox.showerror('Ошибка', "Не введены или некорректны значения смещения")


def choose_color(color, intens):
    return color + (intens, intens, intens)


# сохранить в историю положение рисунка
def save_state():
    global xy_history
    xy_history.append(copy.deepcopy(xy_current))
    # main_history.append(main_point)

# прорисовка ключевой точки
# def draw_main_point(ev_x, ev_y, param):
#     if len(main_point):
#         canvas_win.delete('dot')
#
#         main_x.delete(0, END)
#         main_y.delete(0, END)
#         main_x.insert(0, "%.1f" % main_point[0])
#         main_y.insert(0, "%.1f" % main_point[1])
#
#         if param:
#             x, y = ev_x, ev_y
#         else:
#             x, y = to_canva([main_point[0] / m_board, main_point[1] / m_board])
#         canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
#                                outline='grey', fill='pink', activeoutline='lightgreen', width=2, tag='dot')


# координаты точки из канвасовских в фактические
# (только при клике используется, если будет иначе, надо убрать * m_board)
def to_coords(dot):
    x = (dot[0] - coord_center[0]) / m * m_board
    y = (- dot[1] + coord_center[1]) / m * m_board

    return [x, y]


# координаты точки из фактических в канвасовские
def to_canva(dot):
    global m
    x = coord_center[0] + dot[0]
    y = coord_center[1] - dot[1]

    return [x, y]


def sign(diff):
    if diff < 0:
        return -1
    elif diff == 0:
        return 0
    else:
        return 1


def parse_line(option, option_color):
    try:
        x1 = int(x1_entry.get())
        y1 = int(y1_entry.get())
        x2 = int(x2_entry.get())
        y2 = int(y2_entry.get())
        print(x1)
    except:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    p1 = [x1, y1]
    p2 = [x2, y2]

    parse_methods(p1, p2, option, option_color)


def parse_color(option_color):

    print("Color = ", option_color)

    color = "black" # None

    if option_color == 0:
        color = cu.Color((255, 0, 0)) # "red"
    elif option_color == 1:
        color = cu.Color((0, 0, 0)) # "black"
    elif option_color == 2:
        color = cu.Color((0, 0, 255)) # "blue"
    elif option_color == 3:
        color = cu.Color((255, 255, 255)) # СV_COLOR

    return color


def parse_methods(p1, p2, option, option_color, draw=True):
    print("Method = ", option)

    color = parse_color(option_color)

    if option == 0:
        dots = bresenham_int(p1, p2, color)
        print(dots)

        if draw:
            draw_line(dots)

    elif option == 1:
        dots = bresenham_float(p1, p2, color)

        if draw:
            draw_line(dots)


    elif option == 2:
            dots = bresenham_smooth(p1, p2, color)

            if draw:
                draw_line(dots)

    elif option == 3:
        dots = cda_method(p1, p2, color)

        if draw:
            draw_line(dots)

    elif option == 4:
        dots = wu(p1, p2, color)

        if draw:
            draw_line(dots)

    elif option == 5:
        lib_method(p1, p2, color)
    else:
        messagebox.showerror("Ошибка", "Неизвестный алгоритм")


def bresenham_int(p1, p2, color, step_count=False):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    if (x2 - x1 == 0) and (y2 - y1 == 0):
        return [[x1, y1, color]]

    x = x1
    y = y1

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    s1 = sign(x2 - x1)
    s2 = sign(y2 - y1)

    swaped = 0
    if dy > dx:
        tmp = dx
        dx = dy
        dy = tmp
        swaped = 1

    e = 2 * dy - dx
    i = 1
    dots = []
    steps = 0

    while i <= dx + 1:
        dot = [x, y, color]
        dots.append(dot)

        x_buf = x
        y_buf = y

        while e >= 0:
            if swaped:
                x = x + s1
            else:
                y = y + s2

            e = e - 2 * dx

        if swaped:
            y = y + s2
        else:
            x = x + s1

        e = e + 2 * dy

        if step_count:
            if (x_buf != x) and (y_buf != y):
                steps += 1

        i += 1

    if step_count:
        return steps
    else:
        return dots


def bresenham_float(p1, p2, color, step_count=False):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    if x2 - x1 == 0 and y2 - y1 == 0:
        return [[x1, y1, color]]

    x = x1
    y = y1

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    s1 = sign(x2 - x1)
    s2 = sign(y2 - y1)

    if dy > dx:
        tmp = dx
        dx = dy
        dy = tmp
        swaped = 1
    else:
        swaped = 0

    m = dy / dx
    e = m - 0.5
    i = 1

    dots = []
    steps = 0

    while i <= dx + 1:
        dot = [x, y, color]
        dots.append(dot)

        x_buf = x
        y_buf = y

        while e >= 0:
            if swaped:
                x = x + s1
            else:
                y = y + s2

            e = e - 1

        if swaped:
            y = y + s2
        else:
            x = x + s1

        e = e + m

        if step_count:
            if not((x_buf == x and y_buf != y) or
                    (x_buf != x and y_buf == y)):
                steps += 1

        i += 1

    if step_count:
        return steps
    else:
        return dots


def bresenham_smooth(p1, p2, color, step_count=False):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    if (x2 - x1 == 0) and (y2 - y1 == 0):
        return [[x1, y1, color]]

    x = x1
    y = y1

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    s1 = sign(x2 - x1)
    s2 = sign(y2 - y1)

    if (dy > dx):
        tmp = dx
        dx = dy
        dy = tmp
        swaped = 1
    else:
        swaped = 0

    intens = 255

    m = dy / dx
    e = intens / 2

    m *= intens
    w = intens - m

    dots = [[x, y, choose_color(color, round(e))]]

    i = 1

    steps = 0

    while (i <= dx):
        x_buf = x
        y_buf = y

        if (e < w):
            if (swaped):
                y += s2
            else:
                x += s1
            e += m
        else:
            x += s1
            y += s2

            e -= w

        dot = [x, y, choose_color(color, round(e))]

        dots.append(dot)

        if step_count:
            if not ((x_buf == x and y_buf != y) or
                    (x_buf != x and y_buf == y)):
                steps += 1

        i += 1

    if step_count:
        return steps
    else:
        return dots


def cda_method(p1, p2, color, step_count = False):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    if (x2 - x1 == 0) and (y2 - y1 == 0):
        return [[x1, y1, color]]

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy):
        l = abs(dx)
    else:
        l = abs(dy)

    dx /= l
    dy /= l

    x = round(x1)
    y = round(y1)

    dots = [[round(x), round(y), color]]

    i = 1

    steps = 0

    while i < l:

        x += dx
        y += dy

        dot = [round(x), round(y), color]

        dots.append(dot)

        if step_count:
            if not((round(x + dx) == round(x) and
                        round(y + dy) != round(y)) or
                        (round(x + dx) != round(x) and
                        round(y + dy) == round(y))):
                steps += 1

        i += 1

    if step_count:
        return steps
    else:
        return dots


def wu(p1, p2, color, step_count=False):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]

    if (x2 - x1 == 0) and (y2 - y1 == 0):
        return [[x1, y1, color]]

    dx = x2 - x1
    dy = y2 - y1

    m = 1
    step = 1
    intens = 255

    dots = []

    steps = 0

    if fabs(dy) > fabs(dx):
        if dy != 0:
            m = dx / dy
        m1 = m

        if y1 > y2:
            m1 *= -1
            step *= -1

        y_end = round(y2) - 1 if (dy < dx) else (round(y2) + 1)

        for y_cur in range(round(y1), y_end, step):
            d1 = x1 - floor(x1)
            d2 = 1 - d1

            dot1 = [int(x1) + 1, y_cur, choose_color(color, round(fabs(d2) * intens))]

            dot2 = [int(x1), y_cur, choose_color(color, round(fabs(d1) * intens))]

            if step_count and y_cur < y2:
                if int(x1) != int(x1 + m):
                    steps += 1

            dots.append(dot1)
            dots.append(dot2)

            x1 += m1

    else:
        if dx != 0:
            m = dy / dx

        m1 = m

        if x1 > x2:
            step *= -1
            m1 *= -1

        x_end = round(x2) - 1 if (dy > dx) else (round(x2) + 1)

        for x_cur in range(round(x1), x_end, step):
            d1 = y1 - floor(y1)
            d2 = 1 - d1

            dot1 = [x_cur, int(y1) + 1, choose_color(color, round(fabs(d2) * intens))]

            dot2 = [x_cur, int(y1), choose_color(color, round(fabs(d1) * intens))]

            if step_count and x_cur < x2:
                if int(y1) != int(y1 + m):
                    steps += 1

            dots.append(dot1)
            dots.append(dot2)

            y1 += m1

    if step_count:
        return steps
    else:
        return dots


def draw_line(dots):
    history = []
    history.append(copy.deepcopy(line_history[-1]))
    print(len(line_history[-1]))
    for dot in dots:
        tmp =  to_canva(dot[0:2])
        point = [tmp[0], tmp[1], dot[2]]
        canvas_win.create_line(point[0], point[1], point[0] + 1, point[1], fill=point[2].hex, tag='line')
        history.append(dot)
    # line_history.append([])
    line_history.append(copy.deepcopy(history))
    xy_history.append(copy.deepcopy(xy_history[-1]))
    print(len(line_history[-1]), len(line_history))


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    global main_point
    main_point = to_coords([event.x, event.y])

    draw_main_point(event.x, event.y, PLUS)


# откат
def undo():
    global xy_current, line_history

    print(len(line_history))

    if len(line_history) == 0:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return
    canvas_win.delete('car', 'line')
    line_history.pop()
    xy_current = xy_history[-1]
    draw_line(line_history[-1])
    draw_axes()

    xy_history.pop()



# оси координат и сетка
def draw_axes():
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


# растягивание окна
def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size, coord_center

        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)

        size = SIZE * win_k
        m = size / (2 * border + ten_percent)

        canvas_win.place(x=300 * win_x, y=0 * win_y, width=size, height=size)

        # ключевая точка
        center_lbl.place(x=33 * win_x, y=18 * win_y, width=235 * win_x, height=24 * win_y)
        x1_lbl.place(x=33 * win_x, y=48 * win_y, width=110 * win_x, height=18 * win_y)
        y1_lbl.place(x=158 * win_x, y=48 * win_y, width=110 * win_x, height=18 * win_y)
        x1_entry.place(x=33 * win_x, y=67 * win_y, width=110 * win_x, height=20 * win_y)
        y1_entry.place(x=158 * win_x, y=67 * win_y, width=110 * win_x, height=20 * win_y)

        x2_lbl.place(x=33 * win_x, y=93 * win_y, width=110 * win_x, height=18 * win_y)
        y2_lbl.place(x=158 * win_x, y=93 * win_y, width=110 * win_x, height=18 * win_y)
        x2_entry.place(x=33 * win_x, y=112 * win_y, width=110 * win_x, height=20 * win_y)
        y2_entry.place(x=158 * win_x, y=112 * win_y, width=110 * win_x, height=20 * win_y)

        color_lbl.place(x=33 * win_x, y=150 * win_y, width=235 * win_x, height=20 * win_y)
        color_combo.place(x=33 * win_x, y=172 * win_y, width=235 * win_x, height=24 * win_y)

        method_lbl.place(x=33 * win_x, y=200 * win_y, width=235 * win_x, height=20 * win_y)
        method_combo.place(x=33 * win_x, y=222 * win_y, width=235 * win_x, height=24 * win_y)

        back_color_lbl.place(x=33 * win_x, y=250 * win_y, width=235 * win_x, height=20 * win_y)
        back_color_combo.place(x=33 * win_x, y=272 * win_y, width=235 * win_x, height=24 * win_y)
        bld.place(x=33 * win_x, y=300 * win_y, width=235 * win_x, height=25 * win_y)

        spectra_lbl.place(x=33 * win_x, y=348 * win_y, width=235 * win_x, height=20 * win_y)
        spectra_length_lbl.place(x=33 * win_x, y=371 * win_y, width=110 * win_x, height=20 * win_y)
        spectra_angle_lbl.place(x=158 * win_x, y=371 * win_y, width=110 * win_x, height=20 * win_y)
        spectra_length.place(x=33 * win_x, y=394 * win_y, width=111 * win_x, height=20 * win_y)
        spectra_angle.place(x=158 * win_x, y=394 * win_y, width=110 * win_x, height=20 * win_y)
        sct.place(x=33 * win_x, y=417 * win_y, width=235 * win_x, height=25 * win_y)

        lines_lbl.place(x=33 * win_x, y=465 * win_y, width=235 * win_x, height=20 * win_y)
        lines_step_lbl.place(x=33 * win_x, y=489 * win_y, width=235 * win_x, height=18 * win_y)
        lines_step_length.place(x=33 * win_x, y=509 * win_y, width=235 * win_x, height=20 * win_y)
        lns.place(x=33 * win_x, y=531 * win_y, width=235 * win_x, height=25 * win_y)

        # условие
        con.place(x=30 * win_x, y=650 * win_y, width=235 * win_x, height=28 * win_y)
        # сравнения
        tim.place(x=30 * win_x, y=680 * win_y, width=109 * win_x, height=28 * win_y)
        grd.place(x=157 * win_x, y=680 * win_y, width=109 * win_x, height=28 * win_y)
        # откат
        und.place(x=30 * win_x, y=710 * win_y, width=109 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=157 * win_x, y=710 * win_y, width=109 * win_x, height=28 * win_y)


        # изменение размера
        resize_canv_lbl.place(x=30 * win_x, y=590 * win_y, width=235 * win_x, height=24 * win_y)
        pls.place(x=30 * win_x, y=617 * win_y, width=109 * win_x, height=26 * win_y)
        mns.place(x=157 * win_x, y=617 * win_y, width=109 * win_x, height=26 * win_y)

        coord_center = [size / 2, size / 2]

        canvas_win.delete('all')
        draw_axes()
        # draw_main_point(0, 0, MINUS)


# масштабирование канваса
def change_size(plus_or_minus):
    global k_board, m_board, xy_current
    save_state()
    canvas_win.delete('coord', 'line')

    if plus_or_minus == 0:
        # k_board //= 2
        m_board *= 2
        xy_current = [xy_current[i] * 2 for i in range(len(xy_current))]

    else:
        # k_board *= 2
        m_board /= 2
        xy_current = [xy_current[i] / 2 for i in range(len(xy_current))]


def clean():
    canvas_win.delete('line')


# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #3")

# Канвас
canvas_win = Canvas(win, bg="#ffffff")

# Подписи функционала
center_lbl = Label(text="Координаты отрезков", bg='pink', font="AvantGardeC 14", fg='black')
shift_lbl = Label(text="Перемещение", bg='pink', font="AvantGardeC 14", fg='black')
rotate_lbl = Label(text="Поворот", bg='pink', font="AvantGardeC 14", fg='black')
resize_lbl = Label(text="Масштабирование", bg='pink', font="AvantGardeC 14", fg='black')

# Поля ввода
x1_lbl = Label(text="X1", bg='lightgrey', font="AvantGardeC 14", fg='black')
y1_lbl = Label(text="Y1", bg='lightgrey', font="AvantGardeC 14", fg='black')
x1_entry = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y1_entry = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

x2_lbl = Label(text="X2", bg='lightgrey', font="AvantGardeC 14", fg='black')
y2_lbl = Label(text="Y2", bg='lightgrey', font="AvantGardeC 14", fg='black')
x2_entry = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y2_entry = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

color_lbl = Label(text="Цвет отрезка", bg='pink', font="AvantGardeC 14", fg='black')
color_combo = ttk.Combobox(win, values=["Red", "Black", "Green", "White"])

method_lbl = Label(text="Алгоритм", bg='pink', font="AvantGardeC 14", fg='black')
method_combo = ttk.Combobox(win, values=["Брезенхем (целые)", "Брезенхем (вещ)", "Брезенхем (устран. ступ.)", "ЦДА",
                                         "Ву", "Библиотечный"])

back_color_lbl = Label(text="Цвет фона", bg='pink', font="AvantGardeC 14", fg='black')
back_color_combo = ttk.Combobox(win, values=["January", "February", "March", "April"])

spectra_lbl = Label(text="Построить пучок", bg='pink', font="AvantGardeC 14", fg='black')
spectra_length_lbl = Label(text="Длина", bg='lightgrey', font="AvantGardeC 14", fg='black')
spectra_angle_lbl = Label(text="Угол", bg='lightgrey', font="AvantGardeC 14", fg='black')
spectra_length = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
spectra_angle = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

lines_lbl = Label(text="Построить множество отрезков", bg='pink', font="AvantGardeC 14", fg='black')
lines_step_lbl = Label(text="Шаг", bg='lightgrey', font="AvantGardeC 14", fg='black')
lines_step_length = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

resize_canv_lbl = Label(text="Масштабирование канваса", bg='lightgrey', font="AvantGardeC 14", fg='black')

x1_entry.insert(END, 200)
y1_entry.insert(END, 200)
x2_entry.insert(END, 700)
y2_entry.insert(END, 220)
color_combo.current(0)
method_combo.current(0)


# Список точек
line_history = [[0, 0]] # история координат отрезков
xy_history = [-400, -350, -300, -250, -200, -150, -100, -50,
            0, 50, 100, 150, 200, 250, 300, 350, 400] # история координат на оси
xy_start = [-400, -350, -300, -250, -200, -150, -100, -50,
            0, 50, 100, 150, 200, 250, 300, 350, 400]
xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
            0, 50, 100, 150, 200, 250, 300, 350, 400]


# Кнопки
bld = Button(text="Построить отрезок", font="AvantGardeC 14",
             borderwidth=0, command=lambda: parse_line(method_combo.current(), color_combo.current()))
sct = Button(text="Построить", font="AvantGardeC 14",
             borderwidth=0)
lns = Button(text="Построить", font="AvantGardeC 14",
             borderwidth=0)
tim = Button(text="Сравнить\nвремя", font="AvantGardeC 10",
             borderwidth=0)
grd = Button(text="Сравнить\nступенчатость", font="AvantGardeC 10",
             borderwidth=0)
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK + AUTHOR))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: clean())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())
pls = Button(text="+", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_size(PLUS))
mns = Button(text="-", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_size(MINUS))

win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
coord_center = [400, 400]  # центр координат (в координатах канваса)

k_board = 4
m_board = 1 # коэффициент масштабирования при изменении масштаба канваса


canvas_win.bind('<1>', click)


# Меню
menu = Menu(win)
add_menu = Menu(menu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', TASK + AUTHOR))
add_menu.add_command(label='Выход', command=exit)
menu.add_cascade(label='Help', menu=add_menu)
win.config(menu=menu)

win.bind("<Configure>", config)
win.bind("<<ComboboxSelected>>", )

win.mainloop()
