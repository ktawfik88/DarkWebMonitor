from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.id import ID
from telethon import functions, types


class DatabaseManager:
    def __init__(self, client):
        self.client = client
        self.database = Databases(self.client)

    # def create_collection(self, name):
    #     try:
    #         collection = self.database.create_collection(name=name)
    #         return collection["$id"]
    #     except AppwriteException as e:
    #         print(f"Error creating collection: {e}")
    #         return None

    def create_document(self, database_id, collection_id, document_id, data):
        try:
            document = self.database.create_document(database_id=database_id, collection_id=collection_id,
                                                     document_id=document_id, data=data)
            return document
        except AppwriteException as e:
            print(f"Error creating document: {e}")
            return None

    def update_document(self, database_id,
                        collection_id,
                        document_id,
                        data):
        try:
            updated_document = self.database.update_document(database_id=database_id, collection_id=collection_id,
                                                             document_id=document_id,
                                                             data=data)
            return updated_document["$id"]
        except AppwriteException as e:
            print(f"Error updating document: {e}")
            return None

    def get_document(self, collection_id, document_id):
        try:
            document = self.database.get_document(collection_id=collection_id, document_id=document_id)
            return document
        except AppwriteException as e:
            print(f"Error getting document: {e}")
            return None

    def list_collections(self, database_id,
                         collection_id,
                         queries):
        try:
            collections = self.database.list_collections(database_id=database_id)
            return collections["collections"]
        except AppwriteException as e:
            print(f"Error listing collections: {e}")
            return None

    def list_documents(self, database_id, collection_id, queries):
        try:
            documents = self.database.list_documents(database_id=database_id, collection_id=collection_id,
                                                     queries=queries)
            return documents
        except AppwriteException as e:
            print(f"Error listing documents: {e}")
            return None
