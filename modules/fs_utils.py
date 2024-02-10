"""
Файловые утилиты
https://github.com/yenotas/invoices_generator
"""
import os
import shutil


def recreateFolder(folders):
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)


def getFileNames(target_folder):
    files = []
    for folder_name, _, filenames in os.walk(target_folder):
        for filename in filenames:
            files.append(filename)
    return files


def getFilePaths(target_folder):
    files = []
    for folder_name, _, filenames in os.walk(target_folder):
        for filename in filenames:
            files.append(os.path.join(folder_name, filename))
    return files


def checkFolderExists(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
