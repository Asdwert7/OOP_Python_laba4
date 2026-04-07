
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

from pathlib import Path
import tkinter as tk


SCALE_X = 6
SCALE_Y = 4

COLORS = [
    (0, 0, 0),
    (0, 0, 168),
    (0, 168, 0),
    (0, 168, 168),
    (168, 0, 0),
    (168, 0, 168),
    (168, 84, 0),
    (168, 168, 168),
    (84, 84, 84),
    (84, 84, 252),
    (84, 252, 84),
    (84, 252, 252),
    (252, 84, 84),
    (252, 84, 252),
    (252, 252, 84),
    (252, 252, 252),
]


def color_to_hex(color_index: int) -> str:
    r, g, b = COLORS[color_index & 0x0F]
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_line(coords, color_index):
    if len(coords) < 2:
        return

    points = []
    for x, y in coords:
        points.extend((x * SCALE_X, y * SCALE_Y))

    canvas.create_line(
        *points,
        fill=color_to_hex(color_index),
        width=4,
        smooth=False,
    )


def draw_point(x, y, color_index, size=1):
    x0 = x * SCALE_X
    y0 = y * SCALE_Y
    rx = max(1, size * SCALE_X // 2)
    ry = max(1, size * SCALE_Y // 2)

    canvas.create_oval(
        x0 - rx,
        y0 - ry,
        x0 + rx,
        y0 + ry,
        outline=color_to_hex(color_index),
        fill=color_to_hex(color_index),
    )


def decode_signed_nibble(value: int) -> int:
    magnitude = value & 0x07
    return -magnitude if (value & 0x08) else magnitude

# отладочный метод
def draw(pic: bytes):
    i = 0
    pic_color = 0
    pen_size = 1

    while i < len(pic):
        cmd = pic[i]
        print(f'i={i}, cmd=0x{cmd:02X}')
        i += 1

        if cmd == 0xFF:
            print('END')
            break

        if cmd == 0xF0:
            if i >= len(pic):
                break
            pic_color = pic[i] & 0x0F
            print(f'PIC COLOR = {pic_color}')
            i += 1
            continue

        if cmd == 0xF1:
            print('PIC COLOR OFF')
            pic_color = 0
            continue

        if cmd == 0xF2:
            if i >= len(pic):
                break
            _ = pic[i]
            i += 1
            continue

        if cmd == 0xF3:
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

            print('F4', coords[:5], '...')
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

            print('F5', coords[:5], '...')
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

            print('F6', coords[:5], '...')
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

            print('F7', coords[:5], '...')
            draw_line(coords, pic_color)
            continue

        if cmd == 0xF8:
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:
                i += 2
            continue

        if cmd == 0xF9:
            if i >= len(pic):
                break
            pen_value = pic[i]
            pen_size = (pen_value & 0x07) + 1
            i += 1
            print(f'PEN SIZE = {pen_size}')
            continue

        if cmd == 0xFA:
            while i + 1 < len(pic) and pic[i] < 0xF0 and pic[i + 1] < 0xF0:
                x = pic[i]
                y = pic[i + 1]
                i += 2
                draw_point(x, y, pic_color, pen_size)
            continue
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

pic = Path("data/PIC.1").read_bytes()

root = tk.Tk()
root.title("AGI PIC viewer")

canvas = tk.Canvas(
    root,
    width=160 * SCALE_X,
    height=170 * SCALE_Y,
    bg="#dcdcdc",
)
canvas.pack()

draw(pic)

tk.mainloop()

print('PIC size =', len(pic))
print(pic[:40])