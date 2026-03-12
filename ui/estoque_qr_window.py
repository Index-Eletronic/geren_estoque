import tkinter as tk
from tkinter import ttk, messagebox

from db_estoque import (
    listar_produtos,
    buscar_produto_por_id_texto,
    registrar_movimentacao_produto,
    listar_colaboradores_ativos
)
from ui.utils_ui import configurar_janela


class EstoqueQRWindow(tk.Toplevel):
    def __init__(self, master, usuario_logado):
        super().__init__(master)
        self.master = master
        self.usuario_logado = usuario_logado
        self.item_id = None

        configurar_janela(
            self,
            largura=1000,
            altura=580,
            titulo="Estoque por ID"
        )

        top = ttk.LabelFrame(self, text="Buscar item")
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="ID").grid(row=0, column=0, padx=5, pady=5)
        self.codigo_id = ttk.Entry(top, width=20)
        self.codigo_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(top, text="Buscar no banco", command=self.buscar_codigo).grid(row=0, column=2, padx=5, pady=5)

        info = ttk.LabelFrame(self, text="Dados do item")
        info.pack(fill="x", padx=10, pady=5)

        self.lbl_info = ttk.Label(
            info,
            text="Nenhum item carregado.",
            font=("Arial", 12, "bold")
        )
        self.lbl_info.pack(anchor="w", padx=10, pady=10)

        mov = ttk.LabelFrame(self, text="Movimentação")
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

        ttk.Button(mov, text="Registrar movimentação", command=self.movimentar).grid(row=1, column=5, padx=5, pady=5)

        tabela = ttk.LabelFrame(self, text="Estoque atual")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            tabela,
            columns=("id", "descricao", "unidade", "qtde", "fornecedor", "minimo", "localizacao"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        cols = [
            ("id", "ID", 60, "center"),
            ("descricao", "Descrição", 240, "w"),
            ("unidade", "Unidade", 90, "center"),
            ("qtde", "Qtde Atual", 100, "center"),
            ("fornecedor", "Fornecedor", 220, "w"),
            ("minimo", "Mínimo", 90, "center"),
            ("localizacao", "Localização", 140, "center"),
        ]

        for c, t, w, anchor in cols:
            self.tree.heading(c, text=t, anchor=anchor)
            self.tree.column(c, width=w, anchor=anchor)

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

    def buscar_codigo(self):
        codigo = self.codigo_id.get().strip()
        if not codigo:
            messagebox.showwarning("Atenção", "Informe o ID.")
            return

        item = buscar_produto_por_id_texto(codigo)
        if not item:
            messagebox.showerror("Erro", "ID não encontrado no estoque.")
            return

        self.preencher_item(item)

        self.lbl_info.config(
            text=(
                f'ID: {item["id"]} | Produto: {item["descricao"]} | '
                f'Unidade: {item["unidade"]} | Fornecedor: {item["fornecedor"]} | '
                f'Saldo: {item["qtde_atual"]}'
            )
        )
        self.carregar_tabela()

    def preencher_item(self, item):
        self.item_id = int(item["id"])

    def movimentar(self):
        if self.item_id is None:
            messagebox.showwarning("Atenção", "Carregue um item primeiro.")
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
                produto_id=self.item_id,
                tipo=tipo,
                quantidade=float(qtd),
                colaborador_id=colaborador_id,
                usuario_id=int(self.usuario_logado["id"]),
                observacao=obs
            )
            messagebox.showinfo("Sucesso", "Movimentação registrada.")
            self.quantidade.delete(0, "end")
            self.mov_obs.delete(0, "end")
            self.buscar_codigo()
            self.carregar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_select(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        valores = self.tree.item(selecionado[0], "values")
        codigo = valores[0]

        self.codigo_id.delete(0, "end")
        self.codigo_id.insert(0, codigo)
        self.buscar_codigo()