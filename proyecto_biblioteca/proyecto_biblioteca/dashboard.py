import tkinter as tk
from tkinter import ttk


class DashboardWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biblioteca | Dashboard")
        self.geometry("1200x700")
        self.configure(bg="#f2f1f8")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#332b55", height=90)
        header.pack(fill="x")
        tk.Label(header, text="BIBLIOTECA", bg="#332b55", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=24, pady=(18, 0))
        tk.Label(header, text="Panel de administración", bg="#332b55", fg="#d8d3e8",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(2, 12))

        cards = tk.Frame(self, bg="#f2f1f8")
        cards.pack(fill="x", padx=24, pady=(20, 10))
        for label, value in (("Libros", 128), ("Usuarios", 46), ("Préstamos", 21), ("Autores", 12)):
            card = tk.Frame(cards, bg="white", bd=1, relief="solid")
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=str(value), bg="white", fg="#332b55",
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=16, pady=(14, 0))
            tk.Label(card, text=label, bg="white", fg="#557080",
                     font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 14))

        chart = tk.Frame(self, bg="white", bd=1, relief="solid")
        chart.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        tk.Label(chart, text="REGISTROS POR TABLA", bg="white", fg="#332b55",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(16, 8))

        canvas = tk.Canvas(chart, width=1000, height=400, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        for i, (label, amount) in enumerate((("Usuarios", 46), ("Libros", 128), ("Autores", 12), ("Préstamos", 21))):
            x = 80 + i * 180
            canvas.create_rectangle(x, 320, x + 80, 320 - amount * 2, fill="#6b8fd3")
            canvas.create_text(x + 40, 335, text=label, fill="#557080")
            canvas.create_text(x + 40, 300 - amount * 2, text=str(amount), fill="#332b55", font=("Segoe UI", 9, "bold"))
