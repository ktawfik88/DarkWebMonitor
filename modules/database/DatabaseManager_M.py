from pymongo import MongoClient


class DatabaseManager:
    def __init__(self, connection_string, database_name):
        self.client = MongoClient(connection_string)
        self.database = self.client[database_name]

    def create_document(self, collection_name, document_data):
        try:
            collection = self.database[collection_name]
            result = collection.insert_one(document_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error creating document: {e}")
            return None

    def update_document(self, collection_name, document_id, update_data):
        try:
            collection = self.database[collection_name]
            result = collection.update_one({"_id": document_id}, {"$set": update_data})
            if result.modified_count > 0:
                return document_id
            else:
                print(f"Document with id {document_id} not found.")
                return None
        except Exception as e:
            print(f"Error updating document: {e}")
            return None

    def get_document(self, collection_name, document_id):
        try:
            collection = self.database[collection_name]
            document = collection.find_one({"_id": document_id})
            return document
        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def list_collections(self):
        try:
            return self.database.list_collection_names()
        except Exception as e:
            print(f"Error listing collections: {e}")
            return None

    def list_documents(self, collection_name, query={}):
        try:
            collection = self.database[collection_name]
            documents = collection.find(query)
            return list(documents)
        except Exception as e:
            print(f"Error listing documents: {e}")
            return None
