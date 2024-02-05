import requests
from fastapi import FastAPI
from flask import session

from modules.auth.AuthManager import AuthManager
from modules.database.DatabaseManager import DatabaseManager

from appwrite.query import Query
from appwrite.id import ID


# https://github.com/Devsixth/webapp/blob/8a82eee6c904acff6717d73f7d54ffc00c2ef737/app.py#L47


def authenticate_user(email, password):
    url = "https://foxhat.org/v1/account/sessions/email"
    headers = {'x-appwrite-project': "65af20b9daebac75cc9c"}
    response = requests.post(url, headers=headers, json={'email': email, 'password': password})

    if response.status_code == 201:
        session_data = response.json()
    else:
        print('Authentication failed')
        return None, None


authenticate_user("ee20100112@gmail.com", "Eslam2020@@@")
