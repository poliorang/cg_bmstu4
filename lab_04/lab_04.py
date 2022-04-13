from tkinter import messagebox, ttk, colorchooser
from tkinter import *
from math import radians, cos, sin, fabs, floor, pi, sqrt
import colorutils as cu
import matplotlib.pyplot as plt
import numpy as np
import time

from bresenham_method import bresenham_circle, bresenham_ellipse
from mid_dot_method import mid_dot_circle, mid_dot_ellipse
from canon_method import canon_circle, canon_ellipse
from parametric_method import parametric_circle, parametric_ellipse
from draw import to_canva, to_coords, draw_axes, SIZE, undo

WIN_WIDTH = 1200
WIN_HEIGHT = 800

WIDTH = 100.0
PLUS = 1
MINUS = 0

NUMBER_OF_RUNS = 20
MAX_RADIUS = 10000
STEP = 1000
ITERATION = 4

TASK = "Алгоритмы построения окружностей.\n\n" \
       "Реализовать возможность построения " \
       "окружностей методами Брезенхема, средней точки, " \
       "канонического и параметрического уравнений и " \
       "сравнить время работы."

AUTHOR = "\n\nЕгорова Полина ИУ7-44Б"


def parse(option, option_figure):
    try:
        center_x = int(xc_entry.get())
        center_y = int(yc_entry.get())
        rad_x = float(rx_entry.get())
        rad_y = float(ry_entry.get())
        if option_figure == 1:
            rad_y = rad_x

    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    center = [center_x, center_y]
    radius = [rad_x, rad_y]

    parse_methods(center, option, radius, option_figure, figure_history)


def lib_method(center, rad, color):
    c_x, c_y = to_canva((center[0], center[1]))
    canvas_win.create_oval(c_x - rad[0], c_y - rad[1],
                           c_x + rad[0], c_y + rad[1],
                           outline=color.hex, tag='pixel')
    # figure_history.append()


def parse_methods(center, opt, radius, figure, history, draw=True):
    # print("Method = ", opt)
    color = cu.Color(current_color[0])

    if opt == 0:  # canon
        if figure == 0:
            canon_ellipse(canvas_win, center, radius, color, history, draw)
        elif figure == 1:
            canon_circle(canvas_win, center, radius[0], color, history, draw)

    elif opt == 1:  # param
        if figure == 1:
            parametric_circle(canvas_win, center, radius[0], color, history, draw)
        elif figure == 0:
            parametric_ellipse(canvas_win, center, radius, color, history, draw)

    elif opt == 2:  # bres
        if figure == 1:
            bresenham_circle(canvas_win, center, radius[0], color, history, draw)
        elif figure == 0:
            bresenham_ellipse(canvas_win, center, radius, color, history, draw)

    elif opt == 3:  # mid point
        if figure == 1:
            mid_dot_circle(canvas_win, center, radius[0], color, history, draw)
        elif figure == 0:
            mid_dot_ellipse(canvas_win, center, radius, color, history, draw)

    elif opt == 4:
        lib_method(center, radius, color)

    else:
        messagebox.showerror("Ошибка", "Неизвестный алгоритм")


def draw_point(ev_x, ev_y, point, click_):
    if len(point):
        global xc_entry, yc_entry

        if click_:
            x, y = ev_x, ev_y
        else:
            x, y = to_canva([point[0], point[1]])

        xc_entry.delete(0, END)
        yc_entry.delete(0, END)
        xc_entry.insert(0, "%d" % point[0])
        yc_entry.insert(0, "%d" % point[1])
        canvas_win.delete('dot1')
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='grey', fill='pink', activeoutline='lightgreen', width=2, tag='dot1')


def parse_spectra(opt, option_spectra, option_figure):
    try:
        center_x = int(xc_entry.get())
        center_y = int(yc_entry.get())

        if option_spectra == 0:
            rad_step = float(step_entry.get())
        if option_spectra == 1:
            rad_x_end = float(end_radius_x_entry.get())

        rad_x_start = float(start_radius_x_entry.get())
        rad_y_start = float(start_radius_y_entry.get())
        rad_count = int(count_entry.get())

    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    # количество, начальный радиус и шаг
    if option_spectra == 0:
        rad_x_end = float(rad_x_start + rad_step * rad_count)

    # количество, начальный радиус и конечный радиус
    elif option_spectra == 1:
        rad_step = int((rad_x_end - rad_x_start) / (rad_count - 1))
        print(rad_step)

    if rad_x_start > rad_x_end:
        messagebox.showerror("Ошибка", "Начальный радиус не может быть больше конечного")
        return

    if rad_step <= 0:
        messagebox.showerror("Ошибка", "Шаг радиуса должен быть выше нуля")
        return

    if rad_count <= 0:
        messagebox.showerror("Ошибка", "Количество должно быть больше нуля")
        return

    r_a = rad_x_start
    r_b = rad_y_start
    center = [center_x, center_y]


    spectra_history = []
    for i in range(rad_count):
        rad = [r_a, r_b]

        parse_methods(center, opt, rad, option_figure, spectra_history)

        r_a += rad_step
        r_b += rad_step
    figure_history.append(spectra_history)


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return
    point = to_coords([event.x, event.y])
    draw_point(event.x, event.y, point, 1)


# замер времени
def time_measure(option_figure):
    time_mes = []
    r_a = STEP
    r_b = STEP
    name = "эллипс"

    if option_figure == 1:
        r_a = STEP
        r_b = r_a
        name = "окружность"

    dot_c = [0, 0]

    for i in range(0, 4):
        time_start = [0] * (MAX_RADIUS // STEP)
        time_end = [0] * (MAX_RADIUS // STEP)

        for _ in range(NUMBER_OF_RUNS):
            r_a = STEP
            r_b = STEP

            nothing = []
            for iter in range(ITERATION):
                for k in range(MAX_RADIUS // STEP):
                    rad = [r_a, r_b]

                    time_start[k] += time.time()

                    parse_methods(dot_c, i, rad, option_figure, nothing, draw=False)

                    time_end[k] += time.time()

                    r_a += STEP
                    r_b += STEP

        size = len(time_start)
        res_time = list((time_end[j] / ITERATION - time_start[j] / ITERATION) / NUMBER_OF_RUNS for j in range(size))
        time_mes.append(res_time)

    rad_arr = list(i for i in range(0, MAX_RADIUS, STEP))
    plt.figure(figsize=(14, 6))

    plt.title(f"Фигура: {name}\nКоличество итераций при сравнении: {ITERATION}")

    plt.plot(rad_arr, time_mes[0], label="Каноническое\nуравнеие")
    plt.plot(rad_arr, time_mes[1], label="Параметрическое\nуравнение")
    plt.plot(rad_arr, time_mes[2], label="Брезенхем")
    plt.plot(rad_arr, time_mes[3], label="Алгоритм\nсредней точки")

    plt.xticks(np.arange(STEP, MAX_RADIUS, STEP))
    plt.legend()

    plt.ylabel("Время")
    plt.xlabel("Величина радиуса")

    plt.show()


# изменение цвета фона
def change_bg_color():
    global canvas_bg
    canvas_bg = colorchooser.askcolor()
    canvas_win.configure(bg=cu.Color(canvas_bg[1]))


# изменение цвета отрезка
def choose_line_color():
    global current_color
    current_color = colorchooser.askcolor()


# при нажатии буквы q будет переключать радиобаттон (для быстрого задания концов отрезка)
def change_option_click(event):
    global option
    if option.get() == 1:
        option.set(2)
    elif option.get() == 2:
        option.set(1)


#  очистка канваса
def clean_canvas():
    figure_history.append([])
    canvas_win.delete('pixel', 'coord')
    draw_axes(canvas_win, xy_current, size)


# если строим окружность, задать радиус по игреку будет невозможно
def block_second_radius(opt_figure):
    rx_entry.configure(state=NORMAL)
    ry_entry.configure(state=NORMAL)
    start_radius_y_entry.configure(state=NORMAL)
    end_radius_x_entry.configure(state='readonly')

    if opt_figure == 0:  # эллипс
        step_entry.configure(state=NORMAL)
        end_radius_x_entry.configure(state='readonly')
        start_radius_y_entry.configure(state=NORMAL)
        option_spectra.set(0)
    if opt_figure == 1:  # окружность
        ry_entry.configure(state='readonly')
        start_radius_y_entry.configure(state='readonly')


# блок полей для построения спектра
def block_criteria(opt_spectra, opt_figure):
    step_entry.configure(state = NORMAL)
    end_radius_x_entry.configure(state = 'readonly')

    if opt_spectra == 1:  # спектр по радиусу
        if opt_figure == 1:  # если это круг (то выйдет)
            step_entry.configure(state = 'readonly')
            end_radius_x_entry.configure(state = NORMAL)
    if opt_spectra == 0:  # спектр по шагу
        step_entry.configure(state = NORMAL)
        end_radius_x_entry.configure(state='readonly')


# растягивание окна
def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size

        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)

        size = SIZE * win_k
        m = size / (2 * border + ten_percent)

        canvas_win.place(x=300 * win_x, y=0 * win_y, width=size, height=size)

        # координаты
        center_lbl.place(x=33 * win_x, y=28 * win_y, width=235 * win_x, height=24 * win_y)
        xc_lbl.place(x=33 * win_x, y=58 * win_y, width=110 * win_x, height=18 * win_y)
        yc_lbl.place(x=158 * win_x, y=58 * win_y, width=110 * win_x, height=18 * win_y)
        xc_entry.place(x=33 * win_x, y=77 * win_y, width=110 * win_x, height=20 * win_y)
        yc_entry.place(x=158 * win_x, y=77 * win_y, width=110 * win_x, height=20 * win_y)

        # выбор метода
        method_lbl.place(x=33 * win_x, y=113 * win_y, width=235 * win_x, height=23 * win_y)
        method_combo.place(x=33 * win_x, y=139 * win_y, width=235 * win_x, height=25 * win_y)

        # выбор фигуры
        circle.place(x=33 * win_x, y=174 * win_y, width=110 * win_x, height=23 * win_y)
        ellipse.place(x=170 * win_x, y=174 * win_y, width=110 * win_x, height=23 * win_y)

        # ввод радиуса
        radius_lbl.place(x=33 * win_x, y=210 * win_y, width=235 * win_x, height=24 * win_y)
        rx_lbl.place(x=33 * win_x, y=240 * win_y, width=110 * win_x, height=18 * win_y)
        ry_lbl.place(x=158 * win_x, y=240 * win_y, width=110 * win_x, height=18 * win_y)
        rx_entry.place(x=33 * win_x, y=259 * win_y, width=110 * win_x, height=20 * win_y)
        ry_entry.place(x=158 * win_x, y=259 * win_y, width=110 * win_x, height=20 * win_y)

        # построить
        bld.place(x=33 * win_x, y=290 * win_y, width=235 * win_x, height=25 * win_y)

        # построить пучок
        spectra_lbl.place(x=33 * win_x, y=345 * win_y, width=235 * win_x, height=24 * win_y)
        count_lbl.place(x=33 * win_x, y=375 * win_y, width=110 * win_x, height=18 * win_y)
        count_entry.place(x=158 * win_x, y=375 * win_y, width=110 * win_x, height=20 * win_y)

        start_radius_lbl.place(x=33 * win_x, y=400 * win_y, width=235 * win_x, height=18 * win_y)
        start_radius_x_entry.place(x=33 * win_x, y=420 * win_y, width=110 * win_x, height=20 * win_y)
        start_radius_y_entry.place(x=158 * win_x, y=420 * win_y, width=110 * win_x, height=20 * win_y)

        end_radius_lbl.place(x=41 * win_x, y=445 * win_y, width=100 * win_x, height=18 * win_y)
        end_radius_x_entry.place(x=41 * win_x, y=465 * win_y, width=100 * win_x, height=20 * win_y)
        end_radio.place(x=8 * win_x, y=448 * win_y)

        step_lbl.place(x=168 * win_x, y=445 * win_y, width=100 * win_x, height=18 * win_y)
        step_entry.place(x=168 * win_x, y=465 * win_y, width=100 * win_x, height=20 * win_y)
        step_radio.place(x=145 * win_x, y=448 * win_y)

        spc.place(x=33 * win_x, y=495 * win_y, width=235 * win_x, height=25 * win_y)

        # сравнения
        # measure_lbl.place(x=33 * win_x, y=555 * win_y, width=235 * win_x, height=24 * win_y)
        tim.place(x=33 * win_x, y=630 * win_y, width=235 * win_x, height=28 * win_y)
        # grd.place(x=157 * win_x, y=582 * win_y, width=110 * win_x, height=25 * win_y)

        # условие
        con.place(x=33 * win_x, y=600 * win_y, width=235 * win_x, height=28 * win_y)
        # цвет фона и отрезка
        clr.place(x=33 * win_x, y=660 * win_y, width=110 * win_x, height=28 * win_y)
        bgc.place(x=157 * win_x, y=660 * win_y, width=110 * win_x, height=28 * win_y)
        # откат
        und.place(x=33 * win_x, y=690 * win_y, width=109 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=157 * win_x, y=690 * win_y, width=109 * win_x, height=28 * win_y)

        # coord_center = [size / 2, size / 2]

        block_criteria(option, option_spectra)
        block_second_radius(option_spectra)
        canvas_win.delete('all')
        draw_axes(canvas_win, xy_current, size)


# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #4")

# переменные для радиобаттонов
option = IntVar()
option.set(0)

option_spectra = IntVar()
option_spectra.set(0)

# Канвас
canvas_bg = ((255, 255, 255), "#ffffff")
canvas_win = Canvas(win, bg=cu.Color(canvas_bg[1]))

# Подписи функционала
center_lbl = Label(text="Центр построения", bg='pink', font="AvantGardeC 14", fg='black')

xc_lbl = Label(text="Xс", bg='lightgrey', font="AvantGardeC 14", fg='black')
yc_lbl = Label(text="Yс", bg='lightgrey', font="AvantGardeC 14", fg='black')
xc_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')
yc_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')
xc_entry.insert(END, 0)
yc_entry.insert(END, 0)

method_lbl = Label(text="Алгоритм", bg='pink', font="AvantGardeC 14", fg='black')
method_combo = ttk.Combobox(win, state='readonly', values=["Каноническое уравнение", "Параметрическое уравнение",
                                                           "Алгоритм Брезенхема", "Алгоритм средней точки", "Библиотечный"])
method_combo.current(0)

ellipse = Radiobutton(variable=option, value=0, text='Эллипс',
                      bg="grey", activebackground="grey", highlightbackground="grey",
                      command = lambda : block_second_radius(option.get()))
circle = Radiobutton(variable=option, value=1, text='Окружность',
                     bg="grey", activebackground="grey", highlightbackground="grey",
                     command = lambda : block_second_radius(option.get()))

step_radio = Radiobutton(variable=option_spectra, value=0,
                     bg="grey", activebackground="grey", highlightbackground="grey",
                     command = lambda : block_criteria(option_spectra.get(), option.get()))
end_radio = Radiobutton(variable=option_spectra, value=1,
                     bg="grey", activebackground="grey", highlightbackground="grey",
                     command = lambda : block_criteria(option_spectra.get(), option.get()))

radius_lbl = Label(text="Радиус фигуры", bg='pink', font="AvantGardeC 14", fg='black')
rx_lbl = Label(text="Rx", bg='lightgrey', font="AvantGardeC 14", fg='black')
ry_lbl = Label(text="Ry", bg='lightgrey', font="AvantGardeC 14", fg='black')
rx_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')
ry_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                 borderwidth=0, insertbackground='black', justify='center')
rx_entry.insert(END, 100)
ry_entry.insert(END, 100)

spectra_lbl = Label(text="Спектр", bg='pink', font="AvantGardeC 14", fg='black')
step_lbl = Label(text="Шаг", bg='lightgrey', font="AvantGardeC 14", fg='black')
step_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                   borderwidth=0, insertbackground='black', justify='center')

start_radius_lbl = Label(text="Нач. радиус", bg='lightgrey', font="AvantGardeC 14", fg='black')
start_radius_x_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                           borderwidth=0, insertbackground='black', justify='center')
start_radius_y_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                           borderwidth=0, insertbackground='black', justify='center')

end_radius_lbl = Label(text="Кон. радиус", bg='lightgrey', font="AvantGardeC 14", fg='black')
end_radius_x_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                         borderwidth=0, insertbackground='black', justify='center')

count_lbl = Label(text="Количество", bg='lightgrey', font="AvantGardeC 14", fg='black')
count_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                    borderwidth=0, insertbackground='black', justify='center')

step_entry.insert(END, 20)
count_entry.insert(END, 10)
start_radius_x_entry.insert(END, 50)
start_radius_y_entry.insert(END, 50)
end_radius_x_entry.insert(END, 300)

# spectra_lbl = Label(text="Построить пучок", bg='pink', font="AvantGardeC 14", fg='black')
measure_lbl = Label(text="Сравнить", bg='pink', font="AvantGardeC 14", fg='black')

# Список точек
figure_history = []
xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
              0, 50, 100, 150, 200, 250, 300, 350, 400]


# Кнопки
bld = Button(text="Построить фигуру", font="AvantGardeC 14",
             borderwidth=0, command=lambda: parse(method_combo.current(), option.get()))
sct = Button(text="Построить", font="AvantGardeC 14",
             borderwidth=0)
tim = Button(text="Сравнить время", font="AvantGardeC 14",
             borderwidth=0, command=lambda: time_measure(option.get()))
# grd = Button(text="Ступенчатость", font="AvantGardeC 12",
#              borderwidth=0, command=lambda: steps_go())
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK + AUTHOR))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: clean_canvas())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo(canvas_win, figure_history))
spc = Button(text="Построить спектр", font="AvantGardeC 14",
             borderwidth=0, command=lambda: parse_spectra(method_combo.current(),
                                                                 option_spectra.get(), option.get()))
clr = Button(text="Цвет фигуры", font="AvantGardeC 12",
             borderwidth=0, command=lambda: choose_line_color())
bgc = Button(text="Цвет фона", font="AvantGardeC 12",
             borderwidth=0, command=lambda: change_bg_color())

win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
m_board = 1  # коэффициент масштабирования при изменении масштаба канваса

current_color = (0, 0, 0)

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
