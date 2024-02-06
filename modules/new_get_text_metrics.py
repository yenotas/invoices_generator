"""
Конвертер SVG-файлов в PNG:
- читаю шрифты из папки в массив
- выбираю шрифт
- читаю свг: если есть группы - разбиваю и перечитываю.
- если есть таблица - определяю по координатам, что к ней относится и определяю в нулевую группу

- стили и размеры сохраняю


"""

from wand.image import Image as WandImage
from wand.color import Color
from wand.drawing import Drawing

from config import text_fragments_folder, dim_scale, save_text_fragments

import numpy as np
from PIL import Image as PilImage
import shutil
import os

if save_text_fragments:
    target_folder = text_fragments_folder
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    os.makedirs(target_folder, exist_ok=True)


# Временный рендер надписи для определения размера
def getTextSize(text='тест 0000', font_size=13, bold=False, save=save_text_fragments):
    getTextSize.i = 0 if not hasattr(getTextSize, 'i') else getTextSize.i + 1  # iterator

    draw = Drawing()
    draw.fill_color = Color("black")

    draw.font_size = height = round(font_size*dim_scale)
    draw.font_weight = 700 if bold else 400

    # print(getTextSize.i, text)

    text_image = WandImage(width=20*len(text), height=height, background=Color("white"))

    metrics = draw.get_font_metrics(text_image, text, multiline=False)

    real_width = round(metrics.x)-1
    real_height = round(metrics.y2 - metrics.y1)

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

        # Обрезка холста по границам текста
        trimmed_img = np_img[min_row:max_row + 1, min_col:max_col + 1]

        # Преобразование обрезанного изображения в целочисленный тип, затем в PIL Image
        trimmed_img = trimmed_img.astype(np.uint8)
        bitmap_image = PilImage.fromarray(trimmed_img, mode='L')

        filename = os.path.join(text_fragments_folder, f'text_to_image_{getTextSize.i}.png')
        bitmap_image.save(filename)

        print(f'#{getTextSize.i}:', text, [real_width, real_height])

    return real_width, real_height, metrics.y2
