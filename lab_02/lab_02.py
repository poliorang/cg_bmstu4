import copy
from tkinter import messagebox
from tkinter import *
from math import degrees, radians, cos, sin

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


class Car:
    def __init__(self):
        self.points = []  # двумерный массив, хранятся координаты x и y точек,
                          # 1, если точка соединена со следующей в массиве, 0 - иначе

    def get_car(self, filename):
        self.points.clear()
        with open(filename, 'r') as f:
            line = f.readline()
            while line:
                if len(line) != 0 and line != '\n':
                    dot = list(map(float, line.split()))
                    if len(dot) != 3:
                        messagebox.showerror("Error", "Ошибка при считывании координат точек из файла")
                        self.points.clear()
                        return
                    self.points.append(dot)
                    line = f.readline()
        self.points.append([-0.0, -0.0, 0.0])

    def draw_car(self):
        start_point = to_canva(self.points[0])
        for i in range(len(self.points) - 1):
            prev = to_canva(self.points[i][:-1])
            prev.append(self.points[i][2])
            next = to_canva(self.points[i + 1][:-1])
            next.append(self.points[i][2])
            if prev[2] == 1:
                canvas_win.create_line(prev[0], prev[1], next[0], next[1], fill='black', tag='car')
            else:
                canvas_win.create_line(prev[0], prev[1], start_point[0], start_point[1], fill='black', tag='car')
                if next[0] == -0.0 and next[1] == -0.0 and next[2] == 0.0:
                    break
                start_point = next


def coord_sum(a, b):
    return a[0] + b[0], a[1] + b[1]


def coord_dif(a, b):
    return a[0] - b[0], a[1] - b[1]


# смещение рисунка
def shift_car(shft):
    global car
    shft = [shft[0] / m_board, shft[1] / m_board]
    for i in range(len(car.points) - 1):
        res = coord_sum(car.points[i], shft)
        car.points[i][0] = res[0]
        car.points[i][1] = res[1]
    # check_abroad()
    canvas_win.delete('car')
    Car.draw_car(car)

# связывает кнопку смещения и функцию
def sft_go(shift_x, shift_y):
    try:
        shx = float(shift_x.get())
        shy = float(shift_y.get())
        save_state()
        shift_car([shx, shy])
    except ValueError:
        messagebox.showerror('Ошибка', "Некорректный ввод или пустой ввод")

# поворот точки
def rotate(a, alpha, center):
    alpha = radians(alpha)
    a = coord_dif(a, center)
    res = (cos(alpha) * a[0] - sin(alpha) * a[1],
           sin(alpha) * a[0] + cos(alpha) * a[1])
    res = coord_sum(res, center)

    return res


# поворот рисунка
def rotate_car(alpha, center):
    global car
    for i in range(len(car.points) - 1):
        res = rotate(car.points[i], alpha, center)
        car.points[i][0] = res[0]
        car.points[i][1] = res[1]
    canvas_win.delete('car')
    Car.draw_car(car)


# связывает кнопку поворота и функцию
def rtt_go(rotate_angle, main_x, main_y):
    try:
        angle = float(rotate_angle.get())
    except ValueError:
        messagebox.showerror('Ошибка', "Неверное значение угла")
        return
    try:
        mx = float(main_x.get())
        my = float(main_y.get())

        global main_point
        main_point = [mx, my]
        draw_main_point(0, 0, MINUS)
        save_state()
        rotate_car(angle, [main_point[0] / m_board, main_point[1] / m_board])
    except ValueError:
        messagebox.showerror('Ошибка', "Некорректные координаты ключевой точки")


# сохранить в историю положение рисунка
def save_state():
    global car_history, xy_history, car
    tmp = Car()
    for point in car.points:
        tmp.points.append(copy.deepcopy(point))
    car_history.append(tmp)
    xy_history.append(copy.deepcopy(xy_current))
    main_history.append(main_point)
    # print(tmp.points)


# изменение размера для точки
def resize(a, k, center):
    a = coord_dif(a, center)
    res = (a[0] * k[0], a[1] * k[1])
    res = coord_sum(res, center)
    return res


# изменение размера для рисунка
def resize_car(k, center):
    global car
    for i in range(len(car.points) - 1):
        res = resize(car.points[i], k, center)
        car.points[i][0] = res[0]
        car.points[i][1] = res[1]
    canvas_win.delete('car')
    Car.draw_car(car)


# связывание кнопку масшт и функцию
def rsz_go(resize_x, resize_y, main_x, main_y):
    try:
        rx = float(resize_x.get())
        ry = float(resize_y.get())
    except ValueError:
        messagebox.showerror('Ошибка', "Некорректные коэффициенты масштабироваия")
        return
    try:
        mx = float(main_x.get())
        my = float(main_y.get())

        global main_point
        main_point = [mx, my]
        draw_main_point(0, 0, MINUS)
        save_state()
        resize_car([rx, ry], [main_point[0] / m_board, main_point[1] / m_board])
    except ValueError:
        messagebox.showerror('Ошибка', "Некорректные координаты ключевой точки")


def check_abroad():
    global edge, k_board, main_point, m_board
    for point in car.points:
        if point[0] < -edge or point[1] < -edge or point[0] > edge or point[1] > edge:
            if len(main_point) == 0:
                main_point = [0, 0]
            # print('main ', main_point)
            resize_car([0.5, 0.5], [0.0, 0.0])
            k_board //= 2
            m_board *= 2
            canvas_win.delete('coord')
            draw_axes()


# def check_zero():
#     if m_board != 1 and

def draw_main_point(ev_x, ev_y, param):
    if len(main_point):
        canvas_win.delete('dot')

        main_x.delete(0, END)
        main_y.delete(0, END)
        main_x.insert(0, "%.1f" % main_point[0])
        main_y.insert(0, "%.1f" % main_point[1])

        if param:
            x, y = ev_x, ev_y
        else:
            x, y = to_canva([main_point[0] / m_board, main_point[1] / m_board])
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                               outline='grey', fill='pink', activeoutline='lightgreen', width=2, tag='dot')


def start():
    global k_board, m_board, car_history, xy_history, xy_current
    save_state()

    car.points.clear()
    main_point.clear()

    k_board = 4
    m_board = 1
    canvas_win.delete('all')

    xy_current = xy_start.copy()
    draw_axes()

    Car.get_car(car, "car2.txt")
    Car.draw_car(car)

    main_x.delete(0, END)
    main_y.delete(0, END)
    shift_x.delete(0, END)
    shift_y.delete(0, END)
    resize_x.delete(0, END)
    resize_y.delete(0, END)
    rotate_angle.delete(0, END)


# координаты точки из канвасовских в фактические
def to_coords(dot):
    x = (dot[0] - coord_center[0]) / m * m_board
    y = (- dot[1] + coord_center[1]) / m * m_board

    # print(x, y)
    return [x, y]


# координаты точки из фактических в канвасовские
def to_canva(dot):
    global m
    x = coord_center[0] + dot[0] * m
    y = coord_center[1] - dot[1] * m

    # print(x, y)
    return [x, y]


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    global main_point
    main_point = to_coords([event.x, event.y])

    draw_main_point(event.x, event.y, PLUS)


# откат
def undo():
    if len(car_history) == 0:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    global xy_current, main_point
    xy_current = xy_history[-1]
    canvas_win.delete('car', 'coord', 'dot')
    Car.draw_car(car_history[-1])

    main_point = main_history[-1]
    draw_main_point(0, 0, MINUS)
    draw_axes()

    car_history.pop()
    xy_history.pop()
    main_history.pop()


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
        # canvas_win.create_text(i, s // 2 + 20, text=f'{"%.2f" % float((i - SIZE // 2) // k_board)}' if i - SIZE // 2 else '',
        #                        fill='grey', tag='coord', font="AvantGardeC 10")
        canvas_win.create_text(i, s // 2 + 20, text=f'{"%.2f" % xy_current[j]}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

        canvas_win.create_line(s / 2 - 5, i, s / 2 + 5, i, fill='pink', width=2)
        canvas_win.create_line(0, i, s, i, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(s // 2 - 20, i, text=f'{"%.2f" % xy_current[j]}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

        j += 1

    canvas_win.create_text(s - 20, s // 2 + 20, text='X', font="AvantGardeC 14", fill='grey')
    canvas_win.create_text(s // 2 + 20, 20, text='Y', font="AvantGardeC 14", fill='grey')


# растягивание окна
def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size, coord_center, main_point

        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)

        size = SIZE * win_k
        m = size / (2 * border + ten_percent)

        canvas_win.place(x=300 * win_x, y=0 * win_y, width=size, height=size)

        # ключевая точка
        center_lbl.place(x=33 * win_x, y=18 * win_y, width=215 * win_x, height=24 * win_y)
        main_x_lbl.place(x=33 * win_x, y=52 * win_y, width=110 * win_x, height=20 * win_y)
        main_y_lbl.place(x=158 * win_x, y=52 * win_y, width=110 * win_x, height=20 * win_y)
        main_x.place(x=33 * win_x, y=80 * win_y, width=110 * win_x, height=24 * win_y)
        main_y.place(x=158 * win_x, y=80 * win_y, width=110 * win_x, height=24 * win_y)

        pnt.place(x=252 * win_x, y=18 * win_y, width=16 * win_x, height=24 * win_y)

        # сдвиг
        shift_lbl.place(x=33 * win_x, y=140 * win_y, width=235 * win_x, height=24 * win_y)

        shift_x_lbl.place(x=33 * win_x, y=174 * win_y, width=110 * win_x, height=20 * win_y)
        shift_y_lbl.place(x=158 * win_x, y=174 * win_y, width=110 * win_x, height=20 * win_y)
        shift_x.place(x=33 * win_x, y=202 * win_y, width=110 * win_x, height=24 * win_y)
        shift_y.place(x=158 * win_x, y=202 * win_y, width=110 * win_x, height=24 * win_y)

        sft.place(x=33 * win_x, y=233 * win_y, width=235 * win_x, height=32 * win_y)

        # масштабирование
        resize_lbl.place(x=33 * win_x, y=301 * win_y, width=235 * win_x, height=24 * win_y)
        resize_x_lbl.place(x=33 * win_x, y=335 * win_y, width=110 * win_x, height=20 * win_y)
        resize_y_lbl.place(x=158 * win_x, y=335 * win_y, width=110 * win_x, height=20 * win_y)
        resize_x.place(x=33 * win_x, y=363 * win_y, width=110 * win_x, height=24 * win_y)
        resize_y.place(x=158 * win_x, y=363 * win_y, width=110 * win_x, height=24 * win_y)

        rsz.place(x=33 * win_x, y=394 * win_y, width=235 * win_x, height=32 * win_y)

        # поворот
        rotate_lbl.place(x=33 * win_x, y=464 * win_y, width=235 * win_x, height=24 * win_y)
        rotate_angle_lbl.place(x=33 * win_x, y=498 * win_y, width=235 * win_x, height=22 * win_y)
        rotate_angle.place(x=33 * win_x, y=528 * win_y, width=235 * win_x, height=24 * win_y)

        rtt.place(x=33 * win_x, y=560 * win_y, width=235 * win_x, height=32 * win_y)

        # условие
        con.place(x=30 * win_x, y=640 * win_y, width=235 * win_x, height=28 * win_y)
        # откат
        und.place(x=30 * win_x, y=670 * win_y, width=235 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=30 * win_x, y=700 * win_y, width=235 * win_x, height=28 * win_y)


        # изменение размера
        pls.place(x=30 * win_x, y=600 * win_y, width=110 * win_x, height=24 * win_y)
        mns.place(x=158 * win_x, y=600 * win_y, width=110 * win_x, height=24 * win_y)

        coord_center = [size / 2, size / 2]

        canvas_win.delete('all')
        draw_axes()
        draw_main_point(0, 0, MINUS)
        Car.draw_car(car)


def change_size(plus_or_minus):
    global k_board, m_board, xy_current, main_point
    save_state()
    canvas_win.delete('coord', 'car', 'dot')

    if plus_or_minus == 0:
        # k_board //= 2
        m_board *= 2
        xy_current = [xy_current[i] * 2 for i in range(len(xy_current))]
        resize_car([0.5, 0.5], [0.0, 0.0])
    else:
        # k_board *= 2
        m_board /= 2
        xy_current = [xy_current[i] / 2 for i in range(len(xy_current))]
        resize_car([2, 2], [0.0, 0.0])

    draw_main_point(0, 0, MINUS)
    draw_axes()
    Car.draw_car(car)

# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #2")

# Канвас
canvas_win = Canvas(win, bg="#ffffff")

# Подписи функционала
center_lbl = Label(text="Ключевая точка", bg='pink', font="AvantGardeC 14", fg='black')
shift_lbl = Label(text="Перемещение", bg='pink', font="AvantGardeC 14", fg='black')
rotate_lbl = Label(text="Поворот", bg='pink', font="AvantGardeC 14", fg='black')
resize_lbl = Label(text="Масштабирование", bg='pink', font="AvantGardeC 14", fg='black')

# Поля ввода
main_x_lbl = Label(text="X", bg='lightgrey', font="AvantGardeC 14", fg='black')
main_y_lbl = Label(text="Y", bg='lightgrey', font="AvantGardeC 14", fg='black')
main_x = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
main_y = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

shift_x_lbl = Label(text="dx", bg='lightgrey', font="AvantGardeC 14", fg='black')
shift_y_lbl = Label(text="dy", bg='lightgrey', font="AvantGardeC 14", fg='black')
shift_x = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
shift_y = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

resize_x_lbl = Label(text="kx", bg='lightgrey', font="AvantGardeC 14", fg='black')
resize_y_lbl = Label(text="ky", bg='lightgrey', font="AvantGardeC 14", fg='black')
resize_x = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
resize_y = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

rotate_angle_lbl = Label(text="Угол в градусах", bg='lightgrey', font="AvantGardeC 14", fg='black')
rotate_angle = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

# Список точек
main_point = []
car_history = []
xy_history = []
xy_start = [-100.00, -87.50, -75.00, -62.50, -50.00, -37.50, -25.00, -12.50,
            0.00, 12.50, 25.00, 37.50, 50.00, 62.50, 75.00, 87.50, 100.00]
xy_current = [-100.00, -87.50, -75.00, -62.50, -50.00, -37.50, -25.00, -12.50,
            0.00, 12.50, 25.00, 37.50, 50.00, 62.50, 75.00, 87.50, 100.00]
main_history = []


# Кнопки
sft = Button(text="Переместить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: sft_go(shift_x, shift_y))
rsz = Button(text="Масштабировать", font="AvantGardeC 14",
             borderwidth=0, command=lambda: rsz_go(resize_x, resize_y, main_x, main_y))
rtt = Button(text="Повернуть", font="AvantGardeC 14",
             borderwidth=0, command=lambda: rtt_go(rotate_angle, main_x, main_y))
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
pnt = Button(text="?", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Точка", MAIN_POINT))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: start())
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
actions = []  # возврат действия для undo
edge = 100 # максимальная видимая координата на канвасе, но в координатах сетки
k_board = 4
m_board = 1

car = Car()
Car.get_car(car, "car2.txt")

canvas_win.bind('<1>', click)
win.bind('<Right>', lambda event: shift_car((1 * win_k, 0)))
win.bind('<Left>', lambda event: shift_car((-1 * win_k, 0)))
win.bind('<Up>', lambda event: shift_car((0, 1 * win_k)))
win.bind('<Down>', lambda event: shift_car((0, -1 * win_k)))
win.bind('<Command-Left>', lambda event: rotate_car(2, (0, 0)))
win.bind('<Command-Right>', lambda event: rotate_car(-2, (0, 0)))

# Меню
menu = Menu(win)
add_menu = Menu(menu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', TASK + AUTHOR))
add_menu.add_command(label='Выход', command=exit)
menu.add_cascade(label='Help', menu=add_menu)
win.config(menu=menu)

win.bind("<Configure>", config)

win.mainloop()
