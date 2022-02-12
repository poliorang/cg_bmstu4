import tkinter as tk
from tkinter import *
from math import sqrt
from itertools import combinations

def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


x, y = map(float, input().split())
coords = []
while x != 0 or y != 0:
    coords.append((x, y))
    x, y = map(float, input().split())

diff = 100000
outside_points = []
inside_points = []

for three in combinations(coords, 3):
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

    for point in coords:
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

print(diff, outside_points, inside_points)
'''

win = tk.Tk()
win.geometry('600x400+300+200')
win.title('lab 01')

lbl_input = Label(win, text = 'Input', font = 'AvantGardeC')
lbl_input.place(x = 136, y = 35)

lbl_output = Label(win, text = 'Output', font = 'AvantGardeC')
lbl_output.place(x = 130, y = 82)

input_str = tk.Entry(win, justify = tk.RIGHT, width = 25)
output_str = tk.Entry(win, justify = tk.RIGHT, width = 25)
input_str.place(x = 35, y = 55)
output_str.place(x = 35, y = 100)

win.mainloop()

# print(x, y, round(r, 5))

# res = list(combinations(coords, 2))
# print(res)
'''