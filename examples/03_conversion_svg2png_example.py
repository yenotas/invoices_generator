# Пример конвертации заполненных SVG-документов в PNG с утилитой ImageMagick
import sys
sys.path.append('/content/invoices_generator')

from config import generated_images_files_folder, svg_templates_files_folder
from modules.svg_bitmap_converter import convert_svg_to_png
import os


# Получаем список SVG-файлов в папке
svg_files = [f for f in os.listdir(svg_templates_files_folder) if f.endswith('.svg')]

# Обработка каждого SVG-файла
for svg_file in svg_files:
    input_path = os.path.join(svg_templates_files_folder, svg_file)
    output_path = os.path.join(generated_images_files_folder, svg_file.replace('.svg', '.png'))
    with open(input_path, 'r', encoding='utf-8') as svg:
        content = svg.read()
    convert_svg_to_png(content, output_path)

    print('Сохраняю', input_path.replace('.svg', '.png'))

print()
print('Конвертация SVG-шаблонов в PNG произведена')
print(f'Файлы сохранены в папке "{generated_images_files_folder}"')
