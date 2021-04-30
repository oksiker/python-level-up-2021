from fastapi import FastAPI, Response, status,HTTPException,Cookie
import hashlib
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
from pydantic import BaseModel
from datetime import timedelta
from fastapi.responses import HTMLResponse
from hashlib import sha256


app = FastAPI()
app.counter = 0
app.dicti = {}
app.secret_key = "qwertyuiop"
app.access_tokens = ""
app.access_tokens1 = ""

@app.get("/")
def root():
    return {"message": "Hello world!"}

@app.get("/method")
def root():
    return {"method": "GET"}
    
@app.put("/method")
def root():
    return {"method": "PUT"}

@app.options("/method")
def root():
    return {"method": "OPTIONS"}

@app.delete("/method")
def root():
    return {"method": "DELETE"}

@app.post("/method", status_code=201)
def root():
    return {"method": "POST"}

@app.post("/method")
def root():
    return {"method": "POST"}

@app.get("/auth", status_code=401)
def root(response: Response, password='', password_hash=''):
    pass_hash = hashlib.sha512( password.encode("utf-8") ).hexdigest()
    if pass_hash != password_hash:
        response.status_code = 401
    elif not password:
        response.status_code = 401
    else:
        response.status_code = 204

class Item(BaseModel):
    name: str
    surname:str

@app.post("/register", status_code=201)
def root(item: Item):
    app.counter +=1
    letters =0
    for i in item.name:
        if str(i).isalpha():
            letters += 1
    for i in item.surname:
        if str(i).isalpha():
            letters += 1
    
    register_date = datetime.today()
    json= {
        "id": app.counter,
        "name": item.name,
        "surname": item.surname,
        "register_date": register_date.strftime('%Y-%m-%d'),
        "vaccination_date": ((register_date + timedelta(days=letters)).strftime('%Y-%m-%d'))
        }
    app.dicti[app.counter]=json
    return json

@app.get("/patient/{id}", status_code=200)
def root(id: int, response: Response):
    if id<1:
        response.status_code = 400
    else:
        if id in app.dicti.keys():
            return app.dicti[id]
        else:
            response.status_code = 404

    
#wyklad 3:
@app.get("/hello",response_class=HTMLResponse)
def root():
    register_date = datetime.today()
    data = register_date.strftime('%Y-%m-%d')
    return """
    <html>
        <h1>Hello! Today date is """+ data +"""</h1>
    </html>
    """

@app.post("/login_session")
def login(login: str, password: str, response: Response):
    if (login=="4dm1n" )& (password=="NotSoSecurePa$$"):
        session_token = sha256(f"{login}{password}{app.secret_key}".encode()).hexdigest()
        app.access_tokens=session_token
        response.set_cookie(key="session_token", value=session_token)
    else:
        response.status_code = 404


@app.post("/login_token")
def login(login: str, password: str, response: Response):
    if (login=="4dm1n" )& (password=="NotSoSecurePa$$"):
        session_token = sha256(f"{login}{password}{app.secret_key}".encode()).hexdigest()
        app.access_tokens1=session_token
        return {"token": "Secure Content"}
    else:
        response.status_code = 404

