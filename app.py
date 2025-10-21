from flask import Flask, render_template, request, redirect, url_for, session, g
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a la base de datos con un tiempo de espera de conexión
db = pymysql.connect(
    host='10.3.29.20', 
    port=33060, 
    user='user_gr2', 
    password='portatil123', 
    database='gr2_db', 
    connect_timeout=10  # Timeout de 10 segundos
)

@app.before_request
def before_request():
    """Asegura que la conexión a la base de datos esté activa."""
    try:
        # Realiza un ping a la base de datos para asegurarse de que la conexión sigue activa
        if db.open:
            db.ping(reconnect=True)  # Reconecta si es necesario
    except pymysql.MySQLError as e:
        print(f"Error al mantener la conexión: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT id, password_hash FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))  # Redirige a dashboard después de iniciar sesión correctamente
        else:
            return "Credenciales incorrectas", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password))
        db.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige a login si no está autenticado

    user_id = session['user_id']  # Obtén el ID del usuario autenticado

    cursor = db.cursor()

    # Consulta para obtener los portátiles disponibles (que no están reservados)
    cursor.execute("""
        SELECT * FROM portatiles
        WHERE id NOT IN (SELECT portatil_id FROM reservas)
    """)
    portatiles = cursor.fetchall()

    # Consulta para obtener las reservas del usuario actual
    cursor.execute("""
        SELECT p.id, p.marca, r.fecha_reserva
        FROM reservas r
        JOIN portatiles p ON r.portatil_id = p.id
        WHERE r.usuario_id = %s
    """, (user_id,))
    reservas = cursor.fetchall()

    return render_template('dashboard.html', portatiles=portatiles, reservas=reservas)


@app.route('/alquilar/<int:portatil_id>', methods=['GET', 'POST'])
def alquilar(portatil_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Si no está logueado, redirige a login

    user_id = session['user_id']
    fecha_reserva = datetime.now()

    cursor = db.cursor()

    # Verifica si ya hay una reserva para ese usuario y portátil
    try:
        cursor.execute("SELECT * FROM reservas WHERE usuario_id = %s AND portatil_id = %s", (user_id, portatil_id))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            return "Ya tienes una reserva para este portátil.", 400

        cursor.execute("INSERT INTO reservas (usuario_id, portatil_id, fecha_reserva) VALUES (%s, %s, %s)",
                       (user_id, portatil_id, fecha_reserva))
        db.commit()

        return redirect(url_for('dashboard') + '#mis-reservas')

    except pymysql.MySQLError as e:
        print("Error en MySQL:", str(e))  # Ver el error en la consola
        return f"Error al hacer la reserva: {str(e)}", 500


@app.route('/cancelar_reserva/<int:reserva_id>', methods=['POST'])
def cancelar_reserva(reserva_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige a login si el usuario no está autenticado

    user_id = session['user_id']
    cursor = db.cursor()

    # Verificar si la reserva pertenece al usuario
    cursor.execute("""
        SELECT portatil_id FROM reservas WHERE id = %s AND usuario_id = %s
    """, (reserva_id, user_id))
    reserva = cursor.fetchone()

    if not reserva:
        return "Reserva no encontrada o no pertenece al usuario", 404

    portatil_id = reserva[0]  # Obtener el ID del portátil de la reserva

    # Eliminar la reserva (desvincular usuario y portátil)
    cursor.execute("DELETE FROM reservas WHERE id = %s", (reserva_id,))
    db.commit()

    # Marcar el portátil como disponible
    cursor.execute("UPDATE portatiles SET estado = 'disponible' WHERE id = %s", (portatil_id,))
    db.commit()

    return redirect(url_for('dashboard') + '#mis-reservas')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT id, password FROM admin WHERE correo = %s", (correo,))
        admin = cursor.fetchone()

        if admin and admin[1] == password:
            session['admin_id'] = admin[0]
            return redirect(url_for('admin_dashboard'))
        else:
            return "Correo o contraseña incorrectos", 401

    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))  # Redirige si no está logueado como admin

    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        marca = request.form['marca']
        estado = request.form['estado']
        almacenamiento = request.form['almacenamiento']
        os = request.form['os']
        ram = request.form['ram']  # Captura el valor de RAM

        # Insertar los datos del nuevo portátil en la base de datos
        cursor.execute("""
            INSERT INTO portatiles (marca, estado, almacenamiento, OS, ram)
            VALUES (%s, %s, %s, %s, %s)
        """, (marca, estado, almacenamiento, os, ram))
        db.commit()

    # Eliminar portátil y las reservas asociadas
    if request.args.get('delete_id'):
        delete_id = request.args.get('delete_id')

        # Primero, eliminar las reservas asociadas a este portátil de la tabla 'fecha'
        cursor.execute("DELETE FROM fecha WHERE id_portatiles = %s", (delete_id,))
        db.commit()

        # También eliminar las reservas asociadas de la tabla 'reservas'
        cursor.execute("DELETE FROM reservas WHERE portatil_id = %s", (delete_id,))
        db.commit()

        # Ahora, eliminar el portátil de la tabla 'portatiles'
        cursor.execute("DELETE FROM portatiles WHERE id = %s", (delete_id,))
        db.commit()

    # Obtener los portátiles
    cursor.execute("SELECT * FROM portatiles")
    portatiles = cursor.fetchall()

    # Obtener las reservas realizadas
    cursor.execute("""
        SELECT p.id, p.marca, u.username, r.fecha_reserva
        FROM portatiles p
        JOIN reservas r ON p.id = r.portatil_id
        JOIN usuarios u ON r.usuario_id = u.id
        ORDER BY r.fecha_reserva DESC
    """)
    reservas = cursor.fetchall()

    return render_template('admin_dashboard.html', portatiles=portatiles, reservas=reservas)

@app.route('/reservados')
def reservados():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))  # Si no está logueado como admin, redirige al login

    cursor = db.cursor()

    cursor.execute("""
        SELECT p.id, p.marca, p.estado, p.almacenamiento, p.OS, p.ram, r.fecha_reserva, u.username, u.email
        FROM portatiles p
        LEFT JOIN reservas r ON p.id = r.portatil_id
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        ORDER BY r.fecha_reserva DESC
    """)
    portatiles_reservados = cursor.fetchall()

    current_date = datetime.now().strftime('%Y-%m-%d')  # Formatear la fecha actual en el formato deseado
    return render_template('reservados.html', portatiles_reservados=portatiles_reservados, current_date=current_date)


@app.route('/mis_reservas')
def mis_reservas():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Si no está logueado, redirige a login

    user_id = session['user_id']
    cursor = db.cursor()

    cursor.execute("""
        SELECT p.id, p.marca, r.fecha_reserva, p.ram
        FROM portatiles p
        JOIN reservas r ON p.id = r.portatil_id
        WHERE r.usuario_id = %s
        ORDER BY r.fecha_reserva DESC
    """, (user_id,))
    reservas = cursor.fetchall()

    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('mis_reservas.html', reservas=reservas, current_date=current_date)

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('user_id', None)  # Elimina al usuario también si está logueado
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
