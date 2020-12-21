import os, sys
from werkzeug.utils import secure_filename
from os.path import abspath, dirname, join
import functools
from flask import Flask, render_template, request, flash, session, redirect, url_for, make_response, current_app, send_from_directory
#from flask_mysqldb import MySQL
import sqlite3
from sqlite3 import Error
from formulario import convertToBinaryData, writeTofile
import yagmail
import utils
import os
from flask import g
from forms import FormInicio

app = Flask(__name__)
app.secret_key = os.urandom(24)

from db import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash

app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

BASE_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = BASE_DIR+"/frontend/static/images"
# Media dir

detalleRow = list()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not 'user_id' in session :
            flash('Acceso denegado!')
            return render_template("Bienvenida.html")
        return view()
    return wrapped_view

def uploaded_file():
       conexion = get_db()     
       cur=conexion.cursor()
       cur.execute("SELECT * FROM Producto")
       reg = cur.fetchall() 
       return render_template('productosAdmin.html', reg=reg)

@app.route( '/logout' )
def logout():
     session['user_id'] = None
     session['user_login'] = None
     session['user_email'] = None
     session.clear()
     return render_template("Bienvenida.html")

def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

@app.route('/admin/products/create/', methods=('GET', 'POST'))
def RegisProducto():
     print("Paso 1")
     try:
        if request.method == 'POST':
            productname = request.form['nproduct']
            productdesc = request.form['dproduct']
            productstock = request.form['sproduct']
            print("Paso 2")
            imagen = request.files['iproduct']
            filename = ""
            if 'iproduct' in request.files:
                print("Paso 3")
                if imagen.filename == "":
                    print("No filename")
                    return render_template('agregarProducto.html')
                print("Paso 4")
                if allowed_image(imagen.filename):
                    print("Paso 4.1")
                    print(BASE_DIR)
                    filename = secure_filename(imagen.filename)
                    imagen.save(os.path.join(BASE_DIR, filename)) 
                else:
                    print("That file extension is not allowed")
                    return render_template('agregarProducto.html')
            
            print("Paso 5")
            conexion = get_db()
            cur=conexion.cursor()
            cur = conexion.cursor()
            print("Paso 6")
            cur.execute('INSERT INTO Producto (nombre, descripcion, stock, imagen) VALUES (?,?,?,?)',(productname, productdesc, productstock, filename))
            conexion.commit()
            flash('Producto ingresado satisfactoriamente.')
        return render_template("agregarProducto.html")
     except:
        flash('Hubo un error inesperado')
        return  render_template('agregarProducto.html')

@app.route('/editarProducto/<id>')
def editarProducto(id):
       conexion = get_db()     
       cur=conexion.cursor()
       cur.execute("SELECT * FROM Producto WHERE id=?", (id,))
       reg = cur.fetchall() 
       return render_template('editarProducto.html', reg=reg)

@app.route('/editarStock/<id>')
def editarStock(id):
       conexion = get_db()     
       cur=conexion.cursor()
       cur.execute("SELECT * FROM Producto WHERE id=?", (id,))
       reg = cur.fetchall() 
       return render_template('actualizarStock.html', reg=reg)

@app.route('/buscarNombre',methods=['GET', 'POST'])
def buscarNombre():
    try:
        if request.method == 'POST':            
            buscar = request.form['producto'] 
            busqueda = "%" +buscar +"%"     
            conexion = get_db()     
            cur=conexion.cursor()
            cur.execute("SELECT * FROM Producto WHERE nombre LIKE '%s'"%  (busqueda))
            reg = cur.fetchall()
            return render_template('productosAdmin.html', reg=reg)
    except:
        return redirect(url_for('/admin/products/'))

@app.route('/buscarNombreUsuario',methods=['GET', 'POST'])
def buscarNombreUsuario():
    try:
        if request.method == 'POST':            
            buscar = request.form['producto'] 
            busqueda = "%" +buscar +"%"     
            conexion = get_db()     
            cur=conexion.cursor()
            cur.execute("SELECT * FROM Producto WHERE nombre LIKE '%s'"%  (busqueda))
            reg = cur.fetchall()
            return render_template('inicioUsuario.html', reg=reg)
    except:
        return redirect('/home/')

@app.route('/eliminarProducto/<id>')
def eliminarProducto(id):
       conexion = get_db()     
       cur=conexion.cursor()
       cur.execute("DELETE FROM Producto WHERE id=?",(id,))
       conexion.commit()
       return redirect('/admin/products/')

def send_file(filename):
    return send_from_directory('Productos/', filename)

@app.route('/updateproduct/',methods=('GET', 'POST'))
def updateProduct():
     print("Paso 1")
     try:
        if request.method == 'POST':
            codigo = request.form['codigo']
            nombre = request.form['nuevoNombre']
            descripcion = request.form['nuevaDescripcion']
            stock = request.form['nuevoStock']
            imagen = request.files['nuevaImagen']   
            filename = ""
            print("Paso 2")

            if 'nuevaImagen' in request.files:
                if imagen.filename == "":
                    print("Paso 3")
                    print("No filename")
                if allowed_image(imagen.filename):
                    print("Paso 4")
                    filename = secure_filename(imagen.filename)
                    print("Paso 4.1")
                    print(BASE_DIR)
                    imagen.save(os.path.join(BASE_DIR, filename))
                    print("Paso 4.2") 
                else:
                    print("That file extension is not allowed")                 
            
            print("Paso 5")
            conexion = get_db()           
            cur = conexion.cursor()
            print("Paso 6")
            cur.execute("UPDATE Producto SET nombre=?, descripcion=?, stock=?, imagen=? WHERE id=?",(nombre, descripcion, stock, filename, codigo))          
            conexion.commit()
            print("Paso 7")
            flash('Producto actualizado satisfactoriamente')
        return render_template('editarProducto.html')
     except:
        return render_template('editarProducto.html')

@app.route('/updateStock/<id>', methods = ('GET', 'POST'))
def updateStock(id):
     print("Paso 1")
     try:
        print("Paso 2")
        if request.method == 'POST':
            stock = request.form['nuevoStockUser']
            print(stock)  
            print("Paso 4")               
            
            print("Paso 5")
            conexion = get_db()           
            cur = conexion.cursor()
            print("Paso 6")
            cur.execute("UPDATE Producto SET stock=? WHERE id=?",(stock, id))          
            conexion.commit()
            print("Paso 7")
            flash('Stock actualizado satisfactoriamente')
        return render_template('actualizarStock.html')
     except:
        return render_template('actualizarStock.html')

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
                    session['user_login'] = user[1]
                    session['user_email'] = user[2]   
                    resp = make_response( redirect( url_for( 'bienvenida' ) ) )
                    resp.set_cookie('username', username)
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
                
                if idRolUser == "Administrador":
                    query = 'INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, 1)
                    print(query)
                    db.execute('INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, 1))
                    print("Registro Usuario 5")
                else:
                    query = 'INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, 2)
                    print(query)
                    db.execute('INSERT INTO Usuario (nombre, correo, contraseña, id_Rol) VALUES (?,?,?,?)', (username, email, hashPassword, 2))
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

@app.route('/admin/products/', methods = ('GET', 'POST'))
def productosAdmin():
    return render_template("productosAdmin.html")

#@app.route('/admin/products/update/')
#def crudProductos():
#    return render_template("crudProductos.html")

@app.route('/home/')
def inicioUsuario():
    return render_template("inicioUsuario.html")
