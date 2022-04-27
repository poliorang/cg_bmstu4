from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
from math import radians, cos, sin, fabs, floor, pi, sqrt
import colorutils as cu
import matplotlib.pyplot as plt
import numpy as np
from time import time, sleep

WIN_WIDTH = 1200
WIN_HEIGHT = 800
TEMP_SIDE_COLOR_CHECK = (255, 0, 255) # purple
TEMP_SIDE_COLOR = "#ff00ff"
CV_COLOR = "#ffffff"
COLOR_LINE = "black" #(0, 0, 0) # black

SIZE = 800
WIDTH = 100.0

PLUS = 1
MINUS = 0

TASK = "Алгоритмы растрового заполнения " \
       "сплошных областей.\n" \
       "Алгоритм заполнения со списком " \
       "ребер и флагом."

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


def distance(point1, point2):
    x1 = max(point1[0], point2[0])
    x2 = min(point1[0], point2[0])
    y1 = max(point1[1], point2[1])
    y2 = min(point1[1], point2[1])
    return sqrt(((y2 - y1) * (y2 - y1)) + (x2 - x1) * (x2 - x1))


def sign(diff):
    if diff < 0:
        return -1
    elif diff == 0:
        return 0
    else:
        return 1


def parse_line(opt):
    try:
        x1 = int(x1_entry.get())
        y1 = int(y1_entry.get())
        x2 = int(x2_entry.get())
        y2 = int(y2_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    p1 = [x1, y1]
    p2 = [x2, y2]

    parse_methods(p1, p2, opt)


def manual_add_dot():
    try:
        x = int(x_entry.get())
        y = int(y_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    draw_point(x, y, 0)


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

        while e > 0:
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


def parse_color(num_color):
    color = "orange"

    if (num_color == 1):
        color = "#ff6e41" #"orange"
    elif (num_color == 2):
        color = "#ff5733" #"red"
    elif (num_color == 3):
        color = "#0055ff" #"blue"
    elif (num_color == 4):
        color = "#45ff00" #"green"

    return color


def line_koefs(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1 * y2 - x2 * y1

    return a, b, c


def solve_lines_intersection(a1, b1, c1, a2, b2, c2):
    opr = a1 * b2 - a2 * b1
    opr1 = (-c1) * b2 - b1 * (-c2)
    opr2 = a1 * (-c2) - (-c1) * a2

    x = opr1 / opr
    y = opr2 / opr

    return x, y


def round_side(dot1, dot2):
    if dot1[1] == dot2[1]:
        return

    a_side, b_side, c_side = line_koefs(dot1[0], dot1[1], dot2[0], dot2[1])

    if dot1[1] > dot2[1]:
        y_max = dot1[1]
        y_min = dot2[1]
        x = dot2[0]
    else:
        y_max = dot2[1]
        y_min = dot1[1]
        x = dot1[0]

    y = y_min

    while y < y_max:
        a_scan_line, b_scan_line, c_scan_line = line_koefs(x, y, x + 1, y)

        x_intersec, y_intersec = solve_lines_intersection(a_side, b_side, c_side, a_scan_line, b_scan_line, c_scan_line)

        x_ = int(x_intersec)
        if image_canvas.get(int(x_intersec) + 1, y) != TEMP_SIDE_COLOR_CHECK:
            x_ += 1

        else:
            x_ += 2

        image_canvas.put(TEMP_SIDE_COLOR, (x_, y))
        # canvas_win.create_polygon([x_, y], [x_, y + 1],
        #                           [x_ + 1, y + 1], [x_ + 1, y],
        #                           fill=TEMP_SIDE_COLOR, tag='line')

        y += 1

        canvas_win.update()


def round_figure():
    for figure in range(len(sides_list)):
        sides_num = len(sides_list[figure]) - 1

        for side in range(sides_num + 1):
            round_side(sides_list[figure][side][0], sides_list[figure][side][1])


def get_edges(dots):
    x_max = 0
    x_min = WIN_WIDTH

    y_max = WIN_HEIGHT
    y_min = 0
    #
    for figure in dots:
        for dot in figure:
            if dot[0] > x_max:
                x_max = dot[0]

            if dot[0] < x_min:
                x_min = dot[0]

            if dot[1] < y_max:
                y_max = dot[1]

            if dot[1] > y_min:
                y_min = dot[1]

    block_edges = (x_min, y_min, x_max, y_max)

    return block_edges

def new_dots_check(dots):
    ans = 0
    for i in range(len(dots) - 1):
        print('a ', dots[i][-1][2])
        if dots[i][-1][2] == 0:
            ans = i
            break
    return ans

def parse_fill():
    cur_figure = len(dots_list) - 1

    if len(dots_list[cur_figure]) != 0:
        messagebox.showerror("Ошибка", "Крайняя фигура не замкнута")
        return

    block_edges = get_edges(dots_list)

    if option_filling.get() == 1:
        delay = True
    else:
        delay = False

    fill_with_sides_and_flag(block_edges, delay=delay)


def fill_with_sides_and_flag(block_edges, delay=False):
    round_figure()
    canvas_win.update()

    color_fill = cu.Color(filling_color[1])
    color_line = cu.Color(line_color[1])
    color_background = cu.Color(canvas_bg[1])
    print(canvas_bg)

    x_max = block_edges[2]
    x_min = block_edges[0]

    y_max = block_edges[3]
    y_min = block_edges[1]

    start_time = time()

    for y in range(y_min, y_max - 1, -1):
        flag = False

        for x in range(x_min, x_max + 2):

            # if screen.itemcget(screen.find_overlapping(i+p,j+p,i+p,j+p)[-1], "fill" ) != 'black'
            if image_canvas.get(x, y) == TEMP_SIDE_COLOR_CHECK:
                flag = not flag

            if flag:
                image_canvas.put(color_fill, (x, y))
                canvas_win.create_polygon([x, y], [x, y + 1],
                                          [x + 1, y + 1], [x + 1, y],
                                          fill=color_fill, tag='line')
            else:
                image_canvas.put(color_background, (x, y))
                canvas_win.create_polygon([x, y], [x, y + 1],
                                          [x + 1, y + 1], [x + 1, y],
                                          fill=color_background, tag='line')

        if delay:
            canvas_win.delete('coord')
            draw_axes()
            canvas_win.update()
            sleep(0.001 * 1)

    end_time = time()

    # Sides
    for fig in sides_list:
        for side in fig:
            dots = bresenham_int(side[0], side[1], color_line)
            draw_sides(dots)

    canvas_win.delete('coord')
    draw_axes()
    # time_label = Label(text="Время: %-3.2f с" % (end_time - start_time), font="-family {Consolas} -size 16",
    #                    bg="lightgrey")
    # time_label.place(x=20, y=CV_HEIGHT - 50)


# нарисовать линию
def draw_line(dots):
    global xy_history, line_history
    for dot in dots:
        x, y = dot[0:2]
        canvas_win.create_polygon([x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y], fill=dot[2], tag='line')
    # xy_history.append(xy_current)
    # line_history.append(dots)
    # canvas_win.delete('dot')


def make_figure():
    cur_figure = len(dots_list)
    cur_dot = len(dots_list[cur_figure - 1])

    if cur_dot < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
        return
    draw_point(dots_list[cur_figure - 1][0][0], dots_list[cur_figure - 1][0][1], 1)
    canvas_win.delete('dot')

    dots_list.append(list())
    sides_list.append(list())

    dots_block.insert(END, "-" * 50)


# удаление точки
def del_dot():
    try:
        if str(dots_block.get(END))[0] == '-':
            dots_block.delete(END)

        dots_block.delete(END)

    except:
        messagebox.showerror("Ошибка", "Не выбрана точка")


def draw_point(ev_x, ev_y, click_):
    global dots_block, dots_list

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canva([ev_x, ev_y])

    x_y = to_coords([x, y])
    cur_figure = len(dots_list) - 1
    dots_list[cur_figure].append([int(x), int(y)])

    cur_dot = len(dots_list[cur_figure]) - 1

    dot_str = "%d : (%-3.1f; %-3.1f)" % (cur_dot + 1, x_y[0], x_y[1])
    dots_block.insert(END, dot_str)

    canvas_win.delete('dot')
    canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                           outline='grey', fill='pink', activeoutline='lightgreen', width=2, tag='dot')

    color_line = cu.Color(line_color[1])
    if len(dots_list[cur_figure]) > 1:
        sides_list[cur_figure].append([dots_list[cur_figure][cur_dot - 1], dots_list[cur_figure][cur_dot]])
        dots = bresenham_int(dots_list[cur_figure][cur_dot - 1], dots_list[cur_figure][cur_dot], color_line)

        draw_line(dots)


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return
    draw_point(event.x, event.y, 1)


def draw_lines(click_dots):
    for figure in click_dots:
        for i in range(len(figure) - 1):
            dots = bresenham_int(figure[i], figure[i + 1], cu.Color(line_color[1]))
            draw_line(dots)


def draw_sides(dots):
    for dot in dots:
        x, y = dot[0:2]
        canvas_win.create_polygon([x, y], [x, y + 1],
                                  [x + 1, y + 1], [x + 1, y],
                                  fill=dot[2], tag='line')


# откат
def undo():
    global dots_list, sides_list

    if len(dots_list) == 1 and dots_list[0] == []:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    canvas_win.delete('line', 'coord')

    d = -1
    if dots_list[-1] == []:
        if len(dots_list) > 1:
            d = -2
    dots_list[d].pop()
    del_dot()

    s = -1
    if sides_list[-1] == []:
        if len(sides_list) > 1:
            s = -2
    if sides_list[0] != []:
        sides_list[s].pop()

    if len(dots_list) > 1 and dots_list[-2] == []:
        dots_list = dots_list[:-1]
    if len(sides_list) > 1 and sides_list[-2] == []:
        sides_list = sides_list[:-1]

    # print('del  \n', dots_list, '\n', sides_list)
    draw_lines(dots_list)
    draw_axes()


# оси координат и сетка
def draw_axes():
    s = int(size)
    j = 0

    canvas_win.create_line(0, s // 2, s - 2, s // 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")
    canvas_win.create_line(s // 2, s, s // 2, 2, fill='grey',
                           width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")

    for i in range(0, s, s // 16):
        # canvas_win.create_line(i, s / 2 - 5, i, s / 2 + 5, fill='grey',
        #                        width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")
        canvas_win.create_line(i, s / 2 - 5, i, s / 2 + 5, fill='pink', width=2)
        canvas_win.create_line(i, 0, i, s, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(i, s // 2 + 20, text=f'{"%.2f" % xy_current[j]}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

        # canvas_win.create_line(s / 2 - 5, i, s / 2 + 5, i, fill='grey',
        #                        width=1, arrow=LAST, activefill='lightgreen', arrowshape="10 20 6")
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
        canvas_win.create_image((WIN_WIDTH / 2, WIN_HEIGHT / 2), image=image_canvas, state="normal")

        # координаты
        center_lbl.place(x=30 * win_x, y=28 * win_y, width=150 * win_x, height=24 * win_y)
        dots_block.place(x=30 * win_x, y=55 * win_y, width=237 * win_x, height=350 * win_y)

        # добавить, изменить и удалить точку
        x_lbl.place(x=30 * win_x, y=410 * win_y, width=110 * win_x, height=18 * win_y)
        y_lbl.place(x=157 * win_x, y=410 * win_y, width=110 * win_x, height=18 * win_y)
        x_entry.place(x=30 * win_x, y=430 * win_y, width=110 * win_x, height=20 * win_y)
        y_entry.place(x=157 * win_x, y=430 * win_y, width=110 * win_x, height=20 * win_y)

        add.place(x=30 * win_x, y=452 * win_y, width=237 * win_x, height=25 * win_y)
        # chg.place(x=112 * win_x, y=452 * win_y, width=75 * win_x, height=25 * win_y)
        # dlt.place(x=194 * win_x, y=452 * win_y, width=75 * win_x, height=25 * win_y)

        # закраска
        draw_delay.place(x=30 * win_x, y=510 * win_y)
        draw_without_delay.place(x=150 * win_x, y=510 * win_y)
        fill_figure_btn.place(x=30 * win_x, y=535 * win_y, width=237 * win_x, height=28 * win_y)

        # цвет фона, отрезка и заливки
        color_lbl.place(x=30 * win_x, y=575 * win_y, width=237 * win_x, height=24 * win_y)
        clr.place(x=30 * win_x, y=602 * win_y, width=75 * win_x, height=25 * win_y)
        bgc.place(x=112 * win_x, y=602 * win_y, width=75 * win_x, height=25 * win_y)
        fil.place(x=194 * win_x, y=602 * win_y, width=75 * win_x, height=25 * win_y)

        # условие
        con.place(x=30 * win_x, y=640 * win_y, width=235 * win_x, height=28 * win_y)
        # сравнения
        # measure_lbl.place(x=30 * win_x, y=610 * win_y, width=235 * win_x, height=24 * win_y)
        tim.place(x=30 * win_x, y=670 * win_y, width=109 * win_x, height=28 * win_y)
        grd.place(x=157 * win_x, y=670 * win_y, width=109 * win_x, height=28 * win_y)
        # откат
        und.place(x=30 * win_x, y=700 * win_y, width=109 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=157 * win_x, y=700 * win_y, width=109 * win_x, height=28 * win_y)

        fim.place(x=188 * win_x, y=28 * win_y, width=80 * win_x, height=25 * win_y)

        coord_center = [size / 2, size / 2]

        canvas_win.delete('all')
        draw_axes()


# изменение цвета фона
def change_bg_color():
    global canvas_bg
    canvas_bg = colorchooser.askcolor()
    canvas_win.configure(bg=cu.Color(canvas_bg[1]))
    parse_fill()


# изменение цвета отрезка
def choose_line_color():
    global line_color
    line_color = colorchooser.askcolor()


# изменение цвета заливки
def choose_fill_color():
    global filling_color
    filling_color = colorchooser.askcolor()


# при нажатии буквы q будет переключать радиобаттон (для быстрого задания концов отрезка)
def change_option_click(event):
    global option
    if option.get() == 1:
        option.set(2)
    elif option.get() == 2:
        option.set(1)


#  отчистака канваса
def clean_canvas():
    global canvas_bg

    dots_list.clear()
    sides_list.clear()

    dots_list.append([])
    sides_list.append([])
    canvas_win.delete('line', 'dot')
    draw_axes()
    canvas_bg = ((255, 255, 255), "#ffffff")
    canvas_win.configure(bg=cu.Color(canvas_bg[1]))
    dots_block.delete(0, END)


# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #5")

# переменная для радиобаттона
option = IntVar()
option.set(1)

# Канвас
canvas_bg = ((255, 255, 255), "#ffffff")
canvas_win = Canvas(win, bg=cu.Color(canvas_bg[1]))

filling_color = ((253, 189, 186), "#fdbdba")
line_color = ((0, 0, 0), "#000000")

image_canvas = PhotoImage(width = WIN_WIDTH, height = WIN_HEIGHT)

center_lbl = Label(text="Координаты точек", bg='pink', font="AvantGardeC 14", fg='black')
dots_block = Listbox(bg="#ffffff")
dots_block.configure(font="AvantGardeC 14", fg='black')

dots_list = [[]]
sides_list = [[]]

x_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
y_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
x_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')
y_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')

method_lbl = Label(text="Алгоритм", bg='pink', font="AvantGardeC 14", fg='black')
method_combo = ttk.Combobox(win, state='readonly', values=["Брезенхем (целые)", "Брезенхем (вещ)",
                            "Брезенхем (устран. ступ.)", "ЦДА", "Ву", "Библиотечный"])
method_combo.current(0)

color_lbl = Label(text="Цвет", bg='pink', font="AvantGardeC 14", fg='black')

spectra_lbl = Label(text="Построить пучок", bg='pink', font="AvantGardeC 14", fg='black')
measure_lbl = Label(text="Сравнить", bg='pink', font="AvantGardeC 14", fg='black')

# Список точек
# line_history = []  # история координат отрезков

xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
              0, 50, 100, 150, 200, 250, 300, 350, 400]
xy_history = [xy_current]  # история координат на оси


# Кнопки
sct = Button(text="Построить", font="AvantGardeC 14",
             borderwidth=0)
tim = Button(text="Время", font="AvantGardeC 12",
             borderwidth=0, command=lambda: time_go())
grd = Button(text="Ступенчатость", font="AvantGardeC 12",
             borderwidth=0, command=lambda: steps_go())
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK + AUTHOR))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: clean_canvas())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())
fim = Button(text="Замкнуть", font="AvantGardeC 12",
             borderwidth=0, command=lambda: make_figure())
clr = Button(text="отрезка", font="AvantGardeC 14",
             borderwidth=0, command=lambda: choose_line_color())
bgc = Button(text="фона", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_bg_color())
fil = Button(text="заливки", font="AvantGardeC 14",
             borderwidth=0, command=lambda: choose_fill_color())
add = Button(text="Добавить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: manual_add_dot())
option_filling = IntVar()
option_filling.set(0)

option_color = IntVar()
option_color.set(1)

draw_delay = Radiobutton(text="С задержкой", variable=option_filling, value=1, bg="grey",
                         activebackground="grey", highlightbackground="grey")

draw_without_delay = Radiobutton(text="Без задержки",variable=option_filling,  value=0, bg="grey",
                                 activebackground="grey", highlightbackground="grey")

fill_figure_btn = Button(text="Закрасить", font="AvantGardeC 14",
                         borderwidth=0, command=lambda: parse_fill())

win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
coord_center = [400, 400]  # центр координат (в координатах канваса)

m_board = 1  # коэффициент масштабирования при изменении масштаба канваса

# current_color = (0, 0, 0)
fill_color = (0, 0, 0)

win.bind("<Configure>", config)
win.bind("q", change_option_click)
canvas_win.bind('<1>', click)



# Меню
menu = Menu(win)
add_menu = Menu(menu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', TASK + AUTHOR))
add_menu.add_command(label='Выход', command=exit)
menu.add_cascade(label='Help', menu=add_menu)
win.config(menu=menu)

win.mainloop()
