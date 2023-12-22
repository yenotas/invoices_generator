# invoices generator
#### Код: AndrejPress (Коваленко А.В.) 11/12.2023 в рамках практики УИИ (разработка OCR AI)
https://github.com/yenotas/invoices_generator/
####
Генератор тестовых данных и изображений счетов с искажениями, шумами и печатями, 
для тестирования и обучения системы распознавания документов. 
Библиотека имитации отсканированных документов, с хранением данных 
(по которым строятся счета) в "generated_data.json". 
В JSON при построении SVG-файлов дописываются координаты центров надписей
### Использование:
В "config.py" можно указать количество генерируемых файлов, качество и масштабирование 
изображений, скорректировать размер печати, изменить валюту счета
####
В папке "examples" - скрипты, поочередно запуская которые (по номерам),
можно заполнить все папки генерациями - от "generated_data.json" и шаблонов SVG 
до изображений JPEG с искажениями и добавленными круглыми печатями.
Папка "generated_files" и соответствующие поддиректории, с генерируемыми файлами, 
создаются скриптами.

####  Для конвертации SVG-файлов в PNG выбрать 1й или 2й способ:
1й способ - быстрая конвертация локально, но капризен при запуске из google colab
1. Установить ImageMagick:
   + для Windows: https://imagemagick.org/script/download.php#windows
   + для Linux: sudo apt-get install imagemagick
   + для macOS: brew install imagemagick
   + установить библиотеку Wand (уже включена в requirements.txt)
    
2й способ - заметно медленнее, но нет проблем в google colab
2. Скачать утилиту Poppler 
   + для Windows (на локальный диск): https://github.com/oschwartz10612/poppler-windows/releases/
     + добавить путь к папке \poppler\Library\bin в переменную окружения PATH вашей системы
     + перезагрузить командную строку (или IDE) для обновления PATH
   + для Linux: apt-get install poppler-utils
   + установить библиотеки: svglib reportlab pdf2image (включены в requirements_p.txt)

### Установка локально:
Для установки библиотек:
+ "pip install -r requirements.txt" - если выбрана утилита ImageMagick
  + *для конвертации используйте "03_conversion_svg2png_example.py"
+ "pip install -r requirements_p.txt" - если выбрана утилита Poppler (2й способ)
  * *для второго способа конвертации используйте "03_conversion_svg2png_example_p.py"
  работающий на модуле svg_templates_helper_p.py
+ Перезапустить IDE-редактор



