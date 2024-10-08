import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
import controller.ClientsController as clients
import io
import csv
import re

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app

'''
    Obtiene todas las notas almacenados en la base de datos.
'''
async def get_all_notes():
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM NOTAS;")

    result = cursor.fetchall()

    json_result = await database.covert_to_json(cursor, result)

    connection.close()
    return json_result

'''
    Obtiene todas las notas enlazadas a sus respectivos clientes.
'''
async def get_last_client_note(dni):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT CLIENTES.nombre AS nombre, CLIENTES.apellidos AS apellidos, CLIENTES.dni as dni, NOTAS.texto AS nota, NOTAS.id AS id
        FROM CLIENTES INNER JOIN NOTAS ON CLIENTES.dni = NOTAS.dni
        WHERE CLIENTES.dni = '{dni}' AND NOTAS.dni = '{dni}'
        ORDER BY NOTAS.id DESC
        LIMIT 1;
    """)

    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)

    connection.close()

    return json_result

'''
    Obtiene las notas enlazasos a su respectivo cliente.
'''
async def get_notes_with_clients_by_dni(dni):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT CLIENTES.nombre AS nombre, CLIENTES.apellidos AS apellidos, CLIENTES.dni as dni, NOTAS.texto AS nota, NOTAS.id as id
        FROM CLIENTES INNER JOIN NOTAS ON CLIENTES.dni = NOTAS.dni
        WHERE CLIENTES.dni = '{dni}';
    """)

    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)

    connection.close()

    return json_result


'''
    Crea una nueva nota y lo almacena en la base de datos.
'''
async def new_note(dni, text):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        INSERT INTO NOTAS (dni, texto)
        VALUES ('{dni}', '{text}');    
    """)

    connection.commit()
    connection.close()


'''
    Elimina una nota específica.
'''
async def delete_note(id):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        DELETE FROM NOTAS
        WHERE id = {id};    
    """)

    connection.commit()
    connection.close()

'''
    Comprueba si la nota introducida existe.
'''
async def note_exists(id, dni, texto):
    exists = False
    notas = await get_all_notes()

    for nota in notas:
        if nota['id'] == id and nota['dni'] == dni and nota['texto'] == texto:
            exists = True
    
    return exists


'''
    Edita la nota seleccionada.
'''
async def update_note(id, text):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        UPDATE NOTAS
            SET texto = '{text}'
        WHERE id = {id};
    """)

    connection.commit()
    connection.close()


'''
    Obtiene una nota por id.
'''
async def get_note_by_id(id):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT * FROM NOTAS
        WHERE id = {id};
    """)

    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)

    connection.close()
    return json_result[0]