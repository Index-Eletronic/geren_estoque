import tkinter as tk

from db_estoque import criar_tabelas, criar_admin_padrao
from ui.login_window import LoginWindow


def main():
    criar_tabelas()
    criar_admin_padrao()

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()