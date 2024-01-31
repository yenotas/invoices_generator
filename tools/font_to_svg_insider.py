# Конвертация файла шрифта и встраивание его в документ SVG
import sys
sys.path.append('/content/invoices_generator')

import base64
from config import svg_file_path, font_path, embed_svg_path

def embedFontToSvg(svg_path, font, new_svg_path):
    # Чтение шрифта и кодирование его в base64
    with open(font, 'rb') as font_file:
        font_data = font_file.read()
        font_base64 = base64.b64encode(font_data).decode('utf-8')

    # Формирование строки CSS для встраивания шрифта
    old_font_face = "@font-face {font-family:'Arial'; src: url('fonts/arial.ttf') format('truetype');}"
    font_face = f"@font-face {{ font-family: 'CustomFont'; src: url(data:font/truetype;charset=utf-8;base64,{font_base64}) format('truetype'); }}"

    # Чтение SVG файла
    with open(svg_path, 'r', encoding='utf-8') as svg_file:
        svg_content = svg_file.read()

    # Вставка строки CSS с шрифтом в SVG
    svg_content = svg_content.replace(old_font_face, font_face).replace('Arial', 'CustomFont')

    # Сохранение нового SVG файла
    with open(new_svg_path, 'w', encoding='utf-8') as new_svg_file:
        new_svg_file.write(svg_content)


# Пример использования:
embedFontToSvg(svg_file_path, font_path, embed_svg_path)
