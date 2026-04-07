import numpy as np
import matplotlib.pyplot as plt

import math 
from decimal import Decimal

# =========================
# 2.1. Построить двухмерный график на основе следующих уравнений:
# =========================

t = np.linspace(0, 2 * np.pi, 1000)

x = 16 * np.sin(t) ** 3
y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)

plt.figure(figsize=(6, 6))
plt.plot(x, y, color='red')
plt.title('График по параметрическим уравнениям')
plt.grid(True)
plt.axis('equal')
plt.show()

plt.figure(figsize=(6, 6))
plt.fill(x, y, color='red')
plt.title('График с внутренней заливкой')
plt.grid(True)
plt.axis('equal')
plt.show()

# =========================
# 2.2. Построить трёхмерный график по уравнению:
# =========================

def figure_func(x, y, z):
    return ((x ** 2 + (9 * y ** 2) / 4 + z ** 2 - 1) ** 3
            - x ** 2 * z ** 3
            - (9 * y ** 2 * z ** 3) / 200)


def draw(figure_func, bbox=(-1.5, 1.5)):
    xmin, xmax, ymin, ymax, zmin, zmax = bbox * 3

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection='3d')

    a = np.linspace(xmin, xmax, 120)
    b = np.linspace(xmin, xmax, 25)

    a1, a2 = np.meshgrid(a, a)

    for x0 in b:
        y = a1
        z = a2
        values = figure_func(x0, y, z)
        ax.contour(y, z, values, levels=[0], zdir='x', offset=x0,
                   colors='red')

    for y0 in b:
        x = a1
        z = a2
        values = figure_func(x, y0, z)
        ax.contour(x, z, values, levels=[0], zdir='y', offset=y0,
                   colors='red')

    for z0 in b:
        x = a1
        y = a2
        values = figure_func(x, y, z0)
        ax.contour(x, y, values, levels=[0], zdir='z', offset=z0,
                   colors='red')

    ax.set_xlim3d(xmin, xmax)
    ax.set_ylim3d(ymin, ymax)
    ax.set_zlim3d(zmin, zmax)
    ax.set_box_aspect((1, 1, 1))

    plt.title('2.2 Трёхмерный график')
    plt.show()


draw(figure_func)


# =========================
# 2.3 Белый шум
# =========================
'''
настоящую случайность мы не берём. Вместо этого делаем псевдошум: 
значение пикселя вычисляется по его координатам через математическую формулу, которая даёт на вид хаотичный результат.

Функция noise(x):
- получает номер точки x
- считает по формуле число, которое выглядит хаотично
- берёт дробную часть
- переводит диапазон из [0, 1) в [-1, 1)

'''
def noise(x):
    value = np.sin(x * 12.9898) * 43758.5453
    frac = value - np.floor(value)
    return 2 * frac - 1


x = np.arange(1000)
y = noise(x)

plt.figure(figsize=(18, 6))
plt.plot(x, y, color='blue', linewidth=0.5)
plt.title('2.3 Белый шум')
plt.show()

# =========================
# 2.4. Разработать модель аппаратного ускорителя вычислений для программно-аппаратного комплекса. 
# Построить линейный график результатов ускорения вычислений.
# =========================

#  FIR filter. - КИХ-фильтр = фильтр с конечной импульсной характеристикой
# выход считается только по конечному числу последних входных значений.

'''
Идея решения

Нужно смоделировать работу КИХ-фильтра с заданными коэффициентами k и построить линейную диаграмму АЧХ.

Что делаем:
1 Берём набор частот omega от 0.1 до 2.0 с шагом 0.1.
2 Для каждой частоты подаём на вход синусоидальный сигнал:
    x = 1000 * \sin(\omega t)
3 Для каждого момента времени считаем выход фильтра:
    y = \sum k_i x_i
4 По набору выходных значений для данной частоты находим максимальную амплитуду.
5 Переводим усиление в децибелы:
    20 \log_{10}\left(\frac{A_{out}}{1000}\right)
6 Строим график omega -> усиление.
'''
k = [6, 0, -4, -3, 5, 6, -6, -13, 7, 44, 64, 44, 7, -13, -6, 6, 5, -3, -4, 0, 6]


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += step


omega_list = list(float_range(Decimal('0.1'), Decimal('2.1'), Decimal('0.1')))
ex_list = []

for omega in omega_list:
    y_list = []

    for t in range(1, 100):
        y = 0

        for b in range(0, len(k)):
            x = round(1000 * math.sin(omega * (t + b)))
            y += k[b] * x

        y_list.append(y)

    max_amplitude = max(abs(value) for value in y_list)

    if max_amplitude == 0:
        ex = -120
    else:
        ex = 20 * math.log10(max_amplitude / 1000)

    ex_list.append(ex)

plt.figure(figsize=(18, 6))
plt.plot(omega_list, ex_list)
plt.title('Амплитудно-частотная характеристика КИХ-фильтра')
plt.xlabel('Частота, рад/отсчёт')
plt.ylabel('Усиление, дБ')
plt.grid(True)
plt.show()
