from tkinter import Tk, Button, Label, Entry, END, Listbox, Canvas
from tkinter import messagebox
from tkinter import *
from math import sqrt

from itertools import combinations

coord_center = [400, 400]
actions = []

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

TASK = "На плоскости задано множество из N точек. Определить радиус и центр такой окружности, " \
       "проходящей через ровно три различные точки заданного множества точек на плоскости, " \
       "что минимальна разность количеств точек, лежащих внутри и вне окружности.\n\n"

AUTHOR = "Егорова Полина ИУ7-44Б"


# Лежат ли все точки на одной прямой
def on_same_line(dots_list):
    one_line = 1
    for three in combinations(dots_list, 3):
        ax, ay = three[0][0], three[0][1]
        bx, by = three[1][0], three[1][1]
        cx, cy = three[2][0], three[2][1]

        try:
            if (cx - ax) / (bx - ax) != (cy - ay) / (by - ay):
                one_line = 0
        except ZeroDivisionError:
            one_line = 0

    return one_line


# Расстояние между точками
def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Окна для ввода или изменения координат точки
def dots_win():
    dot_win = Tk()
    dot_win.title("Координаты точки")
    dot_win['bg'] = "grey"
    dot_win.geometry("265x200+400+250")
    dot_win.resizable(False, False)

    dot_x_label = Label(dot_win, text="X", bg="pink", font="AvantGardeC 14", fg='black')
    dot_x_label.place(x=40, y=30, relheight=0.15, relwidth=0.3)
    dot_x = Entry(dot_win, font="AvantGardeC 14", bg='white', fg='black',
                  borderwidth=0, insertbackground='black')
    dot_x.focus()
    dot_x.place(x=40, y=70, relheight=0.15, relwidth=0.3)

    dot_y_label = Label(dot_win, text="Y", bg="pink", font="AvantGardeC 14", fg='black')
    dot_y_label.place(x=130, y=30, relheight=0.15, relwidth=0.3)
    dot_y = Entry(dot_win, font="AvantGardeC 14", bg='white', fg='black',
                  borderwidth=0, insertbackground='black')
    dot_y.place(x=130, y=70, relheight=0.15, relwidth=0.3)

    return dot_win, dot_x, dot_y


# Окно для вывода текстового ответа
def answer_win(center, radius, diff, count_inside, count_outside, onside):
    ans_win = Tk()
    ans_win.title("Ответ")
    ans_win['bg'] = "grey"
    ans_win.geometry("680x200+400+660")
    ans_win.resizable(False, False)

    ans_label = Label(ans_win,
                      text="Окружность с центром в точке (%.1f; %.1f) и радиусом %.1f\n"
                           "Окружность проходит через точки (%.1f; %.1f), (%.1f; %.1f), (%.1f; %.1f)\n\n"
                           "Количество точек внутри окружности  ->  %d\n"
                           "Количество точек вне окружности  ->  %d\n"
                           "Разница количеств  ->  %d" % (center[0], center[1], radius, onside[0][0], onside[0][1],
                                                        onside[1][0], onside[1][1], onside[2][0], onside[2][1],
                                                        count_inside, count_outside, diff),
                      bg="pink", justify='left', font="AvantGardeC 14", fg='black')
    ans_label.place(x=40, y=30)


# Функция для нахождения коэффициента масштабирования
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


def draw_all_dots(dots, color, color_active):
    for dot in dots:
        x0, y0 = to_canva(dot)
        print(x0, y0, coord_center)
        x1, y1 = (x0 - 2), (y0 - 2)
        x2, y2 = (x0 + 2), (y0 + 2)

        canvas_win.create_oval(x1, y1, x2, y2,
                               outline=color, fill=color, activeoutline=color_active, width=3, tag='dot')

        canvas_win.create_text(x1 + 15, y1 + 15, tag='text',
                               text="(%.1f; %.1f)" % (dot[0], dot[1]), font="AvantGardeC 9", fill='black')


def draw_circle(center, radius):
    c_x_1, c_y_1 = to_canva((center[0] - radius, center[1] - radius))
    c_x_2, c_y_2 = to_canva((center[0] + radius, center[1] + radius))
    cir = [c_x_1, c_y_1, c_x_2, c_y_2]
    canvas_win.create_oval(*cir, activeoutline='lightgreen', outline='grey', width=3, tag='oval')

    return [center, radius]


# Функция для чтения координат точки, их обработки и добавления в множество
def read_dot(place, dot_x, dot_y, canva_or_hand):
    try:
        global win_k, m

        if canva_or_hand:
            canva_x_y = [float(dot_x), float(dot_y)]
            fact_x_y = to_coords(canva_x_y)
        else:
            fact_x_y = [float(dot_x), float(dot_y)]
            canva_x_y = to_canva(fact_x_y)

        draw_all_dots([(fact_x_y)], 'pink', 'lightgreen')
        points = canvas_win.find_withtag('dot')
        dot_text = canvas_win.find_withtag('text')

        if place != END:  # изменить точку
            # получение из листбокса координат точки
            num1 = str(dots_block.get(place))[5:-1].split(';')
            num1_1 = float(num1[0])
            num1_2 = float(num1[1][1:])

            # найти точку для удаления с канваса, соотнеся координаты из листбокса и с канваса
            for dot in dot_text:
                # получение координат точки как объекта канваса
                num2 = str(canvas_win.itemconfig(dot)['text'][-1][1:-1]).split(';')
                num2_1 = float(num2[0])
                num2_2 = float(num2[1][1:])

                if num1_1 == num2_1 and num1_2 == num2_2:
                    canvas_win.delete(dot)
                    canvas_win.delete(points[dot_text.index(dot)])
                    break

            tmp_x, tmp_y = dots_list[place][0], dots_list[place][1]

            dot_str = "%d : (%-3.1f; %-3.1f)" % (place + 1, tmp_x, tmp_y)

            dots_block.delete(place)
            dots_list.pop(place)
            fact_x_y.append(place + 1)
            dots_list.insert(place, fact_x_y)

            new_d = canvas_win.find_withtag('dot')[-1]
            new_t = canvas_win.find_withtag('text')[-1]
            actions.append(f'canvas_win.delete({new_t})+'
                           f'canvas_win.delete({new_d})+'
                           # f'dots_list.pop({place})+'
                           f'dots_block.delete({place})+'
                           f'dots_block.insert{place, dot_str}+'
                           f'draw_all_dots{[(tmp_x, tmp_y)], "pink", "lightgreen"}+'
                           f'actions.pop(-1)+')


        else:  # добавить новую точку
            place = len(dots_list)
            fact_x_y.append(place + 1)
            dots_list.append(fact_x_y)

            actions.append(f'canvas_win.delete({points[-1]})+dots_list.pop({place})+dots_block.delete({place}, END)+'
                           f'canvas_win.delete({dot_text[-1]})+actions.pop(-1)+')

        dot_str = "%d : (%-3.1f; %-3.1f)" % (place + 1, fact_x_y[0], fact_x_y[1])
        dots_block.insert(place, dot_str)

        if fact_x_y[0] > size / m or fact_x_y[0] > size / m:
            border = find_scale(dots_list)
            ten_percent = size / 100 * 10
            m = size / (2 * border + ten_percent)
            start_param = 1

            canvas_win.delete("all")
            draw_axies()
            draw_all_dots(dots_list, 'pink', 'lightgreen')
            if start_param:
                draw_circle(*circle)

    except:
       messagebox.showerror("Ошибка", "Неверно введены координаты точки")


# Функция для добавления точки в множество
def add_dot():
    dot_win, dot_x, dot_y = dots_win()

    add_but = Button(dot_win, text="Добавить", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: read_dot(END, dot_x.get(), dot_y.get(), 0))
    add_but.place(x=40, y=120, relheight=0.15, relwidth=0.64)

    dot_win.mainloop()


# Функция для изменения координат точки выбранного множества
def change_dot():
    try:
        place = dots_block.curselection()[0]
    except:
        messagebox.showerror("Ошибка", "Не выбрана точка")
        return

    dot_win, dot_x, dot_y = dots_win()

    add_but = Button(dot_win, text="Изменить", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: read_dot(place, dot_x.get(), dot_y.get(), 0))
    add_but.place(x=40, y=120, relheight=0.15, relwidth=0.64)

    dot_win.mainloop()


# Функция для удаления точки
def del_dot():
    try:
        place = dots_block.curselection()[0]

        points = canvas_win.find_withtag('dot')
        dot_text = canvas_win.find_withtag('text')

        coords = dots_list.pop(place)

        actions.append(f'read_dot{END, coords[0], coords[1], 0}+actions.pop(-1)+actions.pop(-1)')

        # получение из листбокса координат точки
        num1 = str(dots_block.get(place))[5:-1].split(';')
        num1_1 = float(num1[0])
        num1_2 = float(num1[1][1:])

        # найти точку для удаления с канваса, соотнеся координаты из листбокса и с канваса
        for dot in dot_text:
            # получение координат точки как объекта канваса
            num2 = str(canvas_win.itemconfig(dot)['text'][-1][1:-1]).split(';')
            num2_1 = float(num2[0])
            num2_2 = float(num2[1][1:])

            if num1_1 == num2_1 and num1_2 == num2_2:
                canvas_win.delete(dot)
                canvas_win.delete(points[dot_text.index(dot)])
                break

        dots_block.delete(0, END)

        for i in range(len(dots_list)):
            dot_str = "%d : (%-3.1f; %-3.1f)" % (i + 1, float(dots_list[i][0]), float(dots_list[i][1]))
            dots_list[i][2] = i + 1
            dots_block.insert(END, dot_str)

    except:
        messagebox.showerror("Ошибка", "Не выбрана точка")


# Функция для удаления всех точек текущего множества
def del_all_dots(canvas_param):
    if canvas_param:
        canvas_win.delete('dot')
    else:
        global size, m, start_param, circle, border

        circle = [(0, 0), 0]
        border = WIDTH
        size = SIZE * win_k
        m = size / (2 * WIDTH)
        str_eval = ""
        for dot in dots_list:
            str_eval += f'read_dot{END, dot[0], dot[1], 0}+'
        if start_param:
            str_eval += 'draw_solution()+'
        actions.append(str_eval)
        start_param = 0

        dots_block.delete(0, END)
        dots_list.clear()
        canvas_win.delete('all')

        draw_axies()
        draw_start_axies()


# Функция отрисовки подписей осей
def draw_start_axies():
    canvas_win.create_text(795 * win_k, 400.5 * win_k, text="ᐳ", font="AvantGardeC 16", fill='black', tag='start')
    canvas_win.create_text(400.5 * win_k, 9 * win_k, text="ᐱ", font="AvantGardeC 16", fill='black', tag='start')
    canvas_win.create_text(763 * win_k, 413 * win_k,
                           text=f"(%3.1f, %3.1f) X" % (100.0, 100.0), font="AvantGardeC 10", fill='black', tag='start')
    canvas_win.create_text(443 * win_k, 18 * win_k,
                           text=f"Y\n(%3.1f, %3.1f)" % (100.0, 100.0), font="AvantGardeC 10", fill='black', tag='start')
    canvas_win.create_text(424 * win_k, 408 * win_k, text="(0.0; 0.0)", font="AvantGardeC 10", fill='black', tag='start')


# Функция для отрисовки осей координат
def draw_axies():
    global size
    canvas_win.delete('all')
    canvas_win.create_line(0, size / 2, size, size / 2,
                           width=1, fill='black', tag='axies')
    canvas_win.create_line(size / 2, 0, size / 2, size,
                           width=1, fill='black', tag='axies')


# Определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    read_dot(END, event.x, event.y, 1)


# Решение
def solution():
    diff = 100000
    outside_points = []
    inside_points = []
    onside_points = []
    cent = ()
    radi = 0
    one_line = on_same_line(dots_list)

    if one_line:
        return cent, radi, outside_points, inside_points, onside_points, one_line

    for three in combinations(dots_list, 3):
        inside = []
        outside = []
        ax, ay = three[0][0], three[0][1]
        bx, by = three[1][0], three[1][1]
        cx, cy = three[2][0], three[2][1]

        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

        # центр окружности
        if d == 0:
            continue

        x = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
        y = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d

        center = (x, y)

        # радиус окружности
        radius = sqrt((ax - x) ** 2 + (ay - y) ** 2)

        for point in dots_list:
            flag = 0
            for couple in three:
                if point[0] == couple[0] and point[1] == couple[1]:
                    flag = 1

            if flag == 0:
                if distance(point[0], point[1], center[0], center[1]) < radius:
                    inside.append(point)
                else:
                    outside.append(point)

        length = abs(len(outside) - len(inside))
        if length < diff:
            diff = length
            outside_points = outside.copy()
            inside_points = inside.copy()
            onside_points = three
            radi = radius
            cent = center

    return cent, radi, outside_points, inside_points, onside_points, one_line


# Прорисовка всех объектов
def draw_solution():
    if len(dots_list) < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек для построения")
        return

    center, radius, outside_points, inside_points, onside_points, error = solution()
    if error == 1:
        messagebox.showerror("Ошибка", "Все точки лежат на одной прямой")
        return

    global coord_center, m, size, start_param, circle, border, ten_percent

    all_points = dots_list.copy()
    all_points.append((center[0] - radius, center[1]))
    all_points.append((center[0] + radius, center[1]))
    all_points.append((center[0], center[1] - radius))
    all_points.append((center[0], center[1] + radius))

    border = find_scale(all_points)
    ten_percent = size / 100 * 10
    m = size / (2 * border + ten_percent)
    start_param = 1

    canvas_win.delete("all")
    draw_axies()

    draw_all_dots(outside_points, 'pink', 'lightgreen')
    draw_all_dots(inside_points, 'lightgreen', 'pink')
    draw_all_dots(onside_points, 'black', 'grey')

    # Окружность
    circle = draw_circle(center, radius)
    print(circle)

    ovals = canvas_win.find_withtag('oval')
    actions.append(f'canvas_win.delete{ovals[-1]}')

    answer_win(center, radius, abs(len(outside_points) - len(inside_points)),
           len(outside_points), len(inside_points), onside_points)

    actions.append(f'canvas_win.delete({ovals[-1]})+')


# откат
def undo():
    # print(*actions, sep='\n')
    # print('\n')
    if '+' in actions[-1]:
        for act in actions[-1].split('+'):
            print(act)
            eval(act)
    print(*actions, sep='\n')
    print('\n')
    # actions.pop(-1)
    # print('a ', a)
    # print(actions[-1])


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

        dots_label.place(x=47 * win_x, y=18 * win_y, width=137 * win_x, height=24 * win_y)
        dots_block.place(x=30 * win_x, y=55 * win_y, width=237 * win_x, height=450 * win_y)

        add.place(x=30 * win_x, y=530 * win_y, width=117 * win_x, height=41 * win_y)
        dlt.place(x=150 * win_x, y=530 * win_y, width=117 * win_x, height=41 * win_y)
        chg.place(x=30 * win_x, y=575 * win_y, width=117 * win_x, height=41 * win_y)
        dlt_all.place(x=150 * win_x, y=575 * win_y, width=117 * win_x, height=41 * win_y)
        con.place(x=30 * win_x, y=640 * win_y, width=235 * win_x, height=41 * win_y)
        sol.place(x=30 * win_x, y=685 * win_y, width=235 * win_x, height=41 * win_y)
        und.place(x=195 * win_x, y=18 * win_y, width=65 * win_x, height=24 * win_y)

        draw_axies()
        if start_param == 0:
            draw_start_axies()
        else:
            draw_circle(*circle)

        draw_all_dots(dots_list, 'pink', 'lightgreen')

        coord_center = [size / 2, size / 2]


# Окно tkinter
win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #1")

win_x = win_y = win_k = 1

# Канвас
canvas_win = Canvas(win, bg="#ffffff")

# Множество точек
dots_label = Label(text="Координаты точек", bg='pink', font=f"AvantGardeC {14 * win_k}", fg='black')

# Список и блок точек
dots_list = []
dots_list_copy = []
dots_block = Listbox(bg="#ffffff")
dots_block.configure(font="AvantGardeC 14", fg='black')

# Кнопки
add = Button(text="Добавить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: add_dot())
dlt = Button(text="Удалить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: del_dot())
chg = Button(text="Изменить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_dot())
dlt_all = Button(text="Очистить", font="AvantGardeC 14",
                 borderwidth=0, command=lambda: del_all_dots(0))
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
sol = Button(text="Решить задачу", font="AvantGardeC 14",
             borderwidth=0, command=lambda: draw_solution())
und = Button(text="↩", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())

win_k = 1

size = SIZE
border = WIDTH # граница
ten_percent = 0 # 10% от величины границы
m = size * win_k / border
circle = [(0, 0), 0]

start_param = 0 # пока не было увеличения или уменьшения, чтобы при изменении размера окна не ехало
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

# удаление при масштабировании
# откаты все!
# расширять окно (как? изображение тоже едет?)
# наведение на точку