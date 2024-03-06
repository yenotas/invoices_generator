import os
from sys import path
path.append('/content/invoices_generator')
from modules.fs_utils import checkFolderExists

# Количество генерируемых счетов
FILES_NUMBER = 10

# Режим искажений:
# 0 - без искажений чистый документ в PNG
# 1 - со случайным поворотом
# 2 - проворот или перспектива и шум
# 3 - проворот или перспектива, шум, случайные блики и пятна
MODE = 3

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
stamp_size = int(150 * dim_scale * distortion_scale)

# Имя шрифта (например 'Arial'), из папки 'data\fonts\', который будет принудительно использован
# для всех SVG-генераций в svg_templates_generator
# Если оставить '' - будут выбраны случайные из папки Fonts.
# В примерах (examples) операция стартует в 02_generation_svg_from_json_example
TEST_FONT_NAME = ''

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
fonts_folder = os.path.join(data_files_folder, 'fonts')
normal_font_path = os.path.join(fonts_folder, 'regular')
bold_font_path = os.path.join(fonts_folder, 'bold')
italic_font_path = os.path.join(fonts_folder, 'italic')
italic_bold_font_path = os.path.join(fonts_folder, 'bolditalic')


generated_files_folder = os.path.join(base_dir, 'generated_files')
svg_templates_files_folder = os.path.join(generated_files_folder, 'svg_templates')
generated_images_files_folder = os.path.join(generated_files_folder, 'generated_images')
stamps_files_folder = os.path.join(generated_files_folder, 'generated_stamps')
distorted_images_files_folder = os.path.join(generated_files_folder, 'distorted_images')
stamped_images_files_folder = os.path.join(generated_files_folder, 'stamped_images')
text_fragments_folder = os.path.join(generated_files_folder, 'text_fragments')
markup_images_folder = os.path.join(generated_files_folder, 'markup_images')
temp_folder = os.path.join(generated_files_folder, 'temp')

base_folders = [generated_files_folder, svg_templates_files_folder, generated_images_files_folder, text_fragments_folder,
                stamps_files_folder, distorted_images_files_folder, stamped_images_files_folder, markup_images_folder]

checkFolderExists(base_folders)

# Читаем шрифты
normal_fonts = {os.path.splitext(f)[0]: os.path.join(normal_font_path, f)
                for f in os.listdir(normal_font_path) if f.endswith('.ttf')}

bold_fonts = {os.path.splitext(f)[0]: os.path.join(bold_font_path, f)
              for f in os.listdir(bold_font_path) if f.endswith('.ttf')}

italic_fonts = {os.path.splitext(f)[0]: os.path.join(italic_font_path, f)
                for f in os.listdir(italic_font_path) if f.endswith('.ttf')}

italic_bold_fonts = {os.path.splitext(f)[0]: os.path.join(italic_bold_font_path, f)
                     for f in os.listdir(italic_bold_font_path) if f.endswith('.ttf')}

# Сумма счета словами (по-умолчанию - тенге):
currency_main = ('тенге', 'тенге', 'тенге')
currency_additional = ('тиын', 'тиына', 'тиынов')
# currency_main = ('рубль', 'рубля', 'рублей')
# currency_additional = ('копейка', 'копейки', 'копеек')
