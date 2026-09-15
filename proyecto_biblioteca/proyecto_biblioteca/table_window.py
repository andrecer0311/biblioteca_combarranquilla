import tkinter as tk
from tkinter import ttk


class TableWindow(tk.Toplevel):
    def __init__(self, title, table_name, columns, readonly=False):
        super().__init__()
        self.title(title)
        self.geometry("900x560")
        self.table_name = table_name
        self.columns = columns
        self.readonly = readonly
        self.entries = {}
        self.selected_id = None
        self._build()

    def _build(self):
        ttk.Label(self, text=f"Gestión de {self.table_name}",
                  font=("Segoe UI", 16, "bold"), foreground="#332b55").pack(anchor="w", padx=16, pady=(12, 6))
        form = ttk.LabelFrame(self, text="DATOS DEL REGISTRO", padding=(12, 10))
        form.pack(fill="x", padx=16, pady=(0, 8))

        for i, column in enumerate(self.columns):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(form, text=column.replace("_", " ").title()).grid(row=row, column=col, sticky="w", padx=(0, 10), pady=4)
            variable = tk.StringVar()
            self.entries[column] = variable
            widget = ttk.Entry(form, textvariable=variable, width=30)
            widget.grid(row=row, column=col + 1, sticky="ew", padx=(0, 18), pady=4)
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=16, pady=(0, 10))
        ttk.Button(actions, text="INSERTAR", style="Accent.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="ACTUALIZAR", style="Update.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="ELIMINAR", style="Delete.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="LIMPIAR", style="Clear.TButton").pack(side="left", padx=3)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree = ttk.Treeview(list_frame, columns=self.columns, show="headings")
        for column in self.columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=120)
        self.tree.pack(fill="both", expand=True)
