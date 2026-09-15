import os
import tkinter as tk
from tkinter import ttk

ADMIN_USER = os.getenv("APP_USER", "Admin1")
ADMIN_PASSWORD = os.getenv("APP_PASSWORD", "contraseña123")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.ico")


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biblioteca Comfenalco | Iniciar sesión")
        self.geometry("760x480")
        self.resizable(False, False)
        self.authenticated = False
        self.user_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password = tk.BooleanVar(value=False)
        self._build()

    def _set_icon(self):
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except tk.TclError:
                pass

    def _build(self):
        self._set_icon()
        left = tk.Frame(self, bg="#403765", width=330)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="BIBLIOTECA", background="#403765", foreground="white",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=30, pady=(62, 0))
        tk.Label(left, text="COMFENALCO", background="#403765", foreground="#d9d2ee",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=32, pady=(0, 34))
        tk.Label(left, text="Sistema de Gestión\nde Biblioteca", background="#403765",
                 foreground="white", justify="left", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=30)
        tk.Label(left, text="LIBROS  |  USUARIOS  |  PRESTAMOS", background="#403765",
                 foreground="#bdb4d9", font=("Segoe UI", 8)).pack(anchor="w", padx=30, pady=(22, 0))

        right = tk.Frame(self, bg="#f2f1f8")
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="INICIAR SESIÓN", background="#f2f1f8", foreground="#332b55",
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
        ttk.Button(form, text="INGRESAR", style="Accent.TButton", command=self._login).pack(fill="x", pady=(24, 8), ipady=5)
        tk.Button(form, text="SALIR", command=self.destroy).pack(fill="x", ipady=4)
        self.message = ttk.Label(form, text="", foreground="#bd4b42", background="#f2f1f8")
        self.message.pack(anchor="w", pady=(10, 0))
        user_entry.focus_set()
        self.bind("<Return>", lambda _event: self._login())

    def _toggle_password(self):
        self.password_entry.configure(show="" if self.show_password.get() else "*")

    def _login(self):
        if self.user_var.get().strip() == ADMIN_USER and self.password_var.get() == ADMIN_PASSWORD:
            self.authenticated = True
            self.destroy()
        else:
            self.message.configure(text="Usuario o contraseña incorrectos")
            self.password_var.set("")
            self.password_entry.focus_set()
