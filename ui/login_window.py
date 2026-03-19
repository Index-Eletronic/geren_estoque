import tkinter as tk
from tkinter import ttk, messagebox

from auth import login
from ui.utils_ui import configurar_janela


class LoginWindow:
    def __init__(self, root):
        self.root = root
        configurar_janela(
            self.root,
            largura=250,
            altura=220,
            titulo="Login - Controle de Estoque"
        )

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Usuário").pack(anchor="w")
        self.entry_usuario = ttk.Entry(frame)
        self.entry_usuario.pack(fill="x", pady=5)

        ttk.Label(frame, text="Senha").pack(anchor="w")
        self.entry_senha = ttk.Entry(frame, show="*")
        self.entry_senha.pack(fill="x", pady=5)

        ttk.Button(frame, text="Entrar", command=self.entrar).pack(fill="x", pady=15)
        ttk.Label(frame, text="Admin inicial: admin / 1234").pack(anchor="center", pady=10)

        self.entry_usuario.bind("<Return>", self.entrar_evento)
        self.entry_senha.bind("<Return>", self.entrar_evento)

        self.entry_usuario.focus_set()

    def entrar_evento(self, event):
        self.entrar()

    def entrar(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        user = login(usuario, senha)
        if not user:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            return

        from ui.main_window import MainWindow

        self.root.destroy()

        nova_root = tk.Tk()
        MainWindow(nova_root, user)
        nova_root.mainloop()