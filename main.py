from typing import Union
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") #cargar files de static
templates = Jinja2Templates(directory="templates") #cargar templates


@app.get("/login", response_class=HTMLResponse)
def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def post_login(
    request: Request,
    usuario: str = Form(...),
    password: str = Form(...)
):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    consulta_vulnerable = f"""
        SELECT id, username, password, isAdmin
        FROM Usuarios
        WHERE username = '{usuario}' 
          AND password = '{password}'
    """
    print("DEBUG:", consulta_vulnerable) 

    cursor.execute(consulta_vulnerable)
    user = cursor.fetchone()
    conn.close()

    if not user:
        # Falló la "verificación"
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error_message": "Usuario o contraseña incorrectos"
            }
        )
    else:
        return RedirectResponse(url="/panel-admin", status_code=302)



@app.get("/panel-admin", response_class=HTMLResponse)
def panel_admin(request: Request):
    """
    Nueva ruta para renderizar la plantilla panel-admin.html
    y mostrar la lista de productos.
    """
    # Conectarse a la base de datos (asegúrate de que 'app.db' exista y contenga la tabla 'Productos')
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Hacer la consulta a la tabla 'Productos'
    cursor.execute("""
        SELECT nombre, precio, cantidad_stock, categoria
        FROM Productos
    """)
    productos = cursor.fetchall()  # Esto retorna una lista de tuplas (nombre, precio, stock, categoria)

    conn.close()

    # Pasar la lista de productos a la plantilla
    return templates.TemplateResponse(
        "panel-admin.html",
        {
            "request": request,
            "success_message": "¡Bienvenido a tu panel de administrador!",
            "productos": productos
        }
    )


@app.post("/usuarios/")
def create_usuario(
    nombre: str,
    username: str,
    password: str,
    role: str,
    isAdmin: bool,
    telefono: str,
    direccion: str
):
    """
    Endpoint para crear un nuevo usuario en la tabla 'Usuarios'.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Usuarios (nombre, username, password, role, isAdmin, telefono, direccion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, username, password, role, isAdmin, telefono, direccion))

    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Usuario creado exitosamente",
        "user_id": nuevo_id,
        "username": username
    }


@app.post("/productos/")
def create_producto(
    nombre: str,
    precio: float,
    cantidad_stock: int,
    categoria: str
):
    """
    Endpoint para crear un nuevo producto en la tabla 'Productos'.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Productos (nombre, precio, cantidad_stock, categoria)
        VALUES (?, ?, ?, ?)
    """, (nombre, precio, cantidad_stock, categoria))

    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Producto creado exitosamente",
        "producto_id": nuevo_id,
        "nombre": nombre
    }

