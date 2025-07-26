from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
import time, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
time.sleep(5)  # attendre MySQL

db = pymysql.connect(
    host=os.environ.get("MYSQL_HOST", "mysql"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", "password"),
    database=os.environ.get("MYSQL_DATABASE", "eurostar"),
    cursorclass=pymysql.cursors.DictCursor
)

class AssistanceForm(BaseModel):
    nom: str
    prenom: str
    genre: str
    age: int
    email: str
    handicap: str
    autre_handicap: str = None

@app.post("/assistance")
async def assistance(data: AssistanceForm):
    with db.cursor() as cursor:
        sql = """
            INSERT INTO assistance (nom, prenom, genre, age, email, handicap, autre_handicap)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (data.nom, data.prenom, data.genre, data.age, data.email, data.handicap, data.autre_handicap))
    db.commit()
    return {"message": "Demande d'assistance enregistrée."}