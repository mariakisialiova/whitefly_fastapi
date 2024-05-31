from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, JSONResponse

from models import SessionLocal, User, Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/form")
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/submit")
async def submit(request: Request, name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "User with this email already exists."
        })
    try:
        new_user = User(name=name, email=email)
        db.add(new_user)
        db.commit()
        return RedirectResponse(url="/confirmation", status_code=303)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": f"An error occurred: {str(e)}"
        })


@app.get("/confirmation")
async def confirmation(request: Request):
    return templates.TemplateResponse("confirmation.html", {"request": request})
