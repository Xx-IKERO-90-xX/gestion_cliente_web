import os
import sys
from flask import request, Flask, render_template, redirect, session, sessions, url_for
import mysql.connector
import json
import controller.AccessController as access
import controller.DatabaseController as database
import controller.UsersController as users
import controller.ClientsController as clients

app = Flask(__name__)
app.secret_key = "tr4rt34t334yt"

settings = {}
with open('settings.json') as archivo:
    settings = json.load(archivo)


@app.route('/')
async def index(error=0):
    if "id" in session:
        clients_list = await clients.get_all_clients()
        return render_template('index.jinja', session=session, clients=clients_list)
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
                    return render_template('clients/create.jinja', errors=errors, session=session)
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
                return render_template('clients/edit.jinja', client=client, session=session)
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
                    return render_template('clients/edit.jinja', error=error_msg, client=client, session=session)                
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
            return render_template('clients/detalle.jinja', client=client, session=session)
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
            clientes = []
            filterDni = request.form['filterDni']
            filterName = request.form['filterName']
            
            if filterDni or filterName:
                if filterDni and not filterName:
                    clientes = await clients.filter_client_action(None, filterDni)
                elif not filterDni and filterName:
                    clientes = await clients.filter_client_action(filterName, None)
                elif filterDni and filterName:
                    clientes = await clients.filter_client_action(filterName, filterDni)
                
                return render_template('index.jinja', filterName=filterName, filterDni=filterDni, clients=clientes, session=session)
            
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
            usuarios = await users.get_users()
            return render_template('users/index.jinja', users=usuarios, session=session)
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
                    return render_template('users/create.jinja', error=error_msg, session=session)
                elif passwd != passwd2:
                    error_msg = "Ambas contraseñas deben ser iguales para continuar."
                    return render_template('users/create.jinja', error=error_msg, session=session)
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
                usuarios = await users.search_users(text)
                return render_template('users/index.jinja', users=usuarios, text=text, session=session)
            else:
                return redirect(url_for('index_users'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
    
if __name__ == "__main__":
    app.run(debug=True)