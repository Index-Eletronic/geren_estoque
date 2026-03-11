from db_estoque import autenticar as autenticar_usuario


def login(usuario: str, senha: str):
    return autenticar_usuario(usuario, senha)