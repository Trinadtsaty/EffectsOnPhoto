import numpy as np
from PIL import Image

def apply_color_dodge_noise(image_path, output_path, opacity=0.15):
    """Добавляет шум с режимом 'Осветление основы' (Color Dodge)"""
    base_image = Image.open(image_path).convert('RGB')
    width, height = base_image.size

    # Создаем случайный шум (белый на черном)
    noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    noise_image = Image.fromarray(noise)

    # Конвертируем в float для расчетов
    base_arr = np.array(base_image, dtype=np.float32) / 255.0
    noise_arr = np.array(noise_image, dtype=np.float32) / 255.0

    # Формула Color Dodge (Осветление основы)
    result_arr = base_arr / (1 - noise_arr + 1e-6)  # +1e-6 чтобы избежать деления на 0
    result_arr = np.clip(result_arr, 0, 1)  # Ограничиваем значения 0-1

    # Смешивание с непрозрачностью
    final_arr = base_arr * (1 - opacity) + result_arr * opacity
    final_arr = (final_arr * 255).astype(np.uint8)

    Image.fromarray(final_arr).save(output_path)

# Использование
apply_color_dodge_noise('start/input_7.png', 'end/output_8.png', opacity=0.15)