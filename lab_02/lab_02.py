from tkinter import messagebox
from tkinter import *
from math import sqrt

from itertools import combinations

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

TASK = "Геометрические преобразования.\n\n" \
       "Нарисовать исходный рисунок (машинка). " \
       "Осуществить возможность его перемещения, " \
       "масштабирования и поворота."

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
        self.points.append([0.0, 0.0, 0.0])

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
                if next[0] == 0 and next[1] == 0 and next[2] == 0:
                    break
                start_point = next


def coord_sum(a, b):
    return (a[0] + b[0], a[1] + b[1])


def coord_dif(a, b):
    return (a[0] - b[0], a[1] - b[1])


def shift_car(sh):
    global car
    for i in range(len(car.points) - 1):
        res = coord_sum(car.points[i], sh)
        car.points[i][0] = res[0]
        car.points[i][1] = res[1]

def rotate(a, alpha, center):
    a = coord_dif(a, center)
    res = (cos(alpha) * a[0] - sin(alpha) * a[1],
           sin(alpha) * a[0] + cos(alpha) * a[1])
    res = coord_sum(res, center)
    return res

def rotate_car(alpha, center):
    global car
    with open("tmp.txt", 'w') as fout:
        for i in range(len(car.points) - 1):
            res = str(rotate(car.points[i][:-1], alpha, center))[1:-1]
            s1, s2 = str(res).split(',')
            line = s1 + ' ' + s2 + ' ' + str(car.points[i][2]) + '\n'
            fout.write(line)

def resize(a, k, center):
    a = coord_dif(a, center)
    res = (a[0] * k[0], a[1] * k[1])
    res = coord_sum(res, center)
    return res

def resize_car(k, center):
    global car
    for i in range(len(car.points) - 1):
        res = resize(car.points[i], k, center)
        car.points[i][0] = res[0]
        car.points[i][1] = res[1]
    canvas_win.delete('car')
    Car.draw_car(car)

def rsz_go(resize_x, resize_y, main_x, main_y):
    try:
        rx = float(resize_x.get())
        ry = float(resize_y.get())
        mx = - float(main_x.get())
        my = - float(main_y.get())

        resize_car([rx, ry], [mx, my])
    except:
        messagebox.showerror('Ошибка', "Некорректный ввод или пустой ввод")

def start():
    car.points.clear()
    canvas_win.delete('car')
    Car.get_car(car, "car2.txt")
    Car.draw_car(car)
    main_x.delete(0, END)
    main_y.delete(0, END)
    shift_x.delete(0, END)
    shift_y.delete(0, END)
    resize_x.delete(0, END)
    resize_y.delete(0, END)
    rotate_angle_y.delete(0, END)

# нахождение коэффициента масштабирования
def find_scale(dots):
    x_min = dots[0][0]
    y_min = dots[0][1]
    x_max = dots[0][0]
    y_max = dots[0][1]

    for dot in dots:
        if dot[0] < x_min:
            x_min = dot[0]
        if dot[1] < y_min:
            y_min = dot[1]
        if dot[0] > x_max:
            x_max = dot[0]
        if dot[1] > y_max:
            y_max = dot[1]

    k_x = max(abs(x_min), abs(x_max))
    k_y = max(abs(y_min), abs(y_max))

    return max(k_x, k_y)


# координаты точки из канвасовских в фактические
def to_coords(dot):
    x = (dot[0] - coord_center[0]) / m
    y = (- dot[1] + coord_center[1]) / m

    return [x, y]


# координаты точки из фактических в канвасовские
def to_canva(dot):
    global m
    x = coord_center[0] + dot[0] * m
    y = coord_center[1] - dot[1] * m

    return [x, y]


# добавление точки в множество
def add_dot():
    dot_win, dot_x, dot_y = dots_win()

    add_but = Button(dot_win, text="Добавить", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: read_dot(END, dot_x.get(), dot_y.get(), 0))
    add_but.place(x=40, y=120, relheight=0.15, relwidth=0.64)

    dot_win.mainloop()


# определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    read_dot(END, event.x, event.y, 1)


# откат
def undo():
    if len(actions) == 0:
        messagebox.showerror("Ошибка", "Разрешен возврат только на одно действие назад.")
        return

    if '+' in actions[0]:
        for act in actions[-1].split('+'):
            eval(act)
    actions.clear()


def draw_axes():
    canvas_win.create_line(0, size / 2, size - 2, size / 2, fill='grey',
                  width=1, arrow=LAST,
                  activefill='lightgreen',
                  arrowshape="10 20 6")
    canvas_win.create_line(size / 2, size, size / 2, 2, fill='grey',
                  width=1, arrow=LAST,
                  activefill='lightgreen',
                  arrowshape="10 20 6")

    s = int(size)
    for i in range(0, s, 50):
        canvas_win.create_line(i, s / 2 - 5, i, s / 2 + 5, fill='pink', width=2)
        canvas_win.create_line(i, 0, i, s, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(i, s // 2 + 20, text=f'{int((i - SIZE // 2) // 4)}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")
        canvas_win.create_line(s / 2 - 5, i, s / 2 + 5, i, fill='pink', width=2)
        canvas_win.create_line(0, i, s, i, fill='grey', width=1, dash=(1, 9))
        canvas_win.create_text(s // 2 - 20, i, text=f'{int((-(i - SIZE // 2)) // 4)}' if i - SIZE // 2 else '',
                               fill='grey', tag='coord', font="AvantGardeC 10")

    canvas_win.create_text(s - 20, s // 2 + 20, text='X', font="AvantGardeC 14", fill='grey')
    canvas_win.create_text(s // 2 + 20, 20, text='Y', font="AvantGardeC 14", fill='grey')


# Растягивание окна
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
        rotate_angle_y.place(x=33 * win_x, y=528 * win_y, width=235 * win_x, height=24 * win_y)

        rtt.place(x=33 * win_x, y=560 * win_y, width=235 * win_x, height=32 * win_y)

        # условие
        con.place(x=30 * win_x, y=640 * win_y, width=235 * win_x, height=28 * win_y)
        # откат
        und.place(x=30 * win_x, y=670 * win_y, width=235 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=30 * win_x, y=700 * win_y, width=235 * win_x, height=28 * win_y)


        coord_center = [size / 2, size / 2]

        canvas_win.delete('all')
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
rotate_angle_y = Entry(font="AvantGardeC 14", bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

# Список точек
dots_list = []
dots_list_copy = []


# Кнопки
sft = Button(text="Переместить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_dot())
rsz = Button(text="Масштабировать", font="AvantGardeC 14",
             borderwidth=0, command=lambda: rsz_go(resize_x, resize_y, main_x, main_y))
chg = Button(text="Изменить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_dot())
rtt = Button(text="Очистить", font="AvantGardeC 14",
                 borderwidth=0, command=lambda: del_all_dots(0))
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
pnt = Button(text="?", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание",
                                                                "Ключевая точка - точка, относительно которой "
                                                                "будет производиться поворот, масштабирование."))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: start())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())

win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
coord_center = [400, 400]  # центр координат (в координатах канваса)
actions = []  # возврат действия для undo
start_param = 0  # пока не было увеличения или уменьшения, чтобы при изменении размера окна не ехало

car = Car()
Car.get_car(car, "car2.txt")
# resizecar(2, [0, 0])
# Car.get_car(car, "tmp.txt")
# resize_car([1, 4], [0, 0])



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

win.mainloop()
