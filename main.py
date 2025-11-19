from pathlib import Path
from flask import Flask, request, redirect, send_file, send_from_directory, abort, Response, render_template, url_for
from passlib.context import CryptContext
from app.database import engine
from sqlalchemy import text
from datetime import datetime, date
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGIN_HTML = ASSETS_DIR / "html" / "login.html"
SECOND_HTML = ASSETS_DIR / "html" / "second.html"
app = Flask(__name__, template_folder=str(BASE_DIR / "assets" / "html"))

# serve static assets under /assets/...
@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)

# serve login page
@app.route("/test-page", methods=["GET"])
def test_page():
    if LOGIN_HTML.exists():
        return send_file(LOGIN_HTML)
    return Response("<h1>Login page not found</h1>", status=404)

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
        abort(401)

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
        abort(401)

    # LOGIN OK → enviar dados ao second.html usando render_template
    return render_template(
        "livros.html",
        name=row.get("nome_completo"),
        user_id=row.get("id_usuario")
    )

# second page (GET – opcional)
@app.route("/livros", methods=["GET"])
def second_page():
    name = request.args.get("name", "")
    user_id = request.args.get("id", "")

    return render_template("livros.html", name=name, user_id=user_id)

@app.route("/cadastro-livro", methods=["GET"])
def cadastro_livro():
    return render_template("cadastro-livro.html", name='name', user_id='user_id')

@app.route("/cadastrar-livro", methods=["POST"])
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

    return redirect(url_for("second_page"))



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