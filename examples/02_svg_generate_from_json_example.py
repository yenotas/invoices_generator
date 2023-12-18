# -*- coding: utf-8 -*-
# Пример генерации заполненных SVG-документов из JSON

import json

from invoices_generator.config import json_file_name, base_svg_file_name, data_files_folder
from invoices_generator.svg_templates_generator import generate_svg_templates

with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

new_data = generate_svg_templates(json_data, base_svg_file_name)

# пересохранияю дополненый "магнитами" для штампа json
with open(json_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(new_data, json_file, ensure_ascii=False, indent=4)


print()
print('generate SVG templates is complete')
print('files in folder "svg_templates"')
