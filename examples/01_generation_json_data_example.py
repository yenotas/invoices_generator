# Пример: генерация данных и сохраниение записей для счетов
import sys
sys.path.append('/content/invoices_generator')

import random
import json

from config import list_data_files, json_file_path, FILES_NUMBER
from modules.strings_generator import genInvoiceJson, loadDataFromFile

json_data = {}
for file_name, url in list_data_files.items():
    json_data[file_name] = loadDataFromFile(file_name)
    # для скачивания из google disk:
    # data[filename] = load_data_from_file(filename, url)

dataset = []

for i in range(FILES_NUMBER):
    generated_json_data = genInvoiceJson(json_data, i + 1, random.randint(1, 8))
    dataset.append(generated_json_data)

# список JSON-записей в файл
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(dataset, json_file, indent=2, ensure_ascii=False)

print()
print('Данные JSON созданы')
print('Файл', json_file_path, 'сохранен в корневой папке')
