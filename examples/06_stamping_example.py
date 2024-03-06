# Случайные геометрические искажения и шумы на документах, наложение печатей и сохранение в JSON данных об искажениях
import sys
sys.path.append('/content/invoices_generator')

import os
import random
import json

from config import (stamps_files_folder, json_file_path, dim_scale,
                    distorted_images_files_folder, stamped_images_files_folder)
from modules.distortions_generator import load_numpy_images_from_folder, mergeStampToImage


# загрузка PNG-изображекний счетов
images = load_numpy_images_from_folder(distorted_images_files_folder, mode='C')
# загрузка печатей
stamps = load_numpy_images_from_folder(stamps_files_folder, mode='A')
# читаем JSON
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

print(images[3][1])
i = 0
for np_img, filename in images:

    invoice_number = filename.split('_')[-1].replace('.png', '')
    j = int(invoice_number) - 1
    print('\n#'+invoice_number, json_data[j]['title'])

    # Наложение печати и сохранение с печатью
    y_offset = int(json_data[j]['magnet_stamp_y']) - int(dim_scale * 100)
    x_offset = int(np_img.shape[1] // 2 - int(dim_scale * 200) + random.randint(0, 200))

    stamp_image = stamps[i][0]
    i += 1

    img = mergeStampToImage(np_img, stamp_image, (x_offset, y_offset))

    # сохранение изображение
    save_path = os.path.join(stamped_images_files_folder, filename)
    img.save(save_path, 'PNG')

    print(filename, '- штамп добавлен')

print()
print(f'Файлы сохранены в папке "{stamped_images_files_folder}"')
