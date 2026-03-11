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
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_id TEXT NOT NULL UNIQUE,
        data_qr TEXT,
        cliente TEXT,
        produto TEXT NOT NULL,
        quantidade_atual REAL NOT NULL DEFAULT 0,
        estoque_minimo REAL NOT NULL DEFAULT 0,
        unidade TEXT,
        localizacao TEXT,
        observacao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estoque_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA', 'AJUSTE')),
        quantidade REAL NOT NULL,
        colaborador_id INTEGER,
        usuario_id INTEGER NOT NULL,
        data_movimentacao TEXT NOT NULL,
        observacao TEXT,
        FOREIGN KEY (estoque_id) REFERENCES estoque(id),
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
# ESTOQUE
# -------------------------
def listar_estoque():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM estoque
        WHERE ativo = 1
        ORDER BY produto, cliente
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_estoque_baixo():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM estoque
        WHERE ativo = 1
          AND quantidade_atual <= estoque_minimo
        ORDER BY produto
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def buscar_item_estoque_por_codigo_id(codigo_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM estoque
        WHERE codigo_id = ?
    """, (codigo_id,))
    row = cur.fetchone()
    conn.close()
    return row


def inserir_item_estoque(codigo_id, data_qr, cliente, produto,
                         quantidade_atual=0, estoque_minimo=0,
                         unidade="", localizacao="", observacao=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO estoque (
            codigo_id, data_qr, cliente, produto,
            quantidade_atual, estoque_minimo, unidade, localizacao, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo_id, data_qr, cliente, produto,
        quantidade_atual, estoque_minimo, unidade, localizacao, observacao
    ))
    conn.commit()
    conn.close()


def atualizar_item_estoque(item_id, estoque_minimo, unidade, localizacao, observacao, ativo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE estoque
        SET estoque_minimo=?, unidade=?, localizacao=?, observacao=?, ativo=?
        WHERE id=?
    """, (estoque_minimo, unidade, localizacao, observacao, ativo, item_id))
    conn.commit()
    conn.close()


def obter_ou_criar_item_estoque_do_qr(dados_qr):
    item = buscar_item_estoque_por_codigo_id(dados_qr["codigo_id"])
    if item:
        return item

    inserir_item_estoque(
        codigo_id=dados_qr["codigo_id"],
        data_qr=dados_qr["data"],
        cliente=dados_qr["cliente_obra"],
        produto=dados_qr["produto"],
        quantidade_atual=0
    )
    return buscar_item_estoque_por_codigo_id(dados_qr["codigo_id"])


# -------------------------
# MOVIMENTAÇÕES
# -------------------------
def registrar_movimentacao(estoque_id, tipo, quantidade, colaborador_id, usuario_id, observacao=""):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT quantidade_atual FROM estoque WHERE id = ? AND ativo = 1", (estoque_id,))
    item = cur.fetchone()
    if not item:
        conn.close()
        raise ValueError("Item de estoque não encontrado.")

    saldo_atual = float(item["quantidade_atual"])
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
        raise ValueError("Tipo de movimentação inválido.")

    cur.execute("""
        INSERT INTO movimentacoes (
            estoque_id, tipo, quantidade, colaborador_id, usuario_id, data_movimentacao, observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        estoque_id,
        tipo,
        quantidade,
        colaborador_id,
        usuario_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        observacao
    ))

    cur.execute("""
        UPDATE estoque
        SET quantidade_atual = ?
        WHERE id = ?
    """, (novo_saldo, estoque_id))

    conn.commit()
    conn.close()


def listar_movimentacoes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            m.id,
            e.codigo_id,
            e.cliente,
            e.produto,
            m.tipo,
            m.quantidade,
            c.nome AS colaborador,
            u.nome AS usuario,
            m.data_movimentacao,
            m.observacao
        FROM movimentacoes m
        JOIN estoque e ON e.id = m.estoque_id
        LEFT JOIN colaboradores c ON c.id = m.colaborador_id
        JOIN usuarios u ON u.id = m.usuario_id
        ORDER BY m.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def listar_movimentacoes_por_codigo_id(codigo_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            m.id,
            e.codigo_id,
            e.cliente,
            e.produto,
            m.tipo,
            m.quantidade,
            c.nome AS colaborador,
            u.nome AS usuario,
            m.data_movimentacao,
            m.observacao
        FROM movimentacoes m
        JOIN estoque e ON e.id = m.estoque_id
        LEFT JOIN colaboradores c ON c.id = m.colaborador_id
        JOIN usuarios u ON u.id = m.usuario_id
        WHERE e.codigo_id = ?
        ORDER BY m.id DESC
    """, (codigo_id,))
    rows = cur.fetchall()
    conn.close()
    return rows