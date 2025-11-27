from flask import render_template, redirect, url_for, request, session
from sqlalchemy import text

from app.database import engine


def editar_livro_form(id_livro):
    data = request.form

    titulo = data.get("titulo")
    subtitulo = data.get("subtitulo")
    autor = data.get("autor")
    editora = data.get("editora")
    ano_publicacao = data.get("ano_publicacao")
    genero = data.get("genero")
    edicao = data.get("edicao")
    isbn = data.get("isbn")
    quantidade_estoque = data.get("quantidade_estoque")
    preco_compra = data.get("preco_compra")
    preco_emprestimo = data.get("preco_emprestimo")

    disponivel_compra = 1 if data.get("disponivel_compra") == "on" else 0
    disponivel_emprestimo = 1 if data.get("disponivel_emprestimo") == "on" else 0

    with engine.connect() as conn:
        existente = conn.execute(
            text("""
                SELECT 1 FROM livros 
                WHERE isbn = :isbn AND id_livro != :id_livro
            """),
            {"isbn": isbn, "id_livro": id_livro}
        ).fetchone()

    if existente:
        form_data = dict(data)
        form_data["id_livro"] = id_livro

        return render_template(
            "alteracao-livro.html",
            error=f"Já existe um livro com o ISBN {isbn}.",
            livro=form_data,
            name=session.get("user_name")
        )

    sql = text("""
        UPDATE livros SET
            titulo=:titulo,
            subtitulo=:subtitulo,
            autor=:autor,
            editora=:editora,
            ano_publicacao=:ano_publicacao,
            genero=:genero,
            edicao=:edicao,
            isbn=:isbn,
            quantidade_estoque=:quantidade_estoque,
            preco_compra=:preco_compra,
            preco_emprestimo=:preco_emprestimo,
            disponivel_compra=:disponivel_compra,
            disponivel_emprestimo=:disponivel_emprestimo
        WHERE id_livro = :id_livro
    """)

    with engine.begin() as conn:
        conn.execute(sql, {
            "titulo": titulo,
            "subtitulo": subtitulo,
            "autor": autor,
            "editora": editora,
            "ano_publicacao": int(ano_publicacao) if ano_publicacao else None,
            "genero": genero,
            "edicao": edicao,
            "isbn": isbn,
            "quantidade_estoque": int(quantidade_estoque) if quantidade_estoque else 0,
            "preco_compra": float(preco_compra) if preco_compra else 0.0,
            "preco_emprestimo": float(preco_emprestimo) if preco_emprestimo else 0.0,
            "disponivel_compra": disponivel_compra,
            "disponivel_emprestimo": disponivel_emprestimo,
            "id_livro": id_livro
        })

    return redirect(url_for("livro_detalhes", id_livro=id_livro))
