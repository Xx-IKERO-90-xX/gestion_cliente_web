import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
from passlib.hash import pbkdf2_sha256

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app

async def validate_login(username, passwd):
    cod = 1
    
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM USUARIOS;")
    
    result = cursor.fetchall()
    json_users = await database.covert_to_json(cursor, result)
    
    for user in json_users:
        if user['username'] == username and pbkdf2_sha256.verify(passwd, user['passwd']):
            cod = 0
            break
    
    connection.close()
    
    return cod

async def encrypt_password(passwd):
    hash_passwd = pbkdf2_sha256.hash(passwd)
    return hash_passwd
    
    
