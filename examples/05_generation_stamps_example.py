# Генерация изображений круглых печатей по данным из JSON
import sys
sys.path.append('/content/invoices_generator')

import json
import os

from config import stamps_files_folder, json_file_path
from modules.stamps_generator import generateStamp


with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

for i in range(0, len(json_data)):
    line = json_data[i]['seller'].replace('\n', ' ')
    text_outer_circle = line[:55] + ' * '
    pos = line[55:100].find(' ')
    text_inner_circle = line[55+pos:pos+105] + ' * '
    text_center = json_data[i]['sellerName'][:6]+'\n'+json_data[i]['sellerName'][6:12]
    img = generateStamp(text_outer_circle, text_inner_circle, text_center)
    print('Печать для счета ', i+1)
    img.save(os.path.join(stamps_files_folder, 'stamp_' + str(i + 1) + '.png'))

print()
print('Создание круглых печатей из JSON произведено')
print(f'Файлы PNG сохранены в папке "{stamps_files_folder}"')