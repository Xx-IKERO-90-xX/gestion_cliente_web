import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database

sys.path.append("..")

app_route = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
if app_route not in sys.path:
    sys.path.insert(0, app_route)

import app


# Obtenemos todos los clientes registrados en la DB
async def get_all_clients():
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM CLIENTES")
    result = cursor.fetchall()
    
    result_json = await database.covert_to_json(cursor, result)
    connection.close()
    
    return result_json


# Creamos un nuevo cliente
async def create_client(dni, nombre, apellidos, direccion, correo, telefono, googlemap_link):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        INSERT INTO CLIENTES (dni, nombre, apellidos, direccion, email, telefono, googlemap_link)
        VALUES ('{dni}', '{nombre}', '{apellidos}', '{direccion}', '{correo}', '{telefono}', '{googlemap_link}');               
    """)
    connection.commit()
    connection.close()


# Eliminamos un cliente de la base de datos
async def delete_client(dni):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        DELETE FROM CLIENTES
        WHERE dni = '{dni}';    
    """)
    
    connection.commit()
    connection.close()


# Se obtiene el cliente por DNI
async def get_client_by_dni(dni):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        SELECT * FROM CLIENTES 
        WHERE dni = '{dni}';               
    """)
    
    result = cursor.fetchall()
    json_result = await database.covert_to_json(cursor, result)
    
    connection.close()
    return json_result[0]


# Actualiza los datos del cliente registrado en la base de datos
async def update_client(dni, nombre, apellidos, direccion, correo, telefono, googlemap_link):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute(f"""
        UPDATE CLIENTES
        SET nombre = '{nombre}',
            apellidos = '{apellidos}',
            direccion = '{direccion}',
            email = '{correo}',
            telefono = '{telefono}',
            googlemap_link = '{googlemap_link}'
        WHERE dni = '{dni}';                
    """)
    
    connection.commit()
    connection.close()


# Se filtra los clientes dependiendo si se busca por dni o por nombre y apellidos
async def filter_client_action(filterName=None, filterDni=None):
    json_result = []
    
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    if filterName != None and filterDni == None:
        cursor.execute(f"""
            SELECT * FROM CLIENTES
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%';
        """)
        result = cursor.fetchall()
       
        json_result = await database.covert_to_json(cursor, result)
        connection.close()
       
        return json_result
    
    elif filterDni != None and filterName == None:
        cursor.execute(f"""
            SELECT * FROM CLIENTES
            WHERE dni = '{filterDni}';               
        """)
        result = cursor.fetchall()
        
        json_result = await database.covert_to_json(cursor, result)
        connection.close()
        
        return json_result
        
    elif filterDni != None and filterName != None:
        cursor.execute(f"""
            SELECT * FROM CLIENTES
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%'
                AND dni = '{filterDni}';
        """)
        result = cursor.fetchall()
        
        json_result = await database.covert_to_json(cursor, result)
        connection.close()
        
        return json_result
    
    else:
        connection.close()
        return json_result