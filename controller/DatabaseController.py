import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app


'''
    Establece la conexion con la base de datos.
'''
async def open_database_connection():
    connection = mysql.connector.connect(
        host = app.settings["database"]["host"],
        user = app.settings["database"]["user"],
        password = app.settings["database"]["password"],
        database = app.settings["database"]["db"],
    )
    return connection

'''
    Convierte los datos pasados a formato JSON
'''
async def covert_to_json(cursor, result):
    columns = [column[0] for column in cursor.description]
    json_result = []
    for fila in result:
        fila_json = dict(zip(columns, fila))
        json_result.append(fila_json)
    
    return json_result