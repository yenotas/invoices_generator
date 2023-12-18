# -*- coding: utf-8 -*-
# Пример: генерация данных и сохраниение записей для счетов

import random
import json

from invoices_generator.config import list_data_files, json_file_name
from invoices_generator.strings_generator import gen_invoice_json, load_data_from_file

json_data = {}
for file_name, url in list_data_files.items():
    json_data[file_name] = load_data_from_file(file_name)
    # для скачивания из google disk:
    # data[filename] = load_data_from_file(filename, url)

dataset = []
n = 5 # количество счетов
for i in range(n):
    generated_json_data = gen_invoice_json(json_data, i+1, random.randint(1, 8))
    dataset.append(generated_json_data)

# список JSON-записей в файл
with open(json_file_name, "w", encoding="utf-8") as json_file:
    json.dump(dataset, json_file, indent=2, ensure_ascii=False)


print()
print('generate JSON data is complete')
print('file', json_file_name, 'in parent folder')