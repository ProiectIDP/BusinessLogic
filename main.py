from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Email, Base
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class EmailForm(BaseModel):
    sender: str
    recipient: str
    subject: str
    message: str

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/getinbox")
def get_inbox_emails(email: str, db: Session = Depends(get_db)):
    return db.query(Email).filter(Email.recipient == email).all()

@app.get("/getsent")
def get_sent_emails(email: str, db: Session = Depends(get_db)):
    return db.query(Email).filter(Email.sender == email).all()

@app.get("/getstared")
def get_stared_emails(email: str, db: Session = Depends(get_db)):
    return db.query(Email).filter(or_(Email.sender == email, Email.recipient == email), Email.starred == True).all()

@app.post("/starunstar")
async def star_unstar_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if email:
        setattr(email, "starred", not email.starred)
        db.commit()
        return {"message": "Email updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

@app.post("/reademail")
async def read_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if email:
        setattr(email, "read", True)
        db.commit()
        return {"message": "Email updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

@app.post("/sendemail")
async def send_email(form_data: EmailForm, db: Session = Depends(get_db)):
    email = Email(sender=form_data.sender, recipient=form_data.recipient, subject=form_data.subject, message=form_data.message, read=False, starred=False)
    db.add(email)
    db.commit()
    return {"message": "succes"}

@app.get("/inbox", response_class=FileResponse)
def read_login():
    return "templates/inbox_page.html"

@app.get("/sent", response_class=FileResponse)
def read_login():
    return "templates/sent_page.html"

@app.get("/stared", response_class=FileResponse)
def read_login():
    return "templates/stared_page.html"
