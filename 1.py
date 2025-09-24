from PIL import Image
import numpy as np
import cv2

image = Image.open("start/photoshop_input.png").convert("RGBA")
# image.save("start/input.png")
image_png = image.convert("RGBA")  # Эквивалент PNG с прозрачностью
# Открываем изображение и сразу разделяем на RGB и альфа-канал
image_rgb = image_png.convert('RGB')
image_alpha = image_png.getchannel('A')  # Извлекаем только альфа-канал

# Работаем только с RGB-частью
image_bw = image_rgb.convert('L')  # Преобразуем в черно-белое

# Цветовой баланс Через танцы с бубном

# После вашего кода
image_bw_rgba = Image.merge("RGBA", (image_bw, image_bw, image_bw, image_alpha))

# image_bw_rgba.save("end/output_LA.png")

# Преобразование для OpenCV
opencv_image = np.array(image_bw_rgba)  # Pillow to numpy (уже в RGBA)
opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2BGRA)  # RGBA to BGRA

b, g, r, a = cv2.split(opencv_image)  # Разделяем на каналы

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
pil_image.save("end/output_3.png")
