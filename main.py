from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/inbox", response_class=FileResponse)
def read_login():
    return "templates/inbox_page.html"