import os
import re
from urllib.parse import urlparse
from datetime import datetime
import patoolib

# Assuming these functions and variables are defined elsewhere in your code
# Replace these with your actual implementations or values
# get_main_domain(url), databases, ID, country_pattern, log_date_pattern, password_pattern
from appwrite.id import ID
from appwrite.query import Query


class DocumentProcessor:

    def __init__(self, databaseManager):
        self.databaseManager = databaseManager

    def get_main_domain(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain_parts = domain.split('.')
        main_domain = '.'.join(domain_parts[-2:])
        return main_domain

    def extract_keywords(self, url):
        parsed_url = urlparse(url)
        subdomains = parsed_url.hostname.split('.')
        path_segments = [segment for segment in parsed_url.path.split('/') if segment]
        keywords = subdomains + path_segments
        return keywords

    def is_public_email(self, email):
        public_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "mail.com", "zoho.com",
            "gmx.com", "yandex.com", "live.com", "inbox.com", "fastmail.com"
        ]

        try:
            _, domain = email.split('@')
            return domain.lower() in public_domains

        except ValueError:
            return False

    def process_documents(self):
        try:
            documents = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("downloaded", True), Query.equal("completed", False)]
            )
            global current_country
            log_date = ""
            password_pattern = re.compile(r'URL: (.*?)\n(?:USER|Username): (.*?)\n(?:PASS|Password): (.*?)\n',
                                          re.DOTALL)
            country_pattern = r'Country: (.*)'
            log_date_pattern = r'Log date: (.*)'

            passwords_files = ["Passwords.txt", "All Passwords.txt"]
            information_files = ["UserInformation.txt", "Software.txt"]
            extracted_folder = f'unzipped'
            current_country = ""
            data = []
            url = ""
            folder_name = ""
            extracted_data = []
            sorting_order = {"UserInformation.txt": 0,
                             "Software.txt": 1, "Passwords.txt": 2, "All Passwords.txt": 3}
            # if text_after_password:
            #     patoolib.extract_archive(doc["file_path"], outdir=extracted_folder, password=text_after_password)
            # else:
            #     patoolib.extract_archive(doc["file_path"], outdir=extracted_folder)
            for root, dirs, files in os.walk(extracted_folder):

                sorted_files = sorted(files, key=lambda x: sorting_order.get(x, float('inf')))

                for file_name in sorted_files:
                    file_path = os.path.join(root, file_name)

                    if file_name in information_files and os.path.isfile(file_path):
                        with open(file_path, 'r', encoding='utf-8') as file:
                            user_info_content = file.read().strip()
                            country_matches = re.findall(country_pattern, user_info_content)
                            log_date_matches = re.findall(log_date_pattern, user_info_content)
                            if country_matches:
                                current_country = country_matches[0].replace('\r', '')

                            if log_date_matches:
                                log_date = log_date_matches[0].replace('\r', '')

                    if (file_name in passwords_files) and os.path.isfile(file_path):
                        folder_name = os.path.basename(root)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            passwords_content = file.read().strip()
                            matches = re.findall(password_pattern, passwords_content)
                            for match in matches:
                                url, username, password = match
                                parsed_url = urlparse(url.strip())
                                host = parsed_url.hostname
                                main_domain = self.get_main_domain(url)
                                print({"folder_name": folder_name, "current_country": current_country})





        except RuntimeError as e:
            print(f"Error: {e}")
