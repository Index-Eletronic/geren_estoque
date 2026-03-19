import tkinter as tk
from tkinter import ttk

from ui.utils_ui import configurar_janela, abrir_filha


class CadastrosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        configurar_janela(
            self,
            largura=320,
            altura=180,
            titulo="Cadastros"
        )

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Cadastros do Sistema",
            font=("Arial", 12, "bold")
        ).pack(anchor="center", pady=(0, 15))

        ttk.Button(frame, text="Usuários", command=self.abrir_usuarios).pack(fill="x", pady=5)
        ttk.Button(frame, text="Colaboradores", command=self.abrir_colaboradores).pack(fill="x", pady=5)

    def abrir_usuarios(self):
        from ui.usuarios_window import UsuariosWindow
        abrir_filha(self, UsuariosWindow)

    def abrir_colaboradores(self):
        from ui.colaboradores_window import ColaboradoresWindow
        abrir_filha(self, ColaboradoresWindow)