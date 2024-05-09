from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from models import Email, Base
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import timezone, datetime as dt

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

@app.get("/getunreademailsnumber")
def get_unread_emails_number(email: str, db: Session = Depends(get_db)):
    return db.query(func.count(Email.id)).filter(and_(Email.recipient == email, Email.read == False)).scalar()

@app.get("/getsent")
def get_sent_emails(email: str, db: Session = Depends(get_db)):
    return db.query(Email).filter(Email.sender == email).all()

@app.get("/getstared")
def get_stared_emails(email: str, db: Session = Depends(get_db)):
    return db.query(Email).filter(or_(and_(Email.sender == email, Email.starred_by_sender == True), and_(Email.recipient == email, Email.starred_by_recepient == True))).all()

@app.post("/starunstar")
async def star_unstar_email(email_id: int, email: str, db: Session = Depends(get_db)):
    email_data = db.query(Email).filter(Email.id == email_id).first()
    if email_data:
        if email_data.sender == email:
            setattr(email_data, "starred_by_sender", not email_data.starred_by_sender)
        elif email_data.recipient == email:
            setattr(email_data, "starred_by_recepient", not email_data.starred_by_recepient)
        db.commit()
        return {"message": "Email updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

@app.post("/reademail")
async def read_email(email_id: int, email: str, db: Session = Depends(get_db)):
    email_data = db.query(Email).filter(Email.id == email_id).first()
    if email_data and email_data.recipient == email:
        setattr(email_data, "read", True)
        db.commit()
        return {"message": "Email updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

@app.post("/sendemail")
async def send_email(form_data: EmailForm, db: Session = Depends(get_db)):
    now = dt.now(timezone.utc)
    timestamp = dt.isoformat(now)
    email = Email(sender=form_data.sender, recipient=form_data.recipient, subject=form_data.subject, message=form_data.message, timestamp=timestamp, read=False, starred_by_recepient=False, starred_by_sender=False)
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
