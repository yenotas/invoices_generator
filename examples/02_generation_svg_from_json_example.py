# -*- coding: utf-8 -*-
# Пример генерации заполненных SVG-документов из JSON

import json

from config import json_file_name, base_svg_file_name, svg_templates_files_folder, DPI
from modules.svg_templates_generator import generate_svg_templates

with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

new_data = generate_svg_templates(json_data, base_svg_file_name)

# Сохраняю дополненный координатами json
with open(json_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(new_data, json_file, ensure_ascii=False, indent=4)

print()
print('SVG-шаблоны созданы')
print(f'Файлы сохранены в папке "{svg_templates_files_folder}"')
print('generated_data.json дополнен координатами и размерами вставленных текстов при DPI =', DPI)
