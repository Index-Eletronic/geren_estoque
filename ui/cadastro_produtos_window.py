import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db_estoque import (
    listar_produtos,
    inserir_produto,
    atualizar_produto,
    buscar_produto_por_id
)
from ui.utils_ui import configurar_janela


class CadastroProdutosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.produto_id = None

        configurar_janela(
            self,
            largura=900,
            altura=620,
            titulo="Cadastro de Produtos"
        )

        form = ttk.LabelFrame(self, text="Cadastro de Produto")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Data").grid(row=0, column=0, padx=5, pady=5)
        self.data_cadastro = ttk.Entry(form, width=14)
        self.data_cadastro.grid(row=0, column=1, padx=5, pady=5)
        self.data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Label(form, text="Descrição").grid(row=0, column=2, padx=5, pady=5)
        self.descricao = ttk.Entry(form, width=24)
        self.descricao.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Unidade").grid(row=0, column=4, padx=5, pady=5)
        self.unidade = ttk.Entry(form, width=10)
        self.unidade.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Qtde Inicial").grid(row=1, column=0, padx=5, pady=5)
        self.qtde_inicial = ttk.Entry(form, width=12)
        self.qtde_inicial.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Fornecedor").grid(row=1, column=2, padx=5, pady=5)
        self.fornecedor = ttk.Entry(form, width=24)
        self.fornecedor.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form, text="Estoque Mínimo").grid(row=1, column=4, padx=5, pady=5)
        self.estoque_minimo = ttk.Entry(form, width=10)
        self.estoque_minimo.grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(form, text="Localização").grid(row=2, column=0, padx=5, pady=5)
        self.localizacao = ttk.Entry(form, width=18)
        self.localizacao.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form, text="Observação").grid(row=2, column=2, padx=5, pady=5)
        self.observacao = ttk.Entry(form, width=30)
        self.observacao.grid(row=2, column=3, columnspan=2, padx=5, pady=5, sticky="we")

        ttk.Label(form, text="Ativo").grid(row=2, column=5, padx=5, pady=5)
        self.ativo = ttk.Combobox(form, values=["1", "0"], state="readonly", width=8)
        self.ativo.grid(row=2, column=6, padx=5, pady=5)
        self.ativo.set("1")

        botoes = ttk.Frame(form)
        botoes.grid(row=3, column=0, columnspan=7, pady=10, sticky="w")

        ttk.Button(botoes, text="Novo", command=self.novo).pack(side="left", padx=5)
        ttk.Button(botoes, text="Salvar", command=self.salvar).pack(side="left", padx=5)
        ttk.Button(botoes, text="Excluir", command=self.excluir).pack(side="left", padx=5)

        tabela = ttk.LabelFrame(self, text="Produtos cadastrados")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            tabela,
            columns=("id", "data", "descricao", "unidade", "qtde", "fornecedor", "minimo", "localizacao"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        cols = [
            ("id", "ID", 45, "center"),
            ("data", "Data", 85, "center"),
            ("descricao", "Descrição", 200, "w"),
            ("unidade", "Unidade", 70, "center"),
            ("qtde", "Qtde Atual", 85, "center"),
            ("fornecedor", "Fornecedor", 150, "w"),
            ("minimo", "Mínimo", 75, "center"),
            ("localizacao", "Localização", 100, "center"),
        ]

        for c, t, w, anchor in cols:
            self.tree.heading(c, text=t, anchor=anchor)
            self.tree.column(c, width=w, anchor=anchor)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self._configurar_caixa_alta()

        self.carregar_tabela()

    def _configurar_caixa_alta(self):
        campos = [
            self.descricao,
            self.unidade,
            self.fornecedor,
            self.localizacao,
            self.observacao,
        ]
        for campo in campos:
            campo.bind("<KeyRelease>", self._forcar_maiusculas)

    def _forcar_maiusculas(self, event):
        widget = event.widget
        texto = widget.get()
        texto_maiusculo = texto.upper()
        if texto != texto_maiusculo:
            pos = widget.index(tk.INSERT)
            widget.delete(0, tk.END)
            widget.insert(0, texto_maiusculo)
            try:
                widget.icursor(pos)
            except Exception:
                pass

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

    def carregar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in listar_produtos():
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

    def novo(self):
        self.produto_id = None
        self.data_cadastro.delete(0, "end")
        self.data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.descricao.delete(0, "end")
        self.unidade.delete(0, "end")
        self.qtde_inicial.delete(0, "end")
        self.fornecedor.delete(0, "end")
        self.estoque_minimo.delete(0, "end")
        self.localizacao.delete(0, "end")
        self.observacao.delete(0, "end")
        self.ativo.set("1")

    def salvar(self):
        descricao = self.descricao.get().strip().upper()
        unidade = self.unidade.get().strip().upper()
        fornecedor = self.fornecedor.get().strip().upper()
        qtde_inicial = self.qtde_inicial.get().strip()
        estoque_minimo = self.estoque_minimo.get().strip()
        localizacao = self.localizacao.get().strip().upper()
        observacao = self.observacao.get().strip().upper()
        ativo = int(self.ativo.get())
        data_cadastro = self._data_para_bd(self.data_cadastro.get())

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
                    observacao=observacao,
                    data_cadastro=data_cadastro
                )
                messagebox.showinfo("Sucesso", "Produto cadastrado.")
            else:
                atualizar_produto(
                    produto_id=self.produto_id,
                    descricao=descricao,
                    unidade=unidade,
                    fornecedor=fornecedor,
                    estoque_minimo=float(estoque_minimo or 0),
                    localizacao=localizacao,
                    observacao=observacao,
                    ativo=ativo,
                    data_cadastro=data_cadastro
                )
                messagebox.showinfo("Sucesso", "Produto atualizado.")

            self.carregar_tabela()
            self.novo()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir(self):
        if self.produto_id is None:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja inativar este produto?"
        )
        if not confirmar:
            return

        try:
            row = buscar_produto_por_id(self.produto_id)
            if not row:
                messagebox.showerror("Erro", "Produto não encontrado.")
                return

            atualizar_produto(
                produto_id=self.produto_id,
                descricao=row["descricao"],
                unidade=row["unidade"],
                fornecedor=row["fornecedor"] or "",
                estoque_minimo=float(row["estoque_minimo"] or 0),
                localizacao=row["localizacao"] or "",
                observacao=row["observacao"] or "",
                ativo=0,
                data_cadastro=row["data_cadastro"]
            )

            messagebox.showinfo("Sucesso", "Produto inativado.")
            self.carregar_tabela()
            self.novo()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def preencher_form(self, row):
        self.produto_id = int(row["id"])

        self.data_cadastro.delete(0, "end")
        self.data_cadastro.insert(0, self._data_para_tela(row["data_cadastro"]))

        self.descricao.delete(0, "end")
        self.descricao.insert(0, row["descricao"])

        self.unidade.delete(0, "end")
        self.unidade.insert(0, row["unidade"])

        self.qtde_inicial.delete(0, "end")
        self.qtde_inicial.insert(0, str(row["qtde_inicial"]))

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

        produto_id = int(self.tree.item(selecionado[0], "values")[0])
        row = buscar_produto_por_id(produto_id)
        if row:
            self.preencher_form(row)