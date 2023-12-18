# -*- coding: utf-8 -*-
'''
Генерация данных для счетов на оплату. Автор: Коваленко А.В. 11.2023
https://colab.research.google.com/drive/14-MopXdOeDVNon2703N-1R928mNxMmnJ?usp=sharing

set_splitters - расстановщик разделителей в строке с учетом количества первых
буквенных символов и длины заполнителя

str_generator - универсальный генератор строки заданной длинны, кол-ва случайных
символов начала строки и заполнителем. сумма первых символов (a-Z, а-Я) и длины
заполнителя должна быть меньше или равна числу символов, иначе выдаст "400".
по умолчанию подставляет латинские символы - последний параметр = "EN". он может
быть "en", "RU", "ru"

возможные результаты использования set_splitters(str_generator()):
aA-bN/cN-dN, aA-bN-cN, aN/bN и т.п.
aN: b0+cN (b + c = a)
aA, aA + bA
где - a,b,c,d - произвольные числа >1, A-буквы, N-цифры
'''
import random
import string
import requests
import csv
from math import ceil
import os
from invoices_generator.config import data_files_folder

from number_to_string import get_string_by_number

currency_main = ('тенге', 'тенге', 'тенге')
currency_additional = ('тиын', 'тиына', 'тиынов')

from datetime import datetime, timedelta

month = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня', '07': 'июля',
         '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}

# набор возможных разделителей: чем больше одинаковых символов, тем выше их вероятность в строоке
base_splitters = '--/-'

symbols_set = {'EN': string.ascii_uppercase,
               'en': string.ascii_lowercase,
               'RU': ''.join(chr(i) for i in range(1040, 1072) if not i in [1066, 1068]) + chr(1025),
               'ru': ''.join(chr(i) for i in range(1072, 1104) if not i in [1098, 1100]) + chr(1105)}

numeric = '0123456789'


def random_invoice_startswith():
    return random.choice(['Счет', 'Счет №', 'Счет на оплату №'])


def random_endswith():
    return random.choice(['г', 'г.', ''])


def random_space():
    return random.choice([' ', ''])


def random_contract_startswith():
    return random.choice(['', '№', 'Договор поставки №', 'Договор подряда №', 'Договор №', 'Без договора'])


# генератор номера из n цифр без нуля в начале
def random_num_notnull_startswith(n):
    return str(random.randint(1, 9)) + ''.join(random.choices(numeric, k=n - 1))


# альтернатива заполнителю - генератор нулей, по умолчанию = 0000
def nulls_str_generator(nulls_len=4):
    return ''.join(['0'] * nulls_len)


# вывод [n] результатов функции [func] для проверки. формат: loop_print(n, lambda: func(**args))
def loop_print(n, func):
    for _ in range(n):
        print(func())


def str_generator(num_symbols=10, letters_len=0, holder='', lang='EN' ):
    '''
    генератор строки заданной длинны, количества первых символов и заполнителем:
    - num_symbols - длина получаемой строки
    - letters_len - длина фрагмента букв в строке
    - holder - заполнитель, которая будет отделена разделителем
    - lang - язык букв 'RU'/'ru'/'En'/'en'
        * кириллица не включает мягкий и твердый знаки
        * сумма букв и длины заполнителя должна быть меньше или равна
        числу символов, иначе результат "400"
    '''
    holder_len =  len(holder)
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
            numbers_str = nulls_str_generator(nulls_len) + numbers_str

    return letters + holder + numbers_str


def set_splitters(invoice_str, letters_len=0, holder_len=0, num_splitters=1):
    '''
    расстановщик разделителей [base_splitters] в строке с учетом количества букв
    и длины заполнителя:
        invoice_str - исходная строка,
        letters_len - длина группы букв, которая не разбивается разделителем,
        holder_len - длина заполнителя, который не разбивается разделителем
        num_splitters - количество разделителей:
        - 1й ставится после группы букв (если задан letters_len),
        - 2й ставится после заполнителя, остальные делят оставшуюся строку на
        фрагменты произвольной длины, но не менее 1 символа между разделителями.
        Если количество разделителей не позволяет оставить хотя бы 1 символ между
        ними - вернет исходную строку.
    '''
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

        splitter = ''.join(random.choices(base_splitters, k=1))
        invoice_str = invoice_str[0:pos] + splitter + invoice_str[pos:]
        pos += 1

    return invoice_str


# генератор строки даты в указанном диапазоне лет в формате dd.mm.yyyy
def rus_text_date_generator(str_date):
    text_date = str_date.split('.')
    return text_date[0] + ' ' + month[text_date[1]] + ' ' + text_date[2]


def numeric_date_generator(start=2010, end=2023):
    start_date = datetime(start, 1, 1)
    end_date = datetime(end, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    result_date = random_date.strftime("%d.%m.%Y")

    return result_date


# миксер вариантов генерации номера счета
def random_invoice_number():
    return random.choice([
        lambda: set_splitters(str_generator(12, 3, ''), 3, 0, 3),
        lambda: set_splitters(str_generator(12, 2, '000'), 2, 3, 3),
        lambda: set_splitters(str_generator(10, 0, '00'), 0, 2, 3),
        lambda: set_splitters(str_generator(8, 0, ''), 0, 0, 2),
        lambda: set_splitters(str_generator(6, 0, ''), 0, 0, 1),
        lambda: str_generator(4, 0, '0'),
        lambda: str_generator(6, 0, ''),
        lambda: str_generator(6, 1, '-', 'RU'),
        lambda: str_generator(9, 2, '-'),
        lambda: str_generator(10, 0, ''),
        lambda: str_generator(11, 3, '-'),
        lambda: str_generator(12, 0, '')
    ])()


# миксер вариантов генерации номера договора
def random_contract_number():
    d = numeric_date_generator().split('.')
    s = random.choice(base_splitters)
    return random.choice([
        lambda: set_splitters(str_generator(8, 2, ''), 2, 2, 2),
        lambda: set_splitters(str_generator(6, 0, ''), 0, 0, 1),
        lambda: str_generator(4, 0, '0'),
        lambda: str_generator(6, 0, ''),
        lambda: str_generator(9, 1, s, 'RU'),
        lambda: str_generator(10, 0, '0'),
        lambda: str_generator(11, 3, s),
        lambda: str_generator(10, 2, s, 'RU'),
        lambda: str_generator(10, 2, s),
        lambda: str_generator(12, 0, ''),
        lambda: str_generator(2, 2, '', 'RU') + s + d[2] + s + d[1] + s + str(random.randint(10, 9999)),
        lambda: str_generator(2, 2, '') + s + d[2] + s + '0' + str(random.randint(100, 99999))
    ])()


# миксер вариантов генерации даты
def random_date(start=2015, end=2023):
    return random.choice([lambda: numeric_date_generator(start, end),
                          lambda: rus_text_date_generator(numeric_date_generator(start, end)),
                          lambda: rus_text_date_generator(numeric_date_generator(start, end))])()


# генератор названия счета с номером и датой
def get_random_invoice_name(start=2015, end=2023):
    result = random_invoice_startswith()

    if random.randint(0, 8) == 7:
        result = result.upper()

    result += random_space()
    result += random_invoice_number() + ' от '
    result += random_date(start, end) + random_space()
    result += random_endswith()

    return result


# генератор названия договора с номером и датой
def get_random_contract_name(start=2015, end=2023):
    result = random_contract_startswith()

    if random.randint(0, 8) == 7:
        result = result.upper()

    if not result in ['Без договора', 'БЕЗ ДОГОВОРА']:
        result += random_space()
        result += random_contract_number() + ' от '
        result += random_date(start, end) + random_space()
        result += random_endswith()

    return result


# генератор БИК банка Контрагента
def get_random_bik():
    return str_generator(8, 8, '')


# генератор БИН
def get_random_bin():
    return random_num_notnull_startswith(12)


# генератор ИИК
def get_random_iik():
    return 'KZ' + random_num_notnull_startswith(18)


# генератор кода назначения платежа
def get_random_knp():
    return random_num_notnull_startswith(3)


# генератор кода кбе
def get_random_kbe():
    return random_num_notnull_startswith(2)


# генератор почтового индекса
def get_random_post_index():
    return random.choice([random.choice('01') + random_num_notnull_startswith(5), ''])


# генератор телефона
def get_random_telephone():
    return '+7(' + random_num_notnull_startswith(3) + ')-' + set_splitters(random_num_notnull_startswith(7), 3, 2, 2)


# Генерация списка товаров
def get_random_bank(data):
    return random.choice(data['banks.csv'])[0]


# Генерация номера офиса с 10% вероятностью
def get_random_office():
    office = ''
    if random.randint(1, 10) == 1:
        office = f"{random.choice([', офис ', ' к.', ' оф.', ' кв ', '- ', ' п.'])}{random.randint(1, 1000)}"

    return office


# Замена двойных пробелов
def text_clean(text):
    return text.replace('  ', ' ')


# Разбивка одной строки на неколько с переносом по словам
def str_line_splitter(text, num_symbols, num_lines):
    text = text.replace('\n', ' ')
    text_len = len(text)
    if text_len < num_symbols + 2:
        return text_clean(text)

    new_text = [text[i * num_symbols: (i + 1) * num_symbols] for i in range(0, num_lines)]
    line_list, prev_last = [], ''

    num_lines = min(num_lines, ceil(text_len / num_symbols))  # наименьшее необходимое число строк

    i = 0
    for i in range(0, num_lines):
        pos = new_text[i].rfind(" ")
        line_list.append(text_clean(prev_last + new_text[i][:pos]))
        prev_last = new_text[i][pos + 1:]

    if len(prev_last + line_list[i]) < num_symbols + 3:
        line_list[i] = text_clean(line_list[i] + ' ' + prev_last)

    return '\n'.join(line_list)


# Генерация полного адреса: индекс и телефон указываются не всегда, пытаемся уложиться в 2 строки
def gen_full_address(data):
    companies, addresses = data['companies.tsv'], data['addresses.csv']
    city, company_name = random.choice(companies)
    company_name = company_name.replace('`', '"')
    street = ''.join(random.choice(addresses))
    post_index = get_random_post_index() + ' '
    tel = random.choice([', тел:', ', тел:', ', т:', ', телефон:', ', т/ф:', ''])
    tel = '' if tel == '' else f"{tel}{get_random_telephone()}"
    full_address = f"БИН / ИНН {get_random_bin()} {company_name} "
    address = f"Республика Казахстан, {city}, {street}{random.choice([', д.', ' д.', ' д.№', ' вл.', ' дом №', ' дом '])}"
    address += f"{random.randint(1, 300)}{get_random_office()}"

    if len(full_address + post_index + address) < 156:
        full_address = full_address + post_index + address
    else:
        full_address = full_address + address

    if len(full_address + tel) < 156:
        full_address = full_address + tel

    return full_address, company_name


# Генерация списка товаров (с разбивкой наименования до 3х строк)
def gen_products_list(data, n=3):
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
        product_names.append(str_line_splitter(name, 46, 3))
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
def gen_invoice_json(data, number=0, n=1):
    customer_addr, customer_name = gen_full_address(data)
    seller_addr, seller_name = gen_full_address(data)

    customer = str_line_splitter(customer_addr, 78, 2)
    seller = str_line_splitter(seller_addr, 78, 2)
    seller_name = str_line_splitter(seller_name, 55, 2)
    binn = get_random_bin()
    bank = get_random_bank(data)
    iik = get_random_iik()
    kbe = get_random_kbe()
    knp = get_random_knp()
    bik = get_random_bik()
    title = get_random_invoice_name()
    contract = get_random_contract_name()
    product_names, units, prices, vals, summ, amount = gen_products_list(data, n)

    total = "{:.2f}".format(round(amount, 2))
    nds = "{:.2f}".format(round(amount * 12 / (12 + 100), 2))
    items = f'{n}, на сумму {total} KZT'
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

    for i in range(n):
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


def download_file(fn, url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Загрузка", fn)
        with open(os.path.join(data_files_folder, fn), 'wb') as f:
            f.write(response.content)
    else:
        print("Не удалось загрузить", fn, response.status_code)


def load_data_from_file(fn, url=''):
    if url:
        download_file(fn, url)
    # Читаем файлы в массивы
    delimiter = '\t' if fn[-3:] == 'tsv' else ','
    with open(os.path.join(data_files_folder, fn), 'r', encoding='utf-8') as file:
        return [row for row in csv.reader(file, delimiter=delimiter)]
