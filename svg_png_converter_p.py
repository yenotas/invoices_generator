# -*- coding: utf-8 -*-
'''
Конвертер в SVG-PNG.
SVG и PNG именуются по формуле "invoice_" + номер записи JSON (invoice['number'])
Автор: Коваленко А.В. 12.2023

Для конвертации SVG-файлов в PDF и PNG:
(2 способ смотри README)
1. Установить утилиту Poppler
https://github.com/oschwartz10612/poppler-windows/releases/
2. затем библиотеки svglib Pillow pdf2image - включены в requirements_p.txt
'''


from config import dpi
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from pdf2image import convert_from_path


# Двухэтапная конвертация с утилитой Poppler (см README):
def convert_svg_to_pdf(svg_filename, pdf_filename):
    drawing = svg2rlg(svg_filename)
    renderPDF.drawToFile(drawing, pdf_filename)


def convert_pdf_to_png(pdf_filename, png_filename):
    image = convert_from_path(pdf_filename, dpi=dpi)[0]
    image.save(png_filename, 'PNG')
