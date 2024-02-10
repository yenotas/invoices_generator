#Создание превью текстовых вставок в документы в растре в \generated_files\text_fragments
import sys
sys.path.append('/content/invoices_generator')

import json
import os
import random
from PIL import Image, ImageDraw
from config import json_file_path, generated_images_files_folder, markup_images_folder
from modules.fs_utils import recreateFolder


# Генерация случайного цвета RGB
def randomColor():
    return (random.randint(50, 150),
            random.randint(130, 220),
            random.randint(160, 250))


def drawRectangles(canvas, rects):
    for rect in rects:
        canvas.rectangle(rect, outline=randomColor())


def readJSON(json_str):
    values = json_str.split(',')
    cx, cy, w, h = [int(value.strip()) for value in values]
    x1, y1 = cx - w // 2, cy - h // 2
    x2, y2 = cx + w // 2, cy + h // 2
    return  [x1, y1, x2, y2]


# Чтение JSON файла
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
    
for invoice in json_data:
    
    file_name = f"invoice_{invoice['number']}.png"
    print('Открываю', file_name)
    image_path = os.path.join(generated_images_files_folder, file_name)
    output_path = os.path.join(markup_images_folder, file_name)
    bboxes = []

    # Распаковка JSON
    for category, items in invoice['bbox_cx_cy_w_h'].items():
        if category != "itemsList":  # Обрабатываем все категории, кроме 'itemsList'
            for _, bbox_str in items.items():
                bboxes.append(readJSON(bbox_str))
        else:  # Обрабатываем 'itemsList'
            for _, item in items.items():
                for _, subitems in item.items():
                    for _, bbox_str in subitems.items():
                        bboxes.append(readJSON(bbox_str))

    # Сохранение и/или открытие изображения с bbox-ми
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        drawRectangles(draw, bboxes)
        img.save(output_path)
        # img.show()
