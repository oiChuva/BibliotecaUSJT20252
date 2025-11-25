from flask import render_template, session, request
from sqlalchemy import text
from app import engine
import datetime
from datetime import date

def livros_lista_page():
    user_name = session.get("user_name")
    user_id = session.get("user_id")

    filtros = {
        "titulo": request.args.get("titulo"),
        "subtitulo": request.args.get("subtitulo"),
        "autor": request.args.get("autor"),
        "editora": request.args.get("editora"),
        "ano_publicacao": request.args.get("ano_publicacao"),
        "genero": request.args.get("genero"),
        "edicao": request.args.get("edicao"),
        "isbn": request.args.get("isbn"),
        "quantidade_estoque": request.args.get("quantidade_estoque"),
        "preco_compra": request.args.get("preco_compra"),
        "preco_emprestimo": request.args.get("preco_emprestimo"),
        "disponivel_compra": request.args.get("disponivel_compra"),
        "disponivel_emprestimo": request.args.get("disponivel_emprestimo"),
    }

    order_by = request.args.get("order_by")

    direction = request.args.get("direction", "asc").lower()
    if direction not in ("asc", "desc"):
        direction = "asc"

    sql = "SELECT * FROM livros WHERE 1=1 "
    params = {}

    for campo, valor in filtros.items():
        if valor not in (None, "", "null"):
            sql += f" AND {campo} LIKE :{campo}"
            params[campo] = f"%{valor}%"

    valid_order_columns = {
        "titulo", "subtitulo", "autor", "editora", "ano_publicacao", "genero",
        "edicao", "isbn", "quantidade_estoque", "preco_compra", "preco_emprestimo"
    }

    if order_by in valid_order_columns:
        sql += f" ORDER BY {order_by} {direction}"
    elif order_by in (None, "", "null"):
        sql += f" ORDER BY id_livro {direction}"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = result.mappings().all()

    livros = []
    for row in rows:
        livro = dict(row)
        for k, v in livro.items():
            if isinstance(v, (datetime, date)):
                livro[k] = v.isoformat()
        livros.append(livro)

    return render_template(
        "livros.html",
        name=user_name,
        user_id=user_id,
        livros=livros,
        filtros=filtros,
        order_by=order_by,
        direction=direction
    )