# Пример генерации и вывода товаров в счете

import pandas as pd
from modules.strings_generator import genProductsList, get_string_by_number, currency_main, \
    currency_additional, loadDataFromFile, getRandomInvoiceName, getRandomContractName, \
    genFullAddress, strLineSplitter
from config import list_data_files

json_data = {}
for filename, url in list_data_files.items():
    json_data[filename] = loadDataFromFile(filename)
    # для скачивания из google disk:
    # data[filename] = load_data_from_file(filename, url)


n = 4 # количество товаров в счете
product_names, units, prices, vals, summ, amount = genProductsList(json_data, n)
title = getRandomInvoiceName()
contract = getRandomContractName()
seller_addr, _ = genFullAddress(json_data)
seller_addr = strLineSplitter(seller_addr, 55, 3)

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
print(f"Всего наименований: {n}, на сумму {'{:.2f}'.format(amount)} KZT\n")

invoice_amount_str = get_string_by_number(amount, currency_main, currency_additional)

print(f"Всего к оплате: {invoice_amount_str}")