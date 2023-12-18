# -*- coding: utf-8 -*-
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
json_file_name = os.path.join(base_dir, 'generated_data.json')
data_files_folder = os.path.join(base_dir, 'data')
base_svg_file_name = os.path.join(data_files_folder, 'invoice.svg')
svg_templates_files_folder = os.path.join(base_dir, 'svg_templates')
generated_images_files_folder = os.path.join(base_dir, 'generated_images')
stamps_files_folder = os.path.join(base_dir, 'generated_stamps')
distorted_images_files_folder = os.path.join(base_dir, 'distorted_images')
font_path = os.path.join(base_dir, 'assets', 'arialmt.ttf')

list_data_files = {
    'addresses.csv': 'https://drive.google.com/uc?export=download&id=14qnEbj33g6XDxotNZBjEwZE49MrhrPBQ',
    'companies.tsv': 'https://drive.google.com/uc?export=download&id=1JnM0XWKVUPMQeeHDZb0O_pzO9yHhU2SL',
    'products.csv': 'https://drive.google.com/uc?export=download&id=158xXZiDMELAChxU4Gci7p6E-2Ns59qsN',
    'banks.csv': 'https://drive.google.com/uc?export=download&id=1axTYKpLPCeuh943r6s6E8K7Nf9wGg0fz'
    }