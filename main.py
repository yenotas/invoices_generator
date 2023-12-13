import os
import random

from PIL import Image

from distortions import (cv_view, cv_resize, random_perspective_change, random_rotate_image,
                         create_grey_spot, create_shadow, create_light_spot, create_noise)


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
def apply_random_effects(image):
    effects = [create_grey_spot, create_shadow, create_light_spot, create_noise]
    for effect in random.sample(effects, random.randint(1, len(effects))):
        print('эффект:', str(effect.__name__))
        image = effect(image)
    return image


# Основной цикл
def main():
    '''
    input_folder = 'invoices'  # Путь к папке с исходными изображениями
    save_folder = 'transformed'    # Путь к папке для сохранения результатов
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    images = load_images_from_folder(input_folder)
    for img, filename in images:
        print('обработка', filename)
        img = apply_random_effects(img)
        save_path = os.path.join(save_folder, os.path.splitext(filename)[0] + '.jpeg')
        img.save(save_path, 'JPEG') # Сохранение результата
        # сохранение изображение
    '''

    img = Image.open('invoices/invoice_2.png')
    img = img.convert('L')

    np_img = create_light_spot(img)
    # геометрические искажения: на выходе искаженное изображение и новые координаты углов документа
    # np_img, new_corners = random_perspective_change(np_img)
    np_img, new_corners = random_rotate_image(np_img)


    img = Image.fromarray(np_img, 'L')
    np_img = create_grey_spot(img)

    np_img = create_noise(np_img)

    np_img = cv_resize(np_img, 0.5)

    cv_view(np_img)

    print(new_corners)


if __name__ == "__main__":
    main()
