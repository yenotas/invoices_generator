"""
Генерация данных для счетов на оплату. Автор: Коваленко А.В. 11.2023
https://github.com/yenotas/invoices_generator
"""
import random
import string
import requests
import csv
from math import ceil
import os

from config import data_files_folder, currency_main, currency_additional
from number_to_string import get_string_by_number
from datetime import datetime, timedelta

month = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня', '07': 'июля',
         '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}

# набор возможных разделителей: чем больше одинаковых символов, тем выше их вероятность в строоке
base_splitters = '--/'

symbols_set = {'EN': string.ascii_uppercase,
               'en': string.ascii_lowercase,
               'RU': ''.join(chr(i) for i in range(1040, 1072) if not i in [1066, 1068]) + chr(1025),
               'ru': ''.join(chr(i) for i in range(1072, 1104) if not i in [1098, 1100]) + chr(1105)}

numeric = '0123456789'


# случайный пробел
def randomSpace():
    return random.choice([' ', ''])


def randomInvoiceStartswith():
    return random.choice(['Счет ', 'Счет №' + randomSpace(), 'Счет на оплату №' + randomSpace()])


def randomEndswith():
    return random.choice(['г', 'г.', ''])


def randomContractStartswith():
    s = random.choice(['', '№', 'Договор поставки №', 'Договор подряда №', 'Договор №', 'Без договора'])
    s = s + randomSpace() if s else s
    return s


# генератор номера из n цифр без нуля в начале
def notNullDigits(n):
    return str(random.randint(1, 9)) + ''.join(random.choices(numeric, k=n - 1))


# альтернатива заполнителю - генератор нулей, по умолчанию = 0000
def nullsStr(nulls_len=4):
    return ''.join(['0'] * nulls_len)


# вывод [n] выполнений функций [*func] для проверки: nPrint(n, lambda: func(*args), lambda: func(*args), ...)
def nPrint(n, *func):
    for _ in range(n):
        for f in func:
            print(f())


def strGenerator(num_symbols=1, letters_len=1, holder='', num_splitters=0, splitters=base_splitters, lang='EN'):
    """
    Генератор строки заданной длинны, нужного количества первых буквенных символов, с заполнителем и разделителями,
    все параметры не обязательны:
    - num_symbols - длина получаемой строки
    - letters_len - длина фрагмента букв в строке, будет отделен разделителем от holder или цифр
    - holder - строка-заполнитель, которая будет отделена разделителем
    - num_splitters - количество разделителей на всю получаемую строку
    - lang - язык букв 'RU'/'ru'/'En'/'en' (кириллица не включает мягкий и твердый знаки)
    - splitters - символы-разделители, например "#*|" (выбираются случайно)
    """

    holder_len = len(holder)
    n = num_symbols - letters_len - holder_len

    letters = '' if letters_len == 0 else ''.join(random.choices(symbols_set[lang], k=letters_len))

    has_digit = int(n > 0)
    split_hd = int(holder_len > 0 and num_splitters > 0) * has_digit
    split_lh = int(letters_len > 0 and num_splitters > 0 and (n > 0 or holder_len > 0))

    letters += ''.join(random.choices(splitters, k=1)) * split_lh
    if not has_digit:
        return (letters + holder)[:num_symbols + split_lh]

    holder += ''.join(random.choices(splitters, k=1)) * split_hd

    n_nulls = random.randint(0, n - 1)
    digits = '0' * n_nulls + ''.join(random.choices(numeric, k=n - n_nulls))

    num_splitters -= split_hd + split_lh
    digits = setSplitters(digits, num_splitters, splitters)

    return letters + holder + digits


def setSplitters(text='0000', num_splitters=1, splitters=base_splitters):
    """
    Расстановщик разделителей [base_splitters] в строке:
        - text - исходная строка;
        - num_splitters - количество разделителей, делят строку на
        фрагменты произвольной длины, но не менее 1 символа между разделителями.
        - splitters - символы-разделители, например "#*|" (выбираются случайно)
    """
    text_len = len(text)
    if num_splitters <= 0 or text_len < 2: return text

    i, pos = 0, 0
    num_blocks = num_splitters + 1
    symbols_len = text_len
    block_len = int(symbols_len / num_blocks)

    if block_len < 1:
        num_splitters = text_len - 1
        num_blocks = num_splitters + 1
        block_len = int(symbols_len / num_blocks)

    for i in range(0, num_splitters):

        if num_blocks == 2:
            pos += int(random.uniform(1, symbols_len))
        else:
            pos += int(random.uniform(1, block_len + 1))

        num_blocks -= 1
        symbols_len = text_len + i - pos
        block_len = int(symbols_len / num_blocks)

        splitter = ''.join(random.choices(splitters, k=1))
        text = text[0:pos] + splitter + text[pos:]
        pos += 1

    return text


# генератор строки даты в указанном диапазоне лет в формате dd.mm.yyyy
def rusTextDateGenerator(str_date):
    text_date = str_date.split('.')
    return text_date[0] + ' ' + month[text_date[1]] + ' ' + text_date[2]


def numericDateGenerator(start=2010, end=2023):
    start_date = datetime(start, 1, 1)
    end_date = datetime(end, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    result_date = random_date.strftime("%d.%m.%Y")

    return result_date


# миксер вариантов генерации номера счета
def randomInvoiceNumber():
    return random.choice([
        lambda: strGenerator(num_symbols=12, letters_len=3, holder='', num_splitters=3),
        lambda: strGenerator(10, 2, '', 2),
        lambda: strGenerator(8, 0, '', 1),
        lambda: strGenerator(6, 0),
        lambda: strGenerator(4, 0, '0'),
        lambda: strGenerator(6, 0),
        lambda: strGenerator(6, 1, '-', lang='RU'),
        lambda: strGenerator(9, 2, '-'),
        lambda: strGenerator(10, 0),
        lambda: strGenerator(11, 3, '-'),
        lambda: strGenerator(8, 0, '00')
    ])()


# миксер вариантов генерации номера договора
def randomContractNumber():
    d = numericDateGenerator().split('.')
    s = random.choice('./-')
    return random.choice([
        lambda: strGenerator(num_symbols=12, letters_len=3, num_splitters=3),
        lambda: strGenerator(num_symbols=10, letters_len=2, num_splitters=3),
        lambda: strGenerator(8, 2, '', 2),
        lambda: strGenerator(6, 0, ''),
        lambda: strGenerator(4, 0, '0'),
        lambda: strGenerator(6, 0),
        lambda: strGenerator(9, 1, holder=s, lang='RU'),
        lambda: strGenerator(10, 0, '0'),
        lambda: strGenerator(11, 3, holder=s),
        lambda: strGenerator(10, 2, holder=s, lang='RU'),
        lambda: strGenerator(10, 2, holder=s),
        lambda: strGenerator(12, 0),
        lambda: strGenerator(2, 2, '', lang='RU') + s + d[2] + s + d[1] + s + str(random.randint(10, 9999)),
        lambda: strGenerator(2, 2) + s + d[2] + s + '0' + str(random.randint(100, 99999))
    ])()


# миксер вариантов генерации даты
def randomDate(start=2015, end=2023):
    return random.choice([lambda: numericDateGenerator(start, end),
                          lambda: rusTextDateGenerator(numericDateGenerator(start, end)),
                          lambda: rusTextDateGenerator(numericDateGenerator(start, end))])()


# генератор названия счета с номером и датой
def getRandomInvoiceName(start=2015, end=2023):
    result = randomInvoiceStartswith()

    if random.randint(0, 8) == 7:
        result = result.upper()

    result += randomInvoiceNumber() + ' от '
    result += randomDate(start, end) + randomSpace()
    result += randomEndswith()

    return result


# генератор названия договора с номером и датой
def getRandomContractName(start=2015, end=2023):
    result = randomContractStartswith()

    if random.randint(0, 8) == 7:
        result = result.upper()

    if not result in ['Без договора', 'БЕЗ ДОГОВОРА']:
        result += randomSpace()
        result += randomContractNumber() + ' от '
        result += randomDate(start, end) + randomSpace()
        result += randomEndswith()

    return result


# генератор БИК банка Контрагента
def getRandomBik():
    return strGenerator(8, 8, '')


# генератор БИН
def getRandomBin():
    return notNullDigits(12)


# генератор ИИК
def getRandomIik():
    return 'KZ' + notNullDigits(18)


# генератор кода назначения платежа
def getRandomKnp():
    return notNullDigits(3)


# генератор кода кбе
def getRandomKbe():
    return notNullDigits(2)


# генератор почтового индекса
def getRandomPostIndex():
    return random.choice([random.choice('01') + notNullDigits(5), ''])


# генератор телефона
def getRandomTelephone():
    return '+7(' + notNullDigits(3) + ')-' + setSplitters(notNullDigits(7), 3)


# Генерация списка товаров
def getRandomBank(data):
    return random.choice(data['banks.csv'])[0]


def normalCase(text):
    text = strip(text)
    for i, word in enumerate(text.split(' ')):
        if (word.upper() == word and len(word) > 4) or (i == 0 and word[0].lower() == word[0]):
            text = text.replace(word, word.title())
    return text


# Замена символов после открывающейся французской кавычки на заглавные буквы
def upperCaseAfterQuotesStart(text):
    if '«' in text:
        for i, word in enumerate(text.split('«')):
            if not word: continue
            if word[0].lower() == word[0]:
                text = text.replace(word, word.capitalize())
    return text


# Чистка текста от избыточных кавычек, замена любых кавычек на парные французские и если открыто больше то закрыть
def replaceQuotes(text):
    while '""' in text or "''" in text or "``" in text:
        text = text.replace('""', '"')
        text = text.replace("''", "'")
        text = text.replace("``", "`")
    while '"' in text:
        text = text.replace('"', '«', 1).replace('"', '»', 1)
    while '`' in text:
        text = text.replace('`', '«', 1).replace('`', '»', 1)
    while "'" in text:
        text = text.replace("'", '«', 1).replace("'", '»', 1)
    if text[-1] in ".!;:?'`\"«":
        text = text[:-1]
    if text.count('«') > text.count('»'):
        text = text + '»' * (text.count('«') - text.count('»'))

    text = strip(text.replace('« ', ' «').replace(' »', '» '))

    return upperCaseAfterQuotesStart(text)


def randomReplaceQuotes(text):
    if random.randint(1, 4) == 1:
        return replaceQuotes(text)
    else:
        return replaceQuotes(text).replace('«', '"').replace('»', '"')


# Генерация номера офиса с 10% вероятностью
def getRandomOffice():
    office = ''
    if random.randint(1, 10) == 1:
        office = f"{random.choice([', офис ', ' к.', ' оф.', ' кв ', '- ', ' п.'])}{random.randint(1, 1000)}"

    return office


def strip(text):
    text = text.strip() + '\n' if text[-1] == '\n' else text.strip()
    return textDoubleSpacesClean(text)


# Замена двойных пробелов
def textDoubleSpacesClean(text):
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text


# Генерация полного адреса: индекс и телефон указываются не всегда, пытаемся уложиться в 2 строки
def genFullAddress(data):
    companies, addresses = data['companies.csv'], data['addresses.csv']
    city, company_name = random.choice(companies)
    company_name = randomReplaceQuotes(normalCase(company_name))
    street = ''.join(random.choice(addresses))
    post_index = getRandomPostIndex() + ' '
    tel = random.choice([', тел:', ', тел:', ', т:', ', телефон:', ', т/ф:', ''])
    tel = '' if tel == '' else f"{tel}{getRandomTelephone()}"
    full_address = f"БИН / ИНН {getRandomBin()} {company_name} "
    address = f"Республика Казахстан, {city}, {street}{random.choice([', д.', ' д.', ' д.№', ' вл.', ' дом №', ' дом '])}"
    address += f"{random.randint(1, 300)}{getRandomOffice()}"

    if len(full_address + post_index + address) < 156:
        full_address += post_index + address
    else:
        full_address += address

    if len(full_address + tel) < 156:
        full_address += tel

    return full_address, company_name


# Генерация списка товаров (с разбивкой наименования до 3х строк)
def genProductsList(data, n=3):
    products = data['products.csv']

    if not products: return

    product_names, units, prices, vals, summ = [], [], [], [], []
    amount = 0.00

    for i in range(0, n):
        rnd = random.choice(products)
        while len(rnd) != 3:  # проверяю что ряд содержал 3 значения, а не 2 или 1
            rnd = random.choice(products)
        name, unit, price = rnd
        price_val = float(price) + random.uniform(0.00, 0.99)
        product_names.append(strLineSplitter(randomReplaceQuotes(normalCase(name)), 44, 3))
        units.append(unit)
        prices.append("{:.2f}".format(price_val))
        if price_val < 100:
            val = random.randint(1, 100) * 10
        elif price_val < 1000:
            val = random.randint(1, 300)
        elif price_val < 10000:
            val = random.randint(1, 50)
        else:
            val = random.randint(1, 10)
        vals.append(f"{val}")
        sum_val = val * price_val
        summ.append("{:.2f}".format(sum_val))
        amount += sum_val

    return product_names, units, prices, vals, summ, round(amount, 2)


# Генерация всех значиний в счете номер [number] на [n] товаров
# Сборка в JSON
def genInvoiceJson(data, number=0, product_lines=1):
    customer_addr, customer_name = genFullAddress(data)
    seller_addr, seller_name = genFullAddress(data)
    customer = strLineSplitter(customer_addr, 74, 2)
    seller = strLineSplitter(seller_addr, 74, 2)
    seller_name = strLineSplitter(seller_name, 48, 2)
    binn = getRandomBin()
    bank = randomReplaceQuotes(getRandomBank(data))
    iik = getRandomIik()
    kbe = getRandomKbe()
    knp = getRandomKnp()
    bik = getRandomBik()
    title = getRandomInvoiceName()
    contract = getRandomContractName()
    product_names, units, prices, vals, summ, amount = genProductsList(data, product_lines)

    total = "{:.2f}".format(round(amount, 2))
    nds = "{:.2f}".format(round(amount * 12 / 112, 2))
    items = f'{product_lines}, на сумму {total} KZT'
    total_text = get_string_by_number(amount, currency_main, currency_additional)

    fields = {
        "number": str(number),
        "sellerName": seller_name,
        "customerName": customer_name,
        "bin": binn,
        "bank": bank,
        "iik": iik,
        "bik": bik,
        "kbe": kbe,
        "knp": knp,
        "title": title,
        "seller": seller,
        "customer": customer,
        "contract": contract,
        "itemsList": [],
        "amount": total,
        "nds": nds,
        "items": items,
        "total": total_text
    }

    for i in range(product_lines):
        item = {
            "num": str(i + 1),  # Номер продукта
            "name": product_names[i],
            "val": vals[i],
            "unit": units[i],
            "price": prices[i],
            "sum": summ[i]
        }
        fields["itemsList"].append(item)

    return fields


def getOneInvoiceJson(data, fn=0):
    def genProductsListOnes(products):
        n = len(products)
        if n == 0: return

        product_names, units, prices, vals, summ = [], [], [], [], []
        amount = 0.00

        i = 0
        while i < n:
            rnd = products[i]
            while len(rnd) != 3:  # проверяю что ряд содержал 3 значения, а не 2 или 1
                rnd = products[i]
                i += 1
            name, unit, price = rnd
            price_val = float(price) + random.uniform(0.00, 0.99)
            product_names.append(strLineSplitter(randomReplaceQuotes(normalCase(name)), 44, 3))
            units.append(unit)
            prices.append("{:.2f}".format(price_val))
            if price_val < 100:
                val = random.randint(1, 100) * 10
            elif price_val < 1000:
                val = random.randint(1, 300)
            elif price_val < 10000:
                val = random.randint(1, 50)
            else:
                val = random.randint(1, 10)
            vals.append(f"{val}")
            sum_val = val * price_val
            summ.append("{:.2f}".format(sum_val))
            amount += sum_val
            i += 1

        return product_names, units, prices, vals, summ, round(amount, 2)

    def getOneFullAddress(data):
        street = data['addresses.csv']
        city, company_name = data['companies.csv']
        company_name = randomReplaceQuotes(normalCase(company_name))
        post_index = getRandomPostIndex() + ' '
        tel = random.choice([', тел:', ', тел:', ', т:', ', телефон:', ', т/ф:', ''])
        tel = '' if tel == '' else f"{tel}{getRandomTelephone()}"
        full_address = f"БИН / ИНН {getRandomBin()} {company_name} "
        address = f"Республика Казахстан, {city}, {street}{random.choice([', д.', ' д.', ' д.№', ' вл.', ' дом №', ' дом '])}"
        address += f"{random.randint(1, 300)}{getRandomOffice()}"

        if len(full_address + post_index + address) < 156:
            full_address += post_index + address
        else:
            full_address += address

        if len(full_address + tel) < 156:
            full_address += tel

        return full_address, company_name

    customer_addr, customer_name = getOneFullAddress({'addresses.csv': data['addresses.csv'][0],
                                                      'companies.csv': data['companies.csv'][0]})
    seller_addr, seller_name = getOneFullAddress({'addresses.csv': data['addresses.csv'][1],
                                                  'companies.csv': data['companies.csv'][1]})
    customer = strLineSplitter(customer_addr, 74, 2)
    seller = strLineSplitter(seller_addr, 74, 2)
    seller_name = strLineSplitter(seller_name, 48, 2)
    binn = getRandomBin()
    bank = randomReplaceQuotes(data['banks.csv'][0])
    iik = getRandomIik()
    kbe = getRandomKbe()
    knp = getRandomKnp()
    bik = getRandomBik()
    title = getRandomInvoiceName()
    contract = getRandomContractName()
    product_names, units, prices, vals, summ, amount = genProductsListOnes(data['products.csv'])
    product_lines = len(product_names)
    total = "{:.2f}".format(round(amount, 2))
    nds = "{:.2f}".format(round(amount * 12 / 112, 2))
    items = f'{product_lines}, на сумму {total} KZT'
    total_text = get_string_by_number(amount, currency_main, currency_additional)

    fields = {
        "number": f"{fn}",
        "sellerName": seller_name,
        "customerName": customer_name,
        "bin": binn,
        "bank": bank,
        "iik": iik,
        "bik": bik,
        "kbe": kbe,
        "knp": knp,
        "title": title,
        "seller": seller,
        "customer": customer,
        "contract": contract,
        "itemsList": [],
        "amount": total,
        "nds": nds,
        "items": items,
        "total": total_text
    }

    for i in range(product_lines):
        item = {
            "num": str(i + 1),  # Номер продукта
            "name": product_names[i],
            "val": vals[i],
            "unit": units[i],
            "price": prices[i],
            "sum": summ[i]
        }
        fields["itemsList"].append(item)

    return [fields]


def downloadFile(fn, url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Загрузка", fn)
        with open(os.path.join(data_files_folder, fn), 'wb') as f:
            f.write(response.content)
    else:
        print("Не удалось загрузить", fn, response.status_code)


def loadDataFromFile(fn, url=''):
    if url:
        downloadFile(fn, url)
    # Читаем файлы в массивы
    delimiter = '\t' if fn[-3:] == 'tsv' else ','
    with open(os.path.join(data_files_folder, fn), 'r', encoding='utf-8') as file:
        return [row for row in csv.reader(file, delimiter=delimiter)]


# Разбивка одной строки на несколько с переносом по словам
def strLineSplitter(text, num_symbols, num_lines):
    """
    Делит строку на num_lines строк, каждая из которых содержит не более num_symbols символов.
    Если текст не умещается, он обрезается по последнему пробелу.

    :param text: Исходный текст для разделения.
    :param num_symbols: Максимальное количество символов в строке.
    :param num_lines: Желаемое количество строк.
    :return: Текст, разделенный на строки с учетом заданных ограничений.
    """
    # Разделяем текст на слова
    words = text.split()

    # Подготавливаем переменные для результата и текущей строки
    result = []
    current_line = ""

    for word in words:
        # Проверяем, не превышает ли добавление слова максимальную длину строки
        if len(current_line + word) <= num_symbols:
            # Если не превышает, добавляем слово в текущую строку
            current_line += (word + " ")
        else:
            # Если превышает, сохраняем текущую строку и начинаем новую
            result.append(current_line.strip())
            current_line = word + " "
            # Проверяем, достигнуто ли максимальное количество строк
            if len(result) == num_lines:
                break  # Останавливаем добавление строк

    # Добавляем оставшуюся часть, если не достигнуто максимальное количество строк
    if len(result) < num_lines:
        result.append(current_line.strip())

    # Обрезаем текст до нужного количества строк
    result = result[:num_lines]

    # Возвращаем строки, объединенные переносами
    return "\n".join(result)


def strLineSplitter_(text, num_symbols, num_lines):
    """Что не так с алгоритмом - делает осечки, посмотреть.."""
    text = textDoubleSpacesClean(text[:num_symbols * num_lines].strip().replace('\n', ' '))
    text_len = len(text)
    print(text, text_len)
    if text_len < num_symbols + 2:
        return text

    new_text = [text[i * num_symbols: (i + 1) * num_symbols] for i in range(0, num_lines)]
    print(new_text)
    line_list, prev_last = [], ''

    num_lines = min(num_lines, ceil(text_len / num_symbols))  # наименьшее необходимое число строк
    print(num_lines)

    i = 0
    for i in range(0, num_lines):
        pos = new_text[i].rfind(" ")
        line_list.append(prev_last + new_text[i][:pos])
        prev_last = new_text[i][pos + 1:]

    if len(prev_last + line_list[i]) < num_symbols + 3:
        line_list[i] = line_list[i] + ' ' + prev_last

    return '\n'.join(line_list)
