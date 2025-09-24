import numpy as np
from PIL import Image


def create_pixel_grid(width, height, cell_size=4):
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


def apply_grid_to_image(image_path, output_path, opacity=0.6):
    """Накладывает сетку на изображение"""
    # Открываем основное изображение
    base_image = Image.open(image_path).convert('RGBA')
    width, height = base_image.size

    # Создаем сетку
    grid_layer = create_pixel_grid(width, height)

    # Регулируем непрозрачность сетки
    grid_array = np.array(grid_layer)
    grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
    grid_layer = Image.fromarray(grid_array)

    # Наложение с прозрачностью
    result = Image.alpha_composite(base_image, grid_layer)
    result.save(output_path)


# Использование
apply_grid_to_image('start/input_6.png', 'end/output_7.png')