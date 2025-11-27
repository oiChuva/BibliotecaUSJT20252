import json
from datetime import date, datetime

from flask import Response
from sqlalchemy import text

from app.database import engine


def buscar_livros_conn():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM livros"))
        rows = result.mappings().all()  # lista de dicts
    livros = []
    for row in rows:
        livro = dict(row)

        for key, value in livro.items():
            if isinstance(value, (datetime, date)):
                livro[key] = value.isoformat()
        livros.append(livro)

    return Response(
        json.dumps(livros, ensure_ascii=False, indent=4),
        mimetype="application/json"
    )
