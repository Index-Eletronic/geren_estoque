import tkinter as tk
from tkinter import ttk, messagebox

from db_estoque import (
    listar_usuarios,
    inserir_usuario,
    atualizar_usuario,
    excluir_usuario
)
from ui.utils_ui import configurar_janela


class UsuariosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        configurar_janela(
            self,
            largura=600,
            altura=450,
            titulo="Usuários"
        )

        self.usuario_id = None

        form = ttk.LabelFrame(self, text="Cadastro")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Nome").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome = ttk.Entry(form, width=20)
        self.nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Usuário").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.usuario = ttk.Entry(form, width=16)
        self.usuario.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Senha").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.senha = ttk.Entry(form, width=16)
        self.senha.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Nível").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.nivel = ttk.Combobox(
            form,
            values=["admin", "usuario"],
            state="readonly",
            width=14
        )
        self.nivel.grid(row=1, column=3, padx=5, pady=5)
        self.nivel.set("usuario")

        ttk.Label(form, text="Ativo").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ativo = ttk.Combobox(form, values=["1", "0"], state="readonly", width=14)
        self.ativo.grid(row=2, column=1, padx=5, pady=5)
        self.ativo.set("1")

        ttk.Button(form, text="Novo", command=self.novo).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(form, text="Salvar", command=self.salvar).grid(row=3, column=1, padx=5, pady=10)
        ttk.Button(form, text="Excluir", command=self.excluir).grid(row=3, column=2, padx=5, pady=10)

        self.tree = ttk.Treeview(self, columns=("id", "nome", "usuario", "nivel", "ativo"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        configuracao_colunas = [
            ("id", "ID", 40, "center"),
            ("nome", "Nome", 180, "w"),
            ("usuario", "Usuário", 120, "w"),
            ("nivel", "Nível", 80, "center"),
            ("ativo", "Ativo", 50, "center"),
        ]

        for col, txt, width, anchor in configuracao_colunas:
            self.tree.heading(col, text=txt, anchor=anchor)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.carregar()

    def carregar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in listar_usuarios():
            if row["nivel"] not in ("admin", "usuario"):
                continue
            self.tree.insert("", "end", values=(
                row["id"], row["nome"], row["usuario"] or "", row["nivel"], row["ativo"]
            ))

    def novo(self):
        self.usuario_id = None
        self.nome.delete(0, "end")
        self.usuario.delete(0, "end")
        self.senha.delete(0, "end")
        self.nivel.set("usuario")
        self.ativo.set("1")

    def salvar(self):
        nome = self.nome.get().strip()
        usuario = self.usuario.get().strip()
        senha = self.senha.get().strip()
        nivel = self.nivel.get().strip()
        ativo = int(self.ativo.get().strip())

        if not nome or not usuario or not senha or not nivel:
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios.")
            return

        try:
            if self.usuario_id is None:
                inserir_usuario(nome, usuario, senha, nivel)
            else:
                atualizar_usuario(self.usuario_id, nome, usuario, senha, nivel, ativo)

            self.carregar()
            self.novo()
            messagebox.showinfo("Sucesso", "Usuário salvo.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir(self):
        if self.usuario_id is None:
            messagebox.showwarning("Atenção", "Selecione um usuário para excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja excluir este usuário definitivamente?"
        )
        if not confirmar:
            return

        try:
            excluir_usuario(self.usuario_id)
            self.carregar()
            self.novo()
            messagebox.showinfo("Sucesso", "Usuário excluído.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_select(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        valores = self.tree.item(selecionado[0], "values")
        self.usuario_id = int(valores[0])

        self.nome.delete(0, "end")
        self.nome.insert(0, valores[1])

        self.usuario.delete(0, "end")
        self.usuario.insert(0, valores[2])

        self.senha.delete(0, "end")
        self.nivel.set(valores[3])
        self.ativo.set(str(valores[4]))