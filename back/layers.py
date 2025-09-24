from PIL import Image
import numpy as np


class Pixel:
    def create_pixel_grid(self, width, height, cell_size=4):
        """Создает прозрачную сетку 4x4 с белыми углами"""
        # Создаем прозрачный слой
        grid = np.zeros((height, width, 4), dtype=np.uint8)

        # Создаем шаблон для одной ячейки 4x4
        cell = np.zeros((cell_size, cell_size, 4), dtype=np.uint8)

        # Белые пиксели по углам ячейки
        cell[0, 0] = [255, 255, 255, 255]  # левый верхний
        cell[0, -1] = [255, 255, 255, 255]  # правый верхний
        cell[-1, 0] = [255, 255, 255, 255]  # левый нижний
        cell[-1, -1] = [255, 255, 255, 255]  # правый нижний

        # Заполняем всю сетку повторяющимся паттерном
        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                y_end = min(y + cell_size, height)
                x_end = min(x + cell_size, width)
                grid[y:y_end, x:x_end] = cell[:y_end - y, :x_end - x]

        return Image.fromarray(grid)

    def create_pixel_stripes_gradient(self, width, height, cell_h=20, cell_w=2, n=4, y_offset=0):
        """Создает прозрачную сетку 20x2 с белыми углами"""
        # Создаем прозрачный слой
        grid = np.zeros((height, width, 4), dtype=np.uint8)
        # Создаем шаблон для одной ячейки 20*2
        cell = np.zeros((cell_h, cell_w, 4), dtype=np.uint8)

        # Белые пиксели по углам ячейки
        k = 1
        l = 0
        while n > 0 and k > 0:
            for i in range(n):
                for j in range(cell_w):
                    cell[i + l, j] = [255, 255, 255, 255 * k]
            l += n
            n -= 1
            k -= 0.25

        # Заполняем всю сетку повторяющимся паттерном
        for y in range(0 - y_offset % cell_h, height, cell_h):  # Добавляем сдвиг по Y
            for x in range(0, width, cell_w):
                y_end = min(y + cell_h, height)
                x_end = min(x + cell_w, width)
                if y >= 0:  # Проверяем чтобы не выйти за верхнюю границу
                    grid[y:y_end, x:x_end] = cell[:y_end - y, :x_end - x]

        return Image.fromarray(grid)

    def create_pixel_stripes(self, width, height, cell_h=20, n = 4, cell_w=2, y_offset=0):
        """Создает прозрачную сетку 20x2 с белыми углами"""
        # Создаем прозрачный слой
        grid = np.zeros((height, width, 4), dtype=np.uint8)
        # Создаем шаблон для одной ячейки 20*2
        cell = np.zeros((cell_h, cell_w, 4), dtype=np.uint8)

        for i in range(n):
            for j in range(cell_w):
                cell[i, j] = [255, 255, 255, 255]

        for y in range(0 - y_offset % cell_h, height, cell_h):  # Добавляем сдвиг по Y
            for x in range(0, width, cell_w):
                y_end = min(y + cell_h, height)
                x_end = min(x + cell_w, width)
                if y >= 0:  # Проверяем чтобы не выйти за верхнюю границу
                    grid[y:y_end, x:x_end] = cell[:y_end - y, :x_end - x]

        return Image.fromarray(grid)