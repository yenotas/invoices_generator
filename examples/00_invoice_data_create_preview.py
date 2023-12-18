# -*- coding: utf-8 -*-
# Пример генерации и вывода товаров в счете

import pandas as pd
from invoices_generator.strings_generator import gen_products_list, get_string_by_number, currency_main, \
    currency_additional, load_data_from_file, get_random_invoice_name, get_random_contract_name, \
    gen_full_address, str_line_splitter
from invoices_generator.config import list_data_files

json_data = {}
for filename, url in list_data_files.items():
    json_data[filename] = load_data_from_file(filename)
    # для скачивания из google disk:
    # data[filename] = load_data_from_file(filename, url)


n = 4 # количество товаров в счете
product_names, units, prices, vals, summ, amount = gen_products_list(json_data, n)
title = get_random_invoice_name()
contract = get_random_contract_name()
seller_addr, _ = gen_full_address(json_data)
seller_addr = str_line_splitter(seller_addr, 55, 3)

print()
print(title, '\n')
print('По договору:', contract, '\n')
print('Поставщик:', seller_addr, '\n')

df = pd.DataFrame({
    "Наименование": product_names,
    "Кол-во": vals,
    "Ед.": units,
    "Цена": prices,
    "Сумма": summ
})
df.index = df.index + 1
print(df, '\n')
print(f"Итого: {'{:.2f}'.format(amount)}")
print(f"В том числе НДС: {'{:.2f}'.format(round(amount * 12/112, 2))}\n")
print(f"Всего нанаименований: {n}, на сумму {'{:.2f}'.format(amount)} KZT\n")

# Для рублей (по-умолчанию - тенге):
# currency_main = ('рубль', 'рубля', 'рублей')
# currency_additional = ('копейка', 'копейки', 'копеек')
invoice_amount_str = get_string_by_number(amount, currency_main, currency_additional)

print(f"Всего к оплате: {invoice_amount_str}")