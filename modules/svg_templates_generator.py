# -*- coding: utf-8 -*-
"""
Генератор SVG-файлов счетов из JSON + конвертер в PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 11.2023

Для конвертации SVG-файлов в PDF и PNG:
(1 способ - смотри README)
1. установить ImageMagick по ссылке:
Для Windows:
https://imagemagick.org/script/download.php#windows
(Для Linux: sudo apt-get install imagemagick
Для macOS: brew install imagemagick)
2. затем библиотеку Wand - включена в requirements.txt
"""

from config import svg_templates_files_folder, dim_scale, temp_folder, font_path

import os
from bs4 import BeautifulSoup

from wand.image import Image as WandImage
from wand.color import Color
from wand.drawing import Drawing

import numpy as np
# from PIL import Image as PilImage


text_dir = {'right': -1, 'center': 0}  # коэффициент для вычисления центра надписи в зависимости от выравнивания текста
font_sizes = {}
font_weights = {}


# Временный рендер надписи для определения размера
def getTextSize(text, font_size, bold=False):
    getTextSize.i = 0 if not hasattr(getTextSize, 'i') else getTextSize.i + 1  # iterator

    draw = Drawing()
    draw.fill_color = Color("black")

    draw.font_size = height = round(font_size*dim_scale)
    draw.font_weight = 700 if bold else 400

    text_image = WandImage(width=20*len(text), height=height, background=Color("white"))

    metrics = draw.get_font_metrics(text_image, text, multiline=False)
    y = height + int(metrics.descender)  # позиционирование текста по верхнему краю холста

    draw.text(0, y, text)
    draw.draw(text_image)

    # Преобразование изображения в массив NumPy
    np_img = np.array(text_image)[:, :, 0]

    # Определение границ текста
    rows = np.any(np_img < 255, axis=1)
    cols = np.any(np_img < 255, axis=0)
    min_row, max_row = np.where(rows)[0][[0, -1]]
    min_col, max_col = np.where(cols)[0][[0, -1]]

    # Вычисление ширины и высоты обрезанного изображения
    real_width = max_col - min_col + 1
    real_height = max_row - min_row + 1

    # # Обрезание изображения
    # trimmed_img = np_img[min_row:max_row + 1, min_col:max_col + 1]
    # # Преобразование обрезанного изображения в целочисленный тип, затем в PIL Image
    # trimmed_img = trimmed_img.astype(np.uint8)
    # bitmap_image = PilImage.fromarray(trimmed_img, mode='L')
    # filename = os.path.join(svg_templates_files_folder, 'temp', f'000_{getTextSize.i}.png')
    # bitmap_image.save(filename)
    # print(f'#{getTextSize.i}:', text, [real_width, real_height])

    return real_width, real_height, y


# Вычисляю координаты центра и метрики текстовой надписи
def getTextMetrics(text_elem):

    align = 1  # Коэффициент для левого выравнивания текста
    font_class = '.fnt5'
    classes = text_elem.get('class', '').split(' ')
    if len(classes) > 1:
        font_class = '.' + classes[1]
        if len(classes) > 2:
            align = text_dir.get(classes[2], 1)

    font_size = font_sizes.get(font_class, 1300)
    bold = font_weights.get(font_class, False)
    text = text_elem.string.strip()

    tw, th, shift = getTextSize(text, round(font_size / 100), bold)
    x = round(float(text_elem['x']) / 100 * dim_scale)
    cx = round(x + align * tw / 2)
    y = round(float(text_elem['y']) / 100 * dim_scale - shift)
    cy = round(y + th / 2)

    return [[cx, cy, tw, th], font_size, bold, align]


def getFontClass(elem):
    classes = elem.get('class', '').split(' ')
    if len(classes) > 1:
        return classes[1]
    else:
        return 'fnt5'


# Создание SVG-файлов из JSON-данных по шаблону эталонного SVG-файла
def generateSvgTemplates(json_data, base_svg_file):

    with open(base_svg_file, 'r', encoding='utf-8') as svg_file:
        base_soup = BeautifulSoup(svg_file, 'xml')

    soup_string = str(base_soup)  # клон чистого svg

    # Разбор стилей
    style_content = base_soup.find('style').string if base_soup.find('style') else ''

    global font_sizes, font_weights

    for line in style_content.split('\n'):
        if '.fn' in line:
            class_name = line.split('{')[0].strip()
            font_size = next((float(value.split(':')[1].replace('px', '').strip())
                              for value in line.split('{')[1].split(';') if 'font-size' in value), 1200)
            font_sizes[class_name] = round(font_size/100)*100
            font_weight = next((value.split(':')[1].strip()
                                for value in line.split('{')[1].split(';') if 'font-weight' in value), 'normal')
            font_weights[class_name] = True if font_weight == 'bold' else False
            # font_weight = next((value.split(':')[1].strip()
            #                     for value in line.split('{')[1].split(';') if 'font-family' in value), 'FontNormal')
            # font_weights[class_name] = True if 'FontBold' in font_weight else False

    for invoice in json_data:

        invoice['bbox_cx_cy_w_h'] = {}  # раздел метрик вставляемых текстовых надписей

        base_keys = [key for key in invoice if key != 'itemsList']  # подстановки вокруг таблицы
        items = [item for item in invoice['itemsList']]  # подстановки в таблице товаров и услуг

        soup = BeautifulSoup(soup_string, 'xml')  # рабочий суп
        root_svg = soup.find('svg')

        # Находим горизонтальные и вертикальные линии в таблице товаров
        horizontal_lines = soup.select("line[class*='horizontal_line']")
        vertical_lines = soup.select("line[class*='vertical_line']")
        stamp_line = soup.select("line[class*='stamp_line']")[0]
        magnet_stamp_y = float(stamp_line['y1'])/100  # позиция У для прицеливания штампа

        # Параметры первой строки
        text_item = soup.find('text', string=lambda text: f'_name_' in text)
        class_name = text_item.get('class', '').split(' ')[1]
        font_size = font_sizes['.'+class_name]
        table_line_height = font_size * 1.2

        # Считаю прирост по Y после сдвига от новых строк таблицы товаров
        shift_y = 0
        for item in items:
            max_text_lines = len(item['name'].split('\n'))
            shift_y += max_text_lines

        shift_y = int((shift_y - 1) * table_line_height / 100)

        post_lines_keys = ["amount", "nds", "items", "total"]  # подстановки нижней части счета после таблицы

        # Проход и подстановка текста вокруг таблицы

        for key in base_keys:

            text_elem = soup.find('text', string=lambda text: f'_{key}_' in text)
            if text_elem:

                invoice['bbox_cx_cy_w_h'][key] = {}

                elem_y1 = float(text_elem['y']) if 'y' in text_elem.attrs else 0

                font_class = getFontClass(text_elem)
                font_size = font_sizes.get(font_class, 1300)

                line_height = font_size * 1.2

                text_lines = invoice[key].split('\n')
                original_text_elem = text_elem

                for i, line in enumerate(text_lines):
                    new_elem = soup.new_tag('text', **{attr: text_elem[attr] for attr in text_elem.attrs})
                    new_elem.string = line
                    new_elem['y'] = str(round(elem_y1 + i * line_height))
                    new_elem['x'] = str(round(float(text_elem['x'])))
                    text_elem.insert_after(new_elem)

                    # записываю координаты и размер надписи
                    metrics = getTextMetrics(new_elem)[0]

                    # с учетом сдвига от всей таблицы
                    if key in post_lines_keys:
                        metrics[1] += int(shift_y * dim_scale)

                    # print(line, metrics)
                    invoice['bbox_cx_cy_w_h'][key][i] = ', '.join(map(lambda x: str(x), metrics))

                original_text_elem.decompose()

        # Проход и подстановка текста внутри таблицы

        top_line = float(horizontal_lines[1]['y1'])
        bottom_line = float(horizontal_lines[2]['y1'])
        items_line_height = int(bottom_line - top_line)
        border_y = int(top_line)

        invoice['bbox_cx_cy_w_h']['itemsList'] = {}

        # Сохраняю шаблоны элементов
        templates = {key: soup.find('text', string=lambda text: f'_{key}_' in text)
                     for key in ['num', 'name', 'val', 'unit', 'price', 'sum']}

        table_line_y = float(templates['num']['y'])

        for n, item in enumerate(items):
            max_text_lines = len(item['name'].split('\n'))
            invoice['bbox_cx_cy_w_h']['itemsList'][n] = {}

            for key, template in templates.items():
                if template is None:
                    continue

                text_lines = str(item[key]).split('\n')
                invoice['bbox_cx_cy_w_h']['itemsList'][n][key] = {}

                for i, line in enumerate(text_lines):
                    new_elem = soup.new_tag('text', **{attr: template[attr] for attr in template.attrs})
                    new_elem.string = line
                    new_elem['y'] = str(round(table_line_y + i * table_line_height + 200))
                    new_elem['x'] = str(round(float(template['x'])))
                    template.insert_after(new_elem)
                    metrics = getTextMetrics(new_elem)[0]
                    # print(line, metrics)
                    invoice['bbox_cx_cy_w_h']['itemsList'][n][key][i] = ', '.join(map(lambda x: str(x), metrics))

            # Обновление позиции курсора по Y после добавления строки
            shift_line = round(items_line_height * max_text_lines)
            border_y += shift_line
            table_line_y += shift_line

            # Добавление разделительной линии
            new_breaking_line = soup.new_tag('line', **{attr: horizontal_lines[1][attr]
                                                        for attr in horizontal_lines[1].attrs})
            new_breaking_line['y1'] = new_breaking_line['y2'] = str(border_y)

            root_svg.append(new_breaking_line)

        # Удлинение вертикальных линий и сдвиг нижней границы таблицы
        for line in vertical_lines:
            line['y2'] = str(border_y)
            line['y1'] = horizontal_lines[0]['y1']

        horizontal_lines[2]['y1'] = str(border_y)
        horizontal_lines[2]['y2'] = horizontal_lines[2]['y1']

        # Убрал шаблоны
        for key, template in templates.items():
            template.decompose()

        # Сдвиг блока с ИТОГО вниз
        correct_svg_str = str(soup)
        correct_svg_str = correct_svg_str.replace('<g id="bottom" transform="matrix(1 0 0 1 0 0)">',
                                                  f'<g transform="matrix(1 0 0 1 0 {shift_y * 100})" id="bottom">')

        invoice['magnet_stamp_y'] = str(int((magnet_stamp_y + shift_y) * dim_scale))  # уровень по y для штампа

        # Сохраняю SVG
        file_name = f"invoice_{invoice['number']}.svg"
        print("Сохраняю", file_name)
        full_path_svg = os.path.join(svg_templates_files_folder, file_name)
        with open(full_path_svg, "w", encoding="utf-8") as file:
            file.write(correct_svg_str)

    return json_data
