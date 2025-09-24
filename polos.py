import numpy as np
from PIL import Image


def create_pixel_stripes(width, height, cell_h = 20, cell_w = 2, n = 4, y_offset = 0):
    """Создает прозрачную сетку 20x2 с белыми углами"""
    # Создаем прозрачный слой
    grid = np.zeros((height, width, 4), dtype=np.uint8)

    # Создаем шаблон для одной ячейки 20*2
    cell = np.zeros((cell_h, cell_w, 4), dtype=np.uint8)

    # Белые пиксели по углам ячейки
    k=1
    l = 0
    while n > 0 and k > 0:
        for i in range(n):
            for j in range(cell_w):
                cell[i+l,j] = [255,255,255,255*k]
        l += n
        n -= 1
        k -= 0.25

    # Заполняем всю сетку повторяющимся паттерном
    for y in range(0-y_offset % cell_h, height, cell_h): # Добавляем сдвиг по Y
        for x in range(0, width, cell_w):
            y_end = min(y + cell_h, height)
            x_end = min(x + cell_w, width)
            if y >= 0:  # Проверяем чтобы не выйти за верхнюю границу
                grid[y:y_end, x:x_end] = cell[:y_end - y, :x_end - x]

    return Image.fromarray(grid)


def apply_strip_to_image(image_path, output_path, opacity=0.65):
    """Накладывает сетку на изображение с режимом 'Soft Light'"""
    # Открываем основное изображение
    base_image = Image.open(image_path).convert('RGBA')
    width, height = base_image.size

    # Создаем сетку
    grid_layer = create_pixel_stripes(width, height)

    # Регулируем непрозрачность сетки
    grid_array = np.array(grid_layer)
    grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
    grid_layer = Image.fromarray(grid_array)

    # Создаем прозрачный слой для результата
    result = Image.new('RGBA', base_image.size)

    # Наложение с режимом 'Soft Light'
    result = Image.blend(base_image, grid_layer, alpha=opacity)
    result = Image.composite(grid_layer, base_image, grid_layer.split()[3])  # Soft Light эмуляция
    result.save(output_path)

def create_animation(base_image_path, output_gif, n_frames=10, frame_duration=100, opacity=0.65):
    """Создает GIF с движущимися полосами"""
    # Загружаем базовое изображение
    base_image = Image.open(base_image_path).convert('RGBA')
    frames = []

    for i in range(n_frames):
        # Создаем полосы со сдвигом (2 пикселя вниз за кадр)
        grid_layer = create_pixel_stripes(base_image.width, base_image.height, y_offset=i*2)

        # Регулируем непрозрачность
        grid_array = np.array(grid_layer)
        grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
        grid_layer = Image.fromarray(grid_array)

        # Наложение на базовое изображение
        result = Image.new('RGBA', base_image.size)
        result = Image.composite(grid_layer, base_image, grid_layer.split()[3])
        frames.append(result)

        # Сохраняем GIF
        frames[0].save(
            output_gif,
            save_all=True,
            append_images=frames[1:],
            duration=frame_duration,
            loop=0
        )


def apply_strip_to_SoftLight(image_path, output_path, opacity=0.65):
    """Накладывает сетку на изображение с режимом 'Soft Light'"""
    base_image = Image.open(image_path).convert('RGBA')
    width, height = base_image.size

    # Создаем сетку
    grid_layer = create_pixel_stripes(width, height)

    # Регулируем непрозрачность сетки
    grid_array = np.array(grid_layer)
    grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
    grid_layer = Image.fromarray(grid_array)

    # Конвертируем в массивы для обработки
    base_arr = np.array(base_image, dtype=np.float32) / 255.0
    overlay_arr = np.array(grid_layer, dtype=np.float32) / 255.0

    # Формула Soft Light
    result_arr = np.where(overlay_arr[:, :, :3] <= 0.5,
                          2 * base_arr[:, :, :3] * overlay_arr[:, :, :3] +
                          base_arr[:, :, :3] * base_arr[:, :, :3] * (1 - 2 * overlay_arr[:, :, :3]),
                          2 * base_arr[:, :, :3] * (1 - overlay_arr[:, :, :3]) +
                          np.sqrt(base_arr[:, :, :3]) * (2 * overlay_arr[:, :, :3] - 1))

    # Альфа-композиция
    alpha = overlay_arr[:, :, 3:4]
    final_rgb = result_arr * alpha + base_arr[:, :, :3] * (1 - alpha)

    # Собираем результат
    result = (final_rgb * 255).astype(np.uint8)
    result = np.dstack((result, base_arr[:, :, 3] * 255))  # Альфа из базового изображения

    Image.fromarray(result.astype(np.uint8)).save(output_path)

def create_animation_SoftLight(base_image_path, output_gif, n_frames=10, frame_duration=100, opacity=0.65):
    """Создает GIF с движущимися полосами в режиме Soft Light"""
    base_image = Image.open(base_image_path).convert('RGBA')
    frames = []

    for i in range(n_frames):
        # Создаем полосы со сдвигом
        grid_layer = create_pixel_stripes(base_image.width, base_image.height, y_offset=i*2)

        # Регулируем непрозрачность
        grid_array = np.array(grid_layer)
        grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
        grid_layer = Image.fromarray(grid_array)

        # Конвертируем в массивы для Soft Light
        base_arr = np.array(base_image, dtype=np.float32) / 255.0
        overlay_arr = np.array(grid_layer, dtype=np.float32) / 255.0

        # Формула Soft Light
        result_arr = np.where(overlay_arr[:, :, :3] <= 0.5,
                              2 * base_arr[:, :, :3] * overlay_arr[:, :, :3] +
                              base_arr[:, :, :3] * base_arr[:, :, :3] * (1 - 2 * overlay_arr[:, :, :3]),
                              2 * base_arr[:, :, :3] * (1 - overlay_arr[:, :, :3]) +
                              np.sqrt(base_arr[:, :, :3]) * (2 * overlay_arr[:, :, :3] - 1))

        # Альфа-композиция
        alpha = overlay_arr[:, :, 3:4]
        final_rgb = result_arr * alpha + base_arr[:, :, :3] * (1 - alpha)

        # Собираем результат
        result = (final_rgb * 255).astype(np.uint8)
        result = np.dstack((result, base_arr[:, :, 3] * 255))

        frames.append(Image.fromarray(result.astype(np.uint8)))

    # Сохраняем GIF (ВНЕ цикла)
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0
    )


# Использование
create_animation_SoftLight('start/input_8.png', 'end/animation_2.gif', n_frames=10, frame_duration=100, opacity=0.65)
# create_animation('start/input_8.png', 'end/animation_1.gif', n_frames=10, frame_duration=100)
# apply_strip_to_SoftLight('start/input_7.png', 'end/output_9.png', opacity=0.65)
# apply_strip_to_image('start/input_7.png', 'end/output_9.png', opacity=0.25)
# create_pixel_stripes(1000,1000, 20, 4)
