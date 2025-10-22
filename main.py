import random
import uuid
from app.database import engine
from sqlalchemy import text
from datetime import datetime

def test_databaseGET(id):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM usuarios WHERE id_usuario = :id"),{"id" : id})
        rows = result.fetchall()  
        for row in rows:
            print(row)

def test_databasePOST():
    randomizer = uuid.uuid4().hex[:3]
    randomizerNumber = f"{int(randomizer[:2], 16) % 100:02d}"
    with engine.begin() as conn:
        result = conn.execute(text("""INSERT INTO usuarios 
                                    (nome_completo, data_nascimento, email, cpf, senha, tipo, data_criacao) 
                                    VALUES (:nome, :nasc, :email, :cpf, :senha, :tipo, :data_criacao)"""),
                                            {"nome": "gustavo test code",
                                            "nasc": "2002-12-31",
                                            "email": f"{randomizer}@gmail.com",
                                            "cpf": f"444444444{randomizerNumber}",
                                            "senha": "senhasemcriptografia",
                                            "tipo": "admin",
                                            "data_criacao": datetime.now().date()})

        return result.lastrowid

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    id = test_databasePOST()
    test_databaseGET(id)

