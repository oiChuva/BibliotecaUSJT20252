from flask import render_template, session, redirect, url_for, request
from sqlalchemy import text
from app.database import engine

def cadastrar_livro_form():
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

    if isbn:
        with engine.connect() as conn:
            query = conn.execute(
                text("SELECT 1 FROM livros WHERE isbn = :isbn"),
                {"isbn": isbn}
            ).fetchone()

        if query:
            return render_template(
                "cadastro-livro.html",
                error=f"O ISBN {isbn} já está cadastrado.",
                form=data
            )

    ano_publicacao = int(ano_publicacao) if ano_publicacao else None
    quantidade_estoque = int(quantidade_estoque) if quantidade_estoque else 0
    preco_compra = float(preco_compra) if preco_compra else 0.0
    preco_emprestimo = float(preco_emprestimo) if preco_emprestimo else 0.0

    sql = text("""
        INSERT INTO livros (
            titulo, subtitulo, autor, editora, ano_publicacao, genero, edicao,
            isbn, quantidade_estoque, preco_compra, preco_emprestimo,
            disponivel_compra, disponivel_emprestimo
        ) VALUES (
            :titulo, :subtitulo, :autor, :editora, :ano_publicacao, :genero, :edicao,
            :isbn, :quantidade_estoque, :preco_compra, :preco_emprestimo,
            :disponivel_compra, :disponivel_emprestimo
        )
    """)

    with engine.begin() as conn:
        conn.execute(sql, {
            "titulo": titulo,
            "subtitulo": subtitulo,
            "autor": autor,
            "editora": editora,
            "ano_publicacao": ano_publicacao,
            "genero": genero,
            "edicao": edicao,
            "isbn": isbn,
            "quantidade_estoque": quantidade_estoque,
            "preco_compra": preco_compra,
            "preco_emprestimo": preco_emprestimo,
            "disponivel_compra": disponivel_compra,
            "disponivel_emprestimo": disponivel_emprestimo
        })

    return redirect(url_for("livros_lista_page"))