# --------------IMPORTACIÓN DE LAS LIBRERIAS------------------
from flask import Flask 
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime
import os # Permite entrar en carpetas para poder eliminar un archivo

app = Flask(__name__,template_folder='template')

# ---------------CONEXIÓN CON BASE DE DATOS-------------------
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='negocio'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)
# ------------------------------------------------------------

# Crear la referencia de la carpeta "uploads"
CARPETA = os.path.join('uploads') # Crear la referencia a la carpeta de "uploads"
app.config['CARPETA']=CARPETA # Guardamos la ruta como un dato de la variable CARPETA

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
   return render_template('admin.html')

# ----------------Función Agregar Articulo---------------------

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/crear-articulo', methods=["GET", "POST"])
def crear_articulo():
    articulo_articulo=request.form['artNombre']
    articulo_imagen=request.files['artImagen'] # Las imagenes se recepcionan de diferente forma al ser información binaria (siendo que su sintaxis es _nombre=request.file['nombre'])
    articulo_precio=request.form['artPrecio']
    articulo_stock=request.form['artStock']

    # -----------------Guardar la imagen--------------------------
    now = datetime.now() # Una variable que almancena el tiempo
    tiempo=now.strftime("%Y%H%M%S") # En formato de Y (Year/Año), H (Hour/Hora), M (Minute/Minuto) y S (Second/Segundo)

    if articulo_imagen.filename != '': # Si la variable que almacena el dato del campo imegen no esta vacio
        # El '.filename' sirve para que el unico dato que se registr de la imagen sea el nombre
        nuevoNombreFoto=tiempo + articulo_imagen.filename # Se concatenara el nombre de la imagen mas el timepo
        articulo_imagen.save("uploads/" + nuevoNombreFoto) # Y la imagen se guardara en la carpeta de uploads
    # ------------------------------------------------------------

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO articulos (articulo_articulo, articulo_imagen, articulo_precio, articulo_stock) VALUES (%s, %s, %s, %s)", (articulo_articulo, nuevoNombreFoto , articulo_precio, articulo_stock)) 
    mysql.connection.commit()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos")
    articulos = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(articulos) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------
    
    return render_template("admin.html",  articulos=articulos, mensaje_articulo_agregado_exitosamente="Articulo agregado exitosamente") # Envia a la pagina admin.html, envia los registros de los articulos y manda el mensaje

# --------------Fin Función Agregar Articulo---------------------

# -----------------Función Borrar Articulo-----------------------
@app.route('/destroy/<int:id>')
def destroy(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articulos WHERE `articulos`.`articulo_id` = %s", (id,))
    mysql.connection.commit()
    cur.close()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos")
    articulos = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(articulos) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------

    id_eliminado=str(id) # Convierte un int en str(String)
    return render_template("admin.html",  articulos=articulos, mensaje_articulo_eliminado_exitosamente=("Articulo "+ id_eliminado +" eliminado exitosamente"))

# ---------------Fin Función Borrar Articulo---------------------

# -----------------Función Editar Articulo-----------------------
@app.route('/edit/<int:id>')
def edit(id):

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos WHERE `articulos`.`articulo_id` = %s", (id,))
    articulo_del_id = cur.fetchall() # Envia la información del registro
    mysql.connection.commit()
    cur.close()

    print(articulo_del_id)

    return render_template('edit.html', articulo_id=articulo_del_id)

# --------------------Guardar los datos--------------------------
@app.route('/editar-articulo', methods=['POST'])
def editar_articulo():
    articulo_id=request.form['artId']
    articulo_articulo=request.form['artNombre']
    articulo_imagen=request.files['artImagen'] # Las imagenes se recepcionan de diferente forma al ser información binaria (siendo que su sintaxis es _nombre=request.file['nombre'])
    articulo_precio=request.form['artPrecio']
    articulo_stock=request.form['artStock']

    cur = mysql.connection.cursor()

    # ---------------Actualizar la imagen------------------------
    now = datetime.now() # Una variable que almancena el tiempo
    tiempo=now.strftime("%Y%H%M%S") # En formato de Y (Year/Año), H (Hour/Hora), M (Minute/Minuto) y S (Second/Segundo)

    if articulo_imagen.filename != '': # Si la variable que almacena el dato del campo imegen no esta vacio
        # El '.filename' sirve para que el unico dato que se registr de la imagen sea el nombre
        nuevoNombreFoto=tiempo + articulo_imagen.filename # Se concatenara el nombre de la imagen mas el timepo
        articulo_imagen.save("uploads/" + nuevoNombreFoto) # Y la imagen se guardara en la carpeta de uploads

        cur.execute("SELECT articulo_imagen FROM articulos WHERE articulo_id = %s", (articulo_id,))
        fila = cur.fetchone()
        nombre_imagen = fila['articulo_imagen']
        

        os.remove(os.path.join(app.config['CARPETA'], nombre_imagen)) # Remueve de la carpeta uploads la vieja imagen
        cur.execute("UPDATE `articulos` SET `articulo_imagen` = %s WHERE `articulos`.`articulo_id` = %s", (nuevoNombreFoto, articulo_id)) # Modifica de la tabla "articulos" el valor del campo "articulo_imagen" por la nueva imagen, donde el campo "articulo_id" sea igual al id del registro actual

        mysql.connection.commit()
    # ------------------------------------------------------------

    cur.execute("UPDATE `articulos` SET `articulo_articulo`= %s, `articulo_precio` = %s, `articulo_stock` = %s WHERE `articulos`.`articulo_id` = %s", (articulo_articulo, articulo_precio, articulo_stock, articulo_id))
    mysql.connection.commit()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos")
    articulos = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(articulos) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------

    id_modificado=str(articulo_id) # Convierte un int en str(String)

    return render_template("admin.html",  articulos=articulos, mensaje_articulo_modificado_exitosamente=("Articulo "+ id_modificado +" modificado exitosamente"))
# ---------------------------------------------------------------

# ---------------Fin Función Editar Articulo---------------------

# -----------------------Fución login----------------------------
@app.route('/acceso-login', methods=["GET", "POST"]) # Extrae de la pagina de index.html el formulario con action='acceso-login'
def login():
    if request.method == 'POST' and 'usuacorreo' in request.form and 'usuacontra': # Cuando se envien los datos por metodo POST se extraeran los datos de los campos con name="usuacorreo" y name="usuacontra"
        usuario_usuario = request.form['usuacorreo'] #Se duardan los datos en la variable usuario_usuario
        usuario_contrasenia = request.form['usuacontra'] #Se guardan los datos en la variable usuario_contrasenia

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE usuario_usuario = %s AND usuario_contrasenia = %s', (usuario_usuario, usuario_contrasenia,)) #Se selecciona todo de la talba usuarios para comparar los datos de la columna usuario_usuario con el dato que alamacenamos del formulario en la variable usuario_usuario. Y los mismo con los datos de la columna usuario_contrasenia con el dato que se almaceno en la variable usuario_contrasenia
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['usuario_id']
            session['usuario_privilegio'] = account['usuario_privilegio']

            if session['usuario_privilegio'] == 1: #Compara el dato del campo de usuario_privilegio del registro para ver si su valor es 1 (1 = Admin)
                # return render_template("admin.html") #Redirige a la interfaz de Admin
            
                # ------------------- Mostrar los registros------------------
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM articulos")
                articulos = cur.fetchall() # Selecciona todos los registros
                cur.close()

                print(articulos) # Imprime en la terminal los registros
                # ----------------Fin Mostrar los registros------------------

                return render_template("admin.html", articulos=articulos )
            else: 
                if session['usuario_privilegio'] == 2: #Sino compara si el dato es igual a 2 (2 = Usuario)
                    return render_template("usuario.html") #Redirige a la interfaz de Usuario
                
        else:
            return render_template('index.html', mensaje_error_credenciales="Usuario incorrecto") 
        
    else:
        return render_template('index.html')
# ------------------Fin Función login---------------------------

# -------------------Fución registro----------------------------
@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/crear-registro', methods=["GET", "POST"]) # Extrae de la pagina de registro.html el formulario con action='acceso-registro'
def crear_registro():
    usuario_usuario=request.form['usuacorreo'] # Guarda el valor del campo de usuacorreo en la variable usuario_usuario
    usuario_contrasenia=request.form['usuacontra'] # Guarda el valor del campo de usuacontra en la variable usuario_contrasenia

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (usuario_usuario, usuario_contrasenia, usuario_privilegio) VALUES (%s, %s, '2')",(usuario_usuario, usuario_contrasenia))
    mysql.connection.commit()

    return render_template("index.html", mensaje_registro_exitoso="Usuario registrado exitosamente")

# -----------------Fin Función registro-------------------------
if __name__ == '__main__':
    app.secret_key="paco_si"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
