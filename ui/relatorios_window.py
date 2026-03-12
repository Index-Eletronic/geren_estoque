import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

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
            largura=1400,
            altura=700,
            titulo="Relatórios",
            resizable=True
        )

        self._configurar_estilos_treeview()

        topo = ttk.Frame(self)
        topo.pack(fill="x", padx=10, pady=10)

        ttk.Button(topo, text="Exportar Produtos", command=self.exp_prod).pack(side="left", padx=15)
        ttk.Button(topo, text="Exportar Mov. Produtos", command=self.exp_mov_prod).pack(side="left", padx=5)
        ttk.Button(topo, text="Exportar Produtos Baixo", command=self.exp_prod_baixo).pack(side="left", padx=5)

        resumo = ttk.Frame(self)
        resumo.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            resumo,
            text=f"Produtos abaixo do mínimo: {len(listar_produtos_baixo())}"
        ).pack(side="left", padx=20)

        self.tree_prod = ttk.Treeview(
            self,
            columns=("produto_id", "descricao", "unidade", "fornecedor", "tipo", "saldo", "colaborador", "usuario", "data", "obs"),
            show="headings"
        )
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

        self.cols_prod = [
            ("produto_id", "Id Produto", "center", 0.07),
            ("descricao", "Descrição", "w", 0.20),
            ("unidade", "Unidade", "center", 0.07),
            ("fornecedor", "Fornecedor", "w", 0.15),
            ("tipo", "Tipo", "center", 0.08),
            ("saldo", "Saldo", "center", 0.08),
            ("colaborador", "Colaborador", "w", 0.11),
            ("usuario", "Usuário", "w", 0.11),
            ("data", "Data", "center", 0.08),
            ("obs", "Observação", "w", 0.15),
        ]

        for col, txt, anchor, _peso in self.cols_prod:
            self.tree_prod.heading(col, text=txt, anchor=anchor)
            self.tree_prod.column(col, anchor=anchor, width=100)

        self.tree_prod.tag_configure("saldo_baixo", foreground="red", font=("Arial", 9, "bold"))

        self.bind("<Configure>", self._ao_redimensionar)

        self.carregar()
        self.after(100, self._ajustar_larguras_colunas)

    def _configurar_estilos_treeview(self):
        self.tree_style = ttk.Style(self)
        self.tree_style.configure("Treeview", rowheight=24)

    def _formatar_data(self, valor):
        if not valor:
            return ""
        try:
            dt = datetime.strptime(valor[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            try:
                dt = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d/%m/%Y")
            except Exception:
                return valor

    def _ao_redimensionar(self, event):
        if event.widget == self:
            self._ajustar_larguras_colunas()

    def _ajustar_larguras_colunas(self):
        largura_total = self.tree_prod.winfo_width()
        if largura_total <= 50:
            return

        largura_util = max(largura_total - 20, 1000)

        for col, _txt, anchor, peso in self.cols_prod:
            largura = int(largura_util * peso)
            self.tree_prod.column(col, width=largura, anchor=anchor)

    def carregar(self):
        for i in self.tree_prod.get_children():
            self.tree_prod.delete(i)

        for row in listar_movimentacoes_produto():
            qtde_atual = float(row["qtde_atual"] or 0)
            estoque_minimo = float(row["estoque_minimo"] or 0)
            saldo = qtde_atual - estoque_minimo

            tags = ()
            if saldo <= 0:
                tags = ("saldo_baixo",)

            self.tree_prod.insert(
                "",
                "end",
                values=(
                    row["produto_id"],
                    row["descricao"],
                    row["unidade"],
                    row["fornecedor"],
                    row["tipo"],
                    saldo,
                    row["colaborador"],
                    row["usuario"],
                    self._formatar_data(row["data_movimentacao"]),
                    row["observacao"]
                ),
                tags=tags
            )

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