import os
from sys import path
path.append('/content/invoices_generator')
from modules.fs_utils import checkFolderExists

# Количество генерируемых счетов
FILES_NUMBER = 5

# сохранение растровых фрагментов текстовых вставок в папку generated_files/text_fragments и вывод метрик на консоль
# 0 или 1
save_text_fragments = 0

# Разрешение генерируемых файлов
DPI = 192

# Коэффициент соотношения с базовым разрешением. НЕ МЕНЯТЬ: 96 = база!
dim_scale = DPI / 96

# Коэффициент масштабирования при искажениях
distortion_scale = 1.0

# Размер печати в пикселях
stamp_size = int(150 * dim_scale)

# Имена и пути к рабочим файлам
list_data_files = {
    'addresses.csv': 'https://drive.google.com/uc?export=download&id=14qnEbj33g6XDxotNZBjEwZE49MrhrPBQ',
    'companies.csv': 'https://drive.google.com/uc?export=download&id=1oLuaWlcerOiQ-jxdlrg59sYhVJ00rmqK',
    'products.csv': 'https://drive.google.com/uc?export=download&id=158xXZiDMELAChxU4Gci7p6E-2Ns59qsN',
    'banks.csv': 'https://drive.google.com/uc?export=download&id=1axTYKpLPCeuh943r6s6E8K7Nf9wGg0fz'
}

base_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(base_dir, 'generated_data.json')
data_files_folder = os.path.join(base_dir, 'data')
svg_file_path = os.path.join(data_files_folder, 'invoice.svg')
embed_svg_path = os.path.join(data_files_folder, 'invoice_fnt.svg')
fonts_folder = os.path.join(data_files_folder, 'fonts')
font_path = os.path.join(fonts_folder, 'arial.ttf')
bold_font_path = os.path.join(fonts_folder, 'arialbd.ttf')

generated_files_folder = os.path.join(base_dir, 'generated_files')
svg_templates_files_folder = os.path.join(generated_files_folder, 'svg_templates')
generated_images_files_folder = os.path.join(generated_files_folder, 'generated_images')
stamps_files_folder = os.path.join(generated_files_folder, 'generated_stamps')
distorted_images_files_folder = os.path.join(generated_files_folder, 'distorted_images')
stamped_images_files_folder = os.path.join(generated_files_folder, 'stamped_images')
text_fragments_folder = os.path.join(generated_files_folder, 'text_fragments')
markup_images_folder = os.path.join(generated_files_folder, 'markup_images')
temp_folder = os.path.join(generated_files_folder, 'temp')

checkFolderExists(generated_files_folder, svg_templates_files_folder, generated_images_files_folder,
                  stamps_files_folder, distorted_images_files_folder, stamped_images_files_folder, markup_images_folder)


# Размеры SVG-макета
with open(svg_file_path, 'r', encoding='utf-8') as svg:
    content = svg.read().split('<defs>')[0]
WIDTH = round(int(content.split('width="')[1].split('px')[0])*dim_scale)
HEIGHT = round(int(content.split('height="')[1].split('px')[0])*dim_scale)


# Сумма счета словами (по-умолчанию - тенге):
currency_main = ('тенге', 'тенге', 'тенге')
currency_additional = ('тиын', 'тиына', 'тиынов')
# currency_main = ('рубль', 'рубля', 'рублей')
# currency_additional = ('копейка', 'копейки', 'копеек')
