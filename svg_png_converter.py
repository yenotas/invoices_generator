# -*- coding: utf-8 -*-
'''
Конвертер в SVG-PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 12.2023

Для конвертации SVG-файлов в PDF и PNG:
(1 способ - смотри README)
1. установить ImageMagick по ссылке:
Для Windows:
https://imagemagick.org/script/download.php#windows
(Для Linux: sudo apt-get install imagemagick
Для macOS: brew install imagemagick)
2. затем библиотеку Wand - включена в requirements.txt
'''

from config import dpi
from wand.image import Image
from wand.color import Color

def convert_svg_to_png(svg_filename, png_filename):
    with Image(filename=svg_filename, background=Color('white'), resolution=dpi) as img:
        img.format = 'png'
        img.save(filename=png_filename)
