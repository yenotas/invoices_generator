"""
Рендер текстовых вставок, определение размеров и координат надписей в растре
https://github.com/yenotas/invoices_generator
"""

from config import text_fragments_folder, dim_scale, save_text_fragments
from config import normal_fonts, bold_fonts, italic_fonts, italic_bold_fonts

import numpy as np
from PIL import Image as PilImage, ImageFont, ImageDraw
import os
import random


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


# Вычисление размеров текстовой надписи и отступа по У от базовой линии в растре
def getTextSize(text='Iq', font=None, font_size=13, bold=False):

    font_name, normal_font, bold_font = getRandomFont('') if not font else font[0], font[1], font[2]

    font_path = bold_font if bold else normal_font

    font = ImageFont.truetype(font_path, size=font_size)
    img = PilImage.new('L', font.getbbox(text)[2:4], color=255)
    imgDraw = ImageDraw.Draw(img)
    imgDraw.text((0, 0), text, fill=0, font=font)
    textbbox = imgDraw.textbbox((0, 0), text, font=font)

    img = drawText(img)

    text_width = textbbox[2] - textbbox[0]
    text_height = textbbox[3] - textbbox[1] + 1

    return text_width, text_height, font_size - textbbox[1] - 1, img


# Определение координат размещения текста в растре,
# обрезка и сохранение фрагментов при включенном save_text_fragments
def getTextMetrics(text_elem, font, font_sizes, font_weights, save=save_text_fragments):

    getTextMetrics.i = 0 if not hasattr(getTextMetrics, 'i') else getTextMetrics.i + 1  # iterator

    text_dir = {'right': -1,  # коэффициент для вычисления центра надписи
                'center': 0}  # в зависимости от выравнивания текста
    align = 1  # Коэффициент для левого выравнивания текста
    font_class = 'fnt5'
    classes = text_elem.get('class', '').split(' ')
    if len(classes) > 1:
        font_class = classes[1]
        if len(classes) > 2:
            align = text_dir[classes[2]]

    font_size = round(font_sizes[font_class] / 100 * dim_scale)
    bold = font_weights[font_class]
    text = text_elem.string.strip()

    tw, th, shift, img = getTextSize(text, font, font_size, bold)
    x = round(float(text_elem['x']) / 100 * dim_scale)
    cx = round(x + align * tw / 2)
    y = round(float(text_elem['y']) / 100 * dim_scale - shift)
    cy = round(y + th / 2)

    if save == 1:
        # print(text, 'x,y:', (x, y), 'w, h:', tw, th)
        filename = os.path.join(text_fragments_folder, f'text_{getTextMetrics.i}.png')
        img.save(filename)

    return [[cx, cy, tw, th], [x, y, tw, th], img, font_size, bold, align]


def getElementClasses(elem):
    classes = elem.get('class', '').split(' ')
    if len(classes) >= 1:
        return classes
    else:
        return []


def getRandomFont(font_name):
    if not font_name:
        font_name = random.choice(list(normal_fonts.keys()))
    res = [font_name, normal_fonts[font_name], bold_fonts[font_name]]
    if italic_fonts.get(font_name, None) and italic_bold_fonts.get(font_name, None) and random.randint(0, 1) == 0:
        res = [font_name, italic_fonts[font_name], italic_bold_fonts[font_name]]
    return res


def unpackClassesSVG(base_soup):
    style_content = base_soup.find('style').string if base_soup.find('style') else ''
    font_sizes, font_weights, line_widths = {}, {}, {}
    for line in style_content.split('\n'):
        if '.fnt' in line:
            class_name = line.split('{')[0].strip().replace('.', '')
            font_size = next((float(value.split(':')[1].replace('px', '').strip())
                              for value in line.split('{')[1].split(';') if 'font-size' in value), 1200)
            font_sizes[class_name] = round(font_size / 100) * 100
            font_weight = next((value.split(':')[1].strip()
                             for value in line.split('{')[1].split(';') if 'font-weight' in value), 'regular')
            font_weights[class_name] = True if font_weight == 'bold' else False
        if '.str' in line:
            class_name = line.split('{')[0].strip().replace('.', '')
            line_width = next((value.split(':')[1].strip()
                             for value in line.split('{')[1].split(';') if 'stroke-width' in value), '100')
            line_widths[class_name] = line_width

    return font_sizes, font_weights, line_widths

