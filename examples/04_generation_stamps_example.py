# -*- coding: utf-8 -*-
# Генерация изображений круглых печатей по данным из JSON

import json

from invoices_generator.config import stamps_files_folder, json_file_name
from invoices_generator.stamps_generator import generate_stamp

with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

for i in range(0, len(json_data)):
    line = json_data[i]['seller'].replace('\n', ' ')
    text_outer_circle = line[:55] + ' * '
    pos = line[55:100].find(' ')
    text_inner_circle = line[55+pos:pos+105] + ' * '
    text_center = json_data[i]['sellerName'][:6]+'\n'+json_data[i]['sellerName'][6:12]
    generate_stamp(stamps_files_folder, 'stamp_'+str(i+1)+'.png', text_outer_circle, text_inner_circle, text_center)

print()
print('generation PNG circle stamps from JSON is complete')
print(f'files in folder "{stamps_files_folder}"')