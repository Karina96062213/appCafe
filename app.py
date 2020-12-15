from flask import Flask, render_template, request, flash, redirect, url_for, session, g, url_for, send_file, make_response
import sqlite3
from sqlite3 import Error
import utils
import os
import yagmail as yagmail
from flask import g

app = Flask(__name__)
app.secret_key = os.urandom(24)

from db import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def bienvenida():
    return render_template("Bienvenida.html")

@app.route('/login/', methods = ('GET', 'POST'))
def index():
    try:
        if request.method == 'POST':
            close_db()
            db = get_db()
            username = request.form['login-name']
            password = request.form['login-pass']

            if not username:
                error = "Debe ingresar el usuario"
                flash(error)
                return render_template('index.html')
            if not password:
                error = "Se requiere una contraseña"
                flash(error)
                return render_template('index.html')

            print("usuario" + username + " clave:" + password)

            user = db.execute("SELECT * FROM Usuario WHERE nombre=?",(username, )).fetchone()

            if user is None:
               error = 'Usuario o contraseña inválidos'
               flash(error)
            else:
                if check_password_hash(user[3], password):
                    session.clear()
                    session['user_id'] = user[0]
                    role = db.execute("SELECT descripcion FROM Rol INNER JOIN Usuario ON Rol.id = Usuario.id_Rol WHERE Usuario.nombre = ? AND Usuario.contraseña = ?",(username,password)).fetchone()
                    print(role)
                    if (role[0] == "Administrador"):
                        return render_template("inicioAdmin.html")
                    else:
                        return render_template("inicioUsuario.html")
                
                return render_template("index.html")
        
        return render_template("index.html")

    except TypeError as e:
        print("Ocurrió un error: ", e)
        return render_template("index.html")

@app.route('/admin/')
def inicioAdmin():
    return render_template("inicioAdmin.html")

@app.route('/admin/newuser/', methods = ('GET', 'POST'))
def registroUsuario():
    if request.method == 'POST':
            #iduser
            username = request.form['nuser']
            password = request.form['cuser']
            email = request.form['euser']
            #idRoluser
            error = None
            close_db()
            db = get_db()

            if not utils.isUsernameValid(username):
                error = "El usuario debe ser alfanumerico"
                flash(error)
                return render_template('registroUsuario.html')

            if not utils.isEmailValid(email):
                error = 'Correo inválido'
                flash(error)
                return render_template('registroUsuario.html')

            if not utils.isPasswordValid(password):
                error = 'La contraseña debe tener por los menos una mayúscula, una mínuscula y 8 caracteres'
                flash(error)
                return render_template('registroUsuario.html')
             
            if db.execute("SELECT id FROM Usuario WHERE correo=?", (email,)).fetchone() is not None:
                error = 'El correo ya existe'.format(email)
                flash(error)
                return render_template('registroUsuario.html')

            hashPassword = generate_password_hash(password)
            
            query = 'INSERT INTO Usuario (nombre, correo, contraseña) VALUES (?,?,?)', (username, email, hashPassword)
            print(query)
            db.execute('INSERT INTO Usuario (nombre, correo, contraseña) VALUES (?,?,?)', (username, email, hashPassword))
            db.commit()

            serverEmail = yagmail.SMTP('ejemplomisiontic@gmail.com', 'Maracuya1234')
            serverEmail.send(to = email, subject = 'Activa tu cuenta',
                             contents = 'Bienvenido, usa este link para activar tu cuenta')

            flash('Revisa tu correo para activar tu cuenta')

    return render_template("registroUsuario.html")

@app.route('/admin/products/')
def productosAdmin():
    return render_template("productosAdmin.html")

@app.route('/admin/products/update/')
def crudProductos():
    return render_template("crudProductos.html")

@app.route('/home/')
def inicioUsuario():
    return render_template("inicioUsuario.html")

@app.route('/updatestock/')
def actualizarStock():
    return render_template("actualizarStock.html")