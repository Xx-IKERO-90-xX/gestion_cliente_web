import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
import controller.AccessController as access


sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app

async def get_user_by_username(username):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        SELECT * FROM USUARIOS
        WHERE username = '{username}';                   
    """)
    
    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)
    connection.close()
    
    return json_result[0]

async def get_users():
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM USUARIOS;")
    
    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)
    connection.close()
    
    return json_result

async def create_user(username, passwd):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    hash_passwd = await access.encrypt_password(passwd)
    
    cursor.execute(f"""
        INSERT INTO USUARIOS (username, passwd, role)
        VALUES ('{username}', '{hash_passwd}', 'Empleado');               
    """)
    
    connection.commit()
    connection.close()

async def delete_user(id):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        DELETE FROM USUARIOS
        WHERE id = {id};               
    """)
    
    connection.commit()
    connection.close()
