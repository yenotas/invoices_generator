from modules.strings_generator import nPrint, randomContractNumber, randomInvoiceNumber
nPrint(100, lambda: 'Invoice:' + randomInvoiceNumber(), lambda: 'Contract:' + randomContractNumber())