import asyncio
import os
import datetime
import random
import re
import string

import pytz
from appwrite.query import Query
from starlette.background import BackgroundTasks
from telethon.errors import FileReferenceExpiredError
from telethon.sync import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename, PeerChannel
from appwrite.id import ID
from telethon import functions, types

from helper.FastTelethonhelper import fast_download
from modules.database.DatabaseManager import DatabaseManager
from modules.extract.DocumentProcessor import DocumentProcessor

ROOT_Scripts = os.path.join("downloads")


class TelegramFileDownloader:
    def __init__(self, api_id, api_hash, phone_number, databaseManager, documentProcessor):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.databaseManager = databaseManager
        self.documentProcessor = documentProcessor
        self.client = None

    def generate_random_filename(self, length=10):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))

    async def connect_telegram(self, phone):
        self.client = TelegramClient(phone, self.api_id, self.api_hash)
        await self.client.connect()
        await self.client.sign_in(phone, password="Eslam2020@@")

    async def download_files(self):
        folder_channels_ids = []
        result = await self.client(functions.messages.GetDialogFiltersRequest())
        for dialog_filter in result:
            dialog_dict = dialog_filter.to_dict()
            if dialog_dict.get("title") == "D":
                folder_channels_ids.extend(item.get("channel_id") for item in dialog_dict.get("include_peers", []))
        for channel_id in folder_channels_ids:
            channel = await self.client.get_entity(PeerChannel(channel_id))
            tz = pytz.timezone('UTC')
            current_date = datetime.datetime.now(tz).date()
            print(current_date)
            await self.get_messages_at_date(channel, current_date)

    async def background_task(self, event):
        global text_after_password_string, file_extension
        msg = event.message
        peer = msg.peer_id
        print(peer)
        if isinstance(peer, PeerChannel):
            channel_id = peer.channel_id
            r = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("message_id", msg.id), Query.equal("downloaded", True), Query.limit(1)]
            )
            print(r)
            if r["total"] == 0:
                message_date = msg.date
                date_str = message_date.strftime('%Y-%m-%d')
                self.create_folder_if_not_exists(ROOT_Scripts)
                unique_name = f'{msg.id}_{channel_id}_'
                file_path = os.path.join(ROOT_Scripts, unique_name)
                random_file_name = self.generate_random_filename()

                if msg.media and hasattr(msg.media, 'document'):
                    document = msg.media.document
                    for attr in document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name
                            break
                    else:
                        file_name = "unknown_filename.zip"

                    if document.mime_type == 'application/zip' or document.mime_type == 'application/vnd.rar':
                        if document.mime_type == 'application/zip':
                            file_extension = ".zip"
                        elif document.mime_type == 'application/vnd.rar':
                            file_extension = ".rar"
                        zip_download_path = f'{file_path}{random_file_name}{file_extension}'
                        file_name_2 = f'{random_file_name}{file_extension}'
                        text = msg.message
                        pattern = r'.pass: (.*)'
                        match = re.search(pattern, text)
                        if match:
                            text_after_password = match.group(1).encode('utf-8')
                            emoji_bytes = b'\xe2\x9e\x96'
                            if text_after_password == emoji_bytes:
                                text_after_password_string = None
                            else:
                                text_after_password_string = match.group(1)
                        r = self.databaseManager.create_document(
                            database_id="65b13882c47652982a05",
                            collection_id="65b187d22e21dd4a9645",
                            document_id=ID.unique(),
                            data={
                                "channel_id": channel_id,
                                "message_id": msg.id,
                                "file_name": file_name,
                                "file_path": zip_download_path,
                                "password_file": text_after_password_string
                            }

                        )
                        id = r["$id"]
                        try:
                            print(f"Downloading {file_name} (ID: {msg.id}, {document.size} bytes)...")
                            await fast_download(self.client, msg, filename=file_name_2, download_folder=file_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": True,
                                })
                            self.documentProcessor.process_document2(password_file=text_after_password_string,
                                                                     message_id=msg.id, channel_id=channel_id,
                                                                     file_path=zip_download_path, id=id,
                                                                     file_name_=file_name)
                        except FileReferenceExpiredError as e:
                            os.remove(zip_download_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": False,
                                    "error": e.message
                                })
                            pass
                        except Exception as e:
                            os.remove(zip_download_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": False,
                                    "error": str(e)
                                })
                            pass

    async def on_new_message(self, event):
        try:
            asyncio.create_task(self.background_task(event))
        except Exception as e:
            print(f"Error {e}")

            pass

    async def start_listening(self):
        folder_channels_ids = []
        result = await self.client(functions.messages.GetDialogFiltersRequest())
        for dialog_filter in result:
            dialog_dict = dialog_filter.to_dict()
            if dialog_dict.get("title") == "D":
                folder_channels_ids.extend(item.get("channel_id") for item in dialog_dict.get("include_peers", []))
        for channel_id in folder_channels_ids:
            channel = await self.client.get_entity(PeerChannel(channel_id))
            print(channel)
        self.client.add_event_handler(self.on_new_message, events.NewMessage(chats=folder_channels_ids))
        await self.client.run_until_disconnected()

    def create_folder_if_not_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    async def get_messages_at_date(self, channel, date):
        r = BackgroundTasks()
        global text_after_password_string, file_extension
        async for msg in self.client.iter_messages(channel, reverse=True, offset_date=date):
            r = self.databaseManager.list_documents(
                database_id="65b13882c47652982a05",
                collection_id="65b187d22e21dd4a9645",
                queries=[Query.equal("message_id", msg.id), Query.equal("downloaded", True), Query.limit(1)]
            )
            if r["total"] == 0:
                message_date = msg.date
                date_str = message_date.strftime('%Y-%m-%d')
                self.create_folder_if_not_exists(ROOT_Scripts)
                unique_name = f'{msg.id}_{channel.id}_'
                file_path = os.path.join(ROOT_Scripts, unique_name)
                if msg.media and hasattr(msg.media, 'document'):
                    document = msg.media.document
                    for attr in document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name
                            break
                    else:
                        file_name = "unknown_filename.zip"
                    if document.mime_type == 'application/zip' or document.mime_type == 'application/vnd.rar':
                        if document.mime_type == 'application/zip':
                            file_extension = ".zip"
                        elif document.mime_type == 'application/vnd.rar':
                            file_extension = ".rar"
                        file_name_2 = f'{self.generate_random_filename()}{file_extension}'
                        zip_download_path = f'{file_path}{self.generate_random_filename()}{file_extension}'
                        print(zip_download_path)
                        text = msg.message
                        pattern = r'.pass: (.*)'
                        match = re.search(pattern, text)
                        if match:
                            text_after_password = match.group(1).encode('utf-8')
                            emoji_bytes = b'\xe2\x9e\x96'
                            if text_after_password == emoji_bytes:
                                text_after_password_string = None
                            else:
                                text_after_password_string = match.group(1)
                        r = self.databaseManager.create_document(
                            database_id="65b13882c47652982a05",
                            collection_id="65b187d22e21dd4a9645",
                            document_id=ID.unique(),
                            data={
                                "channel_id": channel.id,
                                "message_id": msg.id,
                                "file_name": file_name,
                                "file_path": zip_download_path,
                                "password_file": text_after_password_string
                            }

                        )
                        id = r["$id"]
                        try:
                            print(f"Downloading {file_name} (ID: {msg.id}, {document.size} bytes)...")
                            await fast_download(self.client, msg, filename=file_name_2, download_folder=file_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": True,
                                })
                            self.documentProcessor.process_documents_parallel_by_id(message_id=msg.id)
                        except FileReferenceExpiredError as e:
                            os.remove(zip_download_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": False,
                                    "error": e.message
                                })
                            pass
                        except Exception as e:
                            os.remove(zip_download_path)
                            result = self.databaseManager.update_document(
                                database_id="65b13882c47652982a05",
                                collection_id="65b187d22e21dd4a9645",
                                document_id=id,
                                data={
                                    "downloaded": False,
                                    "error": str(e)
                                })
                            pass
