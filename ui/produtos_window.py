import tkinter as tk
from tkinter import ttk, messagebox

from db_estoque import (
    listar_produtos,
    inserir_produto,
    atualizar_produto,
    buscar_produto_por_id,
    registrar_movimentacao_produto,
    listar_colaboradores_ativos
)
from ui.utils_ui import configurar_janela


class ProdutosWindow(tk.Toplevel):
    def __init__(self, master, usuario_logado):
        super().__init__(master)
        self.master = master
        self.usuario_logado = usuario_logado
        self.produto_id = None

        configurar_janela(
            self,
            largura=1250,
            altura=620,
            titulo="Produtos de Estoque"
        )

        form = ttk.LabelFrame(self, text="Cadastro de Produto")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Descrição").grid(row=0, column=0, padx=5, pady=5)
        self.descricao = ttk.Entry(form, width=30)
        self.descricao.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Unidade").grid(row=0, column=2, padx=5, pady=5)
        self.unidade = ttk.Entry(form, width=12)
        self.unidade.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Qtde Inicial").grid(row=0, column=4, padx=5, pady=5)
        self.qtde_inicial = ttk.Entry(form, width=12)
        self.qtde_inicial.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Fornecedor").grid(row=1, column=0, padx=5, pady=5)
        self.fornecedor = ttk.Entry(form, width=30)
        self.fornecedor.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Estoque Mínimo").grid(row=1, column=2, padx=5, pady=5)
        self.estoque_minimo = ttk.Entry(form, width=12)
        self.estoque_minimo.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form, text="Localização").grid(row=1, column=4, padx=5, pady=5)
        self.localizacao = ttk.Entry(form, width=20)
        self.localizacao.grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(form, text="Observação").grid(row=2, column=0, padx=5, pady=5)
        self.observacao = ttk.Entry(form, width=50)
        self.observacao.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        ttk.Label(form, text="Ativo").grid(row=2, column=4, padx=5, pady=5)
        self.ativo = ttk.Combobox(form, values=["1", "0"], state="readonly", width=10)
        self.ativo.grid(row=2, column=5, padx=5, pady=5)
        self.ativo.set("1")

        ttk.Button(form, text="Novo", command=self.novo).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(form, text="Salvar Cadastro", command=self.salvar).grid(row=3, column=1, padx=5, pady=10)

        mov = ttk.LabelFrame(self, text="Movimentação do Produto")
        mov.pack(fill="x", padx=10, pady=5)

        ttk.Label(mov, text="Tipo").grid(row=0, column=0, padx=5, pady=5)
        self.tipo = ttk.Combobox(mov, values=["ENTRADA", "SAIDA", "AJUSTE"], state="readonly", width=12)
        self.tipo.grid(row=0, column=1, padx=5, pady=5)
        self.tipo.set("ENTRADA")

        ttk.Label(mov, text="Quantidade").grid(row=0, column=2, padx=5, pady=5)
        self.quantidade = ttk.Entry(mov, width=12)
        self.quantidade.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(mov, text="Colaborador").grid(row=0, column=4, padx=5, pady=5)
        self.colaborador = ttk.Combobox(mov, state="readonly", width=25)
        self.colaborador.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(mov, text="Obs").grid(row=1, column=0, padx=5, pady=5)
        self.mov_obs = ttk.Entry(mov, width=50)
        self.mov_obs.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky="we")

        ttk.Button(mov, text="Registrar Movimentação", command=self.movimentar).grid(row=1, column=5, padx=5, pady=5)

        tabela = ttk.LabelFrame(self, text="Produtos cadastrados")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            tabela,
            columns=("id", "descricao", "unidade", "qtde", "fornecedor", "minimo", "localizacao"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        cols = [
            ("id", "ID", 60),
            ("descricao", "Descrição", 240),
            ("unidade", "Unidade", 90),
            ("qtde", "Qtde Atual", 100),
            ("fornecedor", "Fornecedor", 220),
            ("minimo", "Mínimo", 90),
            ("localizacao", "Localização", 140),
        ]

        for c, t, w in cols:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.carregar_colaboradores()
        self.carregar_tabela()

    def carregar_colaboradores(self):
        colaboradores = listar_colaboradores_ativos()
        self.colab_map = {f'{c["id"]} - {c["nome"]}': c["id"] for c in colaboradores}
        self.colaborador["values"] = list(self.colab_map.keys())
        if colaboradores:
            self.colaborador.current(0)

    def carregar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in listar_produtos():
            self.tree.insert("", "end", values=(
                row["id"],
                row["descricao"],
                row["unidade"],
                row["qtde_atual"],
                row["fornecedor"],
                row["estoque_minimo"],
                row["localizacao"]
            ))

    def novo(self):
        self.produto_id = None
        self.descricao.delete(0, "end")
        self.unidade.delete(0, "end")
        self.qtde_inicial.delete(0, "end")
        self.fornecedor.delete(0, "end")
        self.estoque_minimo.delete(0, "end")
        self.localizacao.delete(0, "end")
        self.observacao.delete(0, "end")
        self.ativo.set("1")

    def salvar(self):
        descricao = self.descricao.get().strip()
        unidade = self.unidade.get().strip()
        fornecedor = self.fornecedor.get().strip()
        qtde_inicial = self.qtde_inicial.get().strip()
        estoque_minimo = self.estoque_minimo.get().strip()
        localizacao = self.localizacao.get().strip()
        observacao = self.observacao.get().strip()
        ativo = int(self.ativo.get())

        if not descricao or not unidade:
            messagebox.showwarning("Atenção", "Descrição e unidade são obrigatórios.")
            return

        try:
            if self.produto_id is None:
                inserir_produto(
                    descricao=descricao,
                    unidade=unidade,
                    qtde_atual=float(qtde_inicial or 0),
                    fornecedor=fornecedor,
                    estoque_minimo=float(estoque_minimo or 0),
                    localizacao=localizacao,
                    observacao=observacao
                )
            else:
                atualizar_produto(
                    produto_id=self.produto_id,
                    descricao=descricao,
                    unidade=unidade,
                    fornecedor=fornecedor,
                    estoque_minimo=float(estoque_minimo or 0),
                    localizacao=localizacao,
                    observacao=observacao,
                    ativo=ativo
                )

            self.carregar_tabela()
            self.novo()
            messagebox.showinfo("Sucesso", "Produto salvo.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def movimentar(self):
        if self.produto_id is None:
            messagebox.showwarning("Atenção", "Selecione ou carregue um produto.")
            return

        tipo = self.tipo.get().strip()
        qtd = self.quantidade.get().strip()
        colaborador_str = self.colaborador.get().strip()
        obs = self.mov_obs.get().strip()

        if not tipo or not qtd:
            messagebox.showwarning("Atenção", "Informe tipo e quantidade.")
            return

        colaborador_id = self.colab_map.get(colaborador_str)

        try:
            registrar_movimentacao_produto(
                produto_id=self.produto_id,
                tipo=tipo,
                quantidade=float(qtd),
                colaborador_id=colaborador_id,
                usuario_id=int(self.usuario_logado["id"]),
                observacao=obs
            )
            messagebox.showinfo("Sucesso", "Movimentação registrada.")
            self.quantidade.delete(0, "end")
            self.mov_obs.delete(0, "end")
            self.recarregar_produto()
            self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def recarregar_produto(self):
        if self.produto_id is None:
            return
        row = buscar_produto_por_id(self.produto_id)
        if row:
            self.preencher_form(row)

    def preencher_form(self, row):
        self.produto_id = int(row["id"])

        self.descricao.delete(0, "end")
        self.descricao.insert(0, row["descricao"])

        self.unidade.delete(0, "end")
        self.unidade.insert(0, row["unidade"])

        self.qtde_inicial.delete(0, "end")
        self.qtde_inicial.insert(0, str(row["qtde_atual"]))

        self.fornecedor.delete(0, "end")
        self.fornecedor.insert(0, row["fornecedor"] or "")

        self.estoque_minimo.delete(0, "end")
        self.estoque_minimo.insert(0, str(row["estoque_minimo"]))

        self.localizacao.delete(0, "end")
        self.localizacao.insert(0, row["localizacao"] or "")

        self.observacao.delete(0, "end")
        self.observacao.insert(0, row["observacao"] or "")

        self.ativo.set(str(row["ativo"]))

    def on_select(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        valores = self.tree.item(selecionado[0], "values")
        produto_id = int(valores[0])

        row = buscar_produto_por_id(produto_id)
        if row:
            self.preencher_form(row)