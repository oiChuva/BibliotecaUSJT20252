from flask import render_template, session

def cadastro_livro_page():
    user_name = session.get("user_name")
    user_id = session.get("user_id")
    return render_template(
        "cadastro-livro.html",
        name=user_name,
        user_id=user_id
    )