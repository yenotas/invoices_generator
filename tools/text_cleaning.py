# Утилита чистки больших текстов. В частности - удаление вхождений "(цифры)" и двойных пробелов из текста
import sys
sys.path.append('/content/invoices_generator')

import re
import os
from config import list_data_files, data_files_folder
from modules.strings_generator import strip


def textCleaning(txt):
    return strip(re.sub(r'\(\d{1,3}\)', '', txt))


for file_name, _ in list_data_files.items():

    print(file_name)
    content = ''

    in_file_path = os.path.join(data_files_folder, file_name)
    out_file_path = os.path.join(data_files_folder, 'new_'+file_name)

    with open(in_file_path, 'r', encoding='utf-8') as input_file:
        with open(out_file_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                clean_text = textCleaning(line)
                output_file.write(clean_text)
