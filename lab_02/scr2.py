from math import radians, sin, cos

x0, y0 = map(float, input('center -> ').split())
r = float(input('radius -> '))
n = int(input('count -> '))

angle = (n - 2) * radians(180) / n
tmp = angle
print(angle)
x = []
y = []
for i in range(n):
    x.append("%.2f" % (x0 + r * cos(angle)))
    y.append("%.2f" % (x0 + r * sin(angle) - 3.3))
    print(x[i], y[i])

    angle += tmp

print(*x)
print(*y)