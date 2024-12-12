from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Response
from pydantic import BaseModel


SQLITE_DATABASE_URL = "sqlite:///./note.db"

engine = create_engine(
    SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(servers=[{
    'url': 'http://192.168.110.135:8000'
}])


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReadQueryPayload(BaseModel):
    sql: str


@app.get('/list/table')
async def list_table(db: Session = Depends(get_db)):
    return [i[0] for i in db.execute(text('SELECT name FROM sqlite_master WHERE type = "table"')).fetchall()]

@app.get('/describe/table/{name}')
async def list_table(name: str, db: Session = Depends(get_db)):
    return [{"cid": i[0], 'name': i[1], 'type': i[2], 'notnull': i[3], 'dflt_value': i[4], 'pk': i[5]}  for i in db.execute(text(f'PRAGMA table_info("{name}")')).fetchall()]

@app.post('/read/query')
async def list_table(payload: ReadQueryPayload, db: Session = Depends(get_db)):
    return db.execute(text(payload.sql)).fetchall()

