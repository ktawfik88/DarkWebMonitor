import os

from modules.telegram.TelegramFileDownloader import ROOT_Scripts

filename = '''6436_1935880746_\360\237\246\201Manticore Cloud-Main Channel\342\230\201\357\270\216.rar'''
decoded_filename = filename.encode('latin1').decode('utf-8')
print(decoded_filename)

unique_name = f'{343}_{3443}_Downloading 🦁Manticore Cloud-Main Channel☁︎.rar'
file_path = os.path.join(ROOT_Scripts, unique_name)
print(file_path)