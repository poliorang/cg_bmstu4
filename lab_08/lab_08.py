from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
import colorutils as cu
import copy
from itertools import combinations

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

TASK = "Реализация (и исследование) " \
       "отсечения отрезка нерегулярным отсекателем " \
       "методом Кируса-Бека"

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


# нарисовать отрезок
def draw_line():
    color = cu.Color(line_color[1])
    try:
        dot1 = to_canva([int(x1_entry.get()), int(y1_entry.get())])
        dot2 = to_canva([int(x2_entry.get()), int(y2_entry.get())])
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректные координаты отрезка")
        return

    lines.append([dot1, dot2])
    history.append([[dot1, dot2], 'line'])

    canvas_win.create_line(dot1, dot2, fill=color, tag='line')


# добаление точки по координатам (не через канвас)
def add_clipper_dot():
    try:
        x = int(x1_clipper_entry.get())
        y = int(y1_clipper_entry.get())
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


def draw_clipper():
    color_clipper = cu.Color(clipper_color[1])

    for i in range(len(clipper_coords) - 1):
        canvas_win.create_line(clipper_coords[i], clipper_coords[i + 1], fill=color_clipper, tag='clipper')


# замкнуть фигуру
def make_figure():
    global is_close_figure

    if len(clipper_coords) < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
        return

    draw_point(clipper_coords[0][0], clipper_coords[0][1], 1)
    is_close_figure = 1


# отрисовка и вставка в листбокс добавленной точки
def draw_point(ev_x, ev_y, click_):
    global option_line, line_coords, clipper_coords, is_close_figure

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canva([ev_x, ev_y])

    x_y = to_coords([x, y])

    if option_line.get() == 0:
        x1_entry.delete(0, END)
        y1_entry.delete(0, END)
        x1_entry.insert(0, "%d" % x_y[0])
        y1_entry.insert(0, "%d" % x_y[1])
        canvas_win.delete('dot1')
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='lightgreen', fill='lightgreen', activeoutline='pink', width=2, tag='dot1')
    elif option_line.get() == 1:
        x2_entry.delete(0, END)
        y2_entry.delete(0, END)
        x2_entry.insert(0, "%d" % x_y[0])
        y2_entry.insert(0, "%d" % x_y[1])
        canvas_win.delete('dot2')
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='lightgreen', fill='lightgreen', activeoutline='pink', width=2, tag='dot2')

    elif option_line.get() == 2:

        if is_close_figure:
            for _ in range(len(clipper_coords)):
                clipper_block.delete(END)
            clipper_coords = []
            is_close_figure = 0
            canvas_win.delete('clipper_dot', 'clipper')

        dot_str = "  (%-d; %-d)" % (x_y[0], x_y[1])
        clipper_block.insert(END, dot_str)
        draw_line_clipper([x, y])
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='pink', fill='pink', activeoutline='lightgreen', width=2, tag='clipper_dot')


# Algorithm

def get_vector(dot1, dot2):
    return [dot2[0] - dot1[0], dot2[1] - dot1[1]]


def vector_mul(vec1, vec2):
    return vec1[0] * vec2[1] - vec1[1] * vec2[0]


def scalar_mul(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]


def line_koefs(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1 * y2 - x2 * y1

    return a, b, c


def solve_lines_intersection(a1, b1, c1, a2, b2, c2):
    opr = a1 * b2 - a2 * b1
    opr1 = (-c1) * b2 - b1 * (-c2)
    opr2 = a1 * (-c2) - (-c1) * a2

    if opr == 0:
        return -5, -5  # прямые параллельны

    x = opr1 / opr
    y = opr2 / opr

    return x, y


def is_coord_between(left_coord, right_coord, dot_coord):
    return (min(left_coord, right_coord) <= dot_coord) \
           and (max(left_coord, right_coord) >= dot_coord)


def is_dot_between(dot_left, dot_right, dot_intersec):
    return is_coord_between(dot_left[0], dot_right[0], dot_intersec[0]) \
           and is_coord_between(dot_left[1], dot_right[1], dot_intersec[1])


def are_connected_sides(line1, line2):
    if ((line1[0][0] == line2[0][0]) and (line1[0][1] == line2[0][1])) \
            or ((line1[1][0] == line2[1][0]) and (line1[1][1] == line2[1][1])) \
            or ((line1[0][0] == line2[1][0]) and (line1[0][1] == line2[1][1])) \
            or ((line1[1][0] == line2[0][0]) and (line1[1][1] == line2[0][1])):
        return True

    return False


def extra_check():  # чтобы не было пересечений

    cutter_lines = []

    for i in range(len(clipper_coords) - 1):
        cutter_lines.append([clipper_coords[i], clipper_coords[i + 1]])  # разбиваю отсекатель на линии

    combs_lines = list(combinations(cutter_lines, 2))  # все возможные комбинации сторон

    for i in range(len(combs_lines)):
        line1 = combs_lines[i][0]
        line2 = combs_lines[i][1]

        if are_connected_sides(line1, line2):
            continue

        a1, b1, c1 = line_koefs(line1[0][0], line1[0][1], line1[1][0], line1[1][1])
        a2, b2, c2 = line_koefs(line2[0][0], line2[0][1], line2[1][0], line2[1][1])

        dot_intersection = solve_lines_intersection(a1, b1, c1, a2, b2, c2)

        if (is_dot_between(line1[0], line1[1], dot_intersection)) \
                and (is_dot_between(line2[0], line2[1], dot_intersection)):
            return True

    return False


def check_polygon():
    if len(clipper_coords) < 3:
        return False

    sign = 0

    if vector_mul(get_vector(clipper_coords[1], clipper_coords[2]), get_vector(clipper_coords[0], clipper_coords[1])) > 0:
        sign = 1
    else:
        sign = -1

    for i in range(3, len(clipper_coords)):
        if sign * vector_mul(get_vector(clipper_coords[i - 1], clipper_coords[i]), get_vector(clipper_coords[i - 2], clipper_coords[i - 1])) < 0:
            return False

    check = extra_check()

    if check:
        return False

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


def cyrus_beck_algorithm(line, count):
    dot1 = line[0]
    dot2 = line[1]

    d = [dot2[0] - dot1[0], dot2[1] - dot1[1]]  # директриса

    t_bottom = 0
    t_top = 1

    for i in range(-2, count - 2):
        normal = get_normal(clipper_coords[i], clipper_coords[i + 1], clipper_coords[i + 2])

        w = [dot1[0] - clipper_coords[i][0], dot1[1] - clipper_coords[i][1]]

        d_scalar = scalar_mul(d, normal)
        w_scalar = scalar_mul(w, normal)

        if d_scalar == 0:
            if w_scalar < 0:
                return  # параллельный невидимый
            else:
                continue  # параллельный видимый

        t = -w_scalar / d_scalar

        if d_scalar > 0:  # ближе к началу отрезка
            if t <= 1:
                t_bottom = max(t_bottom, t)
            else:
                return
        elif d_scalar < 0:  # ближе к концу отрезка
            if t >= 0:
                t_top = min(t_top, t)
            else:
                return

        if t_bottom > t_top:
            break

    dot1_res = [round(dot1[0] + d[0] * t_bottom), round(dot1[1] + d[1] * t_bottom)]
    dot2_res = [round(dot1[0] + d[0] * t_top), round(dot1[1] + d[1] * t_top)]

    res_color = cu.Color(result_color[1])

    if t_bottom <= t_top:
        canvas_win.create_line(dot1_res, dot2_res, fill=res_color, tag='result')


def find_start_dot():
    y_max = clipper_coords[0][1]
    dot_index = 0

    for i in range(len(clipper_coords)):
        if clipper_coords[i][1] > y_max:
            y_max = clipper_coords[i][1]
            dot_index = i

    clipper_coords.pop()

    for _ in range(dot_index):
        clipper_coords.append(clipper_coords.pop(0))

    clipper_coords.append(clipper_coords[0])

    if clipper_coords[-2][0] > clipper_coords[1][0]:
        clipper_coords.reverse()


def cut_area():

    if not is_close_figure:
        messagebox.showinfo("Ошибка", "Отсекатель не замкнут")
        return

    if len(clipper_coords) < 3:
        messagebox.showinfo("Ошибка", "Не задан отсекатель")
        return

    if not check_polygon():
        messagebox.showinfo("Ошибка", "Отсекатель должен быть выпуклым многоугольником")
        return

    find_start_dot()
    dot = clipper_coords.pop()

    # print(clipper_coords, dot)

    for line in lines:
        cyrus_beck_algorithm(line, len(clipper_coords))

    clipper_coords.append(dot)


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
def choose_color_line():
    global line_color
    line_color = colorchooser.askcolor()


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
    option_line.set((current_position + 1) % 3)


def change_option_click_up(event):
    global option_line

    current_position = option_line.get()
    option_line.set((current_position - 1) % 3)


# отрисовка по нажатию энтера
def draw_with_enter(event):
    global option_line

    current_position = option_line.get()

    if 0 <= current_position <= 1:
        draw_line()

    elif current_position == 2:
        make_figure()


# определить крайний отсекатель для ундо
def find_rectangle(history):
    for i in range(len(history) - 1, -1, -1):
        if history[i][1] == 'rectangle':
            return history[i][0]

    return []


# заполнить листбокс при ундо
def fill_listbox():
    global clipper_coords,clipper_block

    clipper_block.delete('0', 'end')

    for dot in clipper_coords:
        dot = to_coords(dot)
        dot_str = "  (%-d; %-d)" % (dot[0], dot[1])
        clipper_block.insert(END, dot_str)


# для ундо
def draw_all():
    global clipper_coords

    color_line = cu.Color(line_color[1])

    for figure in history:
        if figure[1] == 'line':
            canvas_win.create_line(figure[0], fill=color_line, tag='line')

    clipper_coords = find_rectangle(history)
    if len(clipper_coords) != 0:
        check_is_close()
        draw_clipper()

    fill_listbox()


def check_is_close():
    global is_close_figure, clipper_coords

    if clipper_coords[0][0] == clipper_coords[-1][0] and clipper_coords[0][1] == clipper_coords[-1][1]:
        is_close_figure = 1
    else:
        is_close_figure = 0


# откат
def undo():
    global history, clipper_coords, lines

    if len(history) == 0:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    canvas_win.delete('line', 'dot1', 'dot2', 'clipper', 'clipper_dot', 'result')

    deleted = history.pop()
    if deleted[1] == 'line':
        lines.pop()

    draw_all()


#  отчистака канваса
def clean_canvas():
    global canvas_color, history, lines, clipper_coords, clipper_block

    history = []
    lines = []
    clipper_coords = []

    clipper_block.delete('0', 'end')

    canvas_win.delete('line', 'dot1', 'dot2', 'clipper', 'clipper_dot', 'result')
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

        x1_lbl.place(x=30 * win_x, y=140 * win_y, width=30 * win_x, height=18 * win_y)
        y1_lbl.place(x=156 * win_x, y=140 * win_y, width=30 * win_x, height=18 * win_y)
        x1_entry.place(x=62 * win_x, y=140 * win_y, width=80 * win_x, height=20 * win_y)
        y1_entry.place(x=188 * win_x, y=140 * win_y, width=80 * win_x, height=20 * win_y)

        x2_lbl.place(x=30 * win_x, y=162 * win_y, width=30 * win_x, height=18 * win_y)
        y2_lbl.place(x=156 * win_x, y=162 * win_y, width=30 * win_x, height=18 * win_y)
        x2_entry.place(x=62 * win_x, y=162 * win_y, width=80 * win_x, height=20 * win_y)
        y2_entry.place(x=188 * win_x, y=162 * win_y, width=80 * win_x, height=20 * win_y)

        add_line.place(x=30 * win_x, y=185 * win_y, width=237 * win_x, height=25 * win_y)

        point1_radio.place(x=3 * win_x, y=135 * win_y)
        point2_radio.place(x=3 * win_x, y=157 * win_y)


        # координаты отсекателя
        clipper_lbl.place(x=30 * win_x, y=230 * win_y, width=237 * win_x, height=24 * win_y)

        clipper_block.place(x=30 * win_x, y=255 * win_y, width=237 * win_x, height=180 * win_y)

        clipper_radio.place(x=3 * win_x, y=437 * win_y)
        x1_clipper_lbl.place(x=30 * win_x, y=442 * win_y, width=30 * win_x, height=18 * win_y)
        y1_clipper_lbl.place(x=156 * win_x, y=442 * win_y, width=30 * win_x, height=18 * win_y)
        x1_clipper_entry.place(x=62 * win_x, y=442 * win_y, width=80 * win_x, height=20 * win_y)
        y1_clipper_entry.place(x=188 * win_x, y=442 * win_y, width=80 * win_x, height=20 * win_y)

        add_dot.place(x=30 * win_x, y=465 * win_y, width=237 * win_x, height=25 * win_y)
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
win.title("Лабораторная работа #8")


# Цвета
color_lbl = Label(text="Цвет", bg='pink', font="AvantGardeC 14", fg='black')
bg_clr = Button(text="фона", font="AvantGardeC 14",
                borderwidth=0, command=lambda: change_bg_color())
clipper_clr = Button(text="отсекателя", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: choose_color_clipper())
line_clr = Button(text="отрезка", font="AvantGardeC 14",
                  borderwidth=0, command=lambda: choose_color_line())
result_clr = Button(text="результата", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: choose_color_result())

clipper_color = ((0, 0, 0), "#000000")  # черный
line_color = ((253, 189, 186), "#fdbdba")  # розовый
canvas_color = ((255, 255, 255), "#ffffff")  # белый
result_color = ((147, 236, 148), "#93ec94")  # светло-зеленый


# Канвас
canvas_win = Canvas(win, bg=cu.Color(canvas_color[1]))
image_canvas = PhotoImage(width = WIN_WIDTH, height = WIN_HEIGHT)
win.bind("<Configure>", config)
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
       "Enter - построить отрезок\n" \
       "        или отсекатель"
info_lbl = Label(text=INFO, font="AvantGardeC 12", fg='grey', bg='lightgrey')

# отрезок
line_lbl = Label(text="Координаты отрезка", bg='pink', font="AvantGardeC 14", fg='black')
x1_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
y1_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
x1_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
y1_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')

x2_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
y2_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
x2_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
y2_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
add_line = Button(text="Добавить отрезок", font="AvantGardeC 14",
             borderwidth=0, command=lambda: draw_line())

point1_radio = Radiobutton(variable=option_line, value=0, bg="grey",
                         activebackground="grey", highlightbackground="grey")
point2_radio = Radiobutton(variable=option_line, value=1, bg="grey",
                         activebackground="grey", highlightbackground="grey")


# отсекатель
clipper_lbl = Label(text="Координаты отсекателя", bg='pink', font="AvantGardeC 14", fg='black')

x1_clipper_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
y1_clipper_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
x1_clipper_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
y1_clipper_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')

clipper_block = Listbox(bg="#ffffff")
clipper_block.configure(font="AvantGardeC 14", fg='black')

add_dot = Button(text="Добавить точку", font="AvantGardeC 14",
                 borderwidth=0, command=lambda: add_clipper_dot())
add_clipper = Button(text="Замкнуть", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: make_figure())

clipper_radio = Radiobutton(variable=option_line, value=2, bg="grey",
                         activebackground="grey", highlightbackground="grey")


line_coords = []
clipper_coords = []
history = []

lines = []
clippers = []

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
