# Случайные геометрические искажения и шумы на документах, наложение печатей и сохранение в JSON данных об искажениях
import sys
sys.path.append('/content/invoices_generator')

import os
import random
import cv2
import json
from config import (generated_images_files_folder, json_file_path, distorted_images_files_folder, MODE)
from modules.distortions_generator import (randomRotateImage, createGreySpot, createLightSpot, createNoise,
                                           load_numpy_images_from_folder, random_geometrical_effects)

# загрузка PNG-изображекний счетов
images = load_numpy_images_from_folder(generated_images_files_folder)

# читаем JSON
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

for np_img, filename in images:

    invoice_number = os.path.splitext(filename)[0].split('_')[1]
    print('\n#' + invoice_number)
    save_path = os.path.join(distorted_images_files_folder, os.path.splitext(filename)[0] + '.png')
    distortion = ''
    new_corners = []

    if MODE == 1:
        # только поворот
        np_img, new_corners, distortion = randomRotateImage(np_img)

    if MODE == 2:
        # поворот или перспектива + шум
        np_img = createNoise(np_img)
        np_img, new_corners, distortion = random_geometrical_effects(np_img)

    if MODE == 3:
        # поворот или перспектива + шум и блики
        np_img = createLightSpot(np_img)
        np_img = createGreySpot(np_img)
        np_img = createNoise(np_img)
        np_img, new_corners, distortion = random_geometrical_effects(np_img)

    cv2.imwrite(save_path, np_img)

    # добавлние координат новых углов
    json_data[int(invoice_number)-1]['distortion'] = distortion
    json_data[int(invoice_number)-1]['new_corners'] = ', '.join(map(str, new_corners.astype(str)))

    # сохранение дополненого json
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    print(f'случайное искажение {distortion} для', filename, 'добавлено')

print()
print('Все случайные искажения применены в режиме MODE =', MODE)
print(f'Файлы сохранены в папке "{distorted_images_files_folder}"')
