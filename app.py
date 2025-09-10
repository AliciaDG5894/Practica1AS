# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_23005256_bd",
    user="u760464709_23005256_usr",
    password="~6ru!MMJZzX"
)

app = Flask(__name__)
CORS(app)


# PUSHER/ listo

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

# RUTA
@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("index.html")

# LOGIN
@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("login.html")
    # return "<h5>Hola, soy la view app</h5>"



# CREAR TABLA DE USUARIO/ listo

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def iniciarSesion():
    if not con.is_connected():
        con.reconnect()

    usuario    = request.form["txtUsuario"]
    contrasena = request.form["txtContrasena"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Usuario
    FROM usuarios

    WHERE Nombre_Usuario = %s
    AND Contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))



@app.route("/rentas")
def rentas():
    return render_template("rentas.html")

@app.route("/tbodyRentas")
def tbodyRentas():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idRenta,
           idCliente,
           idTraje,
           descripcion,
           fechaHoraInicio,
           fechaHoraFin

    FROM rentas

    ORDER BY idRenta DESC

    LIMIT 10 OFFSET 0
    """

# REVISAR FECHA/ listo
    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    
    for registro in registros:
        inicio = registro["fechaHoraInicio"]
        fin = registro["fechaHoraFin"]

        registro["fechaInicioFormato"] = inicio.strftime("%d/%m/%Y")
        registro["horaInicioFormato"]  = inicio.strftime("%H:%M:%S")

        registro["fechaFinFormato"] = fin.strftime("%d/%m/%Y")
        registro["horaFinFormato"]  = fin.strftime("%H:%M:%S")
    
# Y CAMBIE PRODUCTOS=REGIStros / listo
    return render_template("tbodyRentas.html", rentas=registros)

# MODAL

# @app.route("/productos/ingredientes/<int:id>")
# def productosIngredientes(id):
#     if not con.is_connected():
#         con.reconnect()

#     cursor = con.cursor(dictionary=True)
#     sql    = """
#     SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad FROM productos_ingredientes
#     INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
#     INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
#     WHERE productos_ingredientes.Id_Producto = %s
#     ORDER BY productos.Nombre_Producto
#     """

#     cursor.execute(sql, (id, ))
#     registros = cursor.fetchall()

#     return render_template("modal.html", productosIngredientes=registros)


# BUSQUEDA
@app.route("/rentas/buscar", methods=["GET"])
def buscarRentas():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
# EN WHERE BUSQUEDA PUSE SOLO TRES POR EL "VAL" NO SE SI SE LIMITE (si se limita)
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

# CHECAR FECHA/ listo

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas(comentario de profe)

        for registro in registros:
            inicio = registro["fechaHoraInicio"]
            fin = registro["fechaHoraFin"]

            registro["fechaInicioFormato"] = inicio.strftime("%d/%m/%Y")
            registro["horaInicioFormato"]  = inicio.strftime("%H:%M:%S")

            registro["fechaFinFormato"] = fin.strftime("%d/%m/%Y")
            registro["horaFinFormato"]  = fin.strftime("%H:%M:%S")
        

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))


# GUARDAR

@app.route("/renta", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarRenta():
    if not con.is_connected():
        con.reconnect()

    id               = request.form["id"]
    cliente          = request.form["cliente"]
    traje            = request.form["traje"]
    descripcion      = request.form["descripcion"]
    fechahorainicio  = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    fechahorafin     = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE rentas

        SET idCliente       = %s,
            idTraje         = %s,
            descripcion     = %s,
            fechaHoraInicio = %s,
            fechaHoraFin

        WHERE idRenta = %s
        """
        val = (cliente, traje, descripcion, fechahorainicio, fechahorafin, id)
    else:
        # FALTA CAMBIAR/ listo
        sql = """
        INSERT INTO rentas (idCliente, idTraje, descripcion, fechaHoraInicio, fechaHoraFin)
                    VALUES (   %s,        %s,        %s,            %s,            %s)
        """
        val =                 (cliente, traje, descripcion, fechahorainicio, fechahorafin)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

# CAMBIAR PUSHERRRRRR
    pusherRentas()
    
    return make_response(jsonify({}))


# EDITAR
# @app.route("/producto/<int:id>")
# def editarProducto(id):
#     if not con.is_connected():
#         con.reconnect()

#     cursor = con.cursor(dictionary=True)
#     sql    = """
#     SELECT Id_Producto, Nombre_Producto, Precio, Existencias

#     FROM productos

#     WHERE Id_Producto = %s
#     """
#     val    = (id,)

#     cursor.execute(sql, val)
#     registros = cursor.fetchall()
#     con.close()

#     return make_response(jsonify(registros))


# ELIMINAR
# @app.route("/producto/eliminar", methods=["POST"])
# def eliminarProducto():
#     if not con.is_connected():
#         con.reconnect()

#     id = request.form["id"]

#     cursor = con.cursor(dictionary=True)
#     sql    = """
#     DELETE FROM productos
#     WHERE Id_Producto = %s
#     """
#     val    = (id,)

#     cursor.execute(sql, val)
#     con.commit()
#     con.close()

#     return make_response(jsonify({}))


