import os
import tempfile
import webbrowser
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
        ttk.Button(topo, text="Visualizar / Imprimir", command=self.visualizar_impressao).pack(side="left", padx=20)

        resumo = ttk.Frame(self)
        resumo.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            resumo,
            text=f"Produtos abaixo do mínimo: {len(listar_produtos_baixo())}"
        ).pack(side="left", padx=20)

        self.tree_prod = ttk.Treeview(
            self,
            columns=(
                "produto_id", "descricao", "unidade", "fornecedor",
                "tipo", "minimo", "saldo", "total", "ultima_compra",
                "colaborador", "usuario", "data", "obs"
            ),
            show="headings"
        )
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

        self.cols_prod = [
            ("produto_id", "Id Produto", "center", 0.05),
            ("descricao", "Descrição", "w", 0.15),
            ("unidade", "Unidade", "center", 0.06),
            ("fornecedor", "Fornecedor", "w", 0.11),
            ("tipo", "Tipo", "center", 0.06),
            ("minimo", "Mínimo", "center", 0.06),
            ("saldo", "Saldo", "center", 0.06),
            ("total", "Total", "center", 0.06),
            ("ultima_compra", "Última Compra", "center", 0.08),
            ("colaborador", "Colaborador", "w", 0.09),
            ("usuario", "Usuário", "w", 0.09),
            ("data", "Data", "center", 0.07),
            ("obs", "Observação", "w", 0.10),
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
            total = qtde_atual
            ultima_compra = float(row["qtde_inicial"] or 0)

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
                    estoque_minimo,
                    saldo,
                    total,
                    ultima_compra,
                    row["colaborador"],
                    row["usuario"],
                    self._formatar_data(row["data_movimentacao"]),
                    row["observacao"]
                ),
                tags=tags
            )

    def _saldo_baixo(self, valor):
        try:
            return float(str(valor).replace(",", ".")) <= 0
        except Exception:
            return False

    def _montar_html_relatorio(self):
        linhas = []
        for item_id in self.tree_prod.get_children():
            valores = self.tree_prod.item(item_id, "values")
            saldo_val = str(valores[6])
            classe_saldo = "saldo-baixo" if self._saldo_baixo(saldo_val) else ""

            linhas.append(f"""
            <tr>
                <td class="center">{valores[0]}</td>
                <td>{valores[1]}</td>
                <td class="center">{valores[2]}</td>
                <td>{valores[3]}</td>
                <td class="center">{valores[4]}</td>
                <td class="center">{valores[5]}</td>
                <td class="center {classe_saldo}">{valores[6]}</td>
                <td class="center">{valores[7]}</td>
                <td class="center">{valores[8]}</td>
                <td>{valores[9] or ""}</td>
                <td>{valores[10] or ""}</td>
                <td class="center">{valores[11]}</td>
                <td>{valores[12] or ""}</td>
            </tr>
            """)

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Relatório de Movimentações</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 10mm;
    }}

    body {{
        font-family: Arial, sans-serif;
        font-size: 9px;
        color: #000;
        margin: 0;
        padding: 0;
    }}

    h1 {{
        font-size: 16px;
        text-align: center;
        margin: 0 0 10px 0;
    }}

    .resumo {{
        margin-bottom: 10px;
        font-size: 11px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }}

    th, td {{
        border: 1px solid #444;
        padding: 4px;
        vertical-align: middle;
        word-wrap: break-word;
    }}

    th {{
        background: #f0f0f0;
        font-weight: bold;
    }}

    .center {{
        text-align: center;
    }}

    .saldo-baixo {{
        color: red;
        font-weight: bold;
    }}
</style>
</head>
<body>
    <h1>Relatório de Movimentações de Produtos</h1>
    <div class="resumo">Produtos abaixo do mínimo: {len(listar_produtos_baixo())}</div>

    <table>
        <thead>
            <tr>
                <th style="width: 4%;">ID</th>
                <th style="width: 14%;">Descrição</th>
                <th style="width: 5%;">Unid</th>
                <th style="width: 10%;">Fornecedor</th>
                <th style="width: 6%;">Tipo</th>
                <th style="width: 6%;">Mínimo</th>
                <th style="width: 6%;">Saldo</th>
                <th style="width: 6%;">Total</th>
                <th style="width: 8%;">Última Compra</th>
                <th style="width: 9%;">Colaborador</th>
                <th style="width: 9%;">Usuário</th>
                <th style="width: 7%;">Data</th>
                <th style="width: 10%;">Observação</th>
            </tr>
        </thead>
        <tbody>
            {''.join(linhas)}
        </tbody>
    </table>
</body>
</html>
"""
        return html

    def visualizar_impressao(self):
        try:
            html = self._montar_html_relatorio()
            arquivo_temp = os.path.join(tempfile.gettempdir(), "relatorio_movimentacoes_produtos.html")
            with open(arquivo_temp, "w", encoding="utf-8") as f:
                f.write(html)

            webbrowser.open(f"file:///{arquivo_temp.replace(os.sep, '/')}")
            messagebox.showinfo(
                "Visualização",
                "Relatório aberto no navegador.\nUse Ctrl+P para imprimir em A4 vertical."
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a visualização.\n{e}")

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