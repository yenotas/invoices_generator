# -*- coding: utf-8 -*-
# Пример генерации изображения круглой печати

import os
import json

from invoices_generator.config import temp_folder, stamps_files_folder
from invoices_generator.stamp_generator import generate_stamp

json_file_name = 'generated_data.json'

full_path_json = os.path.join(temp_folder, json_file_name)

with open(full_path_json, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

output_folder = stamps_files_folder

base_splitters = ' '

for i in range(0, len(json_data)):
    text_outer_circle = json_data[i]['seller'][:58].replace('\n', ' ')
    pos = json_data[i]['seller'][59:110].find(' ')
    text_inner_circle = json_data[i]['seller'][pos:pos+50].replace('\n', ' ') + ' * '
    text_center = json_data[i]['sellerName'][:6]+'\n'+json_data[i]['sellerName'][6:12]
    generate_stamp(output_folder, 'tmp_stmp_'+str(i)+'.png', text_outer_circle, text_inner_circle, text_center)
