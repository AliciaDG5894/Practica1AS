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

def pusherClientes():
    import pusher
    
    pusher_client = pusher.Pusher(
    app_id="2046017",
    key="b51b00ad61c8006b2e6f",
    secret="d2ec35aa5498a18af7bf",
    cluster="us2",
    ssl=True
    )
    
    pusher_client.trigger("canalClientes", "eventoClientes", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))

# TRAJES
def pusherProductos():
    import pusher
    
    pusher_client = pusher.Pusher(
    app_id="2046017",
    key="b51b00ad61c8006b2e6f",
    secret="d2ec35aa5498a18af7bf",
    cluster="us2",
    ssl=True
    )
    
    pusher_client.trigger("canalTrajes", "eventoTrajes", {"message": "Hola Mundo!"})

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
@app.route("/renta/<int:id>")
def editarProducto(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idRenta, idCliente, idTraje, descripcion, fechaHoraInicio, fechaHoraFin

    FROM rentas

    WHERE idRenta = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

# ELIMINAR
@app.route("/renta/eliminar", methods=["POST"])
def eliminarRenta():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM rentas
    WHERE idRenta = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))


#CLIENTE

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

@app.route("/tbodyClientes")
def tbodyClientes():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idCliente,
           nombreCliente,
           telefono,
           correoElectronico

    FROM clientes

    ORDER BY idCliente DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("tbodyClientes.html", clientes=registros)

@app.route("/api/clientes/buscar", methods=["GET"])
def buscarClientes():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idCliente,
           nombreCliente,
           telefono,
           correoElectronico

    FROM clientes

    WHERE nombreCliente LIKE %s
    OR    telefono          LIKE %s
    OR    correoElectronico     LIKE %s

    ORDER BY idCliente DESC

    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas
        """
        for registro in registros:
            fecha_hora = registro["Fecha_Hora"]

            registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
            registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
        """

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/cliente", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarCliente():
    if not con.is_connected():
        con.reconnect()

    idCliente = request.form.get("idCliente")
    nombre      = request.form["nombreCliente"]
    telefono      = request.form["telefono"]
    correoElectronico = request.form["correoElectronico"]
    
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if idCliente:
        sql = """
        UPDATE clientes

        SET nombreCliente = %s,
            telefono          = %s,
            correoElectronico     = %s

        WHERE idCliente = %s
        """
        val = (nombre, telefono, correoElectronico, idCliente)
    else:
        sql = """
        INSERT INTO clientes (nombreCliente, telefono, correoElectronico)
                    VALUES    (%s,          %s,      %s)
        """
        val =                 (nombre, telefono, correoElectronico)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusherClientes()
    
    return make_response(jsonify({}))

@app.route("/cliente/<int:id>")
def editarClientes(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idCliente, nombreCliente, telefono, correoElectronico

    FROM clientes

    WHERE idCliente = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/clientes/eliminar", methods=["POST"])
def eliminarCliente():
    try:
        if not con.is_connected():
            con.reconnect()

        idCliente = request.form.get("id")

        cursor = con.cursor()
        sql = "DELETE FROM clientes WHERE idCliente = %s"
        val = (idCliente,)

        cursor.execute(sql, val)
        con.commit()
        con.close()

        pusherClientes()

        return make_response(jsonify({"status": "ok"}))

    except Exception as e:
        print("Error eliminando cliente:", e)
        return make_response(jsonify({"error": str(e)}), 500)
    

# TRAJES

@app.route("/trajes")
def trajes():
    return render_template("trajes.html")

@app.route("/tbodyTrajes")
def tbodyTrajes():
    if not con.is_connected():
        con.reconnect()
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT IdTraje,
           nombreTraje,
           descripcion

    FROM trajes

    ORDER BY IdTraje DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("tbodyTrajes.html", trajes=registros)

@app.route("/trajes/guardar", methods=["POST", "GET"])
def guardarTraje():
    if not con.is_connected():
        con.reconnect()

    if request.method == "POST":
        data = request.get_json() or request.form
        nombre = data.get("txtNombre")
        descripcion = data.get("txtDescripcion")
    else: 
        nombre = request.args.get("nombre")
        descripcion = request.args.get("descripcion")
    if not nombre or not descripcion:
        return jsonify({"error": "Faltan parámetros"}), 400
        
    cursor = con.cursor()
    sql = """
    INSERT INTO trajes (nombreTraje, descripcion)
    VALUES (%s, %s)
    """
    cursor.execute(sql, (nombre, descripcion))
    con.commit()
    con.close()

    pusherProductos()

    return make_response(jsonify({"mensaje": "Traje guardado correctamente"}))

@app.route("/trajes/eliminar", methods=["POST", "GET"])
def eliminartraje():
    if not con.is_connected():
        con.reconnect()

    if request.method == "POST":
        IdTraje = request.form.get("id")
    else:
        IdTraje = request.args.get("id")

    cursor = con.cursor()
    sql = "DELETE FROM trajes WHERE IdTraje = %s"
    val = (IdTraje,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusherProductos()

    return make_response(jsonify({"status": "ok"}))

