"""
Конвертер в SVG-PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 02.2024
https://github.com/yenotas/invoices_generator
"""
from config import dim_scale
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

from modules.svg_text_metrics import unpackClassesSVG, getElementClasses, getTextMetrics, getRandomFont


def convert_svg_to_png(input_path, output_path):

    with open(input_path, 'r', encoding='utf-8') as svg_file:
        content = svg_file.read()

    WIDTH = round(int(content.split('<defs>')[0].split('width="')[1].split('px')[0]) * dim_scale)
    HEIGHT = round(int(content.split('<defs>')[0].split('height="')[1].split('px')[0]) * dim_scale)
    font_name = content.split("@font-face {font-family: ")[1].split(";")[0]
    font = getRandomFont(font_name)

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
            metrics = getTextMetrics(text_elem, font, font_sizes, font_weights, 1)
            x, y, tw, th = metrics[1]
            text_image = metrics[2]
            class_names = getElementClasses(text_elem)
            if group['id'] == 'bottom':
                y += y_offset
            if 'center' in class_names:
                x -= round(tw/2)
            if 'right' in class_names:
                x -= tw
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
