from PIL import Image, ImageEnhance
import numpy as np
import cv2

def apply_levels(image, in_black=0, gamma=1.0, in_white=255, out_black=0, out_white=255):
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


# Открытие изображения
image = Image.open("start/photoshop_input.png").convert("RGBA")  # Загружает изображение в объект Image
image_rgb = image.convert('RGB')
image_alpha = image.getchannel('A')

# Работаем только с RGB-частью
image_bw = image_rgb.convert('L')  # Преобразуем в черно-белое

image_bw_rgba = Image.merge("RGBA", (image_bw, image_bw, image_bw, image_alpha))

# Преобразование для OpenCV
opencv_image = np.array(image_bw_rgba)  # Pillow to numpy (уже в RGBA)
opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2BGRA)  # RGBA to BGRA

# Работаем только с цветными каналами (BGR) без альфа
bgr = opencv_image[:,:,:3]  # Берем только BGR каналы

hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)  # BGR to HSV
h, s, v = cv2.split(hsv)

# Цветовой тон (Hue) - сдвиг по цветовому кругу
h = cv2.add(h, 80)  # +80 градусов (0-180 scale в OpenCV)
# Пояснение: Сдвигает все цвета по спектру (как поворот цветового круга)

# Насыщенность (Saturation) - интенсивность цвета
s = cv2.add(s, -80)  # -80 единиц насыщенности
# Пояснение: Уменьшает интенсивность цветов (-80 = более блеклые цвета)

# Яркость (Value) - не меняем (0)

# Обеспечиваем корректные границы значений
h = np.clip(h, 0, 179)  # Hue: 0-179 в OpenCV
s = np.clip(s, 0, 255)  # Saturation: 0-255
v = np.clip(v, 0, 255)  # Value: 0-255

hsv_modified = cv2.merge([h, s, v])

bgr_modified  = cv2.cvtColor(hsv_modified, cv2.COLOR_HSV2BGR) # HSV to BGR
b, g, r = cv2.split(bgr_modified)  # Разделяем на каналы
a = opencv_image[:,:,3]  # Альфа-канал из исходного изображения


r_total = +30 -20 -10    # = 0
g_total = 0 +40 -10      # = +30
b_total = -30 -20 +20    # = -30

b = cv2.add(b, b_total)
g = cv2.add(g, g_total)
r = cv2.add(r, r_total)

# Объединяем каналы обратно
balanced = cv2.merge([b, g, r, a])

# Обрезаем значения за пределы 0-255
balanced = np.clip(balanced, 0, 255).astype(np.uint8)

opencv_image_rgb = cv2.cvtColor(balanced, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(opencv_image_rgb)


pil_image.save("end/output_4.png")
pil_image = pil_image.convert("RGBA")

# Применяем яркость и контраст к ЦВЕТНОМУ изображению
r, g, b, alpha = pil_image.split()

# Работаем с RGB каналами
image_rgb = Image.merge('RGB', (r, g, b))

enhancer = ImageEnhance.Brightness(image_rgb)
image_brightness = enhancer.enhance(0.80)

enhancer = ImageEnhance.Contrast(image_brightness)
image_contrast = enhancer.enhance(1.1)

# Собираем финальное изображение с исходным альфа-каналом
r_final, g_final, b_final = image_contrast.split()
final_image = Image.merge('RGBA', (r_final, g_final, b_final, alpha))
final_image.save("end/output_5.png")

opencv_image = np.array(final_image)  # Pillow to numpy (уже в RGBA)
opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2BGRA)  # RGBA to BGRA

opencv_image_rgb = cv2.cvtColor(apply_levels(opencv_image, in_black=0, gamma=0.50, in_white=255, out_black=0, out_white=255), cv2.COLOR_BGR2RGB)
final_image = Image.fromarray(opencv_image_rgb)

final_image.save("end/output_6.png")