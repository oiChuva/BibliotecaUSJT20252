from flask import render_template, session, redirect, url_for, request
from sqlalchemy import text
from app.database import engine

def excluir_livro_conn(id_livro):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM livros WHERE id_livro = :id"),
            {"id": id_livro}
        )
    return redirect(url_for("livros_lista_page"))
