# -*- coding: utf-8 -*-
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

data_files_folder = os.path.join(current_dir, 'data')
svg_templates_files_folder = os.path.join(current_dir, 'svg_templates')
original_images_files_folder = os.path.join(current_dir, 'generated_images')
stamps_files_folder = os.path.join(current_dir, 'generated_stamps')
distorted_images_files_folder = os.path.join(current_dir, 'distorted_images')
temp_folder = os.path.join(current_dir, 'temp_files')
font_path = os.path.join(current_dir, 'assets', 'arialmt.ttf')

list_data_files = {
    'addresses.csv': 'https://drive.google.com/uc?export=download&id=14qnEbj33g6XDxotNZBjEwZE49MrhrPBQ',
    'companies.tsv': 'https://drive.google.com/uc?export=download&id=1JnM0XWKVUPMQeeHDZb0O_pzO9yHhU2SL',
    'products.csv': 'https://drive.google.com/uc?export=download&id=158xXZiDMELAChxU4Gci7p6E-2Ns59qsN',
    'banks.csv': 'https://drive.google.com/uc?export=download&id=1axTYKpLPCeuh943r6s6E8K7Nf9wGg0fz'
    }