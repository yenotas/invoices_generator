"""
Временный рендер надписи для определения размеров и координат текстовых вставок в растр
"""

from config import text_fragments_folder, dim_scale, save_text_fragments, font_path, bold_font_path

import numpy as np
from PIL import Image as PilImage, ImageFont, ImageDraw
import os


def drawText(img):
    # Преобразование изображения в массив NumPy
    np_img = np.array(img)
    # Определение границ текста на холсте
    rows = np.any(np_img < 255, axis=1)
    cols = np.any(np_img < 255, axis=0)
    min_row, max_row = np.where(rows)[0][[0, -1]]
    min_col, max_col = np.where(cols)[0][[0, -1]]
    # Обрезка холста по границам текста
    trimmed_img = np_img[min_row:max_row + 1, min_col:max_col + 1]
    # Преобразование обрезанного изображения в целочисленный тип, затем в PIL Image
    trimmed_img = trimmed_img.astype(np.uint8)
    img = PilImage.fromarray(trimmed_img, mode='L')
    return img


# Вычисляю координаты центра и метрики текстовой надписи в растре
def getTextSize(text='тест Pp', font_size=13, bold=False):

    font_size = font_size*dim_scale
    f_path = bold_font_path if bold else font_path
    font = ImageFont.truetype(f_path, size=font_size)
    img = PilImage.new('L', font.getbbox(text)[2:4], color=255)
    imgDraw = ImageDraw.Draw(img)
    imgDraw.text((0, 0), text, fill=0, font=font)
    textbbox = imgDraw.textbbox((0, 0), text, font=font)

    text_width = textbbox[2] - textbbox[0]
    text_height = textbbox[3] - textbbox[1] + 1

    return text_width, text_height, font_size - textbbox[1] - 1, img


def getTextMetrics(text_elem, f_sizes, f_weights):

    getTextMetrics.i = 0 if not hasattr(getTextMetrics, 'i') else getTextMetrics.i + 1  # iterator

    text_dir = {'right': -1,  # коэффициент для вычисления центра надписи
                'center': 0}  # в зависимости от выравнивания текста
    align = 1  # Коэффициент для левого выравнивания текста
    font_class = '.fnt5'
    classes = text_elem.get('class', '').split(' ')
    if len(classes) > 1:
        font_class = '.' + classes[1]
        if len(classes) > 2:
            align = text_dir.get(classes[2], 1)

    font_size = f_sizes.get(font_class, 1300)
    bold = f_weights.get(font_class, False)
    text = text_elem.string.strip()

    tw, th, shift, bitmap = getTextSize(text, round(font_size / 100), bold)
    x = round(float(text_elem['x']) / 100 * dim_scale)
    cx = round(x + align * tw / 2)
    y = round(float(text_elem['y']) / 100 * dim_scale - shift)
    cy = round(y + th / 2)

    if save_text_fragments:
        print(text, 'x,y:', (x, y), 'w, h:', tw, th)
        filename = os.path.join(text_fragments_folder, f'text_{getTextMetrics.i}.png')
        img = drawText(bitmap)
        img.save(filename)

    return [[cx, cy, tw, th], [x, y, tw, th], font_size, bold, align]


def getFontClass(elem):
    classes = elem.get('class', '').split(' ')
    if len(classes) > 1:
        return classes[1]
    else:
        return 'fnt5'


def unpackClassesSVG(base_soup):
    style_content = base_soup.find('style').string if base_soup.find('style') else ''
    font_sizes, font_weights, line_widths = {}, {}, {}
    for line in style_content.split('\n'):
        if '.fnt' in line:
            class_name = line.split('{')[0].strip()
            font_size = next((float(value.split(':')[1].replace('px', '').strip())
                              for value in line.split('{')[1].split(';') if 'font-size' in value), 1200)
            font_sizes[class_name] = round(font_size / 100) * 100
            font_weight = next((value.split(':')[1].strip()
                             for value in line.split('{')[1].split(';') if 'font-weight' in value), 'normal')
            font_weights[class_name] = True if font_weight == 'bold' else False
        if '.str' in line:
            class_name = line.split('{')[0].strip()
            line_width = next((value.split(':')[1].strip()
                             for value in line.split('{')[1].split(';') if 'stroke-width' in value), '100')
            line_widths[class_name] = line_width

    return font_sizes, font_weights, line_widths

