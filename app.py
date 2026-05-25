from flask import Flask 
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__,template_folder='template')

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

# Función de login
@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'usuacorreo' in request.form and 'usuacontra':
        _usuario = request.form['usuacorreo']
        _contrasenia = request.form['usuacontra']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE usuario_usuario = %s AND usuario_contrasenia = %s', (_usuario, _contrasenia,))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['usuario_id']

            return render_template('admin.html')
        else:
            return render_template('index.html', mensaje="Usuario incorrecto")
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.secret_key="paco_si"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)