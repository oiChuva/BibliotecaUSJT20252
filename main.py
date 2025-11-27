import os
from pathlib import Path
from flask import Flask, send_from_directory, render_template
from passlib.context import CryptContext

#controladores
from controllers.decorators_controller import *
from controllers.login_controller import login_user
from controllers.cadastro_controller import cadastro_livro_page
from controllers.edit_controller import editar_livro_conn
from controllers.delete_controller import excluir_livro_conn
from controllers.search_controller import buscar_livros_conn

#renders
from renders.livros_render import livros_lista_page
from renders.livro_detalhes_render import livro_detalhes_page

#formulários
from forms.cadastro_form import cadastrar_livro_form
from forms.edit_form import editar_livro_form

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
    return login_user(pwd_context)

@app.route("/livros", methods=["GET"])
@login_required
def livros_lista():
    return livros_lista_page()

@app.route("/cadastro-livro", methods=["GET"])
@login_required
def cadastro_livro_p():
    return cadastro_livro_page()

@app.route("/cadastro-livro", methods=["POST"])
@login_required
def cadastro_livro():
    return cadastrar_livro_form()

@app.route("/livro/<int:id_livro>", methods=["GET"])
@login_required
def livro_detalhes(id_livro):
    return livro_detalhes_page(id_livro)

@app.route("/editar-livro/<int:id_livro>", methods=["GET"])
@login_required
def editar_livro_page(id_livro):
    return editar_livro_conn(id_livro)

@app.route("/editar-livro/<int:id_livro>", methods=["POST"])
@login_required
def editar_livro(id_livro):
    return editar_livro_form(id_livro)

@app.route("/excluir-livro/<int:id_livro>", methods=["POST"])
@login_required
def excluir_livro(id_livro):
    return excluir_livro_conn(id_livro)


# req trazer livros
@app.route("/buscar-livros", methods=["GET"])
def buscar_livros():
    return buscar_livros_conn()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
