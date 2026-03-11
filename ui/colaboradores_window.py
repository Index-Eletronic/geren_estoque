import tkinter as tk
from tkinter import ttk, messagebox

from db_estoque import listar_colaboradores, inserir_colaborador, atualizar_colaborador
from ui.utils_ui import configurar_janela


class ColaboradoresWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        configurar_janela(
            self,
            largura=700,
            altura=420,
            titulo="Colaboradores"
        )

        self.colaborador_id = None

        form = ttk.LabelFrame(self, text="Cadastro")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Nome").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nome = ttk.Entry(form, width=30)
        self.nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Função").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.funcao = ttk.Entry(form, width=25)
        self.funcao.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Ativo").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ativo = ttk.Combobox(form, values=["1", "0"], state="readonly", width=10)
        self.ativo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.ativo.set("1")

        ttk.Button(form, text="Novo", command=self.novo).grid(row=2, column=0, padx=5, pady=10)
        ttk.Button(form, text="Salvar", command=self.salvar).grid(row=2, column=1, padx=5, pady=10)

        self.tree = ttk.Treeview(self, columns=("id", "nome", "funcao", "ativo"), show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col, txt, w in [
            ("id", "ID", 60),
            ("nome", "Nome", 260),
            ("funcao", "Função", 180),
            ("ativo", "Ativo", 80)
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.carregar()

    def carregar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in listar_colaboradores():
            self.tree.insert("", "end", values=(
                row["id"], row["nome"], row["funcao"], row["ativo"]
            ))

    def novo(self):
        self.colaborador_id = None
        self.nome.delete(0, "end")
        self.funcao.delete(0, "end")
        self.ativo.set("1")

    def salvar(self):
        nome = self.nome.get().strip()
        funcao = self.funcao.get().strip()
        ativo = int(self.ativo.get().strip())

        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome.")
            return

        try:
            if self.colaborador_id is None:
                inserir_colaborador(nome, funcao)
            else:
                atualizar_colaborador(self.colaborador_id, nome, funcao, ativo)

            self.carregar()
            self.novo()
            messagebox.showinfo("Sucesso", "Colaborador salvo.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_select(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        valores = self.tree.item(selecionado[0], "values")
        self.colaborador_id = int(valores[0])

        self.nome.delete(0, "end")
        self.nome.insert(0, valores[1])

        self.funcao.delete(0, "end")
        self.funcao.insert(0, valores[2] or "")

        self.ativo.set(str(valores[3]))