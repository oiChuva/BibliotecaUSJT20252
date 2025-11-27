from flask import render_template, session, redirect, url_for, request
from sqlalchemy import text
from app.database import engine

def login_user(pwd_context):
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", erro="Email e senha não podems er vazios.")

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