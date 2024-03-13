# Пример генерации данных и создание счетов в одном потоке
import sys

import numpy as np

from modules.distortions_generator import randomRotateImage, createNoise, random_geometrical_effects, createLightSpot, \
    createGreySpot, mergeStampToImage
from modules.stamps_generator import generateStamp

sys.path.append('/content/invoices_generator')
import time
start_time = time.time()

import os
import csv
import random
import cv2
from config import list_data_files, data_files_folder, generated_images_files_folder, distorted_images_files_folder, \
    dim_scale, stamped_images_files_folder
from modules.strings_generator import getOneInvoiceJson
from config import svg_file_path, base_folders
from modules.svg_templates_generator import readSoupFromSVG, generateSvgTemplates
from modules.fs_utils import recreateFolder
from modules.svg_bitmap_converter import convert_svg_to_png
recreateFolder(base_folders)

# НАСТРОЙКИ ГЕНЕРАЦИИ:
file_number = 10
MODE = 2
STAMP = 1

raw_data = {}
lines, max_lines = {}, {}
for file_name, url in list_data_files.items():
    with open(os.path.join(data_files_folder, file_name), 'r', encoding='utf-8') as file:
        lines[file_name] = [row for row in csv.reader(file, delimiter=',')]
        max_lines[file_name] = len(lines[file_name])-1
        raw_data[file_name] = []

for fn in range(file_number):
    raw_data['companies.csv'] = [lines['companies.csv'][random.randint(0, max_lines['companies.csv'])],
                                 lines['companies.csv'][random.randint(0, max_lines['companies.csv'])]]
    raw_data['addresses.csv'] = [lines['addresses.csv'][random.randint(0, max_lines['addresses.csv'])][0],
                                 lines['addresses.csv'][random.randint(0, max_lines['addresses.csv'])][0]]
    raw_data['banks.csv'] = lines['banks.csv'][random.randint(1, max_lines['banks.csv'])]
    raw_data['products.csv'] = []
    for i in range(1, random.randint(2, 8)):
        prod = lines['products.csv'][random.randint(0, max_lines['products.csv'])]
        raw_data['products.csv'].append(prod)

    json_data = getOneInvoiceJson(raw_data, fn)
    base_soup = readSoupFromSVG(svg_file_path)
    new_data, new_soup = generateSvgTemplates(json_data, base_soup)
    png_name = os.path.join(generated_images_files_folder, f'_invoice_{fn}.png')
    convert_svg_to_png(new_soup, png_name)
    np_img = cv2.imread(png_name, cv2.IMREAD_GRAYSCALE)
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

    if STAMP == 1:
        # + печать
        line = new_data[0]['seller'].replace('\n', ' ')
        text_outer_circle = line[:55] + ' * '
        pos = line[55:100].find(' ')
        text_inner_circle = line[55 + pos:pos + 105] + ' * '
        text_center = new_data[0]['sellerName'][:6] + '\n' + new_data[0]['sellerName'][6:12]
        stamp_image = generateStamp(text_outer_circle, text_inner_circle, text_center)
        y_offset = int(new_data[0]['magnet_stamp_y']) - int(dim_scale * 100)
        x_offset = int(np_img.shape[1] // 2 - int(dim_scale * 200) + random.randint(0, 200))
        image_np = np.array(stamp_image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGRA)
        img = mergeStampToImage(np_img, image_bgr, (x_offset, y_offset))
        save_path = os.path.join(stamped_images_files_folder, f'_invoice_{fn}.png')
        img.save(save_path, format='PNG')
    else:
        save_path = os.path.join(distorted_images_files_folder,  f'_invoice_{fn}.png')
        cv2.imwrite(save_path, np_img)


end_time = time.time()
execution_time = end_time - start_time
print("Время выполнения скрипта: {:.2f} секунд".format(execution_time))







