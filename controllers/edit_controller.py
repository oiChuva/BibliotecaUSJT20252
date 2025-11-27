from flask import render_template, session
from sqlalchemy import text
from app import engine

def editar_livro_conn(id_livro):
    user_name = session.get("user_name")
    user_id = session.get("user_id")

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM livros WHERE id_livro = :id"),
            {"id": id_livro}
        ).mappings().fetchone()

    livro = dict(result)

    return render_template(
        "alteracao-livro.html",
        name=user_name,
        user_id=user_id,
        livro=livro
    )
