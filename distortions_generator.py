# -*- coding: utf-8 -*-
'''
Генератор случайных искажений документов в PNG, иммитирующих сканы документов разного качества.
Автор: Коваленко А.В. 12.2023
'''

import random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2


def cv_view(np_img):
    cv2.imshow('Image', np_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cv_resize(np_img, k):
    return cv2.resize(np_img, None, fx=k, fy=k)


def create_shadow(np_img):
    # Код для создания тени
    pass
    return np_img


# Добавление шума
def create_noise(np_img):
    # Генерируем гауссовский шум (cр. знач. шума, стандартное отклонение шума, размеры изобр.)
    noise = np.random.normal(5, 15, np_img.shape).astype(np.uint8)
    random_image = round(random.uniform(0.9, 1.0), 1)
    random_noise = round(random.uniform(0.0, 0.3), 1)
    # добавляем сгенерированный шум к исходному изображению с помощью функции cv2.addWeighted
    # cv2.bitwise_and, cv2.bitwise_or, cv2.bitwise_xor
    noisy_image = cv2.addWeighted(np_img, random_image, noise, random_noise, 0)

    return noisy_image


def make_gradient_rectangle(width, height, direction='horizontal'):
    gradient = Image.new('L', (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    direct = width if direction == 'horizontal' else height
    for i in range(direct):
        value = int(55 + 200 * i / (direct - 200))
        draw.line([(i, 0), (i, height)] if direction == 'horizontal' else [(0, i), (width, i)], fill=value)
    return gradient


# Создание абстрактного пятна
def create_abstract_spot(width, height):
    # Создание большего рабочего холста
    canvas_width, canvas_height = width * 2, height * 2
    spot_img = Image.new('L', (canvas_width, canvas_height), 0)

    for _ in range(random.randint(3, 9)):
        radius_x = random.randint(width // 8, width // 2)
        radius_y = random.randint(height // 8, height // 2)
        center_x = random.randint(radius_x+200, canvas_width - radius_x)
        center_y = random.randint(radius_y+200, canvas_height - radius_y)
        angle = random.randint(0, 90)

        gradient = make_gradient_rectangle(radius_x * 2, radius_y * 2, random.choice(['horizontal', 'vertical']))

        mask = Image.new('L', (radius_x * 2, radius_y * 2), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, radius_x * 2, radius_y * 2), fill=255)

        masked_gradient = Image.composite(gradient, Image.new('L', gradient.size), mask)

        # Поворот маскированного градиента
        rotated_gradient = masked_gradient.rotate(angle, expand=True)

        # Вычисление новых координат для размещения повернутого эллипса
        new_width, new_height = rotated_gradient.size
        upper_left_x = max(center_x - new_width // 2, 0)
        upper_left_y = max(center_y - new_height // 2, 0)

        # Наложение повернутого эллипса на основное изображение
        spot_img.paste(rotated_gradient, (upper_left_x, upper_left_y), rotated_gradient)

    spot = spot_img.filter(ImageFilter.GaussianBlur(random.randint(50, 200)))

    # Рассчёт случайного смещения
    shift_x = random.randint(-width // 2, width // 2)
    shift_y = random.randint(-height // 2, height // 2)

    # Обеспечение, что координаты обрезки находятся в пределах изображения
    left = max(0, min(shift_x, width))
    upper = max(0, min(shift_y, height))
    right = max(width, min(shift_x + width, width * 2))
    lower = max(height, min(shift_y + height, height * 2))

    # Создание нового изображения для смещённого пятна
    shifted_spot = np.array(spot.crop((left, upper, right, lower)))

    return shifted_spot


# Создания абстрактного серого пятна
def create_grey_spot(np_img):
    width, height = np_img.shape
    overlay_array = create_abstract_spot(width, height)
    limited_overlay = np.clip(overlay_array, random.randint(0, 20), 100)
    np_array = np.where(limited_overlay < np_img, np_img - limited_overlay, np_img)
    return np_array


# Создания абстрактного белого пятна
def create_light_spot(np_img):
    width, height = np_img.shape
    overlay_array = create_abstract_spot(width, height)
    limited_overlay = np.clip(overlay_array, random.randint(0, 80), 120)
    np_array = np.where(np_img < limited_overlay, limited_overlay + np_img, np_img)
    return np_array


def random_perspective_change(np_img):
    rows, cols = np_img.shape[:2]
    shift_y = rows // 20
    shift_x = cols // 20
    top_left = [random.randint(0, shift_x), random.randint(0, shift_y)]
    top_right = [random.randint(cols - shift_x, cols), random.randint(0, shift_y)]
    bottom_left = [random.randint(0, shift_x), random.randint(rows - shift_y, rows)]
    bottom_right = [random.randint(cols - shift_x, cols), random.randint(rows - shift_y, rows)]

    corners = np.int32([[0, 0], [cols, 0], [0, rows], [cols, rows]])
    new_corners = np.int32([top_left, top_right, bottom_left, bottom_right])

    M = cv2.getPerspectiveTransform(corners, new_corners)
    np_img = cv2.warpPerspective(np_img, M, (cols, rows))

    return np_img, new_corners


def random_rotate_image(np_img):
    rows, cols = np_img.shape[:2]
    angle = random.uniform(-5, 5)
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    np_img = cv2.warpAffine(np_img, M, (cols, rows))

    # Расчёт новых координат углов
    corners = np.array([
        [0, 0],
        [cols, 0],
        [0, rows],
        [cols, rows]
    ])
    new_corners = np.int32(np.dot(M[:, :2], corners.T).T + M[:, 2])

    return np_img, new_corners
