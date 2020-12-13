from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
import sqlite3
from sqlite3 import Error
import utils
import os
import yagmail as yagmail
from flask import g

app = Flask(__name__)
app.secret_key = os.urandom(24)

def sql_connection():
    try:
        con = sqlite3.connect("myCafeteria.db")
        return con
    except Error:
        print("Error DB")

@app.route('/GestionarUsuarios/')
def leer():
    strsql="SELECT * FROM Usuario"
    con = sql_connection()
    cursosObj=con.cursor()
    cursosObj.execute(strsql)
    usuarios=cursosObj.fetchall()
    return render_template("CDUsers.html", usuarios = usuarios)


@app.route("/delete/<string:id>/")
def delete(id):
    strsql="DELETE FROM Usuario WHERE id="+id+";"
    con = sql_connection()
    cursosObj=con.cursor()
    cursosObj.execute(strsql)
    con.commit()
    con.close()
    return redirect("/GestionarUsuarios")

@app.route('/')
def bienvenida():
    return render_template("Bienvenida.html")

@app.route('/login/')
def index():
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