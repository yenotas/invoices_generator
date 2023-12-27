import os
import random
import json
import numpy as np
import cv2

from PIL import Image

from config import (stamps_files_folder, generated_images_files_folder, json_file_name,
                                       distortion_scale, distorted_images_files_folder, stamped_images_files_folder)
from distortions_generator import (cv_view, cv_resize, random_perspective_change, random_rotate_image,
                                                      create_grey_spot, create_light_spot, create_noise,
                                                      not_distortions)


# Чтение изображений из папки
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        try:
            with Image.open(img_path) as img:
                images.append((img.copy(), filename))
        except IOError:
            print(f"Не удалось загрузить изображение: {filename}")
    return images


# Миксер эффектов
def random_geometrical_effects(image):
    effect = random.choice([random_perspective_change, random_rotate_image, not_distortions])
    print('эффект:', str(effect.__name__))
    return effect(image)


# загрузка PNG-изображекний счетов
images = load_images_from_folder(generated_images_files_folder)
# загрузка печатей
stamps = load_images_from_folder(stamps_files_folder)
# читаем JSON
with open(json_file_name, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

for img, filename in images:

    invoice_number = os.path.splitext(filename)[0].split('_')[1]
    print('\n#'+ invoice_number)

    np_img = np.array(img.convert('L'))
    np_img = cv_resize(np_img, distortion_scale)

    # графические шумы: светлое и темное пятна и зернистость, размер остается
    np_img = create_light_spot(np_img)
    np_img = create_grey_spot(np_img)
    np_img = create_noise(np_img)

    # геометрические искажения: поворот и перспектива -> искаженное изображение и новые координаты углов документа
    np_img, new_corners, distortion = random_geometrical_effects(np_img)

    save_path = os.path.join(distorted_images_files_folder, os.path.splitext(filename)[0] + '.jpeg')
    img = Image.fromarray(np_img)
    # сохранение изображение
    img.save(save_path, 'JPEG')
    #сохранение координат новых углов
    json_data[int(invoice_number)-1]['new_corners'] = str(new_corners)
    json_data[int(invoice_number)-1]['distortion'] = distortion
    # пересохранияю дополненый "магнитами" для штампа json
    with open(json_file_name, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    # Наложение печати и сохранение с печатью
    # Координаты для наложения маленького изображения на большое
    y_offset = int(json_data[int(invoice_number)-1]['magnet_stamp_y']) - 500
    x_offset = int(new_corners[3][0] / 2 - random.randint(60, 400))

    stamp_image = np.array(stamps[int(invoice_number)-1][0])

    small_height, small_width = stamp_image.shape[:2]

    base_image = cv2.cvtColor(np_img, cv2.COLOR_GRAY2BGR)

    # Извлечение каналов RGB и альфа-канала
    stamp_rgb = stamp_image[..., :3]
    stamp_alpha = stamp_image[..., 3] / 255.0

    # Масштабирование альфа-канала штампа
    stamp_alpha = cv2.merge([stamp_alpha, stamp_alpha, stamp_alpha])

    # Альфа-смешивание
    roi = base_image[y_offset:y_offset + small_height, x_offset:x_offset + small_width]
    blended = cv2.addWeighted(stamp_rgb, 0.3, roi, 0.3, 0) * stamp_alpha + roi * (1 - stamp_alpha)

    # Замена ROI в основном изображении
    base_image[y_offset:y_offset + small_height, x_offset:x_offset + small_width] = blended

    # сохранение изображение
    filename = os.path.splitext(filename)[0] + '.jpeg'
    save_path = os.path.join(stamped_images_files_folder, filename)
    img = Image.fromarray(base_image)
    img.save(save_path, 'JPEG')

    print('случайное искажение для', filename, 'и печать добавлены')


print()
print('Все случайные искажения применены')
print(f'Файлы сохранены в папке "{distorted_images_files_folder}"')
# cv_view(np_img)



