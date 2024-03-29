"""
Генератор SVG-файлов счетов из JSON
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 01.2024
https://github.com/yenotas/invoices_generator
"""

from config import svg_templates_files_folder, dim_scale, TEST_FONT_NAME
from modules.svg_text_metrics import (unpackClassesSVG, getElementClasses, getElementParams, getTextMetrics,
                                      getRandomFont, getTextSize)

import os
from bs4 import BeautifulSoup


def readSoupFromSVG(svg_file):
    with open(svg_file, 'r', encoding='utf-8') as svg:
        return BeautifulSoup(svg, 'xml')


# Создание SVG-файлов из JSON-данных по шаблону эталонного SVG-файла
def generateSvgTemplates(json_data, base_soup):
    last_soup = ''
    # Разбор стилей
    font_sizes, font_weights, _ = unpackClassesSVG(base_soup)
    soup_string = str(base_soup)  # клон чистого svg

    for invoice in json_data:

        font = getRandomFont(TEST_FONT_NAME)  # указан в config.py, если пустой '' то шрифт случайный.

        invoice["bbox_x_y_w_h"] = {}  # раздел метрик вставляемых текстовых надписей

        base_keys = [key for key in invoice if key != "itemsList"]  # подстановки вокруг таблицы
        items = [item for item in invoice["itemsList"]]  # подстановки в таблице товаров и услуг

        soup = BeautifulSoup(soup_string, 'xml')  # новый рабочий суп для текущего документа

        # Находим группы и линии
        table_group = soup.select("g[id='table']")[0]
        bottom_group = soup.select("g[id='bottom']")[0]
        horizontal_lines = soup.select("line.horizontal_line")
        vertical_lines = soup.select("line.vertical_line")
        stamp_line = soup.select("line[class*='stamp_line']")[0]
        magnet_stamp_y = float(stamp_line['y1'])/100  # позиция У для прицеливания штампа

        # Параметры первой строки
        text_item = soup.find('text', string=lambda text: f'_name_' in text)
        class_name = text_item.get('class', '').split(' ')[1]
        font_size = font_sizes[class_name]
        table_line_height = font_size * 1.2

        # Считаю прирост по Y после сдвига от новых строк таблицы товаров
        shift_y = 0
        for item in items:
            max_text_lines = len(item['name'].split('\n'))
            shift_y += max_text_lines

        shift_y = int((shift_y - 1) * table_line_height / 100)

        post_lines_keys = ["amount", "nds", "items", "total"]  # подстановки нижней части счета после таблицы

        # Для svg, где ключи в отдельных тегах, а не включены в текст
        # отодвинуть надписи с суммой, что бы холдер не заходил на надпись при таком шрифте
        pre_summ_text = {'items': 'Всего наименований', 'total': 'Всего к оплате:'}
        x_shift = {}
        for key in pre_summ_text:
            el = soup.find('text', string=lambda text: pre_summ_text[key] in text)
            x = float(el['x'])
            classes = getElementClasses(el)
            font_size, bold, _ = getElementParams(classes, font_sizes, font_weights)
            w = getTextSize(pre_summ_text[key], font, font_size, bold)[0]
            x_shift[key] = x + w * 100 + 1000

        # Проход и подстановка текста вокруг таблицы

        for key in base_keys:

            text_elem = soup.find('text', string=lambda text: f'_{key}_' in text)

            if text_elem:

                invoice["bbox_x_y_w_h"][key] = {}

                elem_y1 = float(text_elem['y']) if 'y' in text_elem.attrs else 0

                font_class = getElementClasses(text_elem)[1]
                font_size = font_sizes.get(font_class, 1300)

                line_height = font_size * 1.2

                text_lines = invoice[key].split('\n')
                original_text_elem = text_elem

                for i, line in enumerate(text_lines):
                    new_elem = soup.new_tag('text', **{attr: text_elem[attr] for attr in text_elem.attrs})
                    new_elem.string = line
                    if line == '': continue
                    # для svg, где ключи не выделены в отдельные теги, а включены в текст как <text>текст _key_</text>
                    # new_elem.string = line if i > 0 else text_elem.string.replace(f'_{key}_', line)
                    # для svg, где ключи в отдельных тегах:
                    if key in x_shift:
                        text_elem['x'] = str(x_shift[key])
                    new_elem['x'] = str(round(float(text_elem['x'])))
                    new_elem['y'] = str(round(elem_y1 + i * line_height))
                    text_elem.insert_after(new_elem)
                    classes = getElementClasses(new_elem)
                    font_size, bold, align = getElementParams(classes, font_sizes, font_weights)
                    # записываю координаты и размер надписи
                    
                    metrics = getTextMetrics(new_elem, font, font_size * dim_scale, bold, align)[0]

                    # с учетом сдвига от всей таблицы
                    if key in post_lines_keys:
                        metrics[1] += int(shift_y * dim_scale)

                    invoice["bbox_x_y_w_h"][key][i] = ', '.join(map(lambda e: str(e), metrics))

                original_text_elem.decompose()

        # Проход и подстановка текста внутри таблицы
        top_line = float(horizontal_lines[1]['y1'])
        bottom_line = float(horizontal_lines[2]['y1'])
        items_line_height = bottom_line - top_line
        border_y = int(top_line)

        invoice["bbox_x_y_w_h"]["itemsList"] = {}

        # Сохраняю шаблоны элементов
        templates = {key: soup.find('text', string=lambda text: f'_{key}_' in text)
                     for key in ['num', 'name', 'val', 'unit', 'price', 'sum']}

        num_elem = templates['num']
        # Реальная высота для выравнивания текста по средней линии строки
        classes = getElementClasses(num_elem)
        font_size, _, _ = getElementParams(classes, font_sizes, font_weights)
        font_size *= 100
        h, _, shift, _ = getTextSize('Йp', font, font_size)

        # Начало первой строки таблицы
        table_line_y = bottom_line - shift - 140*dim_scale

        for n, item in enumerate(items):
            max_text_lines = len(item['name'].split('\n'))
            invoice["bbox_x_y_w_h"]["itemsList"][n] = {}

            for key, template in templates.items():
                if template is None:
                    continue

                text_lines = str(item[key]).split('\n')
                invoice["bbox_x_y_w_h"]["itemsList"][n][key] = {}

                for i, line in enumerate(text_lines):
                    new_elem = soup.new_tag('text', **{attr: template[attr] for attr in template.attrs})
                    new_elem.string = line
                    y = round(table_line_y + i * items_line_height)
                    new_elem['y'] = str(y)
                    new_elem['x'] = str(round(float(template['x'])))
                    template.insert_after(new_elem)
                    classes = getElementClasses(new_elem)
                    font_size, bold, align = getElementParams(classes, font_sizes, font_weights)
                    metrics = getTextMetrics(new_elem, font, font_size * dim_scale, bold, align)[0]

                    invoice["bbox_x_y_w_h"]["itemsList"][n][key][i] = ','.join(map(lambda x: str(x), metrics))

            # Обновление позиции курсора по Y после добавления строки
            shift_line = round(items_line_height * max_text_lines)
            border_y += shift_line
            table_line_y += shift_line

            # Добавление разделительной линии
            new_breaking_line = soup.new_tag('line', **{attr: horizontal_lines[1][attr]
                                                        for attr in horizontal_lines[1].attrs})
            new_breaking_line['y1'] = new_breaking_line['y2'] = str(border_y)

            table_group.append(new_breaking_line)

        # Удлинение вертикальных линий и сдвиг нижней границы таблицы
        for line in vertical_lines:
            line['y2'] = str(border_y)
            line['y1'] = horizontal_lines[0]['y1']

        horizontal_lines[2]['y1'] = str(border_y)
        horizontal_lines[2]['y2'] = horizontal_lines[2]['y1']

        bottom_group.append(stamp_line)

        # Убрал шаблоны
        for key, template in templates.items():
            template.decompose()

        # Сдвиг блока с ИТОГО вниз
        correct_svg_str = str(soup)
        correct_svg_str = correct_svg_str.replace('<g id="bottom" transform="matrix(1 0 0 1 0 0)">',
                                                  f'<g id="bottom" transform="matrix(1 0 0 1 0 {shift_y * 100})">')
        correct_svg_str = (correct_svg_str.replace("font-family: Arial", f"font-family: {font[0]}")
                           .replace('Arial.ttf', font[0]+'.ttf'))
        is_italic = ''
        if 'italic' in font[1]:
            correct_svg_str = correct_svg_str.replace('text {font-family:', 'text {font-style: italic; font-family:')
            is_italic = 'наклонный'

        last_soup = correct_svg_str = correct_svg_str.replace('fonts/regular/', '../../data/fonts/regular/')

        invoice['magnet_stamp_y'] = str(int((magnet_stamp_y + shift_y) * dim_scale))  # уровень по y для штампа

        # Сохраняю SVG
        file_name = f"invoice_{invoice['number']}.svg"
        print("Сохраняю", file_name, "шрифт", font[0], is_italic)
        full_path_svg = os.path.join(svg_templates_files_folder, file_name)

        with open(full_path_svg, "w", encoding="utf-8") as file:
            file.write(correct_svg_str)

    return json_data, last_soup

