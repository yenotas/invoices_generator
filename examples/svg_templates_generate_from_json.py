# -*- coding: utf-8 -*-
# Пример генерации заполненных SVG-документов из JSON

import os
import json

from invoices_generator.config import svg_templates_files_folder, data_files_folder, temp_folder
from invoices_generator.svg_templates_generator import generate_svg_templates


json_file_name = 'generated_data.json'
base_svg_file_name = 'invoice.svg'

base_svg_file_name = os.path.join(data_files_folder, base_svg_file_name)
json_file_name = os.path.join(temp_folder, json_file_name)

with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

new_data = generate_svg_templates(json_data, base_svg_file_name)

# пересохранияю дополненый "магнитами" для штампа json
with open(json_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(new_data, json_file, ensure_ascii=False, indent=4)