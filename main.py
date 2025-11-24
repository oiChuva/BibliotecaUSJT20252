import json
import os
from datetime import datetime, date
from pathlib import Path

from flask import Flask, request, send_from_directory, abort, Response, render_template
from passlib.context import CryptContext
from sqlalchemy import text

from app.database import engine
from decorators import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGIN_HTML = ASSETS_DIR / "html" / "login.html"

app = Flask(__name__, template_folder=str(BASE_DIR / "assets" / "html"))
app.secret_key = os.urandom(32)  # necessária para usar session


# serve static assets under /assets/...
@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route("/")
def home():
    return redirect(url_for("login"))


# login GET
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# login POST
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    if not email or not password:
        abort(400)

    # verify from DB
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id_usuario, senha, nome_completo FROM usuarios WHERE email = :email"),
            {"email": email}
        )
        row = result.mappings().fetchone()

    if not row:
        return render_template("login.html", erro="Email ou senha inválidos!")

    stored = row.get("senha")

    if isinstance(stored, (bytes, bytearray)):
        try:
            stored = stored.decode()
        except:
            pass

    # bcrypt or plaintext
    if stored.startswith("$2"):
        valid = pwd_context.verify(password, stored)
    else:
        valid = (password == stored)

    if not valid:
        return render_template("login.html", erro="Erro ao descriptografar a senha.")

    # LOGIN OK → armazenar os dados na session e redirecionar para a pagina principal
    session["user_id"] = row.get("id_usuario")
    session["user_name"] = row.get("nome_completo")
    return redirect(url_for("livros_lista_page"))


@app.route("/livros", methods=["GET"])
@login_required
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


@app.route("/cadastro-livro", methods=["GET"])
@login_required
def cadastro_livro():
    user_name = session.get("user_name")
    user_id = session.get("user_id")
    return render_template(
        "cadastro-livro.html",
        name=user_name,
        user_id=user_id
    )


@app.route("/cadastro-livro", methods=["POST"])
@login_required
def cadastrar_livro():
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


@app.route("/livro/<int:id_livro>", methods=["GET"])
@login_required
def livro_detalhes(id_livro):
    user_name = session.get("user_name")
    user_id = session.get("user_id")

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM livros WHERE id_livro = :id"),
            {"id": id_livro}
        ).mappings().fetchone()

    if not result:
        abort(404)

    livro = dict(result)

    # converter datas se houver
    for k, v in livro.items():
        if isinstance(v, (datetime, date)):
            livro[k] = v.isoformat()

    return render_template(
        "detalhes-livro.html",
        name=user_name,
        user_id=user_id,
        livro=livro
    )


# req trazer livros
@app.route("/buscar-livros", methods=["GET"])
def buscar_livros():
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
