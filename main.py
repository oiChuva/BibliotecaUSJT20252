import random
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from app.database import engine
from sqlalchemy import text
from datetime import datetime
import uvicorn
from fastapi.responses import RedirectResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
login_html_path = BASE_DIR / "assets" / "html" / "login.html"
second_html_path = BASE_DIR / "assets" / "html" / "second.html"
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")

# def test_databaseGET(id):
#     with engine.connect() as conn:
#         result = conn.execute(text(f"SELECT * FROM usuarios WHERE id_usuario = :id"),{"id" : id})
#         rows = result.fetchall()  
#         for row in rows:
#             print(row)

# def test_databasePOST():
#     randomizer = uuid.uuid4().hex[:3]
#     randomizerNumber = f"{int(randomizer[:2], 16) % 100:02d}"
#     with engine.begin() as conn:
#         result = conn.execute(text("""INSERT INTO usuarios 
#                                     (nome_completo, data_nascimento, email, cpf, senha, tipo, data_criacao) 
#                                     VALUES (:nome, :nasc, :email, :cpf, :senha, :tipo, :data_criacao)"""),
#                                             {"nome": "gustavo test code",
#                                             "nasc": "2002-12-31",
#                                             "email": f"{randomizer}@gmail.com",
#                                             "cpf": f"444444444{randomizerNumber}",
#                                             "senha": "senhasemcriptografia",
#                                             "tipo": "admin",
#                                             "data_criacao": datetime.now().date()})

#         return result.lastrowid

# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

# # Press the green button in the gutter to run the script.
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.get("/test-page", response_class=HTMLResponse)
async def test_page():
    return FileResponse(login_html_path, media_type="text/html")

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """
    Login apenas com email e senha.
    Espera um form HTML com campos name="email" e name="password".
    """
    # consulta usuário pelo email
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id_usuario, senha, nome_completo FROM usuarios WHERE email = :email"),
            {"email": email}
        )
    row = result.mappings().fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # obtém a senha armazenada (pode vir como tuple/row)
    try:
        stored = row["senha"]
    except Exception:
        stored = row[1]

    # se o valor for bytes, decodifica
    if isinstance(stored, (bytes, bytearray)):
        try:
            stored = stored.decode()
        except Exception:
            pass

    # verifica senha: se estiver em formato bcrypt usa passlib, caso contrário compara direto
    if isinstance(stored, str) and (stored.startswith("$2a$") or stored.startswith("$2b$") or stored.startswith("$2y$")):
        valid = pwd_context.verify(password, stored)
    else:
        valid = (password == stored)

    if not valid:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    
    return RedirectResponse(
    url=f"/second-page?name={row['nome_completo']}&id={row['id_usuario']}",
    status_code=303
    )

    # em produção devolva token/JWT em vez de dados sensíveis
    #return JSONResponse({"status": "ok", "user_id": row["id_usuario"], "name": row.get("nome_completo")})

@app.get("/second-page", response_class=HTMLResponse)
async def second_page(request: Request):
    name = request.query_params.get("name", "Usuário")
    user_id = request.query_params.get("id", "Desconhecido")

    html = f"""
    <html>
        <head><title>Second Page</title></head>
        <body>
            <h1>Bem-vindo, {name}!</h1>
            <p>Seu ID é: {user_id}</p>
        </body>
    </html>
    """

    return HTMLResponse(html)
