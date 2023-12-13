font_path = "assets/arialmt.ttf"

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random


def draw_text_along_circle(draw, text, radius, center, font, color, start_angle=-math.pi / 2):
    angle_per_letter = 2 * math.pi / len(text)

    for i, letter in enumerate(text):
        angle = angle_per_letter * i + start_angle
        bbox = draw.textbbox((0, 0), letter, font=font)
        letter_width, letter_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        x = center[0] + radius * math.cos(angle) - letter_width / 2
        y = center[1] + radius * math.sin(angle) - letter_height / 2

        rotated_letter = Image.new('RGBA', (letter_width, letter_height), (0, 0, 0, 0))
        rotated_draw = ImageDraw.Draw(rotated_letter)
        rotated_draw.text((-bbox[0], -bbox[1]), letter, font=font, fill=color)
        rotated_letter = rotated_letter.rotate(-math.degrees(angle + math.pi/2), expand=1)

        # Вставляем повернутую букву на изображение
        image.paste(rotated_letter, (int(x), int(y)), rotated_letter)


def draw_center_text(draw, text, center, font, color):
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    x = center[0] - text_width / 2
    y = center[1] - text_height / 2
    draw.text((x, y), text, font=font, fill=color)


def generate_random_color():
    # Генерируем случайные значения для RGB
    r = random.randint(50, 200)
    g = random.randint(50, 200)
    b = random.randint(g+20, 255)  # Высокий синий всегда больше зеленого
    return f'#{r:02x}{g:02x}{b:02x}'


def generate_stamp(filename, text_outer_circle, text_inner_circle, text_center):
    # Параметры изображения и текста
    img_size = (328, 328)
    center = (img_size[0] / 2, img_size[1] / 2)
    font_by_circle = ImageFont.truetype(font_path, 18)
    font_by_center = ImageFont.truetype(font_path, 45)

    # Тексты
    text_color = generate_random_color()
    radius_outer = 160
    radius_inner = 90
    max_width = 0.8 * radius_inner

    # Создание изображения
    bg_color = (255, 255, 255, 0)  # Прозрачный для PNG, (255, 255, 255) для непрозрачного белого фона
    image = Image.new('RGBA', img_size, bg_color)
    draw = ImageDraw.Draw(image)

    # Рисуем окружности
    draw.ellipse([center[0]-radius_outer, center[1]-radius_outer, center[0]+radius_outer, center[1]+radius_outer], outline=text_color, width=4)
    draw.ellipse([center[0]-radius_outer+8, center[1]-radius_outer+8, center[0]+radius_outer-8, center[1]+radius_outer-8], outline=text_color, width=4)
    draw.ellipse([center[0]-radius_inner, center[1]-radius_inner, center[0]+radius_inner, center[1]+radius_inner], outline=text_color, width=3)

    # Рисуем тексты
    draw_text_along_circle(draw, text_outer_circle, radius_outer-25, center, font_by_circle, text_color)
    draw_text_along_circle(draw, text_inner_circle, radius_inner+20, center, font_by_circle, text_color)
    draw_center_text(draw, text_center, center, font_by_center, text_color)

    # Масштабируем изображение вверх
    scale_factor = 5  # множитель масштабирования
    large_image = image.resize((img_size[0] * scale_factor, img_size[1] * scale_factor), Image.NEAREST)

    # Применяем размытие для сглаживания
    large_image = large_image.filter(ImageFilter.GaussianBlur(radius=4))

    # Поворачиваем изображение
    angle = random.randint(0, 270)
    new_image = Image.new("RGBA", large_image.size, bg_color)
    new_image.paste(large_image, (0, 0))
    rotated_image = new_image.rotate(angle, expand=False)

    # Масштабируем изображение вниз
    final_image = rotated_image.resize(img_size, Image.LANCZOS)

    # Сохраняем
    final_image.save('/stamps/'+filename)


from string_generators import str_generator, set_splitters, str_line_splitter

base_splitters = ' '

for i in range(0, 5):
    num_splitters = random.randint(4, 8)
    holder = str_generator(num_splitters, num_splitters, lang='ru')
    holder_len = len(holder)
    num_symbols = 54
    letters_len = num_symbols - holder_len - num_splitters

    text_outer_circle = holder + str_generator(num_symbols, num_symbols-holder_len, lang='RU')
    text_outer_circle = set_splitters(text_outer_circle, holder_len, 0, num_splitters)
    text_inner_circle = str_generator(num_symbols+4, num_symbols + 4, lang='en')
    text_inner_circle = set_splitters(text_inner_circle, 0, 0, num_splitters+1)
    text_center = str_line_splitter(text_inner_circle[:10], 5, 2)
    generate_stamp('tmp_stmp_'+str(i)+'.png', text_outer_circle, text_inner_circle, text_center)
