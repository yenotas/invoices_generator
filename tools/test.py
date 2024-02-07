from PIL import Image, ImageDraw, ImageFont
from config import font_path


# Создаем объект шрифта
font = ImageFont.truetype(font_path, size=140)  # Размер шрифта 24

metrics = font.getmetrics()

# Создаем объект ImageDraw
img = Image.new('L', (800, 100), color='white')
draw = ImageDraw.Draw(img)

# Текст для измерения
text = "Hellp World!"
draw.text((0, 0), text, fill='black', font=font, stroke_width=0)

# Получаем размер текста
print(font.getbbox(text, stroke_width=2))

img.show()
