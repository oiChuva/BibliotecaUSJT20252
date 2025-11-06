import random
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.database import engine
from sqlalchemy import text
from datetime import datetime
import uvicorn

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
local_html_path = BASE_DIR / "assets" / "html" / "login.html"
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
    return FileResponse(local_html_path, media_type="text/html")
