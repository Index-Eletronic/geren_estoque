import tkinter as tk
from tkinter import ttk, messagebox

from ui.utils_ui import configurar_janela, abrir_filha


class MainWindow:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.usuario_logado = usuario_logado

        configurar_janela(
            self.root,
            largura=360,
            altura=250,
            titulo="Sistema de Estoque"
        )

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=f'Bem-vindo, {usuario_logado["nome"]} ({usuario_logado["nivel"]})',
            font=("Arial", 12, "bold")
        ).pack(anchor="center", pady=10)

        ttk.Button(frame, text="Produtos de Estoque", command=self.abrir_produtos).pack(fill="x", pady=5)
        ttk.Button(frame, text="Relatórios / Exportação Excel", command=self.abrir_relatorios).pack(fill="x", pady=5)

        if self.usuario_logado["nivel"] == "admin":
            ttk.Button(frame, text="Cadastros", command=self.abrir_cadastros).pack(fill="x", pady=5)

        ttk.Button(frame, text="Sair", command=self.root.destroy).pack(fill="x", pady=15)

    def abrir_produtos(self):
        try:
            from ui.produtos_window import ProdutosWindow
            abrir_filha(self.root, ProdutosWindow, self.usuario_logado)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Produtos de Estoque.\n\n{e}")

    def abrir_relatorios(self):
        try:
            from ui.relatorios_window import RelatoriosWindow
            abrir_filha(self.root, RelatoriosWindow)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Relatórios.\n\n{e}")

    def abrir_cadastros(self):
        try:
            from ui.cadastros_window import CadastrosWindow
            abrir_filha(self.root, CadastrosWindow)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Cadastros.\n\n{e}")