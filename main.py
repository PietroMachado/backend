import databases, sqlalchemy
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import List

# MODELO
# DATABASE_URL="postgresql://username@localhost:5432/dbname"
DATABASE_URL="postgresql://username@localhost:5432/testdb"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
app = FastAPI()


filmes = sqlalchemy.Table(
    # Na linha seguinte deve ser inserido o nome escolhido para a tabela
    "filmes",
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('titulo', sqlalchemy.String),
    sqlalchemy.Column('diretor', sqlalchemy.String),
    sqlalchemy.Column('genero', sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)


class ListFilmes(BaseModel):
    id : str
    titulo: str
    diretor: str
    genero: str


class ClasseGenerica(BaseModel):
    id: str = Field(..., example='id')
    titulo: str = Field(..., example='titulo')
    diretor: str = Field(..., example='diretor')
    genero: str = Field(..., example='genero')


# Inicia a conexão com o banco
@app.on_event("startup")
async def startup():
    await database.connect()


# Encerra a conexão com o banco
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Função responsável pela listagem de todos os filmes
@app.get("/filmes", response_model=List[ListFilmes])
async def listar_filmes_cadastrados():
    query = filmes.select()
    return await database.fetch_all(query)


# Função resposável por cadastrar um novo filme
@app.post("/filmes", response_model=ListFilmes)
async def cadastrar_filme(filme: ClasseGenerica):
    query = filmes.insert().values(
        id = filme.id,
        titulo = filme.titulo,
        diretor = filme.diretor,
        genero = filme.genero,
    )

    await database.execute(query)
    return {
        **filme.dict(),
    }


# Função responsável por retornar um filme de acordo com seu id
@app.get("/filmes/{id}", response_model=ListFilmes)
async def retornar_filme_por_id(id: str):
    query = filmes.select().where(filmes.c.id == id)
    return await database.fetch_one(query)


# Função responsável por retornar todos os filmes com o gênero indicado
@app.get("/filmes/genero/{genero}", response_model=List[ListFilmes])
async def listar_por_genero(genero: str):
    query = filmes.select().where(filmes.c.genero == genero)
    return await database.fetch_all(query)


# Função responsável por editar as informações de um filme
@app.put("/filmes/{id}", response_model=ListFilmes)
async def editar_filme(id: str, filme: ClasseGenerica):
    query = filmes.update().where(filmes.c.id == id).values(
        titulo = filme.titulo,
        diretor = filme.diretor,
        genero = filme.genero,
    )
    await database.execute(query)
    return await retornar_filme_por_id(id)


# Função reposável por apagar um filme da tabela
@app .delete("/filmes/{id}")
async def apagar_filme(id: str):
    query = filmes.delete().where(filmes.c.id == id)
    await database.execute(query)
    return {
        "message": "Filme deletado com sucesso"
    }
