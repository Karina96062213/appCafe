from flask import Flask, render_template, request, flash, redirect, url_for, session, g, url_for, send_file, make_response
#from flask_mysqldb import MySQL
import sqlite3
from sqlite3 import Error
from formulario import convertToBinaryData, writeTofile
import yagmail
import utils
import os
from flask import g

app = Flask(__name__)
app.secret_key = os.urandom(24)

from db import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/GestionarUsuarios/')
def leer():
    strsql="SELECT * FROM Usuario"
    con = get_db()
    cursosObj=con.cursor()
    cursosObj.execute(strsql)
    usuarios=cursosObj.fetchall()
    return render_template("CDUsers.html", usuarios = usuarios)

@app.route("/delete/<string:id>/")
def delete(id):
    strsql="DELETE FROM Usuario WHERE id="+id+";"
    con = get_db()
    cursosObj=con.cursor()
    cursosObj.execute(strsql)
    con.commit()
    con.close()
    return redirect("/GestionarUsuarios")

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
                    role = db.execute("SELECT descripcion FROM Rol INNER JOIN Usuario ON Rol.id = Usuario.id_Rol WHERE Usuario.nombre = ?", (username,)).fetchone()
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
    print("Registro Usuario 1")
    try:
        if request.method == 'POST':
                close_db()
                db = get_db()
                username = request.form['nuser']
                password = request.form['cuser']
                email = request.form['euser']
                idRolUser = request.form['ruser']
                error = None
                print("Registro Usuario 2")

                if not utils.isUsernameValid(username):
                    error = "El usuario debe ser alfanumerico"
                    flash(error)
                    print("Entro a USUARIO")
                    return render_template('registroUsuario.html')

                if not utils.isEmailValid(email):
                    error = 'Correo inválido'
                    flash(error)
                    print("Entro a EMAIL")
                    return render_template('registroUsuario.html')

                if not utils.isPasswordValid(password):
                    error = 'La contraseña debe tener por los menos una mayúscula, una mínuscula y 8 caracteres'
                    flash(error)
                    print("Entro a PASSWORD")
                    return render_template('registroUsuario.html')
                
                if db.execute("SELECT id FROM Usuario WHERE correo=?", (email,)).fetchone() is not None:
                    print("Registro Usuario 3")
                    error = 'El correo ya existe'.format(email)
                    flash(error)
                    return render_template('registroUsuario.html')

                hashPassword = generate_password_hash(password)
                print("Registro Usuario 4")

                query = 'INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, idRolUser)
                print(query)
                db.execute('INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, idRolUser))
                print("Registro Usuario 5")
                db.commit()

                serverEmail = yagmail.SMTP('ejemplomisiontic@gmail.com', 'Maracuya1234')
                serverEmail.send(to = email, subject = 'Activa tu cuenta',
                                 contents = 'Bienvenido, usa este link para activar tu cuenta')

                flash('Revisa tu correo para activar tu cuenta')

        return render_template("registroUsuario.html")
    
    except Exception as e:
        print(e)
        return render_template('registroUsuario.html')

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

@app.route('/admin/products/create/', methods = ('GET', 'POST'))
def registroProducto():
    print("Registro Producto 1")
    try:
        if request.method == 'POST':
                close_db()
                db = get_db()
                productname = request.form['nproduct']
                productdesc = request.form['dproduct']
                productstock = request.form['sproduct']
                photoPath = request.form['iproduct']
                print("Registro Producto 1.1")
                product_photo = convertToBinaryData(photoPath)
                print("Registro Producto 1.2")
                error = None
                print("Registro Producto 2")

                if not productname:
                    error = "Debe ingresar el nombre del producto"
                    flash(error)
                    return render_template('agregarProducto.html')

                if not productdesc:
                    error = "Debe ingresar la descripción del producto"
                    flash(error)
                    return render_template('agregarProducto.html')

                if not productstock:
                    error = "Debe ingresar el stock inicial del producto"
                    flash(error)
                    return render_template('agregarProducto.html')
                
                if not product_photo:
                    error = "Debe ingresar la imagen del producto"
                    flash(error)
                    return render_template('agregarProducto.html')
                
                if db.execute("SELECT id FROM Usuario WHERE nombre=?", (productname,)).fetchone() is not None:
                    print("Registro Producto 3")
                    error = 'El producto ya existe'.format(productname)
                    flash(error)
                    return render_template('agregarProducto.html')

                print("Registro Producto 4")

                query = 'INSERT INTO Producto (nombre, descripcion, stock, imagen) VALUES (?,?,?,?)', (productname, productdesc, productstock, product_photo)
                print(query)
                db.execute('INSERT INTO Producto (nombre, descripcion, stock, imagen) VALUES (?,?,?,?)', 
                            (productname, productdesc, productstock, product_photo))
                print("Registro Producto 5")
                db.commit()

        return render_template("agregarProducto.html")
    
    except Exception as e:
        print(e)
        return render_template('agregarProducto.html')
    

#def convertToBinaryData(filename):
    #Convert digital data to binary format
#    with open(filename, 'rb') as file:
#        blobData = file.read()
#    return blobData

#def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
#    with open(filename, 'wb') as file:
#        file.write(data)
#    print("Stored blob data into: ", filename, "\n")