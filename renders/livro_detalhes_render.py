from flask import render_template, session, redirect, url_for, request
from sqlalchemy import text
from app.database import engine
import datetime
from datetime import date

def livro_detalhes_page(id_livro):
    user_name = session.get("user_name")
    user_id = session.get("user_id")

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM livros WHERE id_livro = :id"),
            {"id": id_livro}
        ).mappings().fetchone()

    if not result:
        return redirect(url_for("livros_lista_page"))

    livro = dict(result)

    for k, v in livro.items():
        if isinstance(v, (datetime, date)):
            livro[k] = v.isoformat()

    return render_template(
        "detalhes-livro.html",
        name=user_name,
        user_id=user_id,
        livro=livro
    )