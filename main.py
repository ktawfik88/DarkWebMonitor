import asyncio

from appwrite.client import Client
from appwrite.query import Query
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.database.DatabaseManager import DatabaseManager
from modules.extract.DocumentProcessor import DocumentProcessor
from modules.telegram.TelegramFileDownloader import TelegramFileDownloader
from apscheduler.schedulers.background import BackgroundScheduler

API_ID = '25300272'
API_HASH = 'a0166a57b88631ad00b04746d9af9dae'
phone = "+201159280528"

client = Client()
client.set_endpoint("https://foxhat.org/v1")
client.set_project("65af20b9daebac75cc9c")
client.set_key(
    '8698d00c88eecb9af716e39aae6fa6852dc13ed8f0add7c7bda62010b925957cc10a7aa05620052fa258b0356b54172618e8a45588f6a463edddc52b61215584d561412478866d02d0bfa6847835ce7f17e3cbdd9859fd6390a4773b36d6ebffd7ca0242aa9e49e5fa1ebc071f94231964c18e296bfa90ee5511e6afcbd99bc1')

database = DatabaseManager(client=client)
documentProcessor = DocumentProcessor(database)
downloader = TelegramFileDownloader(API_ID, API_HASH, phone, database, documentProcessor)

attribute_name = "keywords"
method_name = "contains"
attribute_values = ["api"]


async def start_telegram():
    await downloader.connect_telegram(phone)
    start_listening_task = asyncio.create_task(downloader.download_files())
    await asyncio.gather(start_listening_task)


if __name__ == "__main__":
    asyncio.run(start_telegram())
