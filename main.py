import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Button, filedialog, messagebox

# Константы для Коэна-Сазерленда
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


# Функция для вычисления кода точки в алгоритме Коэна-Сазерленда
def compute_out_code(x, y, clip_rect):
    xmin, ymin, xmax, ymax = clip_rect
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code


# Алгоритм Коэна-Сазерленда для отсечения отрезков
def cohen_sutherland_clip(x1, y1, x2, y2, clip_rect):
    xmin, ymin, xmax, ymax = clip_rect
    outcode1 = compute_out_code(x1, y1, clip_rect)
    outcode2 = compute_out_code(x2, y2, clip_rect)
    accept = False

    while True:
        if not (outcode1 | outcode2):  # Полностью внутри
            accept = True
            break
        elif outcode1 & outcode2:  # Полностью вне
            break
        else:
            x, y = 0, 0
            outcode_out = outcode1 if outcode1 else outcode2
            if outcode_out & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif outcode_out & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif outcode_out & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif outcode_out & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_out_code(x1, y1, clip_rect)
            else:
                x2, y2 = x, y
                outcode2 = compute_out_code(x2, y2, clip_rect)

    if accept:
        return [(x1, y1), (x2, y2)]
    return None


# Функция для визуализации отрезков
def plot_segments_with_clipping(segments, clip_window):
    fig, ax = plt.subplots()

    # Координаты отсекателя
    xmin, ymin, xmax, ymax = clip_window
    rect = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]

    # Отрисовка отсекателя
    ax.plot(*zip(*rect), color='b', linewidth=2, label='Clip Rectangle')

    # Отрисовка исходных и отсечённых отрезков
    for (x1, y1), (x2, y2) in segments:
        ax.plot([x1, x2], [y1, y2], color='r', linestyle='--', label='Original Segment')  # Исходные
        clipped = cohen_sutherland_clip(x1, y1, x2, y2, clip_window)
        if clipped:
            ax.plot([clipped[0][0], clipped[1][0]], [clipped[0][1], clipped[1][1]],
                    color='g', linewidth=2, label='Clipped Segment')  # Отсечённые

    ax.legend()
    ax.set_title("Segment Clipping")
    plt.show()


# Алгоритм Sutherland-Hodgman для многоугольников
def inside(p, cp1, cp2):
    return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) > (cp2[1] - cp1[1]) * (p[0] - cp1[0])


def intersection(cp1, cp2, s, e):
    dc = (cp1[0] - cp2[0], cp1[1] - cp2[1])
    dp = (s[0] - e[0], s[1] - e[1])
    n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
    n2 = s[0] * e[1] - s[1] * e[0]
    n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
    return (n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3


def sutherland_hodgman(subject_pol, clip_pol):
    output_list = subject_pol
    cp1 = clip_pol[-1]
    for cp2 in clip_pol:
        input_list = output_list
        output_list = []
        s = input_list[-1]
        for e in input_list:
            if inside(e, cp1, cp2):
                if not inside(s, cp1, cp2):
                    output_list.append(intersection(cp1, cp2, s, e))
                output_list.append(e)
            elif inside(s, cp1, cp2):
                output_list.append(intersection(cp1, cp2, s, e))
            s = e
        cp1 = cp2
    return output_list


# Чтение данных из файлов
def read_segments(file_path):
    with open(file_path, 'r') as f:
        n = int(f.readline().strip())
        segments = [tuple(map(float, f.readline().strip().split())) for _ in range(n)]
        clip_rect = tuple(map(float, f.readline().strip().split()))
    return [(segments[i][:2], segments[i][2:]) for i in range(n)], clip_rect


def read_polygon(file_path):
    with open(file_path, 'r') as f:
        n = int(f.readline().strip())
        polygon = [tuple(map(float, f.readline().strip().split())) for _ in range(n)]
        clip_rect = tuple(map(float, f.readline().strip().split()))
    clip_window = [(clip_rect[0], clip_rect[1]), (clip_rect[2], clip_rect[1]),
                   (clip_rect[2], clip_rect[3]), (clip_rect[0], clip_rect[3])]
    return polygon, clip_window


# Интерфейс Tkinter
def open_file_for_segments():
    file_path = filedialog.askopenfilename()
    if file_path:
        segments, clip_rect = read_segments(file_path)
        plot_segments_with_clipping(segments, clip_rect)


def open_file_for_polygon():
    file_path = filedialog.askopenfilename()
    if file_path:
        polygon, clip_window = read_polygon(file_path)
        clipped_polygon = sutherland_hodgman(polygon, clip_window)
        fig, ax = plt.subplots()
        ax.fill(*zip(*clip_window), edgecolor='b', fill=False, linewidth=2, label='Clip Polygon')
        ax.fill(*zip(*polygon), edgecolor='r', fill=False, linewidth=2, label='Original Polygon')
        ax.fill(*zip(*clipped_polygon), edgecolor='g', fill=False, linewidth=2, label='Clipped Polygon')
        ax.legend()
        plt.show()


def main_gui():
    root = Tk()
    root.title("Clipping Algorithms")

    Button(root, text="Load Segments", command=open_file_for_segments).pack(pady=10)
    Button(root, text="Load Polygon", command=open_file_for_polygon).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main_gui()
