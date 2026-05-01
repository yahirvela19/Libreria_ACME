"""
=============================================================
 LIBRERÍA ACME — Sistema de Gestión de Libros
 Archivo : libreria_acme.py
 Descripción: Sistema con GUI (Tkinter) y base de datos SQLite
              para el control de stock y consulta de libros.
 
 DIVISIÓN DEL TRABAJO:
 ┌──────────┬────────────────────────────────────────────────┐
 │ Miembro  │ Responsabilidad                                │
 ├──────────┼────────────────────────────────────────────────┤
 │    1     │ Base de datos (BaseDeDatosLibros)              │
 │    2     │ Estilos/colores + Widget TablaLibros           │
 │    3     │ Ventana principal + Login de empleado          │
 │    4     │ Panel de empleado (CRUD completo)              │
 │    5     │ Ventana de cliente (búsqueda) + main()         │
 └──────────┴────────────────────────────────────────────────┘
=============================================================
"""
 
# ─────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────
 
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
 
 
# =============================================================
#  SECCIÓN MIEMBRO 1 — CAPA DE BASE DE DATOS
#  Responsable de: conexión SQLite, creación de tablas,
#  datos de muestra, y todos los métodos CRUD.
# =============================================================
 
class BaseDeDatosLibros:
    """Maneja toda la interacción con la base de datos SQLite."""
 
    def __init__(self, nombre_archivo="libreria_acme.db"):
        self.nombre_archivo = nombre_archivo
        self.conexion = None
        self.cursor = None
        self._conectar()
        self.crear_tablas()
 
    def _conectar(self):
        try:
            self.conexion = sqlite3.connect(self.nombre_archivo)
            self.conexion.row_factory = sqlite3.Row
            self.cursor = self.conexion.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"No se pudo conectar a la base de datos: {e}")
 
    def crear_tablas(self):
        try:
            self.cursor.executescript('''
                CREATE TABLE IF NOT EXISTS libros (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT    NOT NULL,
                    autor  TEXT    NOT NULL,
                    genero TEXT    NOT NULL,
                    isbn   TEXT    UNIQUE NOT NULL,
                    stock  INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS empleados (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario    TEXT UNIQUE NOT NULL,
                    contrasena TEXT NOT NULL,
                    nombre     TEXT NOT NULL
                );
            ''')
            # Empleados por defecto
            self.cursor.execute(
                "INSERT OR IGNORE INTO empleados (usuario, contrasena, nombre) VALUES (?,?,?)",
                ("admin", "admin123", "Administrador")
            )
            self.cursor.execute(
                "INSERT OR IGNORE INTO empleados (usuario, contrasena, nombre) VALUES (?,?,?)",
                ("empleado1", "12345", "Juan Perez")
            )
            # Libros de muestra
            libros_muestra = [
                ("Cien Años de Soledad", "Gabriel García Márquez", "Novela", "978-84-376-0494-7", 5),
                ("El Quijote",           "Miguel de Cervantes",   "Clásico","978-84-670-5066-0", 3),
                ("1984",                 "George Orwell",         "Distopía","978-84-233-4095-3", 4),
                ("El Principito",        "Antoine de Saint-Exupéry","Infantil","978-84-261-4777-9", 7),
                ("Sapiens",              "Yuval Noah Harari",     "Historia","978-84-9942-604-5", 2),
            ]
            self.cursor.executemany(
                "INSERT OR IGNORE INTO libros (titulo, autor, genero, isbn, stock) VALUES (?,?,?,?,?)",
                libros_muestra
            )
            self.conexion.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al crear tablas: {e}")
 
    # ── CRUD ──────────────────────────────────
 
    def agregar_libro(self, titulo, autor, genero, isbn, stock=1):
        try:
            self.cursor.execute(
                "INSERT INTO libros (titulo, autor, genero, isbn, stock) VALUES (?,?,?,?,?)",
                (titulo, autor, genero, isbn, stock)
            )
            self.conexion.commit()
            return True, "Libro agregado exitosamente."
        except sqlite3.IntegrityError:
            return False, "El ISBN ya existe en la base de datos."
        except sqlite3.Error as e:
            return False, f"Error al agregar libro: {e}"
 
    def editar_libro(self, libro_id, titulo, autor, genero, isbn, stock):
        try:
            self.cursor.execute(
                "UPDATE libros SET titulo=?, autor=?, genero=?, isbn=?, stock=? WHERE id=?",
                (titulo, autor, genero, isbn, stock, libro_id)
            )
            self.conexion.commit()
            return True, "Libro actualizado exitosamente."
        except sqlite3.IntegrityError:
            return False, "El ISBN ya pertenece a otro libro."
        except sqlite3.Error as e:
            return False, f"Error al editar libro: {e}"
 
    def borrar_libro(self, libro_id):
        try:
            self.cursor.execute("DELETE FROM libros WHERE id=?", (libro_id,))
            self.conexion.commit()
            if self.cursor.rowcount == 0:
                return False, "Libro no encontrado."
            return True, "Libro eliminado exitosamente."
        except sqlite3.Error as e:
            return False, f"Error al borrar libro: {e}"
 
    def buscar_libros(self, criterio, valor):
        columnas = {"titulo": "titulo", "autor": "autor", "genero": "genero", "isbn": "isbn"}
        col = columnas.get(criterio.lower())
        if not col:
            return []
        try:
            self.cursor.execute(
                f"SELECT * FROM libros WHERE {col} LIKE ? ORDER BY titulo",
                (f"%{valor}%",)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []
 
    def obtener_todos_libros(self):
        try:
            self.cursor.execute("SELECT * FROM libros ORDER BY titulo")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []
 
    def obtener_libro_por_id(self, libro_id):
        try:
            self.cursor.execute("SELECT * FROM libros WHERE id=?", (libro_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None
 
    def verificar_empleado(self, usuario, contrasena):
        try:
            self.cursor.execute(
                "SELECT nombre FROM empleados WHERE usuario=? AND contrasena=?",
                (usuario, contrasena)
            )
            row = self.cursor.fetchone()
            return row["nombre"] if row else None
        except sqlite3.Error:
            return None
 
    def cerrar(self):
        if self.conexion:
            self.conexion.close()
 
 
# =============================================================
#  SECCIÓN MIEMBRO 2 — ESTILOS Y WIDGET TABLA
#  Responsable de: definir el diccionario COLORES,
#  y construir el widget reutilizable TablaLibros.
# =============================================================
 
# Diccionario global de colores de la aplicación
# Debe contener al menos: primario, secundario, fondo, blanco,
# texto, texto_claro, exito, error, hover, fila_par, fila_impar, borde
COLORES = {}
 
 
class TablaLibros(tk.Frame):
    """
    Widget reutilizable que muestra una tabla de libros con scroll.
    Se usa tanto en la ventana de empleado como en la de cliente.
    """
 
    COLUMNAS   = ("id", "titulo", "autor", "genero", "isbn", "stock")
    ENCABEZADOS = ("ID", "Título", "Autor", "Género", "ISBN", "Stock")
    ANCHOS     = (40, 200, 160, 100, 140, 50)
 
    def __init__(self, parent, mostrar_stock=True, **kw):
        super().__init__(parent, **kw)
        self._construir(mostrar_stock)
 
    def _construir(self, mostrar_stock):
        """
        Configura el estilo del Treeview con ttk.Style,
        agrega scrollbars vertical y horizontal,
        y define las etiquetas de color para filas alternas.
        El parámetro mostrar_stock oculta la columna 'stock'
        cuando es False (vista de cliente).
        """
        pass
 
    def cargar(self, libros):
        """
        Recibe una lista de dicts y los muestra en la tabla.
        Aplica colores alternos (fila_par / fila_impar).
        """
        pass
 
    def seleccionado_id(self):
        """
        Retorna el id (int) del libro seleccionado en la tabla,
        o None si no hay ninguno seleccionado.
        """
        pass
 
 
# =============================================================
#  SECCIÓN MIEMBRO 3 — VENTANA PRINCIPAL Y LOGIN
#  Responsable de: pantalla de selección de perfil (Cliente /
#  Empleado) y ventana de autenticación de empleados.
# =============================================================
 
class VentanaPrincipal(tk.Tk):
    """
    Ventana raíz de la aplicación.
    Muestra el logo, nombre y dos botones: Cliente y Empleado.
    """
 
    def __init__(self):
        super().__init__()
        self.db = BaseDeDatosLibros()
 
    def _centrar(self):
        """Centra la ventana en la pantalla."""
        pass
 
    def _construir_ui(self):
        """
        Construye el encabezado con logo/nombre,
        los botones de selección de perfil y el footer.
        """
        pass
 
    def _abrir_cliente(self):
        """Instancia y abre VentanaCliente."""
        pass
 
    def _abrir_login(self):
        """Instancia y abre VentanaLogin."""
        pass
 
    def destroy(self):
        """Cierra la conexión a la BD antes de destruir la ventana."""
        pass
 
 
class VentanaLogin(tk.Toplevel):
    """
    Ventana modal de autenticación para empleados.
    Solicita usuario y contraseña, verifica contra la BD
    y abre VentanaEmpleado si las credenciales son correctas.
    """
 
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.parent = parent
 
    def _centrar(self):
        """Centra la ventana en la pantalla."""
        pass
 
    def _construir_ui(self):
        """
        Construye el encabezado, los campos de usuario/contraseña,
        la etiqueta de error y el botón Ingresar.
        Vincula Enter en el campo de contraseña para llamar a _verificar.
        """
        pass
 
    def _verificar(self):
        """
        Lee usuario y contraseña, llama a db.verificar_empleado().
        Si es correcto: cierra esta ventana y abre VentanaEmpleado.
        Si es incorrecto: muestra mensaje de error en la etiqueta.
        Maneja excepciones con messagebox.showerror.
        """
        pass
 
 
# =============================================================
#  SECCIÓN MIEMBRO 4 — PANEL DE EMPLEADO (CRUD)
#  Responsable de: panel con barra de búsqueda, tabla y
#  botones Agregar / Editar / Borrar, y el diálogo de formulario.
# =============================================================
 
class DialogoLibro(tk.Toplevel):
    """
    Ventana modal para agregar o editar un libro.
    Si recibe 'libro' (dict), precarga los campos para edición.
    Si 'libro' es None, funciona como formulario de nuevo libro.
    Al guardar exitosamente llama a on_success() para refrescar la tabla.
    """
 
    def __init__(self, parent, db, libro=None, on_success=None):
        super().__init__(parent)
        self.db = db
        self.libro = libro
        self.on_success = on_success
 
    def _centrar(self):
        """Centra la ventana en la pantalla."""
        pass
 
    def _campo(self, parent, label, row, valor=""):
        """
        Crea una fila con Label + Entry dentro de 'parent' en la fila 'row'.
        Retorna el StringVar asociado al Entry.
        """
        pass
 
    def _construir_ui(self):
        """
        Construye el encabezado, los 5 campos (titulo, autor, genero,
        isbn, stock), la etiqueta de mensaje de error y los botones
        Cancelar / Guardar.
        """
        pass
 
    def _guardar(self):
        """
        Valida que todos los campos estén llenos y que stock sea int >= 0.
        Llama a db.editar_libro() o db.agregar_libro() según corresponda.
        Muestra messagebox de éxito o error según el resultado.
        """
        pass
 
 
class VentanaEmpleado(tk.Toplevel):
    """
    Panel principal del empleado autenticado.
    Contiene: encabezado con nombre del empleado, barra de búsqueda
    con radiobuttons de criterio, TablaLibros y barra de acciones
    (Agregar, Editar, Borrar, Cerrar sesión).
    """
 
    def __init__(self, parent, db, nombre_empleado):
        super().__init__(parent)
        self.db = db
        self.nombre_empleado = nombre_empleado
 
    def _centrar(self):
        """Centra la ventana en la pantalla."""
        pass
 
    def _construir_ui(self):
        """
        Construye: encabezado con nombre, barra de búsqueda
        (criterio + campo + botón Buscar + botón Mostrar todos),
        TablaLibros con mostrar_stock=True, y barra de acciones.
        """
        pass
 
    def _cargar_todos(self):
        """Llama a db.obtener_todos_libros() y actualiza la tabla."""
        pass
 
    def _buscar(self):
        """
        Lee criterio y valor del campo de búsqueda.
        Llama a db.buscar_libros() y actualiza la tabla.
        Si el campo está vacío, llama a _cargar_todos().
        """
        pass
 
    def _agregar(self):
        """Abre DialogoLibro sin libro preseleccionado."""
        pass
 
    def _editar(self):
        """
        Obtiene el id seleccionado en la tabla.
        Si hay selección, obtiene el libro y abre DialogoLibro con él.
        Si no hay selección, muestra aviso con messagebox.
        """
        pass
 
    def _borrar(self):
        """
        Obtiene el id seleccionado.
        Pide confirmación con messagebox.askyesno mostrando el título.
        Si confirma, llama a db.borrar_libro() y recarga la tabla.
        """
        pass
 
 
# =============================================================
#  SECCIÓN MIEMBRO 5 — VENTANA CLIENTE Y PUNTO DE ENTRADA
#  Responsable de: vista de solo-lectura para clientes
#  (búsqueda sin edición) y el bloque main para iniciar la app.
# =============================================================
 
class VentanaCliente(tk.Toplevel):
    """
    Vista de catálogo para clientes.
    SOLO permite buscar libros — sin botones de modificación.
    Muestra columnas: ID, Título, Autor, Género, ISBN (sin Stock).
    """
 
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
 
    def _centrar(self):
        """Centra la ventana en la pantalla."""
        pass
 
    def _construir_ui(self):
        """
        Construye: encabezado de bienvenida, barra de búsqueda
        con criterios, TablaLibros con mostrar_stock=False,
        etiqueta de estado y botón Cerrar.
        NO incluir ningún botón de Agregar, Editar ni Borrar.
        """
        pass
 
    def _cargar_todos(self):
        """Carga y muestra todos los libros en la tabla."""
        pass
 
    def _buscar(self):
        """
        Lee criterio y valor, llama a db.buscar_libros()
        y actualiza la tabla con los resultados.
        """
        pass
 
 
def main():
    """
    Punto de entrada de la aplicación.
    Instancia VentanaPrincipal y llama a mainloop().
    Envuelve en try/except para manejar errores fatales.
    """
    pass
 
 
if __name__ == "__main__":
    main()
 