# -*- coding: utf-8 -*-
# Пример: генерация данных и сохраниение записей для счетов

import os
import random
import json

from invoices_generator.config import list_data_files, temp_folder
from invoices_generator.string_generators import gen_invoice_json, load_data_from_file

json_data = {}
for filename, url in list_data_files.items():
    json_data[filename] = load_data_from_file(filename)
    # для скачивания из google disk:
    # data[filename] = load_data_from_file(filename, url)

file_name = 'generated_data.json'

full_path = os.path.join(temp_folder, file_name)

dataset = []
n = 5 # количество счетов
for i in range(n):
    generated_json_data = gen_invoice_json(json_data, i+1, random.randint(1, 8))
    dataset.append(generated_json_data)

# список JSON-записей в файл
with open(full_path, "w", encoding="utf-8") as json_file:
    json.dump(dataset, json_file, indent=2, ensure_ascii=False)