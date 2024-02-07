from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.id import ID
from telethon import functions, types
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.users import Users



class AuthManager:
    def __init__(self, endpoint, project_id, api_key):
        self.client = Client()
        self.client.set_endpoint("https://foxhat.org/v1")
        self.client.set_project("65af20b9daebac75cc9c")
        self.client.set_key(
            '8698d00c88eecb9af716e39aae6fa6852dc13ed8f0add7c7bda62010b925957cc10a7aa05620052fa258b0356b54172618e8a45588f6a463edddc52b61215584d561412478866d02d0bfa6847835ce7f17e3cbdd9859fd6390a4773b36d6ebffd7ca0242aa9e49e5fa1ebc071f94231964c18e296bfa90ee5511e6afcbd99bc1')
        self.account = Account(self.client)
        self.users = Users(self.client)

    def sign_up(self, email, password, user_id, name):

        try:

            user = self.users.create_argon2_user(user_id=user_id, email=email, password=password, name=name)
            return user
        except AppwriteException as e:
            print(f"Sign-up error: {e}")
            return None

    def sign_in(self, email, password):
        try:
            result = self.account.create_session()
            # Set the obtained session as the default for subsequent requests
            self.client.set_key(result['$id'])
            return True
        except AppwriteException as e:
            print(f"Sign-in error: {e}")
            return False

    def authenticate_user(self, email, password, name):
        try:
            result = self.client.create_session(email=email, password=password)
            # Set the obtained session as the default for subsequent requests
            self.client.set_key(result['$id'])
            return True
        except AppwriteException as e:
            print(f"Authentication error: {e}")
            return False
