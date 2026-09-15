"""Administrador de biblioteca conectado a MySQL.

Uso:
	pip install -r requirements.txt
	python bibioteca.py

La conexion puede configurarse con DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
y DB_NAME. Por defecto apunta a biblioteca_db en localhost.
"""

import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

try:
	import mysql.connector
	from mysql.connector import Error
except ImportError:
	mysql = None
	Error = Exception


DB_CONFIG = {
	"host": os.getenv("DB_HOST", "localhost"),
	"port": int(os.getenv("DB_PORT", "3306")),
	"user": os.getenv("DB_USER", "root"),
	"password": os.getenv("DB_PASSWORD", "0311"),
	"database": os.getenv("DB_NAME", "biblioteca_db"),
}

ADMIN_USER = os.getenv("APP_USER", "Admin1")
ADMIN_PASSWORD = os.getenv("APP_PASSWORD", "contraseña123")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.ico")


TABLES = {
	"Autores": {
		"table": "autores", "id": "id_autor",
		"columns": ["nombre", "nacionalidad"],
	},
	"Categorias": {
		"table": "categorias", "id": "id_categoria",
		"columns": ["nombre"],
	},
	"Editoriales": {
		"table": "editoriales", "id": "id_editorial",
		"columns": ["nombre", "ciudad"],
	},
	"Usuarios": {
		"table": "usuarios", "id": "id_usuario",
		"columns": ["nombres", "apellidos", "documento", "telefono",
					 "correo", "direccion"],
	},
	"Libros": {
		"table": "libros", "id": "id_libro",
		"columns": ["titulo", "isbn", "anio_publicacion", "id_autor",
					 "id_editorial", "id_categoria"],
	},
	"Prestamos": {
		"table": "prestamos", "id": "id_prestamo",
		"columns": ["id_usuario", "fecha_prestamo", "fecha_devolucion",
					 "estado"],
	},
	"Detalle de prestamos": {
		"table": "detalle_prestamo", "id": "id_detalle",
		"columns": ["id_prestamo", "id_libro", "cantidad"],
	},
	"Auditoria": {
		"table": "auditoria", "id": "id_auditoria",
		"columns": ["tabla_afectada", "operacion", "id_registro",
					 "fecha", "descripcion"],
		"readonly": True,
	},
}


class Database:
	"""Pequena capa de acceso parametrizado para la aplicacion."""

	# Inicializa la conexion
	def __init__(self):
		self.connection = None

	# Conecta con MySQL
	def connect(self):
		if mysql is None:
			raise RuntimeError("Falta instalar mysql-connector-python.")
		self.connection = mysql.connector.connect(**DB_CONFIG)

	# Cierra la conexion
	def close(self):
		if self.connection and self.connection.is_connected():
			self.connection.close()

	# Ejecuta consultas SQL
	def query(self, sql, params=(), fetch=True):
		cursor = self.connection.cursor(dictionary=True)
		try:
			cursor.execute(sql, params)
			if fetch:
				return cursor.fetchall()
			self.connection.commit()
			return cursor.lastrowid
		finally:
			cursor.close()

	# Cuenta registros existentes
	def count(self, table):
		result = self.query(f"SELECT COUNT(*) AS total FROM `{table}`")
		return result[0]["total"]


class LoginWindow(tk.Tk):
	"""Pantalla de acceso previa al sistema de administracion."""

	# Prepara la ventana
	def __init__(self):
		super().__init__()
		self.title("Biblioteca Comfenalco | Iniciar sesion")
		self._set_icon()
		self.geometry("760x480")
		self.resizable(False, False)
		self.authenticated = False
		self.user_var = tk.StringVar()
		self.password_var = tk.StringVar()
		self.show_password = tk.BooleanVar(value=False)
		self._build()
		self.protocol("WM_DELETE_WINDOW", self.destroy)

	# Configura el icono
	def _set_icon(self):
		if os.path.exists(ICON_PATH):
			try:
				self.iconbitmap(ICON_PATH)
			except tk.TclError:
				pass

	# Construye el formulario
	def _build(self):
		left = tk.Frame(self, bg="#403765", width=330)
		left.pack(side="left", fill="y")
		left.pack_propagate(False)
		tk.Label(left, text="BIBLIOTECA", background="#403765", foreground="white",
				 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=30, pady=(62, 0))
		tk.Label(left, text="COMFENALCO", background="#403765", foreground="#d9d2ee",
				 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=32, pady=(0, 34))
		tk.Label(left, text="Sistema de Gestion\nde Biblioteca", background="#403765",
				 foreground="white", justify="left", font=("Segoe UI", 15, "bold")).pack(
				 anchor="w", padx=30)
		tk.Label(left, text="LIBROS  |  USUARIOS  |  PRESTAMOS", background="#403765",
				 foreground="#bdb4d9", font=("Segoe UI", 8)).pack(anchor="w", padx=30, pady=(22, 0))

		right = tk.Frame(self, bg="#f2f1f8")
		right.pack(side="left", fill="both", expand=True)
		tk.Label(right, text="INICIAR SESION", background="#f2f1f8", foreground="#332b55",
				 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=42, pady=(70, 6))
		tk.Label(right, text="Ingresa tus credenciales para continuar", background="#f2f1f8",
				 foreground="#657080", font=("Segoe UI", 10)).pack(anchor="w", padx=42, pady=(0, 28))
		form = tk.Frame(right, bg="#f2f1f8")
		form.pack(fill="x", padx=42)
		tk.Label(form, text="Usuario", background="#f2f1f8", foreground="#374052").pack(anchor="w")
		user_entry = ttk.Entry(form, textvariable=self.user_var, width=36)
		user_entry.pack(fill="x", pady=(5, 15), ipady=5)
		tk.Label(form, text="Contraseña", background="#f2f1f8", foreground="#374052").pack(anchor="w")
		self.password_entry = ttk.Entry(form, textvariable=self.password_var, show="*", width=36)
		self.password_entry.pack(fill="x", pady=(5, 4), ipady=5)
		tk.Checkbutton(form, text="Mostrar contraseña", variable=self.show_password,
				 command=self._toggle_password).pack(anchor="w")
		ttk.Button(form, text="INGRESAR", style="Accent.TButton",
				 command=self._login).pack(fill="x", pady=(24, 8), ipady=5)
		tk.Button(form, text="SALIR", command=self.destroy).pack(fill="x", ipady=4)
		self.message = ttk.Label(form, text="", foreground="#bd4b42", background="#f2f1f8")
		self.message.pack(anchor="w", pady=(10, 0))
		user_entry.focus_set()
		self.bind("<Return>", lambda _event: self._login())

	# Cambia visibilidad contraseña
	def _toggle_password(self):
		self.password_entry.configure(show="" if self.show_password.get() else "*")

	# Valida las credenciales
	def _login(self):
		if self.user_var.get().strip() == ADMIN_USER and self.password_var.get() == ADMIN_PASSWORD:
			self.authenticated = True
			self.destroy()
		else:
			self.message.configure(text="Usuario o contraseña incorrectos")
			self.password_var.set("")
			self.password_entry.focus_set()


class LibraryApp(tk.Tk):
	"""Interfaz grafica para administrar todas las tablas del esquema."""

	# Inicializa la aplicación
	def __init__(self):
		super().__init__()
		self.title("Biblioteca Comfenalco | Sistema de Gestion")
		self._set_icon()
		self.geometry("1280x760")
		self.minsize(1050, 650)
		self.db = Database()
		self.tabs = {}
		self._configure_style()
		self._build_header()
		self._build_tabs()
		self.protocol("WM_DELETE_WINDOW", self._close)
		self.after(100, self._connect)

	# Configura el icono
	def _set_icon(self):
		if os.path.exists(ICON_PATH):
			try:
				self.iconbitmap(ICON_PATH)
			except tk.TclError:
				pass

	# Configura estilos visuales
	def _configure_style(self):
		style = ttk.Style(self)
		style.theme_use("clam")
		style.configure("TFrame", background="#f2f1f8")
		style.configure("TLabel", background="#f2f1f8", foreground="#26354a")
		style.configure("Header.TFrame", background="#332b55")
		style.configure("Title.TLabel", background="#332b55", foreground="white",
						font=("Segoe UI", 20, "bold"))
		style.configure("Subtitle.TLabel", background="#332b55", foreground="#d8d3e8",
						font=("Segoe UI", 10))
		style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
		style.configure("CardNumber.TLabel", background="white", foreground="#332b55",
						font=("Segoe UI", 20, "bold"))
		style.configure("CardText.TLabel", background="white", foreground="#557080",
						font=("Segoe UI", 10))
		style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
		style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
		style.configure("Accent.TButton", background="#d66b3d", foreground="white",
						font=("Segoe UI", 9, "bold"))
		style.configure("Insert.TButton", background="#19a86b", foreground="white",
						font=("Segoe UI", 9, "bold"))
		style.configure("Update.TButton", background="#e59b19", foreground="white",
						font=("Segoe UI", 9, "bold"))
		style.configure("Delete.TButton", background="#d9544d", foreground="white",
						font=("Segoe UI", 9, "bold"))
		style.configure("Clear.TButton", background="#354b63", foreground="white",
						font=("Segoe UI", 9, "bold"))
		style.configure("Nav.TButton", background="#403765", foreground="white",
						anchor="w", padding=(14, 9), font=("Segoe UI", 9))
		style.map("Nav.TButton", background=[("active", "#574d82")])

	# Construye el encabezado
	def _build_header(self):
		header = ttk.Frame(self, style="Header.TFrame", padding=(24, 18))
		header.pack(fill="x")
		ttk.Label(header, text="BIBLIOTECA", style="Title.TLabel").pack(anchor="w")
		ttk.Label(header, text="Panel de administracion y control de prestamos",
				  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
		self.status = ttk.Label(header, text="Conectando...", style="Subtitle.TLabel")
		self.status.pack(anchor="e")

	# Construye las pestañas
	def _build_tabs(self):
		workspace = ttk.Frame(self, style="TFrame")
		workspace.pack(fill="both", expand=True)
		navigation = tk.Frame(workspace, bg="#403765", width=190)
		navigation.pack(side="left", fill="y")
		navigation.pack_propagate(False)
		tk.Label(navigation, text="MENU PRINCIPAL", background="#403765",
				 foreground="#c9c2e5", font=("Segoe UI", 9, "bold")).pack(
				 anchor="w", padx=14, pady=(22, 8))

		notebook = ttk.Notebook(workspace)
		notebook.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
		style = ttk.Style(self)
		style.layout("Hidden.TNotebook.Tab", [])
		notebook.configure(style="Hidden.TNotebook")
		dashboard = ttk.Frame(notebook, padding=18)
		notebook.add(dashboard, text="Resumen")
		self._add_nav_button(navigation, "Dashboard", notebook, dashboard)
		self._build_dashboard(dashboard)
		for name, config in TABLES.items():
			frame = ttk.Frame(notebook, padding=10)
			notebook.add(frame, text=name)
			self.tabs[name] = TableView(self, frame, name, config)
			self._add_nav_button(navigation, name, notebook, frame)

	# Agrega botón navegable
	def _add_nav_button(self, parent, label, notebook, frame):
		ttk.Button(parent, text="  " + label, style="Nav.TButton",
				 command=lambda: notebook.select(frame)).pack(fill="x", padx=8, pady=2)

	# Construye el resumen
	def _build_dashboard(self, parent):
		ttk.Label(parent, text="Vista general", font=("Segoe UI", 18, "bold"),
				  foreground="#17324d").pack(anchor="w")
		ttk.Label(parent, text="Consulta el estado actual de tu biblioteca.",
				  foreground="#557080").pack(anchor="w", pady=(2, 18))
		cards = ttk.Frame(parent)
		cards.pack(fill="x")
		self.summary_values = {}
		for label, table in (("Libros", "libros"), ("Usuarios", "usuarios"),
							 ("Prestamos activos", "prestamos"), ("Autores", "autores")):
			card = ttk.Frame(cards, style="Card.TFrame", padding=16)
			card.pack(side="left", fill="x", expand=True, padx=(0, 12))
			value = ttk.Label(card, text="-", style="CardNumber.TLabel")
			value.pack(anchor="w")
			ttk.Label(card, text=label, style="CardText.TLabel").pack(anchor="w")
			self.summary_values[table] = value
		chart_frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
		chart_frame.pack(fill="both", expand=True, pady=(24, 0))
		ttk.Label(chart_frame, text="REGISTROS POR TABLA", font=("Segoe UI", 12, "bold"),
				  foreground="#332b55").pack(anchor="w")
		ttk.Label(chart_frame, text="Cantidad de usuarios, libros, prestamos y demas registros.",
				  foreground="#557080").pack(anchor="w", pady=(2, 8))
		self.chart_canvas = tk.Canvas(chart_frame, height=310, background="white",
								 highlightthickness=0)
		self.chart_canvas.pack(fill="both", expand=True)
		self.chart_canvas.bind("<Configure>", lambda _event: self._draw_chart())

	# Dibuja barras estadísticas
	def _draw_chart(self):
		if not hasattr(self, "chart_canvas"):
			return
		canvas = self.chart_canvas
		canvas.delete("all")
		data = getattr(self, "chart_data", {})
		if not data:
			canvas.create_text(20, 30, anchor="w", text="Conectando con la base de datos...",
							fill="#557080", font=("Segoe UI", 10))
			return
		width = max(canvas.winfo_width(), 600)
		height = max(canvas.winfo_height(), 260)
		left, right, top, bottom = 52, 22, 25, 54
		plot_height = height - top - bottom
		maximum = max(max(data.values()), 1)
		step = (width - left - right) / len(data)
		bar_width = min(58, step * 0.58)
		canvas.create_line(left, top, left, height - bottom, fill="#b7c0cc")
		canvas.create_line(left, height - bottom, width - right, height - bottom,
						fill="#b7c0cc")
		for index, (label, amount) in enumerate(data.items()):
			x_center = left + step * index + step / 2
			bar_height = (amount / maximum) * plot_height if amount else 2
			x1 = x_center - bar_width / 2
			y1 = height - bottom - bar_height
			x2 = x_center + bar_width / 2
			y2 = height - bottom
			canvas.create_rectangle(x1, y1, x2, y2, fill="#6b8fd3", outline="#4969a5")
			canvas.create_text(x_center, y1 - 9, text=str(amount), fill="#332b55",
							font=("Segoe UI", 9, "bold"))
			canvas.create_text(x_center, height - bottom + 14, text=label, fill="#557080",
							font=("Segoe UI", 8))

	# Abre la conexión
	def _connect(self):
		try:
			self.db.connect()
			self.status.configure(text=f"Conectado a {DB_CONFIG['database']}")
			self.refresh_all()
		except Exception as exc:
			self.status.configure(text="Sin conexion")
			messagebox.showerror("Conexion no disponible",
								 f"No se pudo conectar a MySQL.\n\n{exc}\n\n"
								 "Configura DB_USER y DB_PASSWORD e intenta de nuevo.")

	# Actualiza todos los datos
	def refresh_all(self):
		if not self.db.connection:
			return
		chart_tables = (
			("Usuarios", "usuarios"), ("Libros", "libros"), ("Autores", "autores"),
			("Categorias", "categorias"), ("Editoriales", "editoriales"),
			("Prestamos", "prestamos"), ("Detalles", "detalle_prestamo"),
			("Auditoria", "auditoria"),
		)
		self.chart_data = {label: self.db.count(table) for label, table in chart_tables}
		self._draw_chart()
		for name, table in (("libros", "libros"), ("usuarios", "usuarios"),
							("autores", "autores")):
			self.summary_values[table].configure(text=str(self.db.count(name)))
		active = self.db.query("SELECT COUNT(*) AS total FROM prestamos "
							   "WHERE estado IN ('PRESTADO', 'ATRASADO')")[0]["total"]
		self.summary_values["prestamos"].configure(text=str(active))
		for view in self.tabs.values():
			view.refresh()

	# Cierra la aplicación
	def _close(self):
		self.db.close()
		self.destroy()


class TableView:
	# Inicializa la tabla
	def __init__(self, app, parent, name, config):
		self.app = app
		self.parent = parent
		self.name = name
		self.config = config
		self.search = tk.StringVar()
		self.selected_id = None
		self.entries = {}
		self.fullscreen = False
		self._build()

	# Construye la vista
	def _build(self):
		self.title_label = ttk.Label(self.parent, text=f"Gestion de {self.name}",
				  font=("Segoe UI", 16, "bold"), foreground="#332b55")
		self.title_label.pack(anchor="w")
		self.subtitle_label = ttk.Label(self.parent,
				  text="Completa el formulario y usa las acciones para administrar los registros.",
				  foreground="#657080")
		self.subtitle_label.pack(anchor="w", pady=(2, 9))
		self.form = self._build_form()
		self.actions = self._build_actions()
		self.list_label = ttk.Label(self.parent, text="LISTADO DE REGISTROS",
				  font=("Segoe UI", 10, "bold"), foreground="#332b55")
		self.list_label.pack(anchor="w", pady=(10, 3))
		self.search_bar = ttk.Frame(self.parent)
		self.search_bar.pack(fill="x", pady=(0, 5))
		ttk.Label(self.search_bar, text="Buscar:").pack(side="left")
		search = ttk.Entry(self.search_bar, textvariable=self.search, width=30)
		search.pack(side="left", padx=7)
		search.bind("<Return>", lambda _event: self.refresh())
		ttk.Button(self.search_bar, text="Buscar", style="Accent.TButton",
				 command=self.refresh).pack(side="left")
		ttk.Button(self.search_bar, text="Mostrar todos", command=self.show_all).pack(side="left", padx=6)

		columns = [self.config["id"]] + self.config["columns"]
		self.body = ttk.Frame(self.parent)
		self.body.pack(fill="both", expand=True)
		self.tree = ttk.Treeview(self.body, columns=columns, show="headings", selectmode="browse")
		for column in columns:
			self.tree.heading(column, text=column.replace("_", " ").title())
			self.tree.column(column, width=125, minwidth=80)
		self.tree.column(self.config["id"], width=80)
		scrollbar = ttk.Scrollbar(self.body, orient="vertical", command=self.tree.yview)
		self.tree.configure(yscrollcommand=scrollbar.set)
		self.tree.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		self.tree.bind("<<TreeviewSelect>>", self._load_selected)
		self.close_fullscreen = ttk.Button(self.parent, text="✕", command=self.exit_fullscreen)

	# Construye campos formulario
	def _build_form(self):
		form = ttk.LabelFrame(self.parent, text="DATOS DEL REGISTRO", padding=(12, 8))
		form.pack(fill="x")
		for index, column in enumerate(self.config["columns"]):
			row = index // 2
			column_position = (index % 2) * 2
			ttk.Label(form, text=column.replace("_", " ").title()).grid(
				row=row, column=column_position, sticky="w", padx=(0, 7), pady=4)
			variable = tk.StringVar()
			self.entries[column] = variable
			if column == "estado":
				widget = ttk.Combobox(form, textvariable=variable,
						values=("PRESTADO", "DEVUELTO", "ATRASADO"),
						state="readonly", width=27)
			else:
				widget = ttk.Entry(form, textvariable=variable, width=30)
			widget.grid(row=row, column=column_position + 1, sticky="ew", padx=(0, 22), pady=4)
			form.columnconfigure(1, weight=1)
			form.columnconfigure(3, weight=1)
		if self.config.get("readonly"):
			self._set_form_state("disabled")
		return form

	# Construye botones acciones
	def _build_actions(self):
		actions = ttk.Frame(self.parent)
		actions.pack(fill="x", pady=(8, 3))
		if not self.config.get("readonly"):
			ttk.Button(actions, text="＋ INSERTAR", style="Insert.TButton",
					   command=self.insert_record).pack(side="left", padx=(0, 6))
			ttk.Button(actions, text="✎ ACTUALIZAR", style="Update.TButton",
					   command=self.update_record).pack(side="left", padx=3)
			ttk.Button(actions, text="▣ ELIMINAR", style="Delete.TButton",
					   command=self.delete_selected).pack(side="left", padx=3)
			ttk.Button(actions, text="⌫ LIMPIAR", style="Clear.TButton",
					   command=self.clear_form).pack(side="left", padx=3)
		ttk.Button(actions, text="SALIR", command=self.app._close).pack(side="right")
		return actions

	# Cambia estado campos
	def _set_form_state(self, state):
		for widget in self.parent.winfo_children():
			if isinstance(widget, ttk.LabelFrame):
				for child in widget.winfo_children():
					if isinstance(child, (ttk.Entry, ttk.Combobox)):
						child.configure(state=state)

	# Carga fila seleccionada
	def _load_selected(self, _event=None):
		selected = self.tree.selection()
		if not selected:
			return
		values = self.tree.item(selected[0], "values")
		self.selected_id = values[0]
		for index, column in enumerate(self.config["columns"], start=1):
			self.entries[column].set(values[index])

	# Limpia el formulario
	def clear_form(self):
		self.selected_id = None
		for variable in self.entries.values():
			variable.set("")
		for item in self.tree.selection():
			self.tree.selection_remove(item)

	# Muestra todos los registros
	def show_all(self):
		self.search.set("")
		self.refresh()
		self.enter_fullscreen()

	# Activa vista expandida
	def enter_fullscreen(self):
		if self.fullscreen:
			return
		self.fullscreen = True
		for widget in (self.title_label, self.subtitle_label, self.form, self.actions,
					   self.list_label, self.search_bar):
			widget.pack_forget()
		self.close_fullscreen.pack(side="top", anchor="w", padx=2, pady=2)
		self.body.pack(fill="both", expand=True)

	# Restaura vista normal
	def exit_fullscreen(self):
		if not self.fullscreen:
			return
		self.fullscreen = False
		self.close_fullscreen.pack_forget()
		self.body.pack_forget()
		self.title_label.pack(anchor="w")
		self.subtitle_label.pack(anchor="w", pady=(2, 9))
		self.form.pack(fill="x")
		self.actions.pack(fill="x", pady=(8, 3))
		self.list_label.pack(anchor="w", pady=(10, 3))
		self.search_bar.pack(fill="x", pady=(0, 5))
		self.body.pack(fill="both", expand=True)

	# Actualiza el listado
	def refresh(self):
		if not self.app.db.connection:
			return
		for item in self.tree.get_children():
			self.tree.delete(item)
		columns = [self.config["id"]] + self.config["columns"]
		term = self.search.get().strip()
		table = self.config["table"]
		if term:
			conditions = " OR ".join(f"CAST(`{column}` AS CHAR) LIKE %s" for column in columns)
			sql = f"SELECT * FROM `{table}` WHERE {conditions} ORDER BY `{columns[0]}` DESC"
			rows = self.app.db.query(sql, tuple(f"%{term}%" for _ in columns))
		else:
			rows = self.app.db.query(f"SELECT * FROM `{table}` ORDER BY `{columns[0]}` DESC")
		for row in rows:
			self.tree.insert("", "end", values=tuple(row.get(column, "") for column in columns))

	# Obtiene datos formulario
	def _values(self):
		return {column: variable.get().strip() for column, variable in self.entries.items()}

	# Valida campos obligatorios
	def _validate(self, values):
		optional = {"isbn", "telefono", "correo", "direccion", "nacionalidad",
						"ciudad", "fecha_devolucion"}
		if any(not value for column, value in values.items() if column not in optional):
			messagebox.showwarning("Datos incompletos", "Completa los campos obligatorios.")
			return False
		return True

	# Inserta un registro
	def insert_record(self):
		values = self._values()
		if not self._validate(values):
			return
		try:
			table = self.config["table"]
			columns = list(values)
			sql = f"INSERT INTO `{table}` ({', '.join(f'`{c}`' for c in columns)}) VALUES ({', '.join('%s' for _ in columns)})"
			record_id = self.app.db.query(sql, tuple(self._normalize(c, values[c]) for c in columns), fetch=False)
			self._audit("INSERT", record_id)
			self.app.refresh_all()
			self.clear_form()
		except Exception as exc:
			messagebox.showerror("No se pudo insertar", str(exc))

	# Actualiza un registro
	def update_record(self):
		if self.selected_id is None:
			messagebox.showwarning("Seleccion requerida", "Selecciona un registro del listado para actualizarlo.")
			return
		values = self._values()
		if not self._validate(values):
			return
		try:
			table = self.config["table"]
			columns = list(values)
			assignments = ", ".join(f"`{column}` = %s" for column in columns)
			sql = f"UPDATE `{table}` SET {assignments} WHERE `{self.config['id']}` = %s"
			params = tuple(self._normalize(c, values[c]) for c in columns) + (self.selected_id,)
			self.app.db.query(sql, params, fetch=False)
			self._audit("UPDATE", self.selected_id)
			self.app.refresh_all()
			self.clear_form()
		except Exception as exc:
			messagebox.showerror("No se pudo actualizar", str(exc))

	# Elimina registro seleccionado
	def delete_selected(self):
		record_id = self.selected_id
		if record_id is None:
			messagebox.showwarning("Seleccion requerida", "Selecciona un registro del listado primero.")
			return
		if not messagebox.askyesno("Confirmar", "Eliminar el registro seleccionado?"):
			return
		try:
			table = self.config["table"]
			self.app.db.query(f"DELETE FROM `{table}` WHERE `"
							  f"{self.config['id']}` = %s", (record_id,), fetch=False)
			self._audit("DELETE", record_id)
			self.app.refresh_all()
			self.clear_form()
		except Error as exc:
			messagebox.showerror("No se puede eliminar", f"La base de datos rechazo la operacion.\n{exc}")

	# Convierte datos numéricos
	def _normalize(self, column, value):
		if column in ("id_usuario", "id_autor", "id_editorial", "id_categoria",
					  "id_prestamo", "id_libro", "cantidad", "anio_publicacion",
					  "id_registro"):
			return int(value) if value else None
		if column == "fecha_prestamo" and not value:
			return date.today().isoformat()
		return value or None

	# Registra operación realizada
	def _audit(self, operation, record_id):
		table = self.config["table"]
		try:
			self.app.db.query(
				"INSERT INTO auditoria (tabla_afectada, operacion, id_registro, descripcion) "
				"VALUES (%s, %s, %s, %s)",
				(table, operation, record_id, f"{operation} en {table}"), fetch=False)
		except Exception:
			pass


if __name__ == "__main__":
	login = LoginWindow()
	login.mainloop()
	if login.authenticated:
		app = LibraryApp()
		app.mainloop()
