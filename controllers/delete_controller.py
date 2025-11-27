from flask import redirect, url_for
from sqlalchemy import text
from app import engine

def excluir_livro_conn(id_livro):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM livros WHERE id_livro = :id"),
            {"id": id_livro}
        )
    return redirect(url_for("livros_lista"))
