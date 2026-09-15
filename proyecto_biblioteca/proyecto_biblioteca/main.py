from biblioteca_modulos.login_window import LoginWindow
from biblioteca_modulos.app import LibraryApp


if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
    if login.authenticated:
        app = LibraryApp()
        app.mainloop()
