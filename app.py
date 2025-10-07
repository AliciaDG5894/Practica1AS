# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from functools import wraps
from flask import Flask, render_template, request, jsonify, make_response, session

from flask_cors import CORS, cross_origin

import mysql.connector.pooling
import pusher
import pytz
import datetime

app            = Flask(__name__)
app.secret_key = "Test12345"
CORS(app)

con_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    host="185.232.14.52",
    database="u760464709_23005256_bd",
    user="u760464709_23005256_usr",
    password="~6ru!MMJZzX"
)
"""
con_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    host="localhost",
    database="practicas",
    user="root",
    password="Test12345"
)
"""

def pusherRentas():
    import pusher
    
    pusher_client = pusher.Pusher(
    app_id="2046017",
    key="b51b00ad61c8006b2e6f",
    secret="d2ec35aa5498a18af7bf",
    cluster="us2",
    ssl=True
    )
    
    pusher_client.trigger("canalRentas", "eventoRentas", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))


def login(fun):
    @wraps(fun)
    def decorador(*args, **kwargs):
        if not session.get("login"):
            return jsonify({
                "estado": "error",
                "respuesta": "No has iniciado sesión"
            }), 401
        return fun(*args, **kwargs)
    return decorador

@app.route("/")
def landingPage():
    return render_template("landing-page.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def appLogin():
    return render_template("login.html")
    # return "<h5>Hola, soy la view app</h5>"

@app.route("/fechaHora")
def fechaHora():
    tz    = pytz.timezone("America/Matamoros")
    ahora = datetime.datetime.now(tz)
    return ahora.strftime("%Y-%m-%d %H:%M:%S")

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def iniciarSesion():
    usuario    = request.form["usuario"]
    contrasena = request.form["contrasena"]

    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Usuario, Nombre_Usuario, Tipo_Usuario
    FROM usuarios
    WHERE Nombre_Usuario = %s
    AND Contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    session["login"]      = False
    session["login-usr"]  = None
    session["login-tipo"] = 0
    if registros:
        usuario = registros[0]
        session["login"]      = True
        session["login-usr"]  = usuario["Nombre_Usuario"]
        session["login-tipo"] = usuario["Tipo_Usuario"]

    return make_response(jsonify(registros))

@app.route("/cerrarSesion", methods=["POST"])
@login
def cerrarSesion():
    session["login"]      = False
    session["login-usr"]  = None
    session["login-tipo"] = 0
    return make_response(jsonify({}))

@app.route("/preferencias")
@login
def preferencias():
    return make_response(jsonify({
        "usr": session.get("login-usr"),
        "tipo": session.get("login-tipo", 2)
    }))


@app.route("/rentas")
def rentas():
    return render_template("rentas.html")

@app.route("/rentas/buscar", methods=["GET"])
@login
def buscarRentas():
    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    try:
        con    = con_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        sql    = """
        SELECT idRenta,
            idCliente,
            idTraje,
            descripcion,
            fechaHoraInicio,
            fechaHoraFin
        FROM rentas

            WHERE idCliente LIKE %s
            OR    idTraje          LIKE %s
            OR    descripcion      LIKE %s
            OR    fechaHoraInicio  LIKE %s
            OR    fechaHoraFin     LIKE %s

        ORDER BY idRenta DESC
        LIMIT 10 OFFSET 0
        """
        val    = (busqueda, busqueda, busqueda, busqueda, busqueda)

        cursor.execute(sql, val)
        registros = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        registros = []

    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()

    return make_response(jsonify(registros))


@app.route("/renta", methods=["POST"])
@login
def guardarRenta():
    id               = request.form["id"]
    cliente          = request.form["cliente"]
    traje            = request.form["traje"]
    descripcion      = request.form["descripcion"]
    fechahorainicio  = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    fechahorafin     = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))

    con    = con_pool.get_connection()
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE productos
        SET idCliente       = %s,
            idTraje         = %s,
            descripcion     = %s,
            fechaHoraInicio = %s,
            fechaHoraFin

        WHERE idRenta = %s
        """
        val = (cliente, traje, descripcion, fechahorainicio, fechahorafin, id)
    else:
        sql = """
        INSERT INTO rentas (idCliente, idTraje, descripcion, fechaHoraInicio, fechaHoraFin)
        VALUES             (   %s,        %s,        %s,            %s,            %s)
        """
        val =                 (cliente, traje, descripcion, fechahorainicio, fechahorafin)
    
    cursor.execute(sql, val)
    con.commit()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    pusherRentas()

    return make_response(jsonify({}))


@app.route("/renta/<int:id>")
@login
def editarRenta(id):
    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idRenta, idCliente, idTraje, descripcion, fechaHoraInicio, fechaHoraFin
    FROM rentas
    WHERE idRenta = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    return make_response(jsonify(registros))


@app.route("/renta/eliminar", methods=["POST"])
def eliminarRenta():
    id = request.form["id"]

    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM rentas
    WHERE idRenta = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    pusherRentas()

    return make_response(jsonify({}))
