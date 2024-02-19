# Пример генерации заполненных SVG-документов из JSON
import sys
sys.path.append('/content/invoices_generator')

import json

from config import json_file_path, svg_file_path, svg_templates_files_folder, dim_scale, base_folders
from modules.svg_templates_generator import readSoupFromSVG, generateSvgTemplates

from modules.fs_utils import recreateFolder
recreateFolder(base_folders)


with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

base_soup = readSoupFromSVG(svg_file_path)

new_data = generateSvgTemplates(json_data, base_soup)

# Сохраняю дополненный координатами json
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(new_data, json_file, ensure_ascii=False, indent=4)

print()
print('SVG-шаблоны созданы')
print(f'Файлы сохранены в папке "{svg_templates_files_folder}"')
print('generated_data.json дополнен координатами и размерами вставленных текстов при масштабе =', dim_scale)
