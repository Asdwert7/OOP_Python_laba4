#
'''
AGI-картинка хранится как последовательность команд, а не как готовый bitmap. Поэтому программа должна:
1 читать байты из data/PIC.1;
2 идти по ним по одному;
3 распознавать команды рисования;
4 переводить команды в вызовы tkinter.Canvas.

Для AGI-картинок важны команды смены цвета и рисования линий: 0xF0/0xF1 для включения и выключения рисования на обычном экране, 
0xF4 и 0xF5 для “угловых” линий, 0xF6 для абсолютных линий, 0xF7 для коротких относительных линий, 
0xF9 и 0xFA для пера, а 0xFF завершает картинку. Экран приоритетов есть в формате, но в этом задании его можно не отображать. 
AGI обычно работает в логическом разрешении 160×200 с удвоением по горизонтали
'''

from pathlib import Path  # для работы с путями и файлами
import tkinter as tk  # для графического интерфейса


SCALE_X = 6  # масштаб по оси X умножаем для того чтобы картинка не получилась мелкой 
SCALE_Y = 4  # масштаб по оси Y

COLORS = [  # таблица 16 базовых цветов
    (0, 0, 0),  # 0: чёрный
    (0, 0, 168),  # 1: синий
    (0, 168, 0),  # 2: зелёный
    (0, 168, 168),  # 3: бирюзовый
    (168, 0, 0),  # 4: красный
    (168, 0, 168),  # 5: пурпурный
    (168, 84, 0),  # 6: коричневый
    (168, 168, 168),  # 7: светло-серый
    (84, 84, 84),  # 8: тёмно-серый
    (84, 84, 252),  # 9: ярко-синий
    (84, 252, 84),  # 10: ярко-зелёный
    (84, 252, 252),  # 11: ярко-бирюзовый
    (252, 84, 84),  # 12: ярко-красный
    (252, 84, 252),  # 13: ярко-пурпурный
    (252, 252, 84),  # 14: ярко-жёлтый
    (252, 252, 252),  # 15: белый
]


def color_to_hex(color_index: int) -> str:  # перевод индекса цвета в hex-строку для AGI цвет хранится как число, например 6.
    r, g, b = COLORS[color_index & 0x0F]  # берём цвет из таблицы, маскируя индекс
    return f"#{r:02x}{g:02x}{b:02x}"  # возвращаем строку вида #RRGGBB


def draw_line(coords, color_index):  # рисование линии по списку координат
    if len(coords) < 2:  # если точек меньше двух
        return  # линию не рисуем

    points = []  # список координат для tkinter
    for x, y in coords:  # перебираем точки
        points.extend((x * SCALE_X, y * SCALE_Y))  # масштабируем и добавляем

    canvas.create_line(  # рисуем линию на холсте
        *points,  # распаковываем список координат
        fill=color_to_hex(color_index),  # цвет линии
        width=4,  # толщина линии
        smooth=False,  # не сглаживать
    )


def draw_point(x, y, color_index, size=1):  # рисование точки (овала)
    x0 = x * SCALE_X  # масштабируем x
    y0 = y * SCALE_Y  # масштабируем y
    rx = max(1, size * SCALE_X // 2)  # радиус по x
    ry = max(1, size * SCALE_Y // 2)  # радиус по y

    canvas.create_oval(  # рисуем овал как точку пера
        x0 - rx,  # левая граница
        y0 - ry,  # верхняя граница
        x0 + rx,  # правая граница
        y0 + ry,  # нижняя граница
        outline=color_to_hex(color_index),  # цвет обводки
        fill=color_to_hex(color_index),  # цвет заливки
    )

'''
Иногда в файле хранится не новая координата целиком, а только маленькое смещение:
    сдвинься на +2
    сдвинься на -1

Для экономии места эти смещения хранят в 4 битах.

Один такой кусочек из 4 бит называется nibble.

Как устроены эти 4 бита
1 бит отвечает за знак
3 бита отвечают за величину

Например
    0011 → +3
    1011 → -3

Эта функция как раз и превращает такой 4-битный код в обычное число Python.
'''
def decode_signed_nibble(value: int) -> int:  # декодирование 4-битного смещения
    magnitude = value & 0x07  # берём модуль из младших 3 бит
    return -magnitude if (value & 0x08) else magnitude  # старший бит задаёт знак

# отладочный метод

def draw(pic: bytes):  # декодирование и отрисовка AGI-данных
    i = 0  # позиция в массиве байт
    pic_color = 0  # текущий цвет картинки
    pen_size = 1  # текущий размер пера

    while i < len(pic):  # пока есть данные
        cmd = pic[i]  # считываем командуы
        print(f'i={i}, cmd=0x{cmd:02X}')  # выводим отладочную информацию
        i += 1  # сдвигаем позицию
        '''
        	0xF0 = установить цвет
            0xF1 = Это выключение текущего цвета.
            0xF2 = Это команды для приоритетного экрана.
            0xF3 = Это команды для приоритетного экрана. те я вижу, что тут есть приоритет, но рисовать его не буду
            0xF4 = рисовать один тип линии c y
            0xF5 = в F5 чередование начинается с x
            0xF6 = рисовать другой тип линии
            0xF7 = Это линии по относительным смещениям.
            0xF8 = Это команда заливки.(но заливать по тз не надо так что фулл игнорим)
            0xF9 = Это установка размера пера.
            0xFA = Это рисование точек пером. x,y
            0xFF = конец картинки
        '''
        if cmd == 0xFF:  # команда завершения
            print('END')  # печатаем конец
            break  # выходим из цикла

        if cmd == 0xF0:  # команда установки цвета
            if i >= len(pic):  # проверяем границы
                break  # выходим при ошибке
            pic_color = pic[i] & 0x0F  # берём младшие 4 бита цвета
            print(f'PIC COLOR = {pic_color}')  # выводим текущий цвет
            i += 1  # сдвигаем позицию
            continue  # переходим к следующей команде

        if cmd == 0xF1:  # команда выключения цвета
            print('PIC COLOR OFF')  # отладочный вывод
            pic_color = 0  # сбрасываем цвет
            continue  # переходим к следующей команде

        if cmd == 0xF2:  # команда приоритетного цвета (не используется)
            if i >= len(pic):  # проверяем границы
                break  # выходим при ошибке
            _ = pic[i]  # читаем байт и игнорируем
            i += 1  # сдвигаем позицию
            continue  # переходим к следующей команде

        if cmd == 0xF3:  # команда выключения приоритетного цвета
            continue  # ничего не делаем

        if cmd == 0xF4:  # команда «угловых» линий с чередованием координат
            if i + 1 >= len(pic):  # проверяем границы
                break  # выходим при ошибке

            x = pic[i]  # первая координата x
            y = pic[i + 1]  # первая координата y
            i += 2  # сдвигаем позицию

            coords = [(x, y)]  # начинаем список координат
            draw_y = True  # флаг: следующий байт задаёт y

            while i < len(pic) and pic[i] < 0xF0:  # читаем данные до новой команды байты меньше 0xF0 считаются данными 
                value = pic[i]  # читаем очередное значение
                i += 1  # сдвигаем позицию

                if draw_y:  # если следующий байт это y
                    y = value  # обновляем y
                else:
                    x = value  # иначе обновляем x

                coords.append((x, y))  # добавляем точку
                draw_y = not draw_y  # чередуем координаты

            print('F4', coords[:5], '...')  # отладочный вывод
            draw_line(coords, pic_color)  # рисуем линию
            continue  # переходим к следующей команде

        if cmd == 0xF5:  # команда «угловых» линий с чередованием координат
            if i + 1 >= len(pic):  # проверяем границы
                break  # выходим при ошибке

            x = pic[i]  # первая координата x
            y = pic[i + 1]  # первая координата y
            i += 2  # сдвигаем позицию

            coords = [(x, y)]  # начинаем список координат
            draw_x = True  # флаг: следующий байт задаёт x

            while i < len(pic) and pic[i] < 0xF0:  # читаем данные до новой команды
                value = pic[i]  # читаем очередное значение
                i += 1  # сдвигаем позицию

                if draw_x:  # если следующий байт это x
                    x = value  # обновляем x
                else:
                    y = value  # иначе обновляем y

                coords.append((x, y))  # добавляем точку
                draw_x = not draw_x  # чередуем координаты

            print('F5', coords[:5], '...')  # отладочный вывод
            draw_line(coords, pic_color)  # рисуем линию
            continue  # переходим к следующей команде

        if cmd == 0xF6:  # команда абсолютных линий (пары x,y)
            if i + 1 >= len(pic):  # проверяем границы
                break  # выходим при ошибке

            x = pic[i]  # первая координата x
            y = pic[i + 1]  # первая координата y
            i += 2  # сдвигаем позицию
            coords = [(x, y)]  # начинаем список координат

            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:  # читаем пары
                x = pic[i]  # очередной x
                y = pic[i + 1]  # очередной y
                i += 2  # сдвигаем позицию
                coords.append((x, y))  # добавляем точку

            print('F6', coords[:5], '...')  # отладочный вывод
            draw_line(coords, pic_color)  # рисуем линию
            continue  # переходим к следующей команде

        if cmd == 0xF7:  # команда относительных линий (смещения)
            if i + 1 >= len(pic):  # проверяем границы
                break  # выходим при ошибке

            x = pic[i]  # начальная координата x
            y = pic[i + 1]  # начальная координата y
            i += 2  # сдвигаем позицию
            coords = [(x, y)]  # начинаем список координат

            while i < len(pic) and pic[i] < 0xF0:  # читаем байты смещения
                delta = pic[i]  # читаем байт
                i += 1  # сдвигаем позицию

                dx = decode_signed_nibble((delta >> 4) & 0x0F)  # старшие 4 бита - dx
                dy = decode_signed_nibble(delta & 0x0F)  # младшие 4 бита - dy

                x += dx  # применяем смещение по x
                y += dy  # применяем смещение по y
                coords.append((x, y))  # добавляем точку

            print('F7', coords[:5], '...')  # отладочный вывод
            draw_line(coords, pic_color)  # рисуем линию
            continue  # переходим к следующей команде

        if cmd == 0xF8:  # команда заливки (в задании не используется)
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:  # пропускаем пары
                i += 2  # сдвигаем позицию
            continue  # переходим к следующей команде

        if cmd == 0xF9:  # команда установки размера пера
            if i >= len(pic):  # проверяем границы
                break  # выходим при ошибке
            pen_value = pic[i]  # читаем значение пера
            pen_size = (pen_value & 0x07) + 1  # вычисляем размер пера
            i += 1  # сдвигаем позицию
            print(f'PEN SIZE = {pen_size}')  # отладочный вывод
            continue  # переходим к следующей команде

        if cmd == 0xFA:  # команда рисования точек пером
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:  # читаем пары
                x = pic[i]  # координата x
                y = pic[i + 1]  # координата y
                i += 2  # сдвигаем позицию
                draw_point(x, y, pic_color, pen_size)  # рисуем точку
            continue  # переходим к следующей команде

'''def draw(pic: bytes):
    i = 0
    pic_color = None
    pri_color = None
    pen_size = 1

    while i < len(pic):
        cmd = pic[i]
        i += 1

        if cmd == 0xFF:
            break

        if cmd == 0xF0:
            if i >= len(pic):
                break
            pic_color = pic[i] & 0x0F
            i += 1
            continue

        if cmd == 0xF1:
            pic_color = None
            continue

        if cmd == 0xF2:
            if i >= len(pic):
                break
            pri_color = pic[i] & 0x0F
            i += 1
            continue

        if cmd == 0xF3:
            pri_color = None
            continue

        if cmd == 0xF4:
            if i + 1 >= len(pic):
                break

            x = pic[i]
            y = pic[i + 1]
            i += 2

            coords = [(x, y)]
            draw_y = True

            while i < len(pic) and pic[i] < 0xF0:
                value = pic[i]
                i += 1

                if draw_y:
                    y = value
                else:
                    x = value

                coords.append((x, y))
                draw_y = not draw_y

            if pic_color is not None:
                draw_line(coords, pic_color)
            continue

        if cmd == 0xF5:
            if i + 1 >= len(pic):
                break

            x = pic[i]
            y = pic[i + 1]
            i += 2

            coords = [(x, y)]
            draw_x = True

            while i < len(pic) and pic[i] < 0xF0:
                value = pic[i]
                i += 1

                if draw_x:
                    x = value
                else:
                    y = value

                coords.append((x, y))
                draw_x = not draw_x

            if pic_color is not None:
                draw_line(coords, pic_color)
            continue

        if cmd == 0xF6:
            if i + 1 >= len(pic):
                break

            x = pic[i]
            y = pic[i + 1]
            i += 2

            coords = [(x, y)]

            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:
                x = pic[i]
                y = pic[i + 1]
                i += 2
                coords.append((x, y))

            if pic_color is not None:
                draw_line(coords, pic_color)
            continue

        if cmd == 0xF7:
            if i + 1 >= len(pic):
                break

            x = pic[i]
            y = pic[i + 1]
            i += 2

            coords = [(x, y)]

            while i < len(pic) and pic[i] < 0xF0:
                delta = pic[i]
                i += 1

                dx = decode_signed_nibble((delta >> 4) & 0x0F)
                dy = decode_signed_nibble(delta & 0x0F)

                x += dx
                y += dy
                coords.append((x, y))

            if pic_color is not None:
                draw_line(coords, pic_color)
            continue

        if cmd == 0xF8:
            # Fill в этом задании не применяем
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:
                i += 2
            continue

        if cmd == 0xF9:
            if i >= len(pic):
                break
            pen_value = pic[i]
            i += 1
            pen_size = (pen_value & 0x07) + 1
            continue

        if cmd == 0xFA:
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:
                x = pic[i]
                y = pic[i + 1]
                i += 2

                if pic_color is not None:
                    draw_point(x, y, pic_color, pen_size)
            continue

        # Неизвестная команда: молча пропускаем.
        # Формат старый, жизнь коротка.
        continue
'''


pic = Path("data/PIC.44").read_bytes()  # читаем байты из файла

root = tk.Tk()  # создаём главное окно
root.title("AGI PIC viewer")  # задаём заголовок окна

canvas = tk.Canvas(  # создаём холст
    root,  # родительский виджет
    width=160 * SCALE_X,  # ширина с масштабом
    height=170 * SCALE_Y,  # высота с масштабом
    bg="#dcdcdc",  # цвет фона
)
canvas.pack()  # размещаем холст

draw(pic)  # отрисовываем картинку

tk.mainloop()  # запускаем главный цикл Tkinter

print('PIC size =', len(pic))  # печатаем размер файла
print(pic[:40])  # печатаем первые 40 байт
