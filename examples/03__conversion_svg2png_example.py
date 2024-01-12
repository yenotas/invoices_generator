# -*- coding: utf-8 -*-
"""
Конвертер в SVG-PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 01.2024

Для конвертации SVG-файлов в PNG:
(1 способ - смотри README)
1. установить ImageMagick по ссылке:
Для Windows:
https://imagemagick.org/script/download.php#windows
(Для Linux: sudo apt-get install imagemagick
Для macOS: brew install imagemagick)
2. затем библиотеку Wand - включена в requirements.txt
"""
# Пример конвертации заполненных SVG-документов в PNG с утилитой ImageMagick

from config import generated_images_files_folder, svg_templates_files_folder, DPI, bold_font_path, font_path
import os
from wand.image import Image
from wand.color import Color


# Получаем список SVG-файлов в папке
svg_files = [f for f in os.listdir(svg_templates_files_folder) if f.endswith('.svg')]

# Пути к внешним шрифтам
# font_paths = {
#     'Arial': font_path,
#     'ArialBold': bold_font_path,
#     # Добавьте пути к другим шрифтам при необходимости
# }
# # Устанавливаем внешние шрифты в библиотеке Wand
# for font_name, font_path in font_paths.items():
#     library.MagickSetOption(None, f"svg:font-family-{font_name}", font_path.encode())

# Обработка каждого SVG-файла
for svg_file in svg_files:
    input_path = os.path.join(svg_templates_files_folder, svg_file)
    output_path = os.path.join(generated_images_files_folder, svg_file.replace('.svg', '.png'))

    # конвертация с ImageMagick/Wand
    with Image(filename=input_path, background=Color('white'), resolution=DPI) as img:
        img.format = 'png'
        img.save(filename=output_path)

    print('convert', svg_file, 'is complete')

print()
print('Конвертация SVG-шаблонов в PNG произведена')
print(f'Файлы сохранены в папке "{generated_images_files_folder}"')
