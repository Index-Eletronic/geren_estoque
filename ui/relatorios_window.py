import tkinter as tk
from tkinter import ttk, messagebox

from db_estoque import (
    listar_movimentacoes_produto,
    listar_produtos_baixo
)
from excel_export import (
    exportar_produtos_excel,
    exportar_movimentacoes_produto_excel,
    exportar_produtos_baixo_excel
)
from ui.utils_ui import configurar_janela


class RelatoriosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        configurar_janela(
            self,
            largura=1200,
            altura=580,
            titulo="Relatórios"
        )

        topo = ttk.Frame(self)
        topo.pack(fill="x", padx=10, pady=10)

        ttk.Button(topo, text="Exportar Produtos", command=self.exp_prod).pack(side="left", padx=15)
        ttk.Button(topo, text="Exportar Mov. Produtos", command=self.exp_mov_prod).pack(side="left", padx=5)
        ttk.Button(topo, text="Exportar Produtos Baixo", command=self.exp_prod_baixo).pack(side="left", padx=5)

        resumo = ttk.Frame(self)
        resumo.pack(fill="x", padx=10, pady=5)

        ttk.Label(resumo, text=f"Produtos abaixo do mínimo: {len(listar_produtos_baixo())}").pack(side="left", padx=20)

        self.tree_prod = ttk.Treeview(
            self,
            columns=("id", "produto_id", "descricao", "unidade", "fornecedor", "tipo", "quantidade", "colaborador", "usuario", "data", "obs"),
            show="headings"
        )
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

        cols_prod = [
            ("id", "ID Mov", 70),
            ("produto_id", "ID Produto", 80),
            ("descricao", "Descrição", 220),
            ("unidade", "Unidade", 80),
            ("fornecedor", "Fornecedor", 180),
            ("tipo", "Tipo", 90),
            ("quantidade", "Quantidade", 90),
            ("colaborador", "Colaborador", 140),
            ("usuario", "Usuário", 140),
            ("data", "Data", 150),
            ("obs", "Observação", 180),
        ]
        for col, txt, w in cols_prod:
            self.tree_prod.heading(col, text=txt)
            self.tree_prod.column(col, width=w)

        self.carregar()

    def carregar(self):
        for i in self.tree_prod.get_children():
            self.tree_prod.delete(i)

        for row in listar_movimentacoes_produto():
            self.tree_prod.insert("", "end", values=(
                row["id"], row["produto_id"], row["descricao"], row["unidade"], row["fornecedor"],
                row["tipo"], row["quantidade"], row["colaborador"], row["usuario"],
                row["data_movimentacao"], row["observacao"]
            ))

    def exp_prod(self):
        try:
            exportar_produtos_excel()
            messagebox.showinfo("Sucesso", "Arquivo relatorio_produtos.xlsx gerado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exp_mov_prod(self):
        try:
            exportar_movimentacoes_produto_excel()
            messagebox.showinfo("Sucesso", "Arquivo relatorio_movimentacoes_produto.xlsx gerado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exp_prod_baixo(self):
        try:
            exportar_produtos_baixo_excel()
            messagebox.showinfo("Sucesso", "Arquivo relatorio_produtos_baixo.xlsx gerado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))