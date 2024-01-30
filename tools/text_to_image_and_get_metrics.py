from wand.image import Image as WandImage
from wand.color import Color
from wand.drawing import Drawing

from config import svg_templates_files_folder, font_path

import numpy as np
from PIL import Image as PilImage
import os

img = WandImage(width=700, height=30, background=Color("white"))
dim_scale = 2


# Временный рендер надписи для определения размера
def getTextSize(text='Тестовая строка 5701', font_size=13, bold=False):
    getTextSize.i = 0 if not hasattr(getTextSize, 'i') else getTextSize.i + 1

    draw = Drawing()
    draw.fill_color = Color("black")

    draw.font_size = height = round(font_size*dim_scale)
    draw.font_weight = 700 if bold else 400

    m = draw.get_font_metrics(img, text)
    width = int(m.text_width)

    text_image = WandImage(width=width, height=height, background=Color("white"))
    metrics = draw.get_font_metrics(text_image, text, multiline=False)
    y = height + int(metrics.descender)
    width = round(metrics.x)
    draw.text(0, y, text)

    draw.draw(text_image)

    # Преобразование изображения в массив NumPy
    # np_img = np.array(text_image)[:, :, 0]
    #
    # # Вычисление реальной ширины текста
    # non_zero_columns = np.where(np_img.max(axis=0) > 0)
    # real_width = non_zero_columns[0][-1] - non_zero_columns[0][0] + 1
    #
    # # Вычисление высоты текста
    # non_zero_rows = np.where(np_img.max(axis=1) > 0)
    # real_height = non_zero_rows[0][-1] - non_zero_rows[0][0] + 1
    #
    # # Обрезание изображения
    # trimmed_img = np_img[non_zero_rows[0][0]:non_zero_rows[0][-1] + 1,
    #                      non_zero_columns[0][0]:non_zero_columns[0][-1] + 1]
    #
    # trimmed_img = trimmed_img.astype(np.uint8)  # Преобразование в целочисленный тип
    # bitmap_image = PilImage.fromarray(trimmed_img, mode='L')

    filename = os.path.join(svg_templates_files_folder, 'temp', f'000_{getTextSize.i}.png')

    text_image.format = 'png'
    text_image.save(filename=filename)
    # bitmap_image.save(filename)

    print(getTextSize.i, text, width, height)

    # Сохранение изображения в файл
    # bitmap_image.save(filename)



getTextSize("Клиновой анкер Tech-Krep 10х120 1 шт - пакет", 12)
getTextSize("Семьсот шестьдесят шесть тысяч семьсот сорок семь тенге 78 тиынов", 13, True)
