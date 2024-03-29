"""
Конвертер в SVG-PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 02.2024
https://github.com/yenotas/invoices_generator
"""
from config import dim_scale
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

from modules.svg_text_metrics import unpackClassesSVG, getElementClasses, getTextMetrics, getRandomFont, getElementParams


def convert_svg_to_png(content, output_path):

    WIDTH = round(int(content.split('<defs>')[0].split('width="')[1].split('px')[0]) * dim_scale)
    HEIGHT = round(int(content.split('<defs>')[0].split('height="')[1].split('px')[0]) * dim_scale)
    font_name = content.split("@font-face {font-family: ")[1].split(";")[0]
    italic = 'italic' if "text {font-style: italic;" in content else 'not'
    font = getRandomFont(font_name, italic)

    soup = BeautifulSoup(content, 'xml')
    font_sizes, font_weights, line_widths = unpackClassesSVG(soup)

    # Создаем изображение PIL с нужным размером
    image = Image.new('L', (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    for group in soup.find_all('g'):
        y_offset = 0
        if group['id'] == 'bottom':
            y_offset = round(int(group['transform'].split(')')[0].split(' ')[-1]) * dim_scale / 100)
        for text_elem in group.find_all('text'):
            classes = getElementClasses(text_elem)
            font_size, bold, align = getElementParams(classes, font_sizes, font_weights)
            # записываю координаты и размер надписи
            metrics = getTextMetrics(text_elem, font, font_size * dim_scale, bold, align)
            x, y, w, h = metrics[0]
            text_image = metrics[1]
            if group['id'] == 'bottom':
                y += y_offset
            image.paste(text_image, (x, y))

        # Обработка линий
        group_lines = group.find_all('line')
        for i, line in enumerate(group_lines):
            x1, y1 = round(float(line['x1'])/100*dim_scale), round(float(line['y1'])/100*dim_scale)
            x2, y2 = round(float(line['x2'])/100*dim_scale), round(float(line['y2'])/100*dim_scale)
            if x2 - x1 < y2 - y1:
                y1 += 1
                y2 -= 1
                x2 = x1
            class_names = getElementClasses(line)
            line_width = round(int(line_widths[class_names[1]])/75)
            if group['id'] == 'bottom':
                y1 = y2 = y1 + y_offset
            draw.line((x1, y1, x2, y2), fill=0, width=line_width)

    # Сохраняем результирующее изображение
    image.save(output_path)
