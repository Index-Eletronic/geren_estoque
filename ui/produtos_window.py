import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db_estoque import (
    buscar_produtos,
    buscar_produto_por_id,
    registrar_movimentacao_produto,
    listar_colaboradores_ativos
)
from ui.utils_ui import configurar_janela
from ui.cadastro_produtos_window import CadastroProdutosWindow


class ProdutosWindow(tk.Toplevel):
    def __init__(self, master, usuario_logado):
        super().__init__(master)
        self.master = master
        self.usuario_logado = usuario_logado
        self.produto_id = None
        self.colab_map = {}

        configurar_janela(
            self,
            largura=1300,
            altura=680,
            titulo="Movimentação do Produto"
        )

        mov = ttk.LabelFrame(self, text="Movimentação do Produto")
        mov.pack(fill="x", padx=10, pady=10)

        ttk.Label(mov, text="Data").grid(row=0, column=0, padx=5, pady=5)
        self.data_mov = ttk.Entry(mov, width=14)
        self.data_mov.grid(row=0, column=1, padx=5, pady=5)
        self.data_mov.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Label(mov, text="Tipo").grid(row=0, column=2, padx=5, pady=5)
        self.tipo = ttk.Combobox(
            mov,
            values=["ENTRADA", "SAIDA", "AJUSTE"],
            state="disabled",
            width=12
        )
        self.tipo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(mov, text="Quantidade").grid(row=0, column=4, padx=5, pady=5)
        self.quantidade = ttk.Entry(mov, width=12, state="disabled")
        self.quantidade.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(mov, text="Colaborador").grid(row=1, column=0, padx=5, pady=5)
        self.colaborador = ttk.Combobox(mov, state="disabled", width=25)
        self.colaborador.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(mov, text="Obs").grid(row=1, column=2, padx=5, pady=5)
        self.mov_obs = ttk.Entry(mov, width=45, state="disabled")
        self.mov_obs.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky="we")

        self.btn_mov = ttk.Button(
            mov,
            text="Registrar Movimentação",
            command=self.movimentar,
            state="disabled"
        )
        self.btn_mov.grid(row=1, column=5, padx=5, pady=5)

        ttk.Button(
            mov,
            text="Cadastro de Produtos",
            command=self.abrir_cadastro_produtos
        ).grid(row=1, column=6, padx=5, pady=5)

        busca = ttk.LabelFrame(self, text="Pesquisar Produto")
        busca.pack(fill="x", padx=10, pady=5)

        ttk.Label(busca, text="Pesquisar por ID, Nome ou Fornecedor").grid(row=0, column=0, padx=5, pady=5)
        self.filtro = ttk.Entry(busca, width=20)
        self.filtro.grid(row=0, column=1, padx=5, pady=5)
        self.filtro.bind("<Return>", lambda e: self.pesquisar())
        self.filtro.bind("<KeyRelease>", self.on_filtro_change)

        ttk.Button(busca, text="Pesquisar", command=self.pesquisar).grid(row=0, column=2, padx=5, pady=5)

        info = ttk.LabelFrame(self, text="Produto selecionado")
        info.pack(fill="x", padx=10, pady=5)

        self.lbl_info = ttk.Label(
            info,
            text="Nenhum produto selecionado.",
            font=("Arial", 12, "bold")
        )
        self.lbl_info.pack(anchor="w", padx=10, pady=10)

        tabela = ttk.LabelFrame(self, text="Produtos")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            tabela,
            columns=("id", "data", "descricao", "unidade", "qtde", "fornecedor", "minimo", "localizacao"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        cols = [
            ("id", "ID", 60, "center"),
            ("data", "Data", 96, "center"),
            ("descricao", "Descrição", 280, "w"),
            ("unidade", "Unidade", 90, "center"),
            ("qtde", "Qtde Atual", 100, "center"),
            ("fornecedor", "Fornecedor", 200, "w"),
            ("minimo", "Mínimo", 90, "center"),
            ("localizacao", "Localização", 120, "center"),
        ]

        for c, t, w, anchor in cols:
            self.tree.heading(c, text=t, anchor=anchor)
            self.tree.column(c, width=w, anchor=anchor)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.carregar_colaboradores()
        self.pesquisar()

    def _data_para_bd(self, data_str):
        try:
            return datetime.strptime(data_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            raise ValueError("Data inválida. Use dd/mm/aaaa.")

    def _data_para_tela(self, data_str):
        if not data_str:
            return ""
        try:
            return datetime.strptime(data_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return data_str

    def abrir_cadastro_produtos(self):
        janela = CadastroProdutosWindow(self)
        self.wait_window(janela)
        self.pesquisar()

    def carregar_colaboradores(self):
        try:
            colaboradores = listar_colaboradores_ativos()
            self.colab_map = {f'{c["id"]} - {c["nome"]}': c["id"] for c in colaboradores}
            self.colaborador["values"] = list(self.colab_map.keys())

            if colaboradores and not self.colaborador.get():
                self.colaborador.current(0)
            elif not colaboradores:
                self.colaborador.set("")
        except Exception as e:
            self.colab_map = {}
            self.colaborador["values"] = []
            self.colaborador.set("")
            messagebox.showerror("Erro", f"Não foi possível carregar colaboradores.\n\n{e}")

    def on_filtro_change(self, event=None):
        if not self.filtro.get().strip():
            self.pesquisar()

    def pesquisar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in buscar_produtos(self.filtro.get()):
            self.tree.insert("", "end", values=(
                row["id"],
                self._data_para_tela(row["data_cadastro"]),
                row["descricao"],
                row["unidade"],
                row["qtde_atual"],
                row["fornecedor"],
                row["estoque_minimo"],
                row["localizacao"]
            ))

        self.desabilitar_movimentacao()
        self.lbl_info.config(text="Nenhum produto selecionado.")

    def habilitar_movimentacao_total(self):
        self.tipo.config(state="readonly")
        if not self.tipo.get():
            self.tipo.set("ENTRADA")

        self.colaborador.config(state="readonly")
        if self.colaborador["values"] and not self.colaborador.get():
            self.colaborador.current(0)

        self.quantidade.config(state="normal")
        self.mov_obs.config(state="normal")
        self.btn_mov.config(state="normal")

    def desabilitar_movimentacao(self):
        self.produto_id = None
        self.tipo.config(state="disabled")
        self.colaborador.config(state="disabled")
        self.quantidade.config(state="disabled")
        self.mov_obs.config(state="disabled")
        self.btn_mov.config(state="disabled")
        self.tipo.set("")
        self.quantidade.delete(0, "end")
        self.mov_obs.delete(0, "end")

    def movimentar(self):
        if self.produto_id is None:
            messagebox.showwarning("Atenção", "Selecione um produto.")
            return

        tipo = self.tipo.get().strip()
        qtd = self.quantidade.get().strip()
        colaborador_str = self.colaborador.get().strip()
        obs = self.mov_obs.get().strip()
        data_mov = self._data_para_bd(self.data_mov.get())

        if not tipo:
            messagebox.showwarning("Atenção", "Selecione o tipo.")
            return

        if not qtd:
            messagebox.showwarning("Atenção", "Informe a quantidade.")
            return

        colaborador_id = self.colab_map.get(colaborador_str)
        if colaborador_id is None:
            messagebox.showwarning("Atenção", "Selecione um colaborador válido.")
            return

        try:
            registrar_movimentacao_produto(
                produto_id=self.produto_id,
                tipo=tipo,
                quantidade=float(qtd),
                colaborador_id=colaborador_id,
                usuario_id=int(self.usuario_logado["id"]),
                observacao=obs,
                data_movimentacao=data_mov
            )
            messagebox.showinfo("Sucesso", "Movimentação registrada.")
            self.quantidade.delete(0, "end")
            self.mov_obs.delete(0, "end")
            self.data_mov.delete(0, "end")
            self.data_mov.insert(0, datetime.now().strftime("%d/%m/%Y"))

            produto_id_atual = self.produto_id
            self.pesquisar()

            produto = buscar_produto_por_id(produto_id_atual)
            if produto:
                self.selecionar_produto(produto)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def selecionar_produto(self, row):
        self.produto_id = int(row["id"])
        self.lbl_info.config(
            text=(
                f'ID: {row["id"]} | Produto: {row["descricao"]} | '
                f'Unidade: {row["unidade"]} | Fornecedor: {row["fornecedor"]} | '
                f'Saldo Atual: {row["qtde_atual"]}'
            )
        )
        self.habilitar_movimentacao_total()

    def on_select(self, event):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        produto_id = int(self.tree.item(selecionado[0], "values")[0])
        row = buscar_produto_por_id(produto_id)
        if row:
            self.selecionar_produto(row)