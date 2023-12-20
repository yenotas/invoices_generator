# -*- coding: utf-8 -*-
# Пример конвертации заполненных SVG-документов в PNG с утилитой Poppler

from invoices_generator.config import generated_images_files_folder, svg_templates_files_folder
from invoices_generator.svg_templates_helper_p import convert_svg_to_pdf, convert_pdf_to_png
import os

# Получаем список SVG-файлов в папке
svg_files = [f for f in os.listdir(svg_templates_files_folder) if f.endswith('.svg')]

# Обработка каждого SVG-файла
for svg_file in svg_files:
    input_path = os.path.join(svg_templates_files_folder, svg_file)
    output_path = os.path.join(generated_images_files_folder, svg_file.replace('.svg', '.png'))

    # конвертация с Poppler/pdf2image
    pdf_filename = input_path.replace('.svg', '.pdf')
    convert_svg_to_pdf(input_path, pdf_filename)
    convert_pdf_to_png(pdf_filename, output_path)
    os.remove(pdf_filename)

    print('convert', svg_file, 'is complete')

print()
print('conversion all SVG templates to PNG is complete')
print(f'files in folder "{generated_images_files_folder}"')