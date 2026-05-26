# --------------IMPORTACIÓN DE LAS LIBRERIAS------------------
from flask import Flask 
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__,template_folder='template')

# ---------------CONEXIÓN CON BASE DE DATOS-------------------
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='negocio'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# -----------------------Fución login-------------------------
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
                return render_template("admin.html") #Redirige a la interfaz de Admin
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
    usuario_usuario=request.form['usuacorreo']
    usuario_contrasenia=request.form['usuacontra']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (usuario_usuario, usuario_contrasenia, usuario_privilegio) VALUES (%s, %s, '2')",(usuario_usuario, usuario_contrasenia))
    mysql.connection.commit()

    return render_template("index.html", mensaje_registro_exitoso="Usuario registrado exitosamente")

# -----------------Fin Función registro-------------------------
if __name__ == '__main__':
    app.secret_key="paco_si"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)