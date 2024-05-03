from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from models import Email, Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/inbox", response_class=FileResponse)
def read_login():
    return "templates/inbox_page.html"

@app.get("/sent", response_class=FileResponse)
def read_login():
    return "templates/sent_page.html"

@app.get("/stared", response_class=FileResponse)
def read_login():
    return "templates/stared_page.html"
