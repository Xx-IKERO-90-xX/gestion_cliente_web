import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
import controller.ClientsController as clients
import controller.NotasController as notes
import io
import csv
import re

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app


'''
    Subimos todos los datos de los clientes del archivo .csv a la base de datos.
'''
async def upload_csv_clients(file_csv):
    stream = io.StringIO(file_csv.stream.read().decode('UTF8'))
    csv_input = csv.reader(stream)

    connection = await database.open_database_connection()
    cursor = connection.cursor()

    regex = r'^\d{8}[A-Z]$'

    for row in csv_input:
        dni = row[0]
        nombre = row[1]
        apellidos = row[2]
        direccion = row[3]
        email = row[4]
        telefono = row[5]
        googlemap_link = row[6]

        if await clients.client_exists(dni) == 0 and re.match(regex, dni):
            cursor.execute(f"""
                INSERT INTO CLIENTES (dni, nombre, apellidos, direccion, email, telefono, googlemap_link)
                VALUES('{dni}', '{nombre}', '{apellidos}', '{direccion}', '{email}', '{telefono}', '{googlemap_link}');        
            """)

    connection.commit()
    connection.close()


'''
    Subimos todos los datos de las notas del archivo csv la base de datos.
'''
async def upload_csv_notes(file_csv):
    stream = io.StringIO(file_csv.stream.read().decode('UTF8'))
    csv_input = csv.reader(stream)

    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    regex = r'^\d{8}[A-Z]$'

    for row in csv_input:
        id = row[0]
        dni = row[1]
        texto = row[2]

        if not await notes.note_exists(id, dni, texto) and re.match(regex, dni):
            cursor.execute(f"""
                INSERT INTO NOTAS (dni, texto)
                VALUES ('{dni}', '{texto}');            
            """)
    
    connection.commit()
    connection.close()
