"""
Конвертер SVG-файлов в PNG:
- читаю шрифты из папки в массив
- выбираю шрифт
- читаю свг: если есть группы - разбиваю и перечитываю.
- если есть таблица - определяю по координатам, что к ней относится и определяю в нулевую группу

- стили и размеры сохраняю


"""

from config import text_fragments_folder, dim_scale, save_text_fragments, WIDTH, HEIGHT

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from modules.svg_text_metrics import unpackClassesSVG, getFontClass, getTextMetrics


def convert_svg_to_png(svg_path, png_path):

    with open(svg_path, 'r') as file:
        soup = BeautifulSoup(file.read(), 'xml')

    font_sizes, font_weights = unpackClassesSVG(soup)

    # Создаем изображение PIL с нужным размером
    image = Image.new('L', (int(WIDTH*dim_scale), int(HEIGHT*dim_scale)), 'white')
    draw = ImageDraw.Draw(image)

    # Обработка текста
    for text_elem in soup.find_all('text_elem'):
        x, y = int(text_elem['x']), int(text_elem['y'])
        # [cx, cy, tw, th], img, font_size, bold, align
        metrics = getTextMetrics(text_elem, font_sizes, font_weights)
        cx, cy, tw, th = metrics[0]
        text_image = metrics[1]

        # Рендерим текст (предполагаем, что функция render_text_fragment уже есть)
        image.paste(text_image, (x, y))

    # Обработка линий
    for line in soup.find_all('line'):
        x1, y1, x2, y2 = int(line['x1']), int(line['y1']), int(line['x2']), int(line['y2'])
        class_name = line.get('class', [None])[0]
        line_width = 200 if 'str1' in class_name else 100

        # Рисуем линию
        draw.line((x1, y1, x2, y2), fill='black', width=line_width)

    # Сохраняем результирующее изображение
    image.save(png_path)
