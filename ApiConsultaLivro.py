from fastapi import FastAPI
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DECIMAL

DATABASE_URL = "postgresql://admin:S5sou6y5U6PiQHnFbQQDiDDcSRSCxSpf@dpg-d493atf5r7bs738u8f4g-a.oregon-postgres.render.com:5432/dbaulasdrummond"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, 
                            bind=engine)
Base = declarative_base()

# -------------------- Banco de Dados --------------------
# Modelo de tabela
class Livro(Base):
    __tablename__ = "livros"
    titulo = Column(String(200))
    preco = Column(DECIMAL(15, 2))
    disponibilidade = Column(Boolean)
    avaliacao = Column(DECIMAL(10))
    pagina = Column(DECIMAL(10))

# -------------------- FastAPI App --------------------
app = FastAPI(
    title="API de Consulta Livros",
    description="Serviço simples de consulta de livros",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # Ou ["*"] para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/livros")
def listar_livros(db=Depends(get_db)):
    livros = db.query(Livro.titulo, Livro.preco).all()
    return livros

@app.get("/livro/{nome}")
def get_livro(nome: str, db=Depends(get_db)):
    livro = db.query(Livro).filter(Livro.titulo == nome).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)