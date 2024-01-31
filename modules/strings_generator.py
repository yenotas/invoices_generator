# -*- coding: utf-8 -*-
"""
Генерация данных для счетов на оплату. Автор: Коваленко А.В. 11.2023
https://colab.research.google.com/drive/14-MopXdOeDVNon2703N-1R928mNxMmnJ?usp=sharing

setSplitters - расстановщик разделителей в строке с учетом количества первых
буквенных символов и длины заполнителя

strGenerator - универсальный генератор строки заданной длинны, кол-ва случайных
символов начала строки и заполнителем. Сумма первых символов (a-Z, а-Я) и длины
заполнителя должна быть меньше или равна числу символов, иначе выдаст "400".
По-умолчанию подставляет латинские символы - последний параметр = "EN" (может
быть "en", "RU", "ru")

возможные результаты использования set_splitters(str_generator()):
aA-bN/cN-dN, aA-bN-cN, aN/bN и т.п.
aN: b0+cN (b + c = a)
aA, aA + bA
где - a,b,c,d - произвольные числа >1, A-буквы, N-цифры
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
def randomNumNotnullStartswith(n):
    return str(random.randint(1, 9)) + ''.join(random.choices(numeric, k=n - 1))


# альтернатива заполнителю - генератор нулей, по умолчанию = 0000
def nullsStrGenerator(nulls_len=4):
    return ''.join(['0'] * nulls_len)


# вывод [n] результатов функции [func] для проверки. формат: loopPrint(n, lambda: func(**args))
def loopPrint(n, func):
    for _ in range(n):
        print(func())


def strGenerator(num_symbols=10, letters_len=0, holder='', lang='EN'):
    """
    Генератор строки заданной длинны, количества первых символов и заполнителем:
    - num_symbols - длина получаемой строки
    - letters_len - длина фрагмента букв в строке
    - holder - заполнитель, которая будет отделена разделителем
    - lang - язык букв 'RU'/'ru'/'En'/'en'
        * кириллица не включает мягкий и твердый знаки
        * сумма букв и длины заполнителя должна быть меньше или равна
        числу символов, иначе результат "400"
    """
    holder_len = len(holder)
    if letters_len + holder_len > num_symbols: return '400'

    letters = ''.join(random.choices(symbols_set[lang], k=letters_len))

    numbers_len = num_symbols - letters_len - holder_len
    num, numbers_str = 0, ''
    if numbers_len:
        num = random.randint(1, 10**numbers_len - 1)
        if random.randint(0, 2): # вероятность чисел меньше 3000
            num = min(num, random.randint(1, 3000))

        numbers_str = str(num)
        nulls_len = numbers_len - len(numbers_str)
        if nulls_len > 0:
            numbers_str = nullsStrGenerator(nulls_len) + numbers_str

    return letters + holder + numbers_str


def setSplitters(invoice_str='0000', letters_len=0, holder_len=0, num_splitters=1, splitters=base_splitters):
    """
    Расстановщик разделителей [base_splitters] в строке с учетом количества букв
    и длины заполнителя:
        invoice_str - исходная строка;
        letters_len - длина группы букв, не разбиваемая разделителем;
        holder_len - длина заполнителя, не разбиваемого разделителем;
        num_splitters - количество разделителей:
        - 1й ставится после группы букв (если задан letters_len);
        - 2й ставится после заполнителя, остальные делят оставшуюся строку на
        фрагменты произвольной длины, но не менее 1 символа между разделителями.
        Если количество разделителей не позволяет оставить хотя бы 1 символ между
        ними - вернет исходную строку.
    """
    invoice_str_len = len(invoice_str)
    remain_num_splitters = num_splitters - int(letters_len>0) - int(holder_len>0)
    remain_symb = invoice_str_len - letters_len - holder_len
    block_len = int(remain_symb/(remain_num_splitters + 1))

    if block_len < 1: return invoice_str

    pos_splitter = []
    i, pos = 0, 0
    num_blocks = num_splitters + 1
    remain_symb = invoice_str_len
    block_len = int(remain_symb / num_blocks)

    for i in range(0, num_splitters):

        if letters_len and i == 0:
            pos = letters_len

        elif holder_len:
            pos += holder_len
            letters_len, holder_len = 0, 0

        else:
            if num_blocks == 2:
                pos += int(random.uniform(1, remain_symb))
            else:
                pos += int(random.uniform(1, block_len + 1))

        pos_splitter.append(pos)
        num_blocks -= 1
        remain_symb = invoice_str_len + i - pos
        block_len = int(remain_symb / num_blocks)

        splitter = ''.join(random.choices(splitters, k=1))
        invoice_str = invoice_str[0:pos] + splitter + invoice_str[pos:]
        pos += 1

    return invoice_str


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
        lambda: setSplitters(strGenerator(12, 3, ''), 3, 0, 3),
        lambda: setSplitters(strGenerator(12, 2, '000'), 2, 3, 3),
        lambda: setSplitters(strGenerator(10, 0, '00'), 0, 2, 3),
        lambda: setSplitters(strGenerator(8, 0, ''), 0, 0, 2),
        lambda: setSplitters(strGenerator(6, 0, ''), 0, 0, 1),
        lambda: strGenerator(4, 0, '0'),
        lambda: strGenerator(6, 0, ''),
        lambda: strGenerator(6, 1, '-', 'RU'),
        lambda: strGenerator(9, 2, '-'),
        lambda: strGenerator(10, 0, ''),
        lambda: strGenerator(11, 3, '-'),
        lambda: strGenerator(12, 0, '')
    ])()


# миксер вариантов генерации номера договора
def randomContractNumber():
    d = numericDateGenerator().split('.')
    s = random.choice(base_splitters)
    return random.choice([
        lambda: setSplitters(strGenerator(8, 2, ''), 2, 2, 2),
        lambda: setSplitters(strGenerator(6, 0, ''), 0, 0, 1),
        lambda: strGenerator(4, 0, '0'),
        lambda: strGenerator(6, 0, ''),
        lambda: strGenerator(9, 1, s, 'RU'),
        lambda: strGenerator(10, 0, '0'),
        lambda: strGenerator(11, 3, s),
        lambda: strGenerator(10, 2, s, 'RU'),
        lambda: strGenerator(10, 2, s),
        lambda: strGenerator(12, 0, ''),
        lambda: strGenerator(2, 2, '', 'RU') + s + d[2] + s + d[1] + s + str(random.randint(10, 9999)),
        lambda: strGenerator(2, 2, '') + s + d[2] + s + '0' + str(random.randint(100, 99999))
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
    return randomNumNotnullStartswith(12)


# генератор ИИК
def getRandomIik():
    return 'KZ' + randomNumNotnullStartswith(18)


# генератор кода назначения платежа
def getRandomKnp():
    return randomNumNotnullStartswith(3)


# генератор кода кбе
def getRandomKbe():
    return randomNumNotnullStartswith(2)


# генератор почтового индекса
def getRandomPostIndex():
    return random.choice([random.choice('01') + randomNumNotnullStartswith(5), ''])


# генератор телефона
def getRandomTelephone():
    return '+7(' + randomNumNotnullStartswith(3) + ')-' + setSplitters(randomNumNotnullStartswith(7), 3, 2, 2, '-')


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
        text = text + '»'*(text.count('«') - text.count('»'))

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
    text = text.strip()+'\n' if text[-1] == '\n' else text.strip()
    return textDoubleSpacesClean(text)


# Замена двойных пробелов
def textDoubleSpacesClean(text):
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text


# Разбивка одной строки на неколько с переносом по словам
def strLineSplitter(text, num_symbols, num_lines):
    text = textDoubleSpacesClean(text[:num_symbols * num_lines].strip().replace('\n', ' '))
    text_len = len(text)
    if text_len < num_symbols + 2:
        return text

    new_text = [text[i * num_symbols: (i + 1) * num_symbols] for i in range(0, num_lines)]
    line_list, prev_last = [], ''

    num_lines = min(num_lines, ceil(text_len / num_symbols))  # наименьшее необходимое число строк

    i = 0
    for i in range(0, num_lines):
        pos = new_text[i].rfind(" ")
        line_list.append(prev_last + new_text[i][:pos])
        prev_last = new_text[i][pos + 1:]

    if len(prev_last + line_list[i]) < num_symbols + 3:
        line_list[i] = line_list[i] + ' ' + prev_last

    return '\n'.join(line_list)


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
        while len(rnd) < 3:  # проверяю что ряд содержал 3 значения, а не 2 или 1
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
