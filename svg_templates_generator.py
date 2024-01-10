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

from config import svg_templates_files_folder, dim_scale, font_path, bold_font_path

import os
from bs4 import BeautifulSoup

from PIL import Image, ImageDraw, ImageFont
import numpy as np

text_dir = {'right': -1, 'center': 0}  # коэффициент для вычисления центра надписи в зависимости от выравнивания текста
font_sizes = {}
font_weights = {}
countr = 0


# Временный рендер надписи для определения размера
def get_text_size(text, font_size, bold=False):
    global countr
    # Создание изображения
    image = Image.new('L', (len(text) * 20, 30))
    draw = ImageDraw.Draw(image)

    # Загрузка шрифта
    fp = bold_font_path if bold else font_path
    font = ImageFont.truetype(fp, font_size)

    # Рисование текста на изображении
    draw.text((0, 0), text.strip(), font=font, fill=255)

    # Преобразование изображения в массив NumPy
    np_img = np.array(image)

    # Вычисление реальной ширины текста
    non_zero_columns = np.where(np_img.max(axis=0) > 0)
    real_width = non_zero_columns[0][-1] - non_zero_columns[0][0] + 1

    # Вычисление высоты текста
    non_zero_rows = np.where(np_img.max(axis=1) > 0)
    real_height = non_zero_rows[0][-1] - non_zero_rows[0][0] + 1

    # Обрезание изображения
    trimmed_img = np_img[non_zero_rows[0][0]:non_zero_rows[0][-1] + 1,
                         non_zero_columns[0][0]:non_zero_columns[0][-1] + 1]

    # Увеличение размера изображения в N раз
    resized_img = np.kron(trimmed_img, np.ones((round(dim_scale), round(dim_scale))))

    # Создание нового изображения из массива
    resized_img = resized_img.astype(np.uint8)  # Преобразование в целочисленный тип
    resized_image = Image.fromarray(resized_img, mode='L')

    # Сохранение изображения в файл
    resized_image.save(os.path.join(svg_templates_files_folder, 'temp', f'{countr}.png'))
    countr += 1

    return 100 * real_width, 100 * real_height


# Вычисляю координаты центра и метрики текстовой надписи
def get_text_metrics(text_el):

    align = 1  # Коэффициент для левого выравнивания текста
    font_class = '.fnt5'
    classes = text_el.get('class', '').split(' ')
    if len(classes) > 1:
        font_class = '.' + classes[1]
        if len(classes) > 2:
            align = text_dir.get(classes[2], 1)

    font_size = font_sizes.get(font_class, 1300)
    bold = font_weights.get(font_class, False)
    text = text_el.string

    tw, th = get_text_size(text, font_size / 100, bold)
    cx = round((float(text_el['x']) + align * tw / 2) / 100 * dim_scale) - 1
    cy = round((float(text_el['y']) - th / 2) / 100 * dim_scale) + 1
    tw, th = round(tw * dim_scale / 100), round(th * dim_scale / 100)

    return [[cx, cy, tw, th], font_size, bold, align]


# Создание SVG-файлов из JSON-данных по шаблону эталонного SVG-файла
def generate_svg_templates(json_data, base_svg_file):

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
            font_sizes[class_name] = font_size
            font_weight = next((value.split(':')[1].strip()
                                for value in line.split('{')[0].split(';') if 'font-weight' in value), 'normal')
            font_weights[class_name] = True if font_weight == 'bold' else False

    for invoice in json_data:

        invoice['bbox_cx_cy_w_h'] = {}  # раздел метрик вставляемых текстовых надписей

        base_keys = [key for key in invoice if key != 'itemsList']
        items = [item for item in invoice['itemsList']]

        soup = BeautifulSoup(soup_string, 'xml')  # рабочий суп
        root_svg = soup.find('svg')

        # Находим горизонтальные и вертикальные линии в таблице товаров
        horizontal_lines = soup.select("line[class*='horizontal_line']")
        vertical_lines = soup.select("line[class*='vertical_line']")
        stamp_line = soup.select("line[class*='stamp_line']")[0]
        magnet_stamp_y = float(stamp_line['y1'])/100  # позиция У для прицеливания штампа

        top_line = float(horizontal_lines[1]['y1'])
        bottom_line = float(horizontal_lines[2]['y1'])
        items_line_height = bottom_line - top_line

        # Параметры первой строки
        text_item = soup.find('text', string=lambda text: f'_name_' in text)
        class_name = text_item.get('class', '').split(' ')[1]
        font_size = font_sizes['.'+class_name]
        table_line_height = font_size * 1.2

        # Сохраняю шаблоны элементов
        templates = {key: soup.find('text', string=lambda text: f'_{key}_' in text)
                     for key in ['num', 'name', 'val', 'unit', 'price', 'sum']}

        table_line_y = float(templates['num']['y'])

        # Проход и подстановка текста вокруг таблицы
        for key in base_keys:

            text_elem = soup.find('text', string=lambda text: f'_{key}_' in text)
            if text_elem:

                invoice['bbox_cx_cy_w_h'][key] = {}

                original_y1 = float(text_elem['y']) if 'y' in text_elem.attrs else 0

                font_size = get_text_metrics(text_elem)[1]

                line_height = font_size * 1.2

                text_lines = invoice[key].split('\n')
                original_text_elem = text_elem

                for i, line in enumerate(text_lines):
                    new_elem = soup.new_tag('text', **{attr: text_elem[attr] for attr in text_elem.attrs})
                    new_elem.string = line
                    new_elem['y'] = str(round(float(original_y1 + i * line_height)))
                    new_elem['x'] = str(round(float(text_elem['x'])))
                    # записываю координаты и размер надписи
                    metrics = get_text_metrics(new_elem)[0]
                    invoice['bbox_cx_cy_w_h'][key][i] = ', '.join(map(lambda x: str(x), metrics))

                    text_elem.insert_after(new_elem)

                original_text_elem.decompose()

        # Проход и подстановка текста внутри таблицы
        border_y = top_line

        invoice['bbox_cx_cy_w_h']['itemsList'] = {}

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
                    new_elem['y'] = str(round(float(table_line_y + i*table_line_height + 100)))
                    new_elem['x'] = str(round(float(template['x'])))

                    metrics = get_text_metrics(new_elem)[0]
                    invoice['bbox_cx_cy_w_h']['itemsList'][n][key][i] = ', '.join(map(lambda x: str(x), metrics))

                    template.insert_after(new_elem)

            # Обновление позиции курсора по Y после добавления строки
            border_y += round(items_line_height * max_text_lines)
            table_line_y += round(items_line_height * max_text_lines)

            # Добавление разделительной линии
            new_breaking_line = soup.new_tag('line', **{attr: horizontal_lines[1][attr]
                                                        for attr in horizontal_lines[1].attrs})
            new_breaking_line['y1'] = new_breaking_line['y2'] = str(border_y)

            root_svg.append(new_breaking_line)

        # Прирост по Y от новых строк
        shift_y = round(table_line_y - float(templates['num']['y']) - table_line_height)

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
                                                  f'<g transform="matrix(1 0 0 1 0 {shift_y})" id="bottom">')

        invoice['magnet_stamp_y'] = str(int((magnet_stamp_y + shift_y / 100) * dim_scale))  # уровень по y для штампа

        # Сохраняю SVG
        file_name = f"invoice_{invoice['number']}.svg"
        print("Сохраняю", file_name)
        full_path_svg = os.path.join(svg_templates_files_folder, file_name)
        with open(full_path_svg, "w", encoding="utf-8") as file:
            file.write(correct_svg_str)

    return json_data
