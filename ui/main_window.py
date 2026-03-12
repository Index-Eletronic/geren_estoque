import tkinter as tk
from tkinter import ttk, messagebox

from ui.estoque_qr_window import EstoqueQRWindow
from ui.produtos_window import ProdutosWindow
from ui.usuarios_window import UsuariosWindow
from ui.colaboradores_window import ColaboradoresWindow
from ui.relatorios_window import RelatoriosWindow
from ui.utils_ui import configurar_janela, abrir_filha


class MainWindow:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.usuario_logado = usuario_logado

        configurar_janela(
            self.root,
            largura=360,
            altura=220,
            titulo="Sistema de Estoque"
        )

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=f'Bem-vindo, {usuario_logado["nome"]} ({usuario_logado["nivel"]})',
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=10)

        ttk.Button(frame, text="Estoque por ID", command=self.abrir_estoque_qr).pack(fill="x", pady=5)
        ttk.Button(frame, text="Produtos de Estoque", command=self.abrir_produtos).pack(fill="x", pady=5)
        ttk.Button(frame, text="Relatórios / Exportação Excel", command=self.abrir_relatorios).pack(fill="x", pady=5)

        if usuario_logado["nivel"] == "admin":
            ttk.Button(frame, text="Usuários", command=self.abrir_usuarios).pack(fill="x", pady=5)
            ttk.Button(frame, text="Colaboradores", command=self.abrir_colaboradores).pack(fill="x", pady=5)

        ttk.Button(frame, text="Sair", command=self.root.destroy).pack(fill="x", pady=20)

    def abrir_estoque_qr(self):
        abrir_filha(self.root, EstoqueQRWindow, self.usuario_logado)

    def abrir_produtos(self):
        abrir_filha(self.root, ProdutosWindow, self.usuario_logado)

    def abrir_relatorios(self):
        abrir_filha(self.root, RelatoriosWindow)

    def abrir_usuarios(self):
        if self.usuario_logado["nivel"] != "admin":
            messagebox.showerror("Acesso negado", "Somente admin.")
            return
        abrir_filha(self.root, UsuariosWindow)

    def abrir_colaboradores(self):
        if self.usuario_logado["nivel"] != "admin":
            messagebox.showerror("Acesso negado", "Somente admin.")
            return
        abrir_filha(self.root, ColaboradoresWindow)