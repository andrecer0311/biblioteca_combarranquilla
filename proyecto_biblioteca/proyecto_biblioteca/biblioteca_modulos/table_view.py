import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from .database import Database, Error


class TableView:
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

    def _build(self):
        self.title_label = ttk.Label(self.parent, text=f"Gestión de {self.name}",
                                    font=("Segoe UI", 16, "bold"), foreground="#332b55")
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(
            self.parent,
            text="Completa el formulario y usa las acciones para administrar los registros.",
            foreground="#657080",
        )
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
        ttk.Button(self.search_bar, text="Buscar", style="Accent.TButton", command=self.refresh).pack(side="left")
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

    def _build_form(self):
        form = ttk.LabelFrame(self.parent, text="DATOS DEL REGISTRO", padding=(12, 8))
        form.pack(fill="x")
        for index, column in enumerate(self.config["columns"]):
            row = index // 2
            column_position = (index % 2) * 2
            ttk.Label(form, text=column.replace("_", " ").title()).grid(
                row=row, column=column_position, sticky="w", padx=(0, 7), pady=4
            )
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

    def _set_form_state(self, state):
        for widget in self.parent.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Entry, ttk.Combobox)):
                        child.configure(state=state)

    def _load_selected(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        for index, column in enumerate(self.config["columns"], start=1):
            self.entries[column].set(values[index])

    def clear_form(self):
        self.selected_id = None
        for variable in self.entries.values():
            variable.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def show_all(self):
        self.search.set("")
        self.refresh()
        self.enter_fullscreen()

    def enter_fullscreen(self):
        if self.fullscreen:
            return
        self.fullscreen = True
        for widget in (self.title_label, self.subtitle_label, self.form, self.actions,
                       self.list_label, self.search_bar):
            widget.pack_forget()
        self.close_fullscreen.pack(side="top", anchor="w", padx=2, pady=2)
        self.body.pack(fill="both", expand=True)

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

    def _values(self):
        return {column: variable.get().strip() for column, variable in self.entries.items()}

    def _validate(self, values):
        optional = {
            "isbn", "telefono", "correo", "direccion", "nacionalidad",
            "ciudad", "fecha_devolucion"
        }
        if any(not value for column, value in values.items() if column not in optional):
            messagebox.showwarning("Datos incompletos", "Completa los campos obligatorios.")
            return False
        return True

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

    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("Selección requerida", "Selecciona un registro del listado para actualizarlo.")
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

    def delete_selected(self):
        record_id = self.selected_id
        if record_id is None:
            messagebox.showwarning("Selección requerida", "Selecciona un registro del listado primero.")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar el registro seleccionado?"):
            return
        try:
            table = self.config["table"]
            self.app.db.query(f"DELETE FROM `{table}` WHERE `{self.config['id']}` = %s", (record_id,), fetch=False)
            self._audit("DELETE", record_id)
            self.app.refresh_all()
            self.clear_form()
        except Error as exc:
            messagebox.showerror("No se puede eliminar", f"La base de datos rechazó la operación.\n{exc}")

    def _normalize(self, column, value):
        if column in ("id_usuario", "id_autor", "id_editorial", "id_categoria",
                      "id_prestamo", "id_libro", "cantidad", "anio_publicacion",
                      "id_registro"):
            return int(value) if value else None
        if column == "fecha_prestamo" and not value:
            return date.today().isoformat()
        return value or None

    def _audit(self, operation, record_id):
        table = self.config["table"]
        try:
            self.app.db.query(
                "INSERT INTO auditoria (tabla_afectada, operacion, id_registro, descripcion) "
                "VALUES (%s, %s, %s, %s)",
                (table, operation, record_id, f"{operation} en {table}"),
                fetch=False,
            )
        except Exception:
            pass
