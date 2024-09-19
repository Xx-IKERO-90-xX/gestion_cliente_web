import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import controller.DatabaseController as database
import re

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

# Obtenemos los clientes por numero de pagina
async def get_paged_clients(per_page, offset):
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM CLIENTES LIMIT %s OFFSET %s", (per_page, offset))
    result = cursor.fetchall()
    
    json_result = await database.covert_to_json(cursor, result)
    connection.close()

    return json_result


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
async def filter_client_action(filterName=None, filterDni=None, perpage=5, offset=0):
    json_result = []
    
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    if filterName != None and filterDni == None:
        cursor.execute(f"""
            SELECT * FROM CLIENTES LIMIT {perpage} OFFSET {offset}
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%'
        """, (perpage, offset))
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
            SELECT * FROM CLIENTES LIMIT {perpage} OFFSET {offset}
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


'''
    Comprueba si el formato del es valido.
'''
async def gmail_has_two_parts(gmail):
    parts = gmail.split('@')
    return len(parts) == 2 and parts[0] != '' and parts[1] != ''


'''
    Comprueba si el DNI esta en uso.
'''
async def dni_in_use(dni):
    inUse = False
    clientes = await get_all_clients()
    
    for client in clientes:
        if client['dni'] == dni:
            inUse = True
    
    return inUse        

'''
    Comprueba si el correo ya esta en uso.
'''
async def gmail_in_use(gmail):
    inUse = False
    clientes = await get_all_clients()
    
    for client in clientes:
        if gmail == client['correo']:
            inUse = True
    
    return inUse
            

'''
    Valida los datos del cliente.
'''
async def validate_client(gmail, dni):
    errors = []
    regex = r'^\d{8}[A-Z]$'

    if await gmail_has_two_parts(gmail) == False:
        errors.append("El formato del correo no es valido.")
    
    if dni != None:
        if await dni_in_use(dni):
            errors.append("El DNI introducido esta en uso.")
        if not re.match(regex, dni):
            errors.append("El formato del DNI es incorrecto.")
    
    return errors

'''
    Se obtiene el numero total de clientes en la base de datos
'''
async def get_total_client_number():
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM CLIENTES;")
    
    result = cursor.fetchone()[0]
    connection.close()
    
    return result

'''
Obtiene los clientes de manera filtrada
'''
async def filter_client_action(filterName=None, filterDni=None, per_page=5, offset=0):
    json_result = []
    
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    if filterName != None and filterDni == None:
        cursor.execute(f"""
            SELECT * FROM CLIENTES 
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%'
            LIMIT {per_page} OFFSET {offset};
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
                AND dni = '{filterDni}'
            LIMIT {per_page} OFFSET {offset};
        """)
        result = cursor.fetchall()
        
        json_result = await database.covert_to_json(cursor, result)
        connection.close()
        
        return json_result
    
    else:
        connection.close()
        return json_result

'''
    Obtiene el numero de registro de clientes filtrados.
'''
async def get_number_filtered_clients(filterName=None, filterDni=None):
    result = 0
    
    connection = await database.open_database_connection()
    cursor = connection.cursor()
    
    if filterName != None and filterDni == None:
        cursor.execute(f"""
            SELECT COUNT(*) FROM CLIENTES
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%';
        """)
        
    elif filterDni != None and filterName == None:
        cursor.execute(f"""
            SELECT COUNT(*) FROM CLIENTES
            WHERE dni = '{filterDni}';               
        """)
        
    elif filterDni != None and filterName != None:
        cursor.execute(f"""
            SELECT COUNT(*) FROM CLIENTES
            WHERE CONCAT(nombre, ' ', apellidos) LIKE '%{filterName}%'
                OR CONCAT(nombre, ' ', apellidos) LIKE '[{filterName}]%'
                AND dni = '{filterDni}';
        """)
        
    result = cursor.fetchone()[0]
    connection.close()
    
    return result


'''
    Comprueba si el cliente existe o no.
'''
async def client_exists(dni):
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute(f"""
        SELECT COUNT(*) FROM CLIENTES
        WHERE dni = '{dni}';
    """)
    result = cursor.fetchone()[0]
    connection.close()

    return result



'''
    Obtiene los clientes de la base de datos pero solo el nombre, apellidos y dni.
'''
async def get_clients_dni_name():
    connection = await database.open_database_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT dni, nombre, apellidos FROM CLIENTES;")

    result = cursor.fetchall()

    json_result = await database.covert_to_json(cursor, result)

    connection.close() 
    return json_result