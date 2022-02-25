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

PLACE_TO_DRAW = 0.8
INDENT_WIDTH = 0.1

TASK = "На плоскости задано множество из N точек. Определить радиус и центр такой окружности, " \
       "проходящей через ровно три различные точки заданного множества точек на плоскости, " \
       "что минимальна разность количеств точек, лежащих внутри и вне окружности.\n\n"

AUTHOR = "Егорова Полина ИУ7-44Б"


# Точка пересечения прямых
def line_intersection(line1, line2):
    x_coord = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_coord = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(x_coord, y_coord)
    if div == 0:
       return

    d = (det(*line1), det(*line2))
    x = det(d, x_coord) / div
    y = det(d, y_coord) / div
    return x, y


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
def find_scale(points):
    x_min = points[0][0]
    y_min = points[0][1]
    x_max = points[0][0]
    y_max = points[0][1]

    for point in points:
        if point[0] < x_min:
            x_min = point[0]
        if point[1] < y_min:
            y_min = point[1]
        if point[0] > x_max:
            x_max = point[0]
        if point[1] > y_max:
            y_max = point[1]

    if y_min > 0:
        y_min = -1
    if x_min > 0:
        x_min = -1
    if x_max < 0:
        x_max = 1
    if y_max < 0:
        y_max = 1

    k_x = (PLACE_TO_DRAW * SIZE) / (x_max - x_min)
    k_y = (PLACE_TO_DRAW * SIZE) / (y_max - y_min)

    # print('k ', k_x, k_y)
    return min(k_x, k_y), x_min, y_min


# Функция для чтения координат точки, их обработки и добавления в множество
def read_dot(place, dot_x, dot_y):
    #try:
        x = float(dot_x)
        y = float(dot_y)
        coords_dot = [x, y]

        global x_min, y_min, k, start_param

        # костыль
        if start_param:
            draw_all_points([(x, y)], -400 - x_min, -400 - y_min, k, 'pink', 'lightgreen')
        else:
            draw_all_points([(x, y)], x_min, y_min, k, 'pink', 'lightgreen')

        if place != END:  # изменить точку
            point = canvas_win.find_withtag('dot')[place]
            text = canvas_win.find_withtag('text')[place]
            canvas_win.delete(point)
            canvas_win.delete(text)
            dots_block.delete(place)
            dots_list.pop(place)
            coords_dot.append(place + 1)
            dots_list.insert(place, coords_dot)
        else:  # добавить новую точку
            place = len(dots_list)
            coords_dot.append(place + 1)
            dots_list.append(coords_dot)


        dot_str = "%d : (%-3.1f; %-3.1f)" % (place + 1, x, y)
        dots_block.insert(place, dot_str)

        points = canvas_win.find_withtag('dot')
        dot_text = canvas_win.find_withtag('text')
        actions.append(f'canvas_win.delete({points[-1]})+dots_list.pop({place})+dots_block.delete({place}, END)+'
                       f'canvas_win.delete({dot_text[-1]})+actions.pop(-1)')


        #actions.append(f'canvas_win.delete({points[-1]})+dots_list.pop({place})+dots_block.delete({place}, END)+canvas_win.delete({text[-1]}')
    #except:
    #    messagebox.showerror("Ошибка", "Неверно введены координаты точки")



# Функция для добавления точки в множество
def add_dot():
    dot_win, dot_x, dot_y = dots_win()

    add_but = Button(dot_win, text="Добавить", font="AvantGardeC 14",
                     borderwidth=0, command=lambda: read_dot(END, dot_x.get(), dot_y.get()))
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
                     borderwidth=0, command=lambda: read_dot(place, dot_x.get(), dot_y.get()))
    add_but.place(x=40, y=120, relheight=0.15, relwidth=0.64)

    dot_win.mainloop()


# Функция для удаления точки
def del_dot():
    try:
        place = dots_block.curselection()[0]

        points = canvas_win.find_withtag('dot')
        dot_text = canvas_win.find_withtag('text')

        coords = dots_list.pop(place)

        x0, y0 = translate_point(coords[0], -coords[1], -80, -80, 4)
        # x1, y1 = x0 - 2, y0 - 2
        # x2, y2 = x0 + 2, y0 + 2

        actions.append(f'read_dot{END, coords[0], coords[1]}+actions.pop(-1)+actions.pop(-1)')

        # canvas_win.delete(point)
        canvas_win.delete(points[place])
        canvas_win.delete(dot_text[place])
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
        dots_block.delete(0, END)
        dots_list.clear()
        canvas_win.delete('all')
        global k, x_min, y_min, start_param
        start_param = 1
        k = 4
        x_min = y_min = -320
        draw_axies(x_min, y_min, 1, 'black')
        draw_start_axies('black')


# Функция отрисовки подписей осей
def draw_start_axies(color):
    canvas_win.create_text(795, 400.5, text="ᐳ", font="AvantGardeC 16", fill=color)
    canvas_win.create_text(400.5, 9, text="ᐱ", font="AvantGardeC 16", fill=color)
    canvas_win.create_text(763, 413, text="(100.0; 100.0) X", font="AvantGardeC 10", fill=color)
    canvas_win.create_text(443, 18, text="Y\n(100.0; 100.0)", font="AvantGardeC 10", fill=color)
    canvas_win.create_text(424, 408, text="(0.0; 0.0)", font="AvantGardeC 10", fill=color)


# Функция для отрисовки осей координат
def draw_axies(x_min, y_min, k, color):
    x_x1, x_y1 = translate_point(SIZE, 0, x_min, y_min, k)
    x_x2, x_y2 = translate_point(-SIZE, 0, x_min, y_min, k)

    y_x1, y_y1 = translate_point(0, SIZE, x_min, y_min, k)
    y_x2, y_y2 = translate_point(0, -SIZE, x_min, y_min, k)

    canvas_win.create_line(-SIZE, -x_y1 + SIZE, SIZE, -x_y2 + SIZE, width=1, fill=color)
    canvas_win.create_line(y_x1, -SIZE, y_x2, SIZE, width=1, fill=color)

    global coord_center

    x, y = line_intersection([(x_x1, x_y1), (x_x2, x_y2)], [(y_x1, y_y1), (y_x2, y_y2)])
    coord_center = x, SIZE - y


# Определение и запись координат точки по клику
def click(event):
    if event.x < 0 or event.x > 800 or event.y < 0 or event.y > 800:
        return

    global dots_block, dots_list, coord_center

    x = (event.x - coord_center[0]) / k
    y = (- event.y + coord_center[1]) / k

    read_dot(END, x, y)


# Решение
def solution():
    diff = 100000
    outside_points = []
    inside_points = []

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

    return cent, radi, outside_points, inside_points, onside_points


# Прорисовка всех точек
def draw_all_points(dots, x_min, y_min, k, color, color_active):
    for point in dots:
        x0, y0 = translate_point(point[0], point[1], x_min, y_min, k)
        x1, y1 = (x0 - 2), (y0 - 2)
        x2, y2 = (x0 + 2), (y0 + 2)
        canvas_win.create_oval(x1, - y1 + SIZE, x2, - y2 + SIZE,
                               outline=color, fill=color, activeoutline=color_active, width=3, tag='dot')
        canvas_win.create_text(x0 + 15, -y0 + SIZE + 15, tag='text',
                               text="(%.1f; %.1f)" % (point[0], point[1]), font="AvantGardeC 9", fill='black')


# Координаты точки для масштабирования
def translate_point(x, y, x_min, y_min, k):
    x = INDENT_WIDTH * SIZE + (x - x_min) * k
    y = INDENT_WIDTH * SIZE + (y - y_min) * k

    return x, y


# Прорисовка всех объектов
def draw_solution():
    if len(dots_list) < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек для построения")
        return

    canvas_win.delete("all")
    global coord_center, k, x_min, y_min, start_param

    center, radius, outside_points, inside_points, onside_points = solution()
    all_points = dots_list.copy()
    all_points.append((center[0] - radius, center[1]))
    all_points.append((center[0] + radius, center[1]))
    all_points.append((center[0], center[1] - radius))
    all_points.append((center[0], center[1] + radius))

    start_param = 0
    k, x_min, y_min = find_scale(all_points)
    draw_axies(x_min, y_min, k, 'black')
    print('sol ', x_min, y_min, k)
    draw_all_points(outside_points, x_min, y_min, k, 'pink', 'lightgreen')
    draw_all_points(inside_points, x_min, y_min, k, 'lightgreen', 'pink')
    draw_all_points(onside_points, x_min, y_min, k, 'black', 'pink')

    # Окружность
    x1, y1 = translate_point(center[0] - radius, center[1] + radius, x_min, y_min, k)
    x2, y2 = translate_point(center[0] + radius, center[1] - radius, x_min, y_min, k)
    canvas_win.create_oval(x1, - y1 + SIZE, x2, - y2 + SIZE,
                           activeoutline='lightgreen', outline='grey', width=3, tag='oval')

    # Центр окружности
    cx1, cy1 = translate_point(center[0] - 0.01 * k, center[1] + 0.01 * k, x_min, y_min, k)
    cx2, cy2 = translate_point(center[0] + 0.01 * k, center[1] - 0.01 * k, x_min, y_min, k)
    canvas_win.create_oval(cx1, - cy1 + SIZE, cx2, - cy2 + SIZE, outline='grey', width=1, tag='cent')

    ovals = canvas_win.find_withtag('oval')
    centers = canvas_win.find_withtag('cent')
    actions.append(f'canvas_win.delete({ovals[-1]})+canvas_win.delete({centers[-1]})')

    answer_win(center, radius, abs(len(outside_points) - len(inside_points)),
           len(outside_points), len(inside_points), onside_points)


# откат
def undo():
    print(*actions, sep='\n')
    print('\n')
    if '+' in actions[-1]:
        for act in actions[-1].split('+'):
            print(act)
            eval(act)
    print(*actions, sep='\n')
    print('\n')
    # actions.pop(-1)
    # print('a ', a)
    # print(actions[-1])

dots_list = []

win = Tk()
win['bg'] = 'grey'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа #1")
#win.resizable(False, False)

canvas_win = Canvas(win, width=SIZE, height=SIZE, bg="#ffffff")
canvas_win.place(x=300, y=0)

# Множество точек
dots_label = Label(text="Координаты точек", bg='pink', font="AvantGardeC 14", fg='black')
dots_label.place(x=47, y=18)

# Список точек
dots_block = Listbox(bg="#ffffff")
dots_block.configure(height=25, width=28, font="AvantGardeC 14", fg='black')
dots_block.place(x=30, y=55)

add = Button(text="Добавить", width=12, height=2, font="AvantGardeC 14",
             borderwidth=0, command=lambda: add_dot())
add.place(x=30, y=530)

del1 = Button(text="Удалить", width=12, height=2, font="AvantGardeC 14",
              borderwidth=0, command=lambda: del_dot())
del1.place(x=150, y=530)

chg = Button(text="Изменить", width=12, height=2, font="AvantGardeC 14",
             borderwidth=0, command=lambda: change_dot())
chg.place(x=30, y=575)

del_all = Button(text="Очистить", width=12, height=2, font="AvantGardeC 14",
                 borderwidth=0, command=lambda: del_all_dots(0))
del_all.place(x=150, y=575)

condition = Button(text="Условие задачи", width=27, height=2, font="AvantGardeC 14",
                   borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
condition.place(x=30, y=640)

solut = Button(text="Решить задачу", width=27, height=2, font="AvantGardeC 14",
               borderwidth=0, command=lambda: draw_solution())
solut.place(x=30, y=685)

undo_but = Button(text="↩", width=5, height=1, font="AvantGardeC 14",
                  borderwidth=0, command=lambda: undo())
undo_but.place(x=195, y=19)


# 1 - если центр координат в центре канвы, 0 - иначе (костыль)
start_param = 1

# коэффициент масштабирования
k = 4

# крайняя нижняя левая точка
x_min = y_min = -320

draw_axies(x_min, y_min, 1, 'black')
draw_start_axies('black')
canvas_win.bind('<1>', click)

# Меню
mmenu = Menu(win)

add_menu = Menu(mmenu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', TASK + AUTHOR))
add_menu.add_command(label='Выход', command=exit)
mmenu.add_cascade(label='Help', menu=add_menu)

win.config(menu=mmenu)

win.mainloop()


# точка одна съезжает когда рядом с кругом ставить - масштабирование
# откаты все!
# расширять окно (как? изображение тоже едет?)
# наведение на точку