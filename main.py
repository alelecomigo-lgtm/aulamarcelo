from fastapi import FastAPI
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DECIMAL

DATABASE_URL = "postgresql://admin:N3ggq9r65Yx15dUZ4kC5m7lyNzoLJeHD@dpg-d4b9ks75r7bs7391csug-a.oregon-postgres.render.com/dbalexandre"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, 
                            bind=engine)
Base = declarative_base()
# -------------------- Banco de Dados --------------------
# Modelo de tabela
class Livro(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), index=True)    
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
    # Modificação: Usar db.query(Livro).all() para retornar TODOS os campos de cada objeto Livro.
    livros = db.query(Livro).all()
    return livros

@app.get("/livros/{livro_id}") 
def get_livro(livro_id: int, db=Depends(get_db)): # O parâmetro agora é um inteiro
    livro = db.query(Livro).filter(Livro.id == livro_id).first() # Busca pelo ID
    if not livro:
        raise HTTPException(status_code=404, detail=f"Livro com ID {livro_id} não encontrado")
    return livro

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=5001)