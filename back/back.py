from PIL import Image, ImageEnhance
from .layers import Pixel
import numpy as np
import cv2


class AdjustmentLayer:
    def __init__(self, image, output_p:str):
        self.image = image
        self.output_p = output_p

    def apply_levels(self, image, in_black=0, gamma=1.0, in_white=255, out_black=0, out_white=255):
        """
           Уровни как в фотошопе
           RGB; 0, 0.50, 255; 0, 255
           """
        # Создаем LUT таблицу преобразования
        lut = np.zeros(256, dtype=np.uint8)

        for i in range(256):
            # 1. Нормализация входного диапазона (0-255 -> 0-1)
            if i <= in_black:
                normalized = 0.0
            elif i >= in_white:
                normalized = 1.0
            else:
                normalized = (i - in_black) / (in_white - in_black)

            # 2. Применение гамма-коррекции (средние тона)
            if gamma != 1.0:
                normalized = normalized ** (1.0 / gamma)

            # 3. Масштабирование в выходной диапазон
            value = normalized * (out_white - out_black) + out_black
            lut[i] = np.clip(value, 0, 255)

        # Применяем LUT ко всем каналам RGB
        return cv2.LUT(image, lut)


    def photoshop(self):
        image_rgb = self.image.convert('RGB')
        image_alpha = self.image.getchannel('A')

        # Превращаю в ЧБ
        image_bw = image_rgb.convert('L')

        self.image = Image.merge("RGBA", (image_bw, image_bw, image_bw, image_alpha))

        # Преобразование для OpenCV
        opencv_image = np.array(self.image)  # Pillow to numpy (уже в RGBA)
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2BGRA)  # RGBA to BGRA

        # Работаем только с цветными каналами (BGR) без альфа
        bgr = opencv_image[:, :, :3]  # Берем только BGR каналы
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)  # BGR to HSV
        h, s, v = cv2.split(hsv)

        # Цветовой тон (Hue) - сдвиг по цветовому кругу
        h = cv2.add(h, 80)  # +80 градусов (0-180 scale в OpenCV)

        # Насыщенность (Saturation) - интенсивность цвета
        s = cv2.add(s, -80)  # -80 единиц насыщенности

        # Обеспечиваем корректные границы значений
        h = np.clip(h, 0, 179)  # Hue: 0-179 в OpenCV
        s = np.clip(s, 0, 255)  # Saturation: 0-255
        v = np.clip(v, 0, 255)  # Value: 0-255

        hsv_modified = cv2.merge([h, s, v])

        bgr_modified = cv2.cvtColor(hsv_modified, cv2.COLOR_HSV2BGR)  # HSV to BGR
        b, g, r = cv2.split(bgr_modified)  # Разделяем на каналы
        a = opencv_image[:, :, 3]  # Альфа-канал из исходного изображения

        r_total = +30 - 20 - 10  # = 0
        g_total = 0 + 40 - 10  # = +30
        b_total = -30 - 20 + 20  # = -30

        b = cv2.add(b, b_total)
        g = cv2.add(g, g_total)
        r = cv2.add(r, r_total)

        # Объединяем каналы обратно
        balanced = cv2.merge([b, g, r, a])

        # Обрезаем значения за пределы 0-255
        balanced = np.clip(balanced, 0, 255).astype(np.uint8)

        opencv_image_rgb = cv2.cvtColor(balanced, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(opencv_image_rgb).convert("RGBA")

        # Применяем яркость и контраст к ЦВЕТНОМУ изображению
        r, g, b, alpha = self.image.split()

        # Работаем с RGB каналами
        image_rgb = Image.merge('RGB', (r, g, b))

        enhancer = ImageEnhance.Brightness(image_rgb)
        image_brightness = enhancer.enhance(0.80)

        enhancer = ImageEnhance.Contrast(image_brightness)
        image_contrast = enhancer.enhance(1.1)

        r_final, g_final, b_final = image_contrast.split()
        self.image = Image.merge('RGBA', (r_final, g_final, b_final, alpha))

        opencv_image = np.array(self.image)  # Pillow to numpy (уже в RGBA)
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2BGRA)  # RGBA to BGRA

        opencv_image_rgb = cv2.cvtColor(
            self.apply_levels(opencv_image, in_black=0, gamma=0.50, in_white=255, out_black=0, out_white=255),
            cv2.COLOR_BGR2RGB)

        self.image = Image.fromarray(opencv_image_rgb)

    def save(self):
        self.image.save(f'{self.output_p}_photoshop.png')


class Grid(Pixel):
    def __init__(self, image, output_p:str):
        self.image = image
        self.output_p = output_p

    def apply_grid_to_image(self, opacity=0.6):
        """Накладывает сетку на изображение"""
        # Открываем основное изображение
        self.image = self.image.convert('RGBA')
        width, height = self.image.size

        # Создаем сетку
        grid_layer = self.create_pixel_grid(width, height)

        # Регулируем непрозрачность сетки
        grid_array = np.array(grid_layer)
        grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
        grid_layer = Image.fromarray(grid_array)

        # Наложение с прозрачностью
        self.image = Image.alpha_composite(self.image, grid_layer)

    def save(self):
        self.image.save(f'{self.output_p}_grid.png')

class Strip(Pixel):
    def __init__(self, image, output_p:str):
        self.image = image
        self.output_p = output_p

    def apply_strip_to_image(self, opacity=0.65, gradient = True):
        """Накладывает сетку на изображение с режимом 'Soft Light'"""
        # Открываем основное изображение
        self.image = self.image.convert('RGBA')
        width, height = self.image.size

        # Создаем сетку
        if gradient:
            grid_layer = self.create_pixel_stripes_gradient(width, height)
            self.output_p += '_gradient'
        else:
            grid_layer = self.create_pixel_stripes(width, height)
            self.output_p += '_ungradient'

        # Регулируем непрозрачность сетки
        grid_array = np.array(grid_layer)
        grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
        grid_layer = Image.fromarray(grid_array)

        # Создаем прозрачный слой для результата
        blended = Image.blend(self.image, grid_layer, alpha=opacity)
        self.image = Image.composite(blended, self.image, grid_layer.split()[3])

    def save(self):
        self.image.save(f'{self.output_p}_strip.png')



class StripAnimation(Pixel):
    def __init__(self, image, output_p:str, frame_duration = 100):
        self.image = image
        self.output_p = output_p
        self.frames = []
        self.frame_duration = frame_duration

    def create_animation(self, n_frames=10, opacity=0.65, gradient = True):
        """Создает GIF с движущимися полосами в режиме Soft Light"""
        self.image = self.image.convert('RGBA')

        if gradient:
            self.output_p += '_gradient'
        else:
            self.output_p += '_ungradient'

        for i in range(n_frames):
            # Создаем полосы со сдвигом

            if gradient:
                grid_layer = self.create_pixel_stripes_gradient(self.image.width, self.image.height, y_offset=i * 2)
            else:
                grid_layer = self.create_pixel_stripes(self.image.width, self.image.height, y_offset=i * 2)

            # Регулируем непрозрачность
            grid_array = np.array(grid_layer)
            grid_array[:, :, 3] = (grid_array[:, :, 3] * opacity).astype(np.uint8)
            grid_layer = Image.fromarray(grid_array)

            # Конвертируем в массивы для Soft Light
            base_arr = np.array(self.image, dtype=np.float32) / 255.0
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

            self.frames.append(Image.fromarray(result.astype(np.uint8)))

    def save(self):
        if self.frames:
            self.frames[0].save(
                f'{self.output_p}_animation.gif',
                save_all=True,
                append_images=self.frames[1:],
                duration=self.frame_duration,
                loop=0
            )
class Noise:
    def __init__(self, image, output_p:str):
        self.image = image
        self.output_p = output_p

    def apply_color_dodge_noise(self, opacity=0.15):
        """Добавляет шум с режимом 'Осветление основы' (Color Dodge)"""
        self.image = self.image.convert('RGB')
        width, height = self.image.size

        # Создаем случайный шум (белый на черном)
        noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        noise_image = Image.fromarray(noise)

        # Конвертируем в float для расчетов
        base_arr = np.array(self.image, dtype=np.float32) / 255.0
        noise_arr = np.array(noise_image, dtype=np.float32) / 255.0

        # Формула Color Dodge (Осветление основы)
        result_arr = base_arr / (1 - noise_arr + 1e-6)  # +1e-6 чтобы избежать деления на 0
        result_arr = np.clip(result_arr, 0, 1)  # Ограничиваем значения 0-1

        # Смешивание с непрозрачностью
        final_arr = base_arr * (1 - opacity) + result_arr * opacity
        final_arr = (final_arr * 255).astype(np.uint8)

        self.image = Image.fromarray(final_arr)

    def save(self):
        self.image.save(f'{self.output_p}_noise.png')
