import os
import random
import json
import numpy as np

from PIL import Image

from invoices_generator.distortions_generator import (cv_view, cv_resize, random_perspective_change, random_rotate_image,
                                                      create_grey_spot, create_light_spot, create_noise,
                                                      no_distortions)

from invoices_generator.config import (stamps_files_folder, generated_images_files_folder, json_file_name,
                                       distorted_images_files_folder)
from invoices_generator.stamps_generator import generate_stamp


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
    effect = random.choice([random_perspective_change, random_rotate_image, no_distortions])
    print('\nэффект:', str(effect.__name__))
    return effect(image)


images = load_images_from_folder(generated_images_files_folder)

for img, filename in images:

    np_img = np.array(img.convert('L'))
    np_img = cv_resize(np_img, 0.5)

    # графические шумы: светлое и темное пятна и зернистость, размер остается
    np_img = create_light_spot(np_img)
    np_img = create_grey_spot(np_img)
    np_img = create_noise(np_img)

    # геометрические искажения: поворот и перспектива -> искаженное изображение и новые координаты углов документа
    np_img, new_corners = random_geometrical_effects(np_img)
    save_path = os.path.join(distorted_images_files_folder, os.path.splitext(filename)[0] + '.jpeg')

    img = Image.fromarray(np_img)

    img.save(save_path, 'JPEG') # сохранение результата
    # сохранение изображение
    print('random distortions', filename, 'is complete')

print()
print('all images random distortions is complete')
print('files in folder "distorted_images"')
# cv_view(np_img)



