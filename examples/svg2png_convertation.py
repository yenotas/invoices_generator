from invoices_generator.config import original_images_files_folder, temp_folder
from invoices_generator.svg_templates_generator import convert_svg_to_pdf, convert_pdf_to_png
import os

input_folder = temp_folder
output_folder = original_images_files_folder

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Получаем список SVG-файлов в папке
svg_files = [f for f in os.listdir(input_folder) if f.endswith('.svg')]

# Обработка каждого SVG-файла
for svg_file in svg_files:
    input_path = os.path.join(input_folder, svg_file)
    output_path = os.path.join(output_folder, svg_file.replace('.svg', '.png'))

    pdf_filename = input_path.replace('.svg', '.pdf')
    convert_svg_to_pdf(input_path, pdf_filename)
    convert_pdf_to_png(pdf_filename, output_path)

    os.remove(pdf_filename)
    print(output_path)