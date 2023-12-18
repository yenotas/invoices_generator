# -*- coding: utf-8 -*-
# Пример генерации изображения круглой печати

import json

from invoices_generator.config import stamps_files_folder, json_file_name
from invoices_generator.stamps_generator import generate_stamp

with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

for i in range(0, len(json_data)):
    text_outer_circle = json_data[i]['seller'][:58].replace('\n', ' ')
    pos = json_data[i]['seller'][59:110].find(' ')
    text_inner_circle = json_data[i]['seller'][pos:pos+50].replace('\n', ' ') + ' * '
    text_center = json_data[i]['sellerName'][:6]+'\n'+json_data[i]['sellerName'][6:12]
    generate_stamp(stamps_files_folder, 'tmp_stmp_'+str(i)+'.png', text_outer_circle, text_inner_circle, text_center)


print()
print('generation PNG circle stamps from JSON is complete')
print('files in folder "generated_stamps"')