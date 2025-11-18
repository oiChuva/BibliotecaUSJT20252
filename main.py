from pathlib import Path
from flask import Flask, request, redirect, send_file, send_from_directory, abort, Response, render_template
from passlib.context import CryptContext
from app.database import engine
from sqlalchemy import text
from datetime import datetime

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



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)