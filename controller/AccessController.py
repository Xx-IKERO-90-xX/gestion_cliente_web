import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
import controller.UsersController as users
from passlib.hash import pbkdf2_sha256

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app

'''
    Validamos el usuario y la contraseña.
'''
async def validate_login(username, passwd):
    cod = 1
    usuarios = await users.get_users()
    
    for user in usuarios:
        if user['username'] == username and pbkdf2_sha256.verify(passwd, user['passwd']):
            cod = 0
            break
        
    return cod


'''
    Encripta la contraseña que se le pasa.
'''
async def encrypt_password(passwd):
    hash_passwd = pbkdf2_sha256.hash(passwd)
    return hash_passwd
    
    
