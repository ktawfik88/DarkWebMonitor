import os
import re
import shutil
from urllib.parse import urlparse
from datetime import datetime
import patoolib

from appwrite.id import ID
from appwrite.query import Query
import concurrent.futures


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
        if parsed_url.hostname:
            subdomains = parsed_url.hostname.split('.')
        else:
            subdomains = []

        path_segments = [segment for segment in parsed_url.path.split('/') if segment]
        keywords = subdomains + path_segments
        return keywords

    def email2(self, email):
        obj = re.search(r'[\w.]+\@[\w.]+', email)
        if obj:
            return True
        else:
            return False

    def is_public_email(self, email):
        public_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "mail.com", "zoho.com",
            "gmx.com", "yandex.com", "live.com", "inbox.com", "fastmail.com"
        ]

        try:
            if self.email2(email):
                _, domain = email.split('@')
                return domain.lower() in public_domains
            else:
                return True


        except ValueError:
            return False

    def process_document(self, doc):
        print(doc["file_path"])
        print("work process_document")
        password_pattern = re.compile(
            r'(?:URL|Host): (.*?)\n(?:USER|Username|Login): (.*?)\n(?:PASS|Password): (.*?)\n', re.DOTALL)
        country_pattern = r'Country: (.*)'
        log_date_pattern = r'(?:Log date|Date): (.*)'
        text_after_password = doc.get("password_file", "")
        current_country = ""
        log_date = ""
        passwords_files = ["Passwords.txt", "All Passwords.txt", "passwords.txt"]
        information_files = ["UserInformation.txt", "Software.txt", "information.txt", "System.txt"]
        extracted_folder = f'unzipped/{doc["message_id"]}_{doc["channel_id"]}'
        sorting_order = {"UserInformation.txt": 0,
                         "Software.txt": 1, "information.txt": 2, "System.txt": 3, "Passwords.txt": 4,
                         "All Passwords.txt": 5, "passwords.txt": 6}
        folder_name2 = ""
        print("extracted zip")
        last_part = doc["file_path"].split('/')[-1]
        zip_path = f"downloads/'{last_part}'"
        try:
            if text_after_password:
                print(extracted_folder)
                patoolib.extract_archive(zip_path, outdir=extracted_folder, password=text_after_password)
            else:
                print("work text_after_password")
                patoolib.extract_archive(zip_path, outdir=extracted_folder)
        except Exception as e:
            print("Error")
            pass

        print("work root")
        for root, dirs, files in os.walk(extracted_folder):
            print(root)
            sorted_files = sorted(files, key=lambda x: sorting_order.get(x, float('inf')))
            try:
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

                    elif (file_name in passwords_files) and os.path.isfile(file_path):
                        folder_name = os.path.basename(root)
                        folder_name2 = root
                        with open(file_path, 'r', encoding='utf-8') as file:
                            passwords_content = file.read().strip()
                            matches = re.findall(password_pattern, passwords_content)
                            for match in matches:
                                url, username, password = match
                                parsed_url = urlparse(url.strip())
                                host = parsed_url.hostname
                                main_domain = self.get_main_domain(url)
                                print({"f": folder_name, "c": current_country, "url": url})
                                self.databaseManager.create_document(
                                    database_id="65b13882c47652982a05",
                                    collection_id="65b1396263d312b93ee3",
                                    document_id=ID.unique(),
                                    data={
                                        "channel_title": ".boxed.pw",
                                        "channel_id": doc.get("channel_id", ""),
                                        "message_id": doc.get("message_id", ""),
                                        "file_name_t": doc.get("file_name", ""),
                                        "file_size": 0,  # Update with the actual file size
                                        "domain": main_domain,
                                        "host": host,
                                        "full_url": url,
                                        "username": username.strip(),
                                        "password": password.strip(),
                                        "country": current_country,
                                        "folder_name": folder_name,
                                        "keywords": self.extract_keywords(url),
                                        "log_date": log_date,
                                        "created_at": datetime.now().strftime("%Y-%m-%d"),
                                        "isCompany": not self.is_public_email(username.strip())

                                    }
                                )
            except Exception as e:
                print(f"Error {e}")
                continue

        shutil.rmtree(extracted_folder)
        result = self.databaseManager.update_document(
            database_id="65b13882c47652982a05",
            collection_id="65b187d22e21dd4a9645",
            document_id=doc["$id"],
            data={
                "completed": True
            })

    def process_document2(self, password_file, message_id, channel_id, file_path, id, file_name_):
        print("work process_document")
        password_pattern = re.compile(
            r'(?:URL|Host): (.*?)\n(?:USER|Username|Login): (.*?)\n(?:PASS|Password): (.*?)\n', re.DOTALL)
        country_pattern = r'Country: (.*)'
        log_date_pattern = r'(?:Log date|Date): (.*)'
        text_after_password = password_file
        current_country = ""
        log_date = ""
        passwords_files = ["Passwords.txt", "All Passwords.txt", "passwords.txt"]
        information_files = ["UserInformation.txt", "Software.txt", "information.txt", "System.txt"]
        extracted_folder = f'unzipped/{message_id}_{channel_id}'
        if not os.path.exists(extracted_folder):
            os.makedirs(extracted_folder)
            print(f"The directory {extracted_folder} has been created.")
        else:
            print(f"The directory {extracted_folder} already exists.")
        sorting_order = {"UserInformation.txt": 0,
                         "Software.txt": 1, "information.txt": 2, "System.txt": 3, "Passwords.txt": 4,
                         "All Passwords.txt": 5, "passwords.txt": 6}
        folder_name2 = ""
        print("extracted zip")
        try:
            if text_after_password:
                print(extracted_folder)
                patoolib.extract_archive(file_path, outdir=extracted_folder, password=text_after_password)
            else:
                print("work text_after_password")
                patoolib.extract_archive(file_path, outdir=extracted_folder)
        except Exception as e:
            print(f"Error {e}")
            pass

        print("work root")
        for root, dirs, files in os.walk(extracted_folder):
            sorted_files = sorted(files, key=lambda x: sorting_order.get(x, float('inf')))
            try:
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

                    elif (file_name in passwords_files) and os.path.isfile(file_path):
                        folder_name = os.path.basename(root)
                        folder_name2 = root
                        with open(file_path, 'r', encoding='utf-8') as file:
                            passwords_content = file.read().strip()
                            matches = re.findall(password_pattern, passwords_content)
                            for match in matches:
                                url, username, password = match
                                parsed_url = urlparse(url.strip())
                                host = parsed_url.hostname
                                main_domain = self.get_main_domain(url)
                                self.databaseManager.create_document(
                                    database_id="65b13882c47652982a05",
                                    collection_id="65b1396263d312b93ee3",
                                    document_id=ID.unique(),
                                    data={
                                        "channel_title": ".boxed.pw",
                                        "channel_id": channel_id,
                                        "message_id": message_id,
                                        "file_name_t": file_name_,
                                        "file_size": 0,  # Update with the actual file size
                                        "domain": main_domain,
                                        "host": host,
                                        "full_url": url,
                                        "username": username.strip(),
                                        "password": password.strip(),
                                        "country": current_country,
                                        "folder_name": folder_name,
                                        "keywords": self.extract_keywords(url),
                                        "log_date": log_date,
                                        "created_at": datetime.now().strftime("%Y-%m-%d"),
                                        "isCompany": not self.is_public_email(username.strip())

                                    }
                                )
            except Exception as e:
                print(f"Error {e}")
                continue

        shutil.rmtree(extracted_folder)
        result = self.databaseManager.update_document(
            database_id="65b13882c47652982a05",
            collection_id="65b187d22e21dd4a9645",
            document_id=id,
            data={
                "completed": True
            })

    def process_documents(self):
        try:
            documents = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("downloaded", True), Query.equal("completed", False), Query.is_null("error"),
                         Query.order_desc("$createdAt"), Query.limit(10)]
            )

            for doc in documents:
                self.process_document(doc)
        except RuntimeError as e:
            print(f"Error: {e}")

    def process_documents_parallel(self):
        try:
            documents = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("downloaded", True), Query.equal("completed", False), Query.is_null("error"),
                         Query.order_desc("$createdAt"), Query.limit(10)]
            )

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_document, doc) for doc in documents]
                concurrent.futures.wait(futures)

        except Exception as e:
            print(f"Error processing documents in parallel {e}")

    def process_documents_parallel_by_id(self, message_id):
        print("Start process_documents_parallel_by_id")
        try:
            print("Start process_documents_parallel_by_id 2")
            documents = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("downloaded", True), Query.equal("completed", False), Query.is_null("error"),
                         Query.order_desc("$createdAt"), Query.equal("message_id", message_id), Query.limit(1)]
            )
            print(documents)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.process_document, doc) for doc in documents]
                concurrent.futures.wait(futures)
        except Exception as e:
            print(f"Error processing documents in parallel {e}")
