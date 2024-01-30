# -*- coding: utf-8 -*-
"""
Для конвертации SVG-файлов в PDF и PNG:
(1 способ - смотри README)
1. установить ImageMagick по ссылке:
Для Windows:
https://imagemagick.org/script/download.php#windows
(Для Linux: sudo apt-get install imagemagick
Для macOS: brew install imagemagick)
2. затем библиотеку Wand - включена в requirements.txt
"""

from wand.image import Image as WandImage
from wand.color import Color
from wand.drawing import Drawing

from config import svg_templates_files_folder, dim_scale

import numpy as np
from PIL import Image as PilImage
import os


# Временный рендер надписи для определения размера
def getTextSize(text='тест 0000', font_size=13, bold=False, save=True):
    getTextSize.i = 0 if not hasattr(getTextSize, 'i') else getTextSize.i + 1  # iterator

    draw = Drawing()
    draw.fill_color = Color("black")

    draw.font_size = height = round(font_size*dim_scale)
    draw.font_weight = 700 if bold else 400

    text_image = WandImage(width=20*len(text), height=height, background=Color("white"))

    metrics = draw.get_font_metrics(text_image, text, multiline=False)

    real_width = round(metrics.x)-1
    real_height = round(metrics.y2 - metrics.y1)

    print(f'#{getTextSize.i}:', text, [real_width, real_height])

    if save:

        y = height + int(metrics.descender)  # позиционирование текста по верхнему краю холста

        draw.text(0, y, text)
        draw.draw(text_image)

        # Преобразование изображения в массив NumPy (255 оттенков серого)
        np_img = np.array(text_image)[:, :, 0]

        # Определение границ текста на холсте
        rows = np.any(np_img < 255, axis=1)
        cols = np.any(np_img < 255, axis=0)
        min_row, max_row = np.where(rows)[0][[0, -1]]
        min_col, max_col = np.where(cols)[0][[0, -1]]

        # Обрезка изображения
        trimmed_img = np_img[min_row:max_row + 1, min_col:max_col + 1]

        # Преобразование обрезанного изображения в целочисленный тип, затем в PIL Image
        trimmed_img = trimmed_img.astype(np.uint8)
        bitmap_image = PilImage.fromarray(trimmed_img, mode='L')

        filename = os.path.join(svg_templates_files_folder, 'temp', f'text_to_image_{getTextSize.i}.png')
        bitmap_image.save(filename)

    return real_width, real_height, metrics.y2
