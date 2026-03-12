import sqlite3
from datetime import datetime

DB_ESTOQUE = "estoque.db"


def get_conn():
    conn = sqlite3.connect(DB_ESTOQUE)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        nivel TEXT NOT NULL CHECK (nivel IN ('admin', 'usuario')),
        ativo INTEGER NOT NULL DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        funcao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        unidade TEXT NOT NULL,
        qtde_atual REAL NOT NULL DEFAULT 0,
        fornecedor TEXT,
        estoque_minimo REAL NOT NULL DEFAULT 0,
        localizacao TEXT,
        observacao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes_produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA', 'AJUSTE')),
        quantidade REAL NOT NULL,
        colaborador_id INTEGER,
        usuario_id INTEGER NOT NULL,
        data_movimentacao TEXT NOT NULL,
        observacao TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()


def criar_admin_padrao():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE usuario = ?", ("admin",))
    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios (nome, usuario, senha, nivel)
            VALUES (?, ?, ?, ?)
        """, ("Administrador", "admin", "1234", "admin"))

    conn.commit()
    conn.close()


# -------------------------
# USUÁRIOS
# -------------------------
def autenticar(usuario: str, senha: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM usuarios
        WHERE usuario = ? AND senha = ? AND ativo = 1
    """, (usuario, senha))
    row = cur.fetchone()
    conn.close()
    return row


def listar_usuarios():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def inserir_usuario(nome, usuario, senha, nivel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios (nome, usuario, senha, nivel)
        VALUES (?, ?, ?, ?)
    """, (nome, usuario, senha, nivel))
    conn.commit()
    conn.close()


def atualizar_usuario(usuario_id, nome, usuario, senha, nivel, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE usuarios
        SET nome=?, usuario=?, senha=?, nivel=?, ativo=?
        WHERE id=?
    """, (nome, usuario, senha, nivel, ativo, usuario_id))
    conn.commit()
    conn.close()


# -------------------------
# COLABORADORES
# -------------------------
def listar_colaboradores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM colaboradores ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_colaboradores_ativos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM colaboradores WHERE ativo = 1 ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def inserir_colaborador(nome, funcao):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO colaboradores (nome, funcao)
        VALUES (?, ?)
    """, (nome, funcao))
    conn.commit()
    conn.close()


def atualizar_colaborador(colaborador_id, nome, funcao, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE colaboradores
        SET nome=?, funcao=?, ativo=?
        WHERE id=?
    """, (nome, funcao, ativo, colaborador_id))
    conn.commit()
    conn.close()


# -------------------------
# PRODUTOS
# -------------------------
def listar_produtos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM produtos
        WHERE ativo = 1
        ORDER BY descricao
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_produtos_baixo():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM produtos
        WHERE ativo = 1
          AND qtde_atual <= estoque_minimo
        ORDER BY descricao
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def buscar_produto_por_id(produto_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM produtos
        WHERE id = ? AND ativo = 1
    """, (produto_id,))
    row = cur.fetchone()
    conn.close()
    return row


def buscar_produto_por_id_texto(produto_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM produtos
        WHERE id = ? AND ativo = 1
    """, (produto_id,))
    row = cur.fetchone()
    conn.close()
    return row


def inserir_produto(descricao, unidade, qtde_atual, fornecedor, estoque_minimo=0, localizacao="", observacao=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produtos (
            descricao, unidade, qtde_atual, fornecedor,
            estoque_minimo, localizacao, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        descricao, unidade, qtde_atual, fornecedor,
        estoque_minimo, localizacao, observacao
    ))
    conn.commit()
    conn.close()


def atualizar_produto(produto_id, descricao, unidade, fornecedor, estoque_minimo, localizacao, observacao, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE produtos
        SET descricao=?, unidade=?, fornecedor=?, estoque_minimo=?,
            localizacao=?, observacao=?, ativo=?
        WHERE id=?
    """, (
        descricao, unidade, fornecedor, estoque_minimo,
        localizacao, observacao, ativo, produto_id
    ))
    conn.commit()
    conn.close()


# -------------------------
# MOVIMENTAÇÕES
# -------------------------
def registrar_movimentacao_produto(produto_id, tipo, quantidade, colaborador_id, usuario_id, observacao=""):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT qtde_atual FROM produtos WHERE id = ? AND ativo = 1", (produto_id,))
    item = cur.fetchone()
    if not item:
        conn.close()
        raise ValueError("Produto não encontrado.")

    saldo_atual = float(item["qtde_atual"])
    quantidade = float(quantidade)

    if tipo == "ENTRADA":
        novo_saldo = saldo_atual + quantidade
    elif tipo == "SAIDA":
        if quantidade > saldo_atual:
            conn.close()
            raise ValueError("Saldo insuficiente para saída.")
        novo_saldo = saldo_atual - quantidade
    elif tipo == "AJUSTE":
        novo_saldo = quantidade
    else:
        conn.close()
        raise ValueError("Tipo inválido.")

    cur.execute("""
        INSERT INTO movimentacoes_produto (
            produto_id, tipo, quantidade, colaborador_id, usuario_id, data_movimentacao, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        produto_id,
        tipo,
        quantidade,
        colaborador_id,
        usuario_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        observacao
    ))

    cur.execute("""
        UPDATE produtos
        SET qtde_atual = ?
        WHERE id = ?
    """, (novo_saldo, produto_id))

    conn.commit()
    conn.close()


def listar_movimentacoes_produto():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            m.id,
            p.id AS produto_id,
            p.descricao,
            p.unidade,
            p.fornecedor,
            p.qtde_atual,
            p.estoque_minimo,
            m.tipo,
            m.quantidade,
            c.nome AS colaborador,
            u.nome AS usuario,
            m.data_movimentacao,
            m.observacao
        FROM movimentacoes_produto m
        JOIN produtos p ON p.id = m.produto_id
        LEFT JOIN colaboradores c ON c.id = m.colaborador_id
        JOIN usuarios u ON u.id = m.usuario_id
        ORDER BY m.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows