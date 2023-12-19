# -*- coding: utf-8 -*-
import os

# количество генерируемых счетов
files_number = 5
# разрешение генерируемых файлов
dpi = 144
# коэфициент масштабирования при генерации
dim_scale = dpi / 72
# коэффициент масштабирования при искажениях
distortion_scale = 1.0
# размер печати в пикселях
stamp_size = int(130 * dim_scale)

# имена и пути к рабочим файлам
list_data_files = {
    'addresses.csv': 'https://drive.google.com/uc?export=download&id=14qnEbj33g6XDxotNZBjEwZE49MrhrPBQ',
    'companies.tsv': 'https://drive.google.com/uc?export=download&id=1JnM0XWKVUPMQeeHDZb0O_pzO9yHhU2SL',
    'products.csv': 'https://drive.google.com/uc?export=download&id=158xXZiDMELAChxU4Gci7p6E-2Ns59qsN',
    'banks.csv': 'https://drive.google.com/uc?export=download&id=1axTYKpLPCeuh943r6s6E8K7Nf9wGg0fz'
    }
base_dir = os.path.dirname(os.path.abspath(__file__))
json_file_name = os.path.join(base_dir, 'generated_data.json')
data_files_folder = os.path.join(base_dir, 'data')
base_svg_file_name = os.path.join(data_files_folder, 'invoice.svg')
svg_templates_files_folder = os.path.join(base_dir, 'svg_templates')
generated_images_files_folder = os.path.join(base_dir, 'generated_images')
stamps_files_folder = os.path.join(base_dir, 'generated_stamps')
distorted_images_files_folder = os.path.join(base_dir, 'distorted_images')
stamped_images_files_folder = os.path.join(base_dir, 'stamped_images')
font_path = os.path.join(base_dir, 'assets', 'arialmt.ttf')

# Сумма счета словами (по-умолчанию - тенге):
currency_main = ('тенге', 'тенге', 'тенге')
currency_additional = ('тиын', 'тиына', 'тиынов')

# currency_main = ('рубль', 'рубля', 'рублей')
# currency_additional = ('копейка', 'копейки', 'копеек')