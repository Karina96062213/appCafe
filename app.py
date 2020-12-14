from flask import Flask, render_template, request, flash

import utils
import os
import yagmail as yagmail

app = Flask(__name__)
app.secret_key = os.urandom(24)

from db import get_db

@app.route('/')
def bienvenida():
    return render_template("Bienvenida.html")

@app.route('/login/', methods = ('GET', 'POST'))
def index():
    try:
        if request.method == 'POST':
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

            user = db.execute("SELECT * FROM Usuario WHERE nombre=? AND contraseña=?",(username,password)).fetchone()

            if user is None:
               error = 'Usuario o contraseña inválidos'
            else:
                role = db.execute('SELECT descripcion FROM Rol INNER JOIN Usuario ON Rol.id = Usuario.id WHERE Usuario.nombre = ? AND Usuario.contraseña = ?'),(username,password).fetchone()
                if (role == 'Administrador'):
                    return render_template("inicioAdmin.html")
                else:
                    return render_template("inicioUsuario.html")
                flash(error)
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
            username = request.form['nuser']
            password = request.form['cuser']
            email = request.form['euser']
            error = None

            if not utils.isUsernameValid(username):
                error = "El usuario debe ser alfanumerico"
                flash(error)
                return render_template('registroUsuario.html')

            if not utils.isEmailValid(email):
                error = 'Correo inválido'
                flash(error)
                return render_template('registroUsuario.html')

            if not utils.isPasswordValid(password):
                error = 'La contraseña debe tener por los menos una mayúsccula y una mínuscula y 8 caracteres'
                flash(error)
                return render_template('registroUsuario.html')
            
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