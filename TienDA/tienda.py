import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector  # Importa la librería mysql.connector

# --- Configuración de la conexión a la base de datos ---
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'init'
}

# --- Funciones para la base de datos ---
def conectar_db():
    global conexion
    try:
        conexion = mysql.connector.connect(**db_config)
        print("Conexión exitosa a la base de datos.")
        return True
    except mysql.connector.Error as error:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {error}")
        return False

def cerrar_db():
    global conexion
    if conexion.is_connected():
        conexion.close()
        print("Conexión cerrada.")

def ejecutar_consulta(consulta, *args):
    global conexion
    cursor = conexion.cursor()
    try:
        cursor.execute(consulta, args)
        conexion.commit()
        print("Consulta ejecutada con éxito.")
    except mysql.connector.Error as error:
        messagebox.showerror("Error de consulta", f"Error al ejecutar la consulta: {error}")

# --- Datos de usuarios (se obtiene de la base de datos) ---
def obtener_usuarios():
    if conectar_db():
        cursor = conexion.cursor()
        cursor.execute("SELECT username, password FROM users")
        usuarios = {row[0]: row[1] for row in cursor}
        cerrar_db()
        return usuarios
    else:
        return {}

usuarios = obtener_usuarios()  # Actualiza el diccionario 'usuarios' con datos de la base de datos

# --- Datos de productos (se obtiene de la base de datos) --
def obtener_productos():
    if conectar_db():
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, plan, servicio, cantidad, precio FROM productos")
        productos = []  # Inicializa la lista de productos

        # Itera sobre las filas obtenidas de la base de datos
        for row in cursor:
            # Crea un diccionario para cada producto
            producto = {
                "nombre": row[0],
                "plan": row[1],
                "servicio": row[2],
                "cantidad": row[3],
                "precio": row[4]
            }
            # Agrega el producto a la lista
            productos.append(producto)

        cerrar_db()
        return productos
    else:
        return []
 

productos = obtener_productos()  # Actualiza la lista 'productos' con datos de la base de datos

# --- Funciones para el carrito ---
def agregar_producto(listbox_productos):
    seleccion = listbox_productos.curselection()
    if seleccion:
        indice = seleccion[0]
        producto = listbox_productos.get(indice)
        carrito.append(producto)
        actualizar_carrito("listbox_carrito")
        calcular_total()

def eliminar_producto():
    seleccion = "listbox_carrito".curselection()
    if seleccion:
        indice = seleccion[0]
        producto = "listbox_carrito".get(indice)
        carrito.remove(producto)
        actualizar_carrito("listbox_carrito")
        calcular_total()

def vaciar_carrito():
    carrito.clear()
    actualizar_carrito("listbox_carrito")
    calcular_total()

def actualizar_carrito(listbox_carrito):
    listbox_carrito.delete(0, tk.END)
    for producto in carrito:
        listbox_carrito.insert(tk.END, producto)

def calcular_total():
    total = 0.00
    for producto in carrito:
        for item in productos:
            if item["nombre"] == producto:
                total += item["precio"]
    label_total.config(text=f"Total: ${total:.2f}")

# --- Funciones para el panel de administrador ---
def actualizar_listbox_productos_admin():
    listbox_productos_admin.delete(0, tk.END)
    for producto in productos:
        listbox_productos_admin.insert(tk.END, producto["nombre"])

def agregar_producto_admin(listbox_productos_admin):
    nombre_producto = simpledialog.askstring("Nuevo producto", "Ingresa el nombre del producto:")
    precio_producto = simpledialog.askfloat("Precio del producto", "Ingresa el precio del producto:")

    if nombre_producto and precio_producto is not None:
        # Guardar el nuevo producto en la base de datos
        ejecutar_consulta("INSERT INTO products (nombre, plan, servicio, cantidad, precio ) VALUES (%s, %s, %s, %s, %s)", nombre_producto, precio_producto)
        productos.append({"nombre": nombre_producto, "precio": precio_producto})  # Agrega a la lista local
        actualizar_listbox_productos_admin()

def eliminar_producto_admin(listbox_productos_admin):
    seleccion = listbox_productos_admin.curselection()
    if seleccion:
        indice = seleccion[0]
        producto = listbox_productos_admin.get(indice)
        # Eliminar el producto de la base de datos
        ejecutar_consulta("DELETE FROM products WHERE nombre = %s", producto)
        productos.pop(indice)  # Eliminar el producto de la lista local
        actualizar_listbox_productos_admin()

def editar_producto_admin():
    seleccion = listbox_productos_admin.curselection()
    if seleccion:
        indice = seleccion[0]
        nombre_producto = listbox_productos_admin.get(indice)

        # Obtener el índice del producto en la lista 'productos'
        for i, producto in enumerate(productos):
            if producto["nombre"] == nombre_producto:
                indice_producto = i
                break

        # --- Ventana para editar el producto ---
        ventana_editar = tk.Toplevel(ventana_panel_admin)
        ventana_editar.title("Editar Producto")
        ventana_editar.geometry("300x150")

        # --- Etiquetas y campos de entrada ---
        label_nombre = tk.Label(ventana_editar, text="Nombre:")
        label_nombre.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_nombre = tk.Entry(ventana_editar)
        entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        entry_nombre.insert(0, productos[indice_producto]["nombre"])

        label_precio = tk.Label(ventana_editar, text="Precio:")
        label_precio.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry_precio = tk.Entry(ventana_editar)
        entry_precio.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        entry_precio.insert(0, str(productos[indice_producto]["precio"]))

        # --- Botón para guardar los cambios ---
        def guardar_cambios():
            nuevo_nombre = entry_nombre.get()
            nuevo_precio = float(entry_precio.get())

            # Actualizar el producto en la base de datos
            ejecutar_consulta("UPDATE products SET nombre = %s plan= %s servivio =%s cantidad = %s  precio = %s WHERE nombre = %s", nuevo_nombre, nuevo_precio, nombre_producto)
            productos[indice_producto] = {"nombre": nuevo_nombre, "precio": nuevo_precio}  # Actualiza la lista local
            actualizar_listbox_productos_admin()
            ventana_editar.destroy()

        boton_guardar = tk.Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios)
        boton_guardar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# --- Funciones para la ventana de inicio de sesión ---
def iniciar_sesion():
    nombre_usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()

    # Verifica si el usuario existe en el diccionario 'usuarios'
    if nombre_usuario in usuarios and usuarios[nombre_usuario] == contraseña:
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso!")
        abrir_ventana_principal(nombre_usuario)  # Abre la ventana principal
        ventana_inicio.withdraw()  # Oculta la ventana de inicio de sesión
    else:
        messagebox.showerror("Error", "Nombre de usuario o contraseña incorrectos.")


def abrir_ventana_registro():
    ventana_registro = tk.Toplevel(ventana_inicio)
    ventana_registro.title("Registrarse")
    ventana_registro.geometry("400x300")  # Tamaño de la ventana de registro
    ventana_registro.resizable(False, False)  # Impide que el usuario redimensione la ventana

    # Etiquetas
    label_nombre = tk.Label(ventana_registro, text="Nombre:")
    label_nombre.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    label_apellido = tk.Label(ventana_registro, text="Apellido:")
    label_apellido.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    label_cedula = tk.Label(ventana_registro, text="Cédula:")
    label_cedula.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    label_usuario = tk.Label(ventana_registro, text="Nombre de usuario:")
    label_usuario.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    label_contraseña = tk.Label(ventana_registro, text="Contraseña:")
    label_contraseña.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    # Campos de entrada
    global entry_nombre, entry_apellido, entry_cedula, entry_usuario_registro, entry_contraseña_registro
    entry_nombre = tk.Entry(ventana_registro)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    entry_apellido = tk.Entry(ventana_registro)
    entry_apellido.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    entry_cedula = tk.Entry(ventana_registro)
    entry_cedula.grid(row=2, column=1, padx=10, pady=10, sticky="w")
    entry_usuario_registro = tk.Entry(ventana_registro)
    entry_usuario_registro.grid(row=3, column=1, padx=10, pady=10, sticky="w")
    entry_contraseña_registro = tk.Entry(ventana_registro, show="*")
    entry_contraseña_registro.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def registrar():
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        cedula = entry_cedula.get()
        nombre_usuario = entry_usuario_registro.get()
        contraseña = entry_contraseña_registro.get()

        if not nombre or not apellido or not cedula or not nombre_usuario or not contraseña:
            messagebox.showerror("Error", "Debes ingresar todos los datos.")
            return

        if nombre_usuario in usuarios:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")
            return

        # Guardar el nuevo usuario en la base de datos
        ejecutar_consulta("INSERT INTO users (username, password) VALUES (%s, %s)", nombre_usuario, contraseña)
        usuarios[nombre_usuario] = contraseña  # Agrega a la lista local
        messagebox.showinfo("Éxito", "Registro exitoso!")
        ventana_registro.destroy()

    # Botón de registro
    boton_registrar = tk.Button(ventana_registro, text="Registrarse", command=registrar)
    boton_registrar.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

def abrir_ventana_admin():
    global ventana_panel_admin # Declara la variable como global
    ventana_admin = tk.Toplevel(ventana_inicio)
    ventana_admin.title("Administrador")
    ventana_admin.geometry("400x200")
    ventana_admin.resizable(False, False)

    # Etiquetas para inicio de sesión de administrador
    label_admin_usuario = tk.Label(ventana_admin, text="Nombre de usuario:")
    label_admin_usuario.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    label_admin_contraseña = tk.Label(ventana_admin, text="Contraseña:")
    label_admin_contraseña.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Campos de entrada para inicio de sesión de administrador
    global entry_admin_usuario, entry_admin_contraseña
    entry_admin_usuario = tk.Entry(ventana_admin)
    entry_admin_usuario.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    entry_admin_contraseña = tk.Entry(ventana_admin, show="*")
    entry_admin_contraseña.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    def admin_login():
        nombre_usuario = entry_admin_usuario.get()
        contraseña = entry_admin_contraseña.get()

        if nombre_usuario == "admin" and contraseña == "admin123":
            messagebox.showinfo("Éxito", "Acceso al panel de administrador concedido.")
            ventana_admin.destroy()
            abrir_ventana_panel_admin()
        else:
            messagebox.showerror("Error", "Nombre de usuario o contraseña incorrectos.")

    # Botón de inicio de sesión de administrador
    boton_admin_login = tk.Button(ventana_admin, text="Iniciar Sesión", command=admin_login)
    boton_admin_login.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

def abrir_ventana_panel_admin():
    global ventana_panel_admin # Declara la variable como global
    ventana_panel_admin = tk.Toplevel(ventana_inicio)
    ventana_panel_admin.title("Panel de Administrador")
    ventana_panel_admin.geometry("400x350")  # Ajuste de tamaño
    ventana_panel_admin.resizable(False, False)

    # --- Frame para el Listbox de productos ---
    frame_productos_admin = tk.Frame(ventana_panel_admin)
    frame_productos_admin.pack(pady=20)

    # --- Listbox para mostrar productos ---
    global listbox_productos_admin
    listbox_productos_admin = tk.Listbox(frame_productos_admin, width=50, height=10)
    listbox_productos_admin.pack(side=tk.LEFT)

    # --- Agregar productos al Listbox ---
    actualizar_listbox_productos_admin()

    # --- Frame para los botones ---
    frame_botones = tk.Frame(frame_productos_admin)
    frame_botones.pack(side=tk.LEFT)

    # --- Botones para agregar, eliminar y editar productos ---
    boton_agregar_producto = tk.Button(frame_botones, text="Agregar producto", command=lambda: agregar_producto_admin(listbox_productos_admin))
    boton_agregar_producto.pack(side=tk.LEFT, padx=5)  # Usando side=tk.LEFT
    boton_eliminar_producto = tk.Button(frame_botones, text="Eliminar producto", command=lambda: eliminar_producto_admin(listbox_productos_admin))
    boton_eliminar_producto.pack(side=tk.LEFT, padx=5)  # Usando side=tk.LEFT
    boton_editar_producto = tk.Button(frame_botones, text="Editar producto", command=editar_producto_admin)
    boton_editar_producto.pack(side=tk.LEFT, padx=5)  # Usando side=tk.LEFT

def abrir_ventana_productos():
    ventana_productos = tk.Toplevel(ventana_inicio)
    ventana_productos.title("Productos")
    ventana_productos.geometry("400x300")
    ventana_productos.resizable(False, False)

    # --- Frame para el Listbox de productos ---
    frame_productos = tk.Frame(ventana_productos)
    frame_productos.pack(pady=20)

    # --- Listbox para mostrar productos ---
    listbox_productos = tk.Listbox(frame_productos, width=50, height=10)
    listbox_productos.pack(side=tk.LEFT)

    # --- Agregar productos al Listbox ---
    for producto in productos:
        listbox_productos.insert(tk.END, producto["nombre"])

def abrir_ventana_principal(nombre_usuario):
    global ventana_panel_admin # Declara la variable como global
    global carrito, label_total, agregar_producto, eliminar_producto, vaciar_carrito  # Agrega las funciones del carrito como globales
    ventana_principal = tk.Toplevel(ventana_inicio)
    ventana_principal.title("Bienvenido")
    ventana_principal.geometry("600x400")  # Tamaño ajustado para el carrito
    ventana_principal.resizable(False, False)

    label_bienvenida = tk.Label(ventana_principal, text=f"Bienvenido, {nombre_usuario}!", font=("Arial", 16))
    label_bienvenida.pack(pady=20)

    # --- Carrito de compras ---
    carrito = []  # Inicializar la lista del carrito
    label_total = tk.Label(ventana_principal, text="Total: $0.00", font=("Arial", 14))
    label_total.pack()

    # --- Botón para ver productos ---
    boton_ver_productos = tk.Button(ventana_principal, text="Ver productos", command=abrir_ventana_productos)
    boton_ver_productos.pack(pady=10)

    # --- Frame para el Listbox de productos ---
    frame_productos = tk.Frame(ventana_principal)
    frame_productos.pack()

    # --- Listbox para mostrar productos ---
    listbox_productos = tk.Listbox(frame_productos, width=50, height=10)
    listbox_productos.pack(side=tk.LEFT)

    # --- Agregar productos al Listbox ---
    for producto in productos:
        listbox_productos.insert(tk.END, producto["nombre"])

    # --- Frame para los botones ---
    frame_botones = tk.Frame(frame_productos)
    frame_botones.pack(side=tk.LEFT)

    # --- Botones para el carrito ---
    boton_agregar = tk.Button(frame_botones, text="Agregar al carrito", command=lambda: agregar_producto(listbox_productos))
    boton_agregar.pack(side=tk.LEFT, padx=5)  # Usando side=tk.LEFT
    boton_eliminar = tk.Button(frame_botones, text="Eliminar del carrito", command=eliminar_producto)
    boton_eliminar.pack(side=tk.LEFT, padx=5)  # Usando side=tk.LEFT

    # --- Frame para el Listbox del carrito ---
    frame_carrito = tk.Frame(ventana_principal)
    frame_carrito.pack(pady=20)

    # --- Listbox para el carrito de compras ---
    listbox_carrito = tk.Listbox(frame_carrito, width=50, height=10)
    listbox_carrito.pack(side=tk.LEFT)

    # --- Frame para el botón de vaciar carrito ---
    frame_vaciar = tk.Frame(frame_carrito)
    frame_vaciar.pack(side=tk.LEFT)

    # --- Botón para vaciar el carrito ---
    boton_vaciar = tk.Button(frame_vaciar, text="Vaciar carrito", command=vaciar_carrito)
    boton_vaciar.pack()

# --- Ventana de inicio de sesión ---
ventana_inicio = tk.Tk()
ventana_inicio.title("Inicio de Sesión")
ventana_inicio.geometry("400x300")
ventana_inicio.resizable(False, False)

# --- Título de la pantalla de inicio ---
titulo = tk.Label(ventana_inicio, text="Streaming.Vzla", font=("Arial", 24), pady=10)
titulo.grid(row=0, column=0, columnspan=2)

# --- Contenedor para el formulario de inicio de sesión ---
frame_login = tk.Frame(ventana_inicio)
frame_login.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# --- Etiquetas para inicio de sesión ---
label_usuario = tk.Label(frame_login, text="Nombre de usuario:")
label_usuario.grid(row=0, column=0, padx=5, pady=5, sticky="w")
label_contraseña = tk.Label(frame_login, text="Contraseña:")
label_contraseña.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# --- Campos de entrada para inicio de sesión ---
global entry_usuario, entry_contraseña
entry_usuario = tk.Entry(frame_login)
entry_usuario.grid(row=0, column=1, padx=5, pady=5, sticky="w")
entry_contraseña = tk.Entry(frame_login, show="*")
entry_contraseña.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# --- Botón de inicio de sesión ---
boton_login = tk.Button(frame_login, text="Iniciar Sesión", command=iniciar_sesion)
boton_login.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# --- Botón de registro ---
boton_registro = tk.Button(ventana_inicio, text="Registrarse", command=abrir_ventana_registro)
boton_registro.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# --- Botón de administrador ---
boton_admin = tk.Button(ventana_inicio, text="Administrador", command=abrir_ventana_admin)
boton_admin.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# --- Iniciar el bucle principal de la ventana ---
ventana_inicio.mainloop()