import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for, send_file, flash
import mysql.connector
import json
import controller.AccessController as access
import controller.DatabaseController as database
import controller.UsersController as users
import controller.ClientsController as clients
import controller.BackupController as backups
import controller.NotasController as notes
import io
import csv

app = Flask(__name__)
app.secret_key = "tr4rt34t334yt"

settings = {}
with open('settings.json') as archivo:
    settings = json.load(archivo)


@app.route('/')
async def index(error=0):
    if "id" in session:
        page = request.args.get('page', 1, type=int)
        per_page = settings['config']['clients']['per_page']
        offset = (page - 1) * per_page
        
        clients_list = await clients.get_paged_clients(per_page, offset)
        total_items = await clients.get_total_client_number()
        total_pages = (total_items + per_page - 1) // per_page
        
        notas = await notes.get_notes_with_clients()

        return render_template(
            'index.jinja', 
            session=session, 
            page=page,
            notas=notas, 
            total_pages=total_pages, 
            clients=clients_list
        )
    else:
        return render_template('login.jinja', error=error)

@app.route('/login', methods=['GET','POST'])
async def login():
    username = request.form['name']
    passwd = request.form['passwd']

    error_cod = await access.validate_login(username, passwd)
    
    if error_cod == 0:
        user = await users.get_user_by_username(username)
        session['id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return redirect(url_for('index'))  
    else:
        return redirect(url_for('index', error=error_cod))    
    
@app.route('/logout', methods=['GET'])
async def logout():
    session.clear()
    return redirect(url_for('index'))


"""
-----------------------------------------------------------
  [ CLIENTES ]
-----------------------------------------------------------
"""

'''
    Se crea un nuevo cliente y lo almacena en la base de datos.
'''
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
async def new_client():
    if 'id' in session:
        if session['role'] == 'Administrador':
            if request.method == 'GET':
                return render_template('clients/create.jinja', session=session)
            else:
                dni = request.form['dni']
                nombre = request.form['nombre']
                apellidos = request.form['apellidos']
                direccion = request.form['direccion']
                correo = request.form['email']
                telefono = request.form['telefono']
                googlemap_link = request.form['googlemap_link']

                errors = await clients.validate_client(correo, dni)
                
                if len(errors) == 0:
                    await clients.create_client(dni, nombre, apellidos, direccion, correo, telefono, googlemap_link)
                    return redirect(url_for('index'))
                
                else:
                    return render_template(
                        'clients/create.jinja', 
                        errors=errors,
                        nombre=nombre,
                        apellidos=apellidos,
                        direccion=direccion,
                        correo=correo,
                        telefono=telefono,
                        googlemap_link=googlemap_link,
                        session=session
                    )
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))




'''
    Se elimina un cliente dependiendo del DNI pasado en el parametro
'''
@app.route('/clientes/delete/<string:dni>', methods=['GET'])
async def delete_client(dni):
    if 'id' in session:
        if session['role'] == "Administrador":
            await clients.delete_client(dni)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))



'''
    Actualiza los datos de un cliente.
'''
@app.route('/clientes/edit/<string:dni>', methods=['GET', 'POST'])
async def edit_client(dni):
    if 'id' in session:
        if session['role'] == 'Administrador':
            if request.method == "GET":
                client = await clients.get_client_by_dni(dni)
                return render_template(
                    'clients/edit.jinja', 
                    client=client, 
                    session=session
                )
            else:
                nombre = request.form['nombre']
                apellidos = request.form['apellidos']
                direccion = request.form['direccion']
                correo = request.form['email']
                telefono = request.form['telefono']
                googlemap_link = request.form['googlemap_link']
                
                if await clients.gmail_has_two_parts(correo):
                    await clients.update_client(dni, nombre, apellidos, direccion, correo, telefono, googlemap_link)
                    return redirect(url_for('index'))
                else:
                    error_msg = "El formato del correo es invalido."
                    client = await clients.get_client_by_dni(dni)
                    return render_template(
                        'clients/edit.jinja', 
                        error=error_msg, 
                        client=client, 
                        session=session
                    )                
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Genera una plantilla donde se muestra la informacion detallada de un cliente. 
'''
@app.route('/clientes/detalles/<string:dni>', methods=['GET'])
async def client_details(dni):
    if 'id' in session:
        if session['role'] == 'Empleado' or session['role'] == 'Administrador':
            client = await clients.get_client_by_dni(dni)
            notas = await notes.get_notes_with_clients_by_dni(dni)

            return render_template(
                'clients/detalle.jinja',
                notas=notas, 
                client=client, 
                session=session
            )
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Se filtra los clientes almacenados en la base de datos dependiendo de los datos que se les pase en la peticion POST.
'''
@app.route('/clientes/filtered', methods=['GET', 'POST'])
async def filter_clients():
    if 'id' in session:
        if session['role'] == 'Empleado' or session['role'] == 'Administrador':
            
            page = request.args.get('page', 1, type=int)
            per_page = settings['config']['clients']['per_page']
            offset = (page - 1) * per_page
            total_pages = 0
            total_items = 0
            
            clientes = []
            filterDni = request.form['filterDni']
            filterName = request.form['filterName']
            
            if filterDni or filterName:
                if filterDni and not filterName:
                    clientes = await clients.filter_client_action(None, filterDni, per_page, offset)
                    total_items = await clients.get_number_filtered_clients(None, filterDni)
                    total_pages = 1
                
                elif not filterDni and filterName:
                    clientes = await clients.filter_client_action(filterName, None, per_page, offset)
                    total_items = await clients.get_number_filtered_clients(filterName, None)
                    total_pages = (total_items + per_page - 1) // per_page
                    
                elif filterDni and filterName:
                    clientes = await clients.filter_client_action(filterName, filterDni, per_page, offset)
                    total_items = await clients.get_number_filtered_clients(filterName, filterDni)
                    total_pages = (total_items + per_page - 1) // per_page
                
                return render_template( 
                    'index.jinja', 
                    filterName=filterName, 
                    filterDni=filterDni, 
                    clients=clientes, 
                    session=session,
                    total_pages=total_pages, 
                    page=page
                )

            else:
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    

'''
    Descarga un archivo csv con todos los clientes almacenados en la base de datos.
'''
@app.route('/clientes/download')
async def download_csv_clients():
    if 'id' in session:
        if session['role'] == 'Administrador':
            connection = await database.open_database_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM CLIENTES;")

            column_names = [i[0] for i in cursor.description]

            output = io.StringIO()
            writer = csv.writer(output)
    
            writer.writerow(column_names)

            for row in cursor:
                writer.writerow(row)
    

            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='clientes_backup.csv'
            ) 

        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Sube un archivo.csv y lo almacena en la base de datos en la tabla de Clientes
'''
@app.route('/clientes/upload', methods=['POST'])
async def upload_clients_csv():
    if 'id' in session:
        if session['role'] == "Administrador":
            if 'file' not in request.files:
                print('No se ha subido ningún archivo.')
                return redirect(url_for('index'))
    
            file_csv = request.files['file']

            if file_csv.filename == '':
                print('No se ha seleccionado ningun archivo.')
                return redirect(url_for('index'))

            if file_csv and file_csv.filename.endswith('.csv'):
                await backups.upload_csv_clients(file_csv)
                return redirect(url_for('index'))
            
            else:
                return redirect(url_for('index'))
            
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

"""
----------------------------------------------------------------------------------------------
    [ USUARIOS ]
----------------------------------------------------------------------------------------------
"""

'''
    Genera la plantilla donde se muestra una tabla con todos los usuarios.
'''
@app.route('/usuarios', methods=['GET'])
async def index_users():
    if 'id' in session:
        if session['role'] == "Administrador":
            page = request.args.get('page', 1, type=int)
            per_page = settings['config']['users']['per_page']
            offset = (page - 1) * per_page
            
            usuarios = await users.get_paged_users(per_page, offset)
            total_items = await users.get_total_users_number()
            total_pages = (total_items + per_page - 1) // per_page
            
            return render_template(
                'users/index.jinja', 
                users=usuarios, 
                session=session, 
                total_pages=total_pages, 
                page=page
            )
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))



'''
    Crea un nuevo usuario y lo registra en la base de datos
'''
@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
async def new_user():
    if 'id' in session:
        if session['role'] == "Administrador":
            if request.method == 'GET':
                return render_template('users/create.jinja', session=session)
            else:
                username = request.form['username']
                passwd = request.form['passwd']
                passwd2 = request.form['passwd2']
                
                if await users.user_name_in_use(username):
                    error_msg = f"El nombre de usuario {username} esta en uso."
                    return render_template(
                        'users/create.jinja', 
                        error=error_msg, 
                        session=session
                    )
                elif passwd != passwd2:
                    error_msg = "Ambas contraseñas deben ser iguales para continuar."
                    return render_template(
                        'users/create.jinja', 
                        error=error_msg,
                        session=session
                    )
                else:
                    await users.create_user(username, passwd)
                    return redirect(url_for('index_users'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Borra a un usuario de la base de datos.
'''
@app.route('/usuarios/delete/<int:id>', methods=['GET'])
async def delete_user(id):
    if 'id' in session:
        if session['role'] == "Administrador":
            await users.delete_user(id)
            return redirect(url_for('index_users'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Filtra los usuarios dependiendo del texto que se le pase en el POST
'''
@app.route('/usuarios/filtered', methods=['GET', 'POST'])
async def filter_users():
    if 'id' in session:
        if session['role'] == "Administrador":
            text = request.form['filterText']
            if text:
                page = request.args.get('page', 1, type=int)
                per_page = settings['config']['users']['per_page']
                offset = (page - 1) * per_page
                
                usuarios = await users.search_users(text, per_page, offset)
                total_items = await users.get_filtered_users_number(text)
                total_pages = (total_items + per_page - 1) // per_page
                
                return render_template(
                    'users/index.jinja', 
                    users=usuarios, 
                    text=text, 
                    session=session, 
                    total_pages=total_pages, 
                    page=page
                )
            else:
                return redirect(url_for('index_users'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    




"""
----------------------------------------------------------------------------------------------
    [ NOTAS ]
----------------------------------------------------------------------------------------------
"""


'''
    Creamos una nueva nota en un usuario.
'''
@app.route('/notas/new/<string:dni>', methods=['POST'])
async def new_note(dni):
    if 'id' in session:
        text = request.form['nota']
        if text and text != "":
            await notes.new_note(dni, text)
            return redirect(url_for('client_details', dni=dni))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

'''
    Borra una nota especifica.
'''
@app.route('/notas/delete/<int:id>', methods=['GET'])
async def delete_nota(id):
    if 'id' in session:
        if session['role'] == 'Administrador':
            await notes.delete_note(id)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


'''
    Descarga las notas en un archivo .csv
'''
@app.route('/notas/download')
async def download_csv_notes():
    if 'id' in session:
        if session['role'] == 'Administrador':
            connection = await database.open_database_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM NOTAS;")

            column_names = [i[0] for i in cursor.description]

            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(column_names)
            
            for row in cursor:
                writer.writerow(row)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='notas_backup.csv'
            )
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

'''
    Sube el archivo .csv que contiene todas las notas.
'''
@app.route('/notas/upload', methods=['POST'])
async def upload_notes_csv():
    if 'id' in session:
        if session['role'] == 'Administrador':
            if 'file' not in request.files:
                print('No se ha subido ningún archivo.')
                return redirect(url_for('index'))
    
            file_csv = request.files['file']

            if file_csv.filename == '':
                print('No se ha seleccionado ningun archivo.')
                return redirect(url_for('index'))

            if file_csv and file_csv.filename.endswith('.csv'):
                await backups.upload_csv_notes(file_csv)
                return redirect(url_for('index'))
            
            else:
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(
        debug=True,
        host=settings['flask']['host'],
        port=settings['flask']['port']
    )