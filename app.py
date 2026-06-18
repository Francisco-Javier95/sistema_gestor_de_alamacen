# --------------IMPORTACIÓN DE LAS LIBRERIAS-------------------------
from flask import Flask 
from flask import render_template, redirect, request, Response, session, url_for, flash
from flask_mysqldb import MySQL, MySQLdb
from flask import send_from_directory
from datetime import datetime
import os # Permite entrar en carpetas para poder eliminar un archivo

app = Flask(__name__,template_folder='template')

# ---------------CONEXIÓN CON BASE DE DATOS--------------------------
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='negocio'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)
# -------------------------------------------------------------------

# Crear la referencia de la carpeta "uploads"
CARPETA = os.path.join('uploads') # Crear la referencia a la carpeta de "uploads"
app.config['CARPETA']=CARPETA # Guardamos la ruta como un dato de la variable CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    # ------------------- Mostrar los registros----------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos")
    articulos = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(articulos) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros----------------------
    return render_template('admin.html', articulos=articulos)

# ----------------Función Agregar Articulo---------------------------
@app.route('/create-articulo')
def pagina_create_articulo():
    return render_template('create-articulos.html')

@app.route('/crear-articulo', methods=["GET", "POST"])
def crear_articulo():
    articulo_articulo=request.form['artNombre']
    articulo_imagen=request.files['artImagen'] # Las imagenes se recepcionan de diferente forma al ser información binaria (siendo que su sintaxis es _nombre=request.file['nombre'])
    articulo_precio=request.form['artPrecio']
    articulo_stock=request.form['artStock']

    # Mandar mensaje sí algun campo esta vacio
    if articulo_articulo=='' or articulo_imagen=='' or articulo_precio=='' or articulo_stock=='':
        flash('Recuerda llenar los datos de todos los campos')
        return redirect(url_for('pagina_create_articulo'))

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
# --------------Fin Función Agregar Articulo-------------------------

# -----------------Función Borrar Articulo---------------------------
@app.route('/destroy-articulo/<int:id>')
def destroy_articulo(id):
    cur = mysql.connection.cursor()

    # ---------------------Eliminar vieja imagen------------------
    cur.execute("SELECT articulo_imagen FROM articulos WHERE articulo_id = %s", (id,))
    vieja_imagen = cur.fetchone()
    nombre_imagen = vieja_imagen['articulo_imagen'] # Sacar de "{'articulo_imagen': '2026185156nombre.jpg'}"" solo el nombre (2026185156nombre.jpg)
    os.remove(os.path.join(app.config['CARPETA'], nombre_imagen)) # Remueve de la carpeta uploads la vieja imagen (a partir de su ruta y nombre)
    # ------------------------------------------------------------

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
# ---------------Fin Función Borrar Articulo-------------------------

# -----------------Función Editar Articulo---------------------------
@app.route('/edit-articulo/<int:id>')
def edit_articulo(id):

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articulos WHERE `articulos`.`articulo_id` = %s", (id,))
    articulo_id = cur.fetchall() # Envia la información del registro
    mysql.connection.commit()
    cur.close()

    print(articulo_id)

    return render_template('edit-articulos.html', articulo_id=articulo_id)

# --------------------Guardar los datos------------------------------
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

        # ---------------------Eliminar vieja imagen------------------
        cur.execute("SELECT articulo_imagen FROM articulos WHERE articulo_id = %s", (articulo_id,))
        vieja_imagen = cur.fetchone()
        nombre_imagen = vieja_imagen['articulo_imagen'] # Sacar de "{'articulo_imagen': '2026185156nombre.jpg'}"" solo el nombre (2026185156nombre.jpg)
        os.remove(os.path.join(app.config['CARPETA'], nombre_imagen)) # Remueve de la carpeta uploads la vieja imagen (a partir de su ruta y nombre)
        # ------------------------------------------------------------

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
# -------------------------------------------------------------------
# ---------------Fin Función Editar Articulo-------------------------


@app.route('/admin/usuarios')
def usuario():
    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(usuarios) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------
    return render_template("usuarios.html", usuarios=usuarios)

# -------------------Función registro--------------------------------
@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/crear-registro', methods=["GET", "POST"]) # Extrae de la pagina de registro.html el formulario con action='acceso-registro'
def crear_registro():
    usuario_usuario=request.form['usuanombre'] # Guarda el valor del campo de usuarionombre en la variable usuario_nombre
    usuario_apellido_paterno=request.form['usuaapellidop'] # Guarda el valor del campo de usuaapellidop en la variable usuario_apellido_paterno
    usuario_apellido_materno=request.form['usuaapellidom'] # Guarda el valor del campo de usuaapellidom en la variable usuario_apellido_materno
    usuario_numero_empleado=request.form['usuanumempleado'] # Guarda el valor del campo de usuanumempleado en la variabl usuario_numero_empleado
    usuario_correo=request.form['usuacorreo'] # Guarda el valor del campo de usuacorreo en la variable usuario_usuario
    usuario_contrasenia=request.form['usuacontra'] # Guarda el valor del campo de usuacontra en la variable usuario_contrasenia
    usuario_privilegio=request.form['usuapriv'] # Guarda el valor del campo de usuapriv en la variable usuario_privilegio

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (usuario_usuario, usuario_aPaterno, usuario_aMaterno, usuario_nuEmpleado, usuario_correo, usuario_contrasenia, usuario_privilegio) VALUES (%s, %s, %s, %s, %s, %s, %s)",(usuario_usuario, usuario_apellido_paterno, usuario_apellido_materno, usuario_numero_empleado, usuario_correo, usuario_contrasenia, usuario_privilegio))
    mysql.connection.commit()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(usuarios) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------

    return render_template("usuarios.html", usuarios=usuarios, mensaje_registro_exitoso="Usuario registrado exitosamente")

# -----------------Fin Función registro------------------------------

# ----------------Función Editar Registro----------------------------
@app.route('/edit-usuario/<int:id>')
def edit_usuario(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE usuario_id = %s", (id,))
    usuario_del_id = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    print(usuario_del_id)

    return render_template('edit-usuarios.html', usuario_registro=usuario_del_id)

# --------------------Guardar los datos------------------------------
@app.route('/editar-usuario', methods=["POST"])
def editar_usuario():
    usuario_id = request.form['usuaId']
    usuario_nombre= request.form['usuanombre']
    usuario_apellido_paterno = request.form['usuaapellidop']
    usuario_apellido_materno = request.form['usuaapellidom']
    usuario_numero_empleado = request.form['usuanumempleado']
    usuario_correo_electronico = request.form['usuacorreo']
    usuario_contrasenia = request.form['usuacontra']
    usuario_privilegio = request.form['usuapriv']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuarios SET usuario_usuario = %s, usuario_aPaterno = %s, usuario_aMaterno = %s, usuario_nuEmpleado = %s, usuario_correo = %s, usuario_contrasenia = %s, usuario_privilegio = %s WHERE usuario_id = %s", (usuario_nombre, usuario_apellido_paterno, usuario_apellido_materno, usuario_numero_empleado, usuario_correo_electronico, usuario_contrasenia, usuario_privilegio, usuario_id))
    mysql.connection.commit()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(usuarios) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------

    id_modificado=str(usuario_id) # Convierte un int en str(String)

    return render_template('usuarios.html', usuarios=usuarios, mensaje_usuario_modificado_exitosamente=("Usuario "+ id_modificado +" modificado exitosamente"))
# -------------------------------------------------------------------
# --------------Fin Función Editar Registro--------------------------

# -----------------Función Borrar Usuario----------------------------
@app.route('/destroy-usuario/<int:id>')
def destroy_usuario(id):

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE `usuarios`.`usuario_id` = %s", (id,))
    mysql.connection.commit()
    cur.close()

    # ------------------- Mostrar los registros------------------
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(usuarios) # Imprime en la terminal los registros
    # ----------------Fin Mostrar los registros------------------

    id_eliminado=str(id) # Convierte un int en str(String)
    return render_template("usuarios.html",  usuarios=usuarios, mensaje_usuario_eliminado_exitosamente=("Usuario "+ id_eliminado +" eliminado exitosamente"))
# ----------------Fin Función Borrar Usuario-------------------------

@app.route('/admin/proveedores')
def proveedor():
    #--------------------Mostrar proveedores-------------------------
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores")
    proveedores = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(proveedores) # Imprime en la terminal los registros
    #------------------Fin Mostara proveedores-----------------------
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/create-proveedor')
def pagina_crear_proveedor():
    return render_template('create-proveedor.html')

# --------------------Función agregar proveedor----------------------
@app.route('/crear-proveedor', methods=["GET", "POST"])
def crear_proveedor():
    proveedor_proveedor = request.form['pronombre']
    proveedor_apellido_paterno = request.form['proapellidop']
    proveedor_apellido_materno = request.form['proapellidom']
    proveedor_telefono = request.form['protelefono']
    proveedor_direccion = request.form['prodireccion']
    proveedor_correo = request.form['procorreo']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO proveedores (proveedor_proveedor, proveedor_aPaterno, proveedor_aMaterno, proveedor_telefono, proveedor_direccion, proveedor_correo) VALUES (%s, %s, %s, %s, %s, %s)", (proveedor_proveedor, proveedor_apellido_paterno, proveedor_apellido_materno, proveedor_telefono, proveedor_direccion, proveedor_correo))
    mysql.connection.commit()

    #--------------------Mostrar proveedores-------------------------
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores")
    proveedores = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(proveedores) # Imprime en la terminal los registros
    #------------------Fin Mostara proveedores-----------------------

    return render_template("proveedores.html", proveedores=proveedores, mensaje_proveedor_agregado_exitosamente="Proveedor agregado exitosamente")
# ------------------Fin Función agregar proveedor--------------------

# --------------------Función Editar proveedor-----------------------
@app.route('/edit-proveedor/<int:id>')
def pagina_editar_proveedor(id):
    cur= mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores WHERE `proveedores`.`proveedor_id` = %s", (id,))
    proveedor_id = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    print(proveedor_id)

    return render_template("edit-proveedor.html", proveedor_id=proveedor_id)

# ------------------------Guardar los datos--------------------------
@app.route('/editar-proveedor', methods=["GET", "POST"])
def editar_registro():
    proveedor_id = request.form['proID']
    proveedor_proveedor = request.form['pronombre']
    proveedor_apellido_paternpo = request.form['proapellidop']
    proveedor_apellido_materno = request.form['proapellidom']
    proveedor_telefono = request.form['protelefono']
    proveedor_direccion = request.form['prodireccion']
    proveedor_correo = request.form['procorreo']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE proveedores SET proveedor_proveedor=%s, proveedor_aPaterno=%s, proveedor_aMaterno=%s, proveedor_telefono=%s, proveedor_direccion=%s, proveedor_correo=%s WHERE proveedor_id=%s", (proveedor_proveedor, proveedor_apellido_paternpo, proveedor_apellido_materno, proveedor_telefono, proveedor_direccion, proveedor_correo, proveedor_id))
    mysql.connection.commit()

    #--------------------Mostrar proveedores-------------------------
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores")
    proveedores = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(proveedores) # Imprime en la terminal los registros
    #------------------Fin Mostara proveedores-----------------------

    id_modificado=str(proveedor_id)

    return render_template('proveedores.html', proveedores=proveedores, mensaje_proveedor_editado_exitosamente=("Proveedor "+ id_modificado +" modificado exitosamente"))
# -------------------------------------------------------------------
# ------------------Fin Función Editar proveedor---------------------

# ---------------------Función borrar proveedor----------------------
@app.route('/destroy-proveedor/<int:id>')
def destroy_proveedor(id):

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM proveedores WHERE proveedor_id = %s", (id,))
    mysql.connection.commit()

    #--------------------Mostrar proveedores-------------------------
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM proveedores")
    proveedores = cur.fetchall() # Selecciona todos los registros
    cur.close()

    print(proveedores) # Imprime en la terminal los registros
    #------------------Fin Mostrar proveedores-----------------------

    id_eliminado = str(id) # Convierte un int en str(String)

    return render_template('proveedores.html', proveedores=proveedores, mensaje_proveedor_eliminado_exitosamente=("Proveedor "+ id_eliminado +" eliminado exitosamente"))
# -------------------Fin Función borrar proveedor--------------------

# -----------------------Fución login--------------------------------
@app.route('/acceso-login', methods=["GET", "POST"]) # Extrae de la pagina de index.html el formulario con action='acceso-login'
def login():
    if request.method == 'POST' and 'usuacorreo' in request.form and 'usuacontra': # Cuando se envien los datos por metodo POST se extraeran los datos de los campos con name="usuacorreo" y name="usuacontra"
        usuario_correo = request.form['usuacorreo'] #Se guardan los datos en la variable usuario_usuario
        usuario_contrasenia = request.form['usuacontra'] #Se guardan los datos en la variable usuario_contrasenia

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE usuario_correo = %s', (usuario_correo,)) #Se selecciona todo de la tlaba usuarios para comparar los datos de la columna usuario_usuario con el dato que alamacenamos del formulario en la variable usuario_usuario.
        correo_correcto = cur.fetchone()

        if correo_correcto:

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM usuarios WHERE usuario_contrasenia = %s AND usuario_correo = %s', (usuario_contrasenia, usuario_correo)) #  Y los mismo con los datos de la columna usuario_contrasenia con el dato que se almaceno en la variable usuario_contrasenia
            contrasenia_correcta = cur.fetchone()

            if contrasenia_correcta:
                session['logueado'] = True
                session['id'] = correo_correcto['usuario_id']
                session['usuario_privilegio'] = correo_correcto['usuario_privilegio']

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
                    if session['usuario_privilegio'] == 2: #Sino, compara si el dato es igual a 2 (2 = Supervisor)
                        return render_template("supervisor.html") #Redirige a la interfaz de Supervisor
                    else:
                        if session['usuario_privilegio'] == 3: #Sino, compara si el privilegio es igual a 3 (3 = Cajero)
                            return render_template("cajero.html")
            else:
                return render_template ('index.html', mensaje_error_contrasenia="Contraseña incorrecta")
                
        else:
            return render_template('index.html', mensaje_error_correo="Correo electronico incorrecto") 
        
    else:
        return render_template('index.html')
# ------------------Fin Función login--------------------------------

# -------------Función restablecer contraseña------------------------
@app.route('/restore-contraseña')
def restore_contrasenia():
    return render_template('restablecer-contraseña.html')

@app.route('/restaurar-contraseña', methods=["GET", "POST"])
def restaurar_contrasenia():
    restaurar_correo = request.form['rescorreo']
    restaurar_numero_empleado = request.form['resnumeroempleado']
    restaurar_nueva_contrasenia = request.form['rescontrasenia']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE usuario_correo = %s", (restaurar_correo,))
    restaurar_correo_correcto = cur.fetchone()

    if restaurar_correo_correcto:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario_nuEmpleado = %s AND usuario_correo = %s", (restaurar_numero_empleado, restaurar_correo,))
        restaurar_numero_empleado_correcto = cur.fetchone()

        if restaurar_numero_empleado_correcto:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usuarios SET usuario_contrasenia = %s WHERE usuario_correo = %s AND usuario_nuEmpleado = %s", (restaurar_nueva_contrasenia, restaurar_correo, restaurar_numero_empleado))
            mysql.connection.commit()
            cur.close()

            return render_template('index.html', mensaje_contrasenia_restablecida_exitosamente="Contraseña restablecida exitosamente")
        else:
            return render_template('restablecer-contraseña.html', mensaje_numero_empleado_incorrecto="Número de empleado incorrecto")
    else:
        return render_template('restablecer-contraseña.html', mensaje_correo_incorrecto="Correo electrónico incorrecto")
# -----------Fin Función restablecer contraseña----------------------

if __name__ == '__main__':
    app.secret_key="paco_si"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
