"""
Генератор случайных искажений документов в PNG, имитирующих сканы документов разного качества.
Автор: Коваленко А.В. 12.2023
https://github.com/yenotas/invoices_generator
"""
import random
from PIL import Image, ImageDraw, ImageFilter
from config import distortion_scale
import numpy as np
import cv2
import os


def cvView(np_img):
    cv2.imshow('Image', np_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Миксер эффектов
def random_geometrical_effects(image):
    effect = random.choice([randomPerspectiveChange, randomRotateImage, notDistortions])
    print('эффект:', str(effect.__name__))
    return effect(image)


# Наложение штампа на исходный документ
def mergeStampToImage(background_cv2, overlay_cv2, position):
    # Переводим изображения в формат float для корректной обработки
    background = cv2.cvtColor(background_cv2, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    overlay = overlay_cv2.astype(np.float32) / 255

    # Размеры штампа
    oh, ow = overlay.shape[:2]

    # Регион на фоне, где будет штамп
    x, y = position
    bg_region = background[y:y + oh, x:x + ow]

    # Альфа-канал для наложения
    alpha_overlay = overlay[:, :, 3]

    # Пиксели фона, которые будут изменены (осветлены)
    mask_dark = (bg_region < 0.5).all(axis=2)  # Маска для темных пикселей фона

    # Перекрытие штампа с учетом альфа-канала и осветления темных точек
    for c in range(3):  # RGB каналы
        bg_c = bg_region[:, :, c]
        ol_c = overlay[:, :, c]

        # Осветление темных пикселей фона
        lightened_bg = bg_c + (ol_c * alpha_overlay * 0.1)

        # Пиксели штампа непосредственно
        stamp_pixels = ol_c * alpha_overlay + bg_c * (1 - alpha_overlay)

        # Объединяем осветленный фон и пиксели штампа
        bg_region[:, :, c] = np.where(mask_dark, lightened_bg, stamp_pixels)

    # Записываем измененный регион обратно в исходное изображение
    background[y:y + oh, x:x + ow] = bg_region

    # Преобразуем обратно в формат, подходящий для отображения с помощью OpenCV
    result = (background * 255).astype(np.uint8)
    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    # Преобразуем результат обратно в формат cv2 для вывода или сохранения
    result_image = Image.fromarray(np.uint8(result), mode='RGB')

    return result_image


# Чтение изображений из папки
def load_numpy_images_from_folder(folder, mode='L'):
    """
    :param folder:
    :param mode: 'L' = grey, 'C' = color, 'A'|any = without mode | with alfa-channel
    :return: img_arr array
    """
    img_arr = []
    for filename in sorted(os.listdir(folder)):
        img_path = os.path.join(folder, filename)
        try:
            if mode == 'L':
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            elif mode == 'C':
                img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            else:
                img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            img = cvResize(img, distortion_scale) if distortion_scale != 1.0 else img
            img_arr.append((img, filename))
        except IOError:
            print(f"Не удалось загрузить изображение: {filename}")
    return img_arr


def cvResize(np_img, k):
    return cv2.resize(np_img, None, fx=k, fy=k)


# Добавление шума
def createNoise(np_img):
    # Генерируем гауссовский шум (cр. знач. шума, стандартное отклонение шума, размеры изобр.)
    noise = np.random.normal(5, 15, np_img.shape).astype(np.uint8)
    random_image = round(random.uniform(0.9, 1.0), 1)
    random_noise = round(random.uniform(0.0, 0.3), 1)
    # добавляем сгенерированный шум к исходному изображению
    # cv2.bitwise_and, cv2.bitwise_or, cv2.bitwise_xor
    noisy_image = cv2.addWeighted(np_img, random_image, noise, random_noise, 0)

    return noisy_image


def makeGradientRectangle(width, height, direction='horizontal'):
    gradient = Image.new('L', (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    direct = width if direction == 'horizontal' else height
    for i in range(direct):
        value = int(55 + 200 * i / (direct - 200))
        draw.line([(i, 0), (i, height)] if direction == 'horizontal' else [(0, i), (width, i)], fill=value)
    return gradient


# Создание абстрактного пятна
def createAbstractSpot(width, height):
    # Создание большего рабочего холста
    canvas_width, canvas_height = width * 2, height * 2
    spot_img = Image.new('L', (canvas_width, canvas_height), 0)

    for _ in range(random.randint(3, 9)):
        radius_x = random.randint(width // 8, width // 2)
        radius_y = random.randint(height // 8, height // 2)
        center_x = random.randint(radius_x+200, canvas_width - radius_x)
        center_y = random.randint(radius_y+200, canvas_height - radius_y)
        angle = random.randint(0, 90)

        gradient = makeGradientRectangle(radius_x * 2, radius_y * 2, random.choice(['horizontal', 'vertical']))

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

    # Расчёт случайного смещения
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
def createGreySpot(np_img):
    height, width = np_img.shape
    overlay_array = createAbstractSpot(width, height)
    limited_overlay = np.clip(overlay_array, random.randint(0, 20), 100)
    np_array = np.where(limited_overlay < np_img, np_img - limited_overlay, np_img)
    return np_array


# Создания абстрактного белого пятна
def createLightSpot(np_img):
    height, width = np_img.shape
    overlay_array = createAbstractSpot(width, height)
    limited_overlay = np.clip(overlay_array, random.randint(0, 80), 120)
    np_array = np.where(np_img < limited_overlay, limited_overlay + np_img, np_img)
    return np_array


def randomPerspectiveChange(np_img):
    height, width = np_img.shape[:2]
    max_shift_y = height // 20
    max_shift_x = width // 20
    top_left = [random.randint(0, max_shift_x), random.randint(0, max_shift_y)]
    top_right = [random.randint(width - max_shift_x, width), random.randint(0, max_shift_y)]
    bottom_left = [random.randint(0, max_shift_x), random.randint(height - max_shift_y, height)]
    bottom_right = [random.randint(width - max_shift_x, width), random.randint(height - max_shift_y, height)]

    corners = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    new_corners = np.float32([top_left, top_right, bottom_left, bottom_right])

    matrix2D = cv2.getPerspectiveTransform(corners, new_corners)
    np_img = cv2.warpPerspective(np_img, matrix2D, (width, height))
    return np_img, new_corners.astype(int), 'perspective'


def randomRotateImage(np_img):
    height, width = np_img.shape[:2]
    angle = round(random.uniform(0.1, 5.0), 2)
    angle *= random.choice([-1, 1])

    # Центр поворота изображения
    center = (width / 2, height / 2)

    # Расчет матрицы поворота без масштабирования
    matrix2D = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Расчет координат углов после поворота
    corners = np.array([
        [0, 0],
        [width - 1, 0],
        [0, height - 1],
        [width - 1, height - 1]
    ], dtype="float32")

    new_corners = np.dot(matrix2D[:, :2], corners.T).T + matrix2D[:, 2]

    # Вычисление размера ограничивающего прямоугольника новых углов и масштаба
    x_coords, y_coords = new_corners[:, 0], new_corners[:, 1]
    new_width = np.max(x_coords) - np.min(x_coords)
    new_height = np.max(y_coords) - np.min(y_coords)

    scale_w = width / new_width
    scale_h = height / new_height
    scale = min(scale_w, scale_h, 1)  # Масштаб не должен быть больше 1

    # Расчет матрицы поворота с учетом масштаба
    matrix2D = cv2.getRotationMatrix2D(center, angle, scale)
    np_img = cv2.warpAffine(np_img, matrix2D, (width, height))

    # Вычисление новых координат углов с учетом масштаба
    new_corners_scaled = np.dot(matrix2D[:, :2], corners.T).T + matrix2D[:, 2]

    return np_img, new_corners_scaled.astype(int), 'rotate'


# Заглушка - никаких преобразований
def notDistortions(np_img):
    rows, cols = np_img.shape[:2]
    corners = np.array([
        [0, 0],
        [cols, 0],
        [0, rows],
        [cols, rows]
    ])
    return np_img, corners, 'Никаких изменений'
