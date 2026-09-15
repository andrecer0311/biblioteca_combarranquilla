import tkinter as tk
from tkinter import messagebox, ttk

from .config import TABLES, ICON_PATH, DB_CONFIG
from .database import Database
from .table_view import TableView


class LibraryApp(tk.Tk):
    """Interfaz gráfica para administrar todas las tablas del esquema."""

    def __init__(self):
        super().__init__()
        self.title("Biblioteca Comfenalco | Sistema de Gestión")
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

    def _set_icon(self):
        if ICON_PATH and __import__("os").path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except tk.TclError:
                pass

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

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(24, 18))
        header.pack(fill="x")
        ttk.Label(header, text="BIBLIOTECA", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Panel de administración y control de préstamos",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
        self.status = ttk.Label(header, text="Conectando...", style="Subtitle.TLabel")
        self.status.pack(anchor="e")

    def _build_tabs(self):
        workspace = ttk.Frame(self, style="TFrame")
        workspace.pack(fill="both", expand=True)
        navigation = tk.Frame(workspace, bg="#403765", width=190)
        navigation.pack(side="left", fill="y")
        navigation.pack_propagate(False)
        tk.Label(navigation, text="MENU PRINCIPAL", background="#403765",
                 foreground="#c9c2e5", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=14, pady=(22, 8)
        )

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

    def _add_nav_button(self, parent, label, notebook, frame):
        ttk.Button(parent, text="  " + label, style="Nav.TButton",
                   command=lambda: notebook.select(frame)).pack(fill="x", padx=8, pady=2)

    def _build_dashboard(self, parent):
        ttk.Label(parent, text="Vista general", font=("Segoe UI", 18, "bold"),
                  foreground="#17324d").pack(anchor="w")
        ttk.Label(parent, text="Consulta el estado actual de tu biblioteca.",
                  foreground="#557080").pack(anchor="w", pady=(2, 18))

        cards = ttk.Frame(parent)
        cards.pack(fill="x")
        self.summary_values = {}
        for label, table in (("Libros", "libros"), ("Usuarios", "usuarios"),
                             ("Préstamos activos", "prestamos"), ("Autores", "autores")):
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
        ttk.Label(chart_frame, text="Cantidad de usuarios, libros, préstamos y demás registros.",
                  foreground="#557080").pack(anchor="w", pady=(2, 8))
        self.chart_canvas = tk.Canvas(chart_frame, height=310, background="white",
                                     highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        self.chart_canvas.bind("<Configure>", lambda _event: self._draw_chart())

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
        canvas.create_line(left, height - bottom, width - right, height - bottom, fill="#b7c0cc")
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

    def _connect(self):
        try:
            self.db.connect()
            self.status.configure(text=f"Conectado a {DB_CONFIG['database']}")
            self.refresh_all()
        except Exception as exc:
            self.status.configure(text="Sin conexión")
            messagebox.showerror(
                "Conexión no disponible",
                f"No se pudo conectar a MySQL.\n\n{exc}\n\nConfigura DB_USER y DB_PASSWORD e intenta de nuevo."
            )

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
        for name, table in (("libros", "libros"), ("usuarios", "usuarios"), ("autores", "autores")):
            self.summary_values[table].configure(text=str(self.db.count(name)))
        active = self.db.query(
            "SELECT COUNT(*) AS total FROM prestamos WHERE estado IN ('PRESTADO', 'ATRASADO')"
        )[0]["total"]
        self.summary_values["prestamos"].configure(text=str(active))
        for view in self.tabs.values():
            view.refresh()

    def _close(self):
        self.db.close()
        self.destroy()
