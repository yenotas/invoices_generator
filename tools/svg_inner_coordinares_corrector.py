# Извлечение текстовых элементов из групп SVG с пересчетом координат
import sys
sys.path.append('/content/invoices_generator')

import re


def parseMatrix(matrix_str):
    # Разбиваем строку матрицы на числа
    matrix_values = list(map(float, re.findall(r'-?\d+\.\d+|-?\d+', matrix_str)))
    return matrix_values


def transformCoordinates(matrix_values, x, y):
    # Применяем преобразование координат с использованием матрицы
    new_x = matrix_values[0] * x + matrix_values[2] * y + matrix_values[4]
    new_y = matrix_values[1] * x + matrix_values[3] * y + matrix_values[5]
    return round(new_x), round(new_y)


def processSvg(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    # Ищем теги <g> с матрицей преобразования
    groups = re.findall(r'<g\s+transform="matrix\((.*?)\)"\s*>(.*?)</g>', svg_content, re.DOTALL)

    for matrix_str, group_content in groups:

        matrix_values = parseMatrix(matrix_str)

        # Ищем элементы внутри <g>
        text_elements = re.findall(r'<text(.*?)<\/text>', group_content, re.DOTALL)
        new_text_elements = ''

        for text_element in text_elements:
            x_match = text_element.split('"')[1]
            y_match = text_element.split('"')[3]

            if x_match and y_match:
                x = float(x_match)
                y = float(y_match)

                new_x, new_y = transformCoordinates(matrix_values, x, y)

                new_text_elements += ('<text' + text_element.replace(x_match, f'{new_x}')
                                .replace(y_match, f'{new_y}') + '</text>')

        # Заменяем старые теги
        if f'<g transform="matrix({matrix_str})">{group_content}</g>' in svg_content:
            svg_content = svg_content.replace(f'<g transform="matrix({matrix_str})">{group_content}</g>',
                                              new_text_elements)

    # Сохраняем SVG-файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)


# Пример использования
processSvg('invoice.svg', 'output.svg')
