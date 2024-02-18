#Создание превью текстовых вставок в документы в растре в \generated_files\text_fragments
import sys
sys.path.append('/content/invoices_generator')

import json
import os
import random
from PIL import Image, ImageDraw
from config import json_file_path, generated_images_files_folder, markup_images_folder


# Генерация случайного цвета RGB
def randomColor():
    return (random.randint(50, 150),
            random.randint(130, 220),
            random.randint(160, 250))


def drawRectangles(canvas, rects):
    for rect in rects:
        canvas.rectangle(rect, outline=randomColor())


def readStrToList(json_str):
    values = json_str.split(',')
    x1, y1, w, h = [round(float(value.strip())) for value in values]
    x2, y2 = x1 + w, y1 + h
    return [x1, y1, x2, y2]


def drawBBoxes(data):
    for invoice in data:

        file_name = f"invoice_{invoice['number']}.png"
        image_path = os.path.join(generated_images_files_folder, file_name)
        if os.path.exists(image_path):
            print('Открываю', file_name)
        else:
            print(file_name + " отсутствует. Проверь папку " + generated_images_files_folder)
            return False

        output_path = os.path.join(markup_images_folder, file_name)
        bboxes = []

        # Распаковка JSON
        for category, items in invoice['bbox_x_y_w_h'].items():
            if category != "itemsList":  # Обрабатываем все категории, кроме 'itemsList'
                for _, bbox_str in items.items():
                    bboxes.append(readStrToList(bbox_str))
            else:  # Обрабатываем 'itemsList'
                for _, item in items.items():
                    for _, sub_items in item.items():
                        for _, bbox_str in sub_items.items():
                            bboxes.append(readStrToList(bbox_str))

        # Сохранение и/или открытие изображения с bbox-ми
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)
            drawRectangles(draw, bboxes)
            img.save(output_path)
            # img.show()
    return True


# Чтение JSON файла
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

if drawBBoxes(json_data):
    print()
    print('Разметка текстовых фрагментов расставлена!')
    print('Сгенерированные тексты обведены рамками по координатам из generated_data.json')
    print('Файлы с превью в папке ' + markup_images_folder)
