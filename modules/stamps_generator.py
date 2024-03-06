"""
Генератор круглых печатей с синтетическими данными.
Автор: Коваленко А.В. 12.2023
https://github.com/yenotas/invoices_generator
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import numpy as np
import cv2
from config import normal_fonts, stamp_size
import os


font_path = normal_fonts['Arial']


def drawTextAroundCircle(image, draw, text, radius, center, font, color, start_angle=-math.pi / 2):
    angle_per_letter = 2 * math.pi / len(text)
    for i, letter in enumerate(text):
        angle = angle_per_letter * i + start_angle
        bbox = draw.textbbox((0, 0), letter, font=font)
        letter_width, letter_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        x = center[0] + radius * math.cos(angle) - letter_width / 2
        y = center[1] + radius * math.sin(angle) - letter_height / 2

        rotated_letter = Image.new('RGBA', (letter_width, letter_height), (0, 0, 0, 0))
        rotated_draw = ImageDraw.Draw(rotated_letter)
        rotated_draw.text((-bbox[0], -bbox[1]), letter, font=font, fill=color)
        rotated_letter = rotated_letter.rotate(-math.degrees(angle + math.pi/2), expand=1)

        # Вставляем повернутую букву на изображение
        image.paste(rotated_letter, (int(x), int(y)), rotated_letter)


def drawCenterText(draw, text, center, font, color):
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    x = center[0] - text_width / 2
    y = center[1] - text_height / 2
    draw.text((x, y), text, font=font, fill=color)


def generateRandomColor():
    # Генерируем случайные значения для RGB
    r = random.randint(0, 50)
    g = random.randint(0, 100)
    b = random.randint(g+100, 255)  # Высокий синий всегда больше зеленого
    return f'#{r:02x}{g:02x}{b:02x}'


def generateStamp(text_outer_circle, text_inner_circle, text_center):
    # Параметры изображения и текста

    center = (int(stamp_size / 2), int(stamp_size / 2))
    font_by_circle = ImageFont.truetype(font_path, int(18 / 328 * stamp_size))
    font_by_center = ImageFont.truetype(font_path, int(45 / 328 * stamp_size))

    # Тексты
    text_color = generateRandomColor()
    radius_outer = int(160 / 328 * stamp_size)
    radius_inner = int(90 / 328 * stamp_size)
    max_width = 0.8 * radius_inner / 328 * stamp_size

    # Создание изображения
    bg_color = (255, 255, 255, 0)  # Прозрачный для PNG, (255, 255, 255) для непрозрачного белого фона
    image = Image.new('RGBA', (stamp_size, stamp_size), bg_color)
    draw = ImageDraw.Draw(image)
    k = int(8 / 328 * stamp_size)
    # Рисуем окружности
    draw.ellipse([center[0]-radius_outer, center[1]-radius_outer, center[0]+radius_outer, center[1]+radius_outer],
                 outline=text_color, width=int(4/328*stamp_size))
    draw.ellipse([center[0]-radius_outer+k, center[1]-radius_outer+k, center[0]+radius_outer-k, center[1]+radius_outer-k],
                 outline=text_color, width=int(4/328*stamp_size))
    draw.ellipse([center[0]-radius_inner, center[1]-radius_inner, center[0]+radius_inner, center[1]+radius_inner],
                 outline=text_color, width=int(3/328*stamp_size))

    # Рисуем тексты
    drawTextAroundCircle(image, draw, text_outer_circle, radius_outer - 25 / 328 * stamp_size, center, font_by_circle, text_color)
    drawTextAroundCircle(image, draw, text_inner_circle, radius_inner + 20 / 328 * stamp_size, center, font_by_circle, text_color)
    drawCenterText(draw, text_center, center, font_by_center, text_color)

    # Масштабируем изображение вверх
    scale_factor = 5  # множитель масштабирования
    new_size = stamp_size * scale_factor
    large_image = image.resize((new_size, new_size), Image.NEAREST)

    # Применяем размытие для сглаживания
    large_image = large_image.filter(ImageFilter.GaussianBlur(radius=int(4/328*stamp_size)))

    # Поворачиваем изображение
    angle = random.randint(0, 270)
    new_image = Image.new("RGBA", large_image.size, bg_color)
    new_image.paste(large_image, (0, 0))
    rotated_image = new_image.rotate(angle, expand=False)

    # Масштабируем изображение вниз
    final_image = rotated_image.resize((stamp_size, stamp_size), Image.LANCZOS)

    return final_image
