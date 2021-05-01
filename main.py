from fastapi import FastAPI, Response, status,HTTPException, Cookie, Depends
import hashlib
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
from pydantic import BaseModel
from datetime import timedelta
from fastapi.responses import HTMLResponse,ORJSONResponse,PlainTextResponse
from hashlib import sha256
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse 


app = FastAPI()
app.counter = 0
app.dicti = {}
app.secret_key = "qwertyuiop"
app.access_tokens = []
app.access_tokens1 = []
security = HTTPBasic()
app.counter=0

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
@app.get("/hello", response_class=HTMLResponse)
def root():
    register_date = datetime.today()
    data = register_date.strftime('%Y-%m-%d')
    return """
    <html>
        <h1>Hello! Today date is """+ data +"""</h1>
    </html>
    """

@app.post("/login_session")
def login(credentials: HTTPBasicCredentials = Depends(security), response: Response=None):
    login = credentials.username
    password = credentials.password
    if (login=="4dm1n" )& (password=="NotSoSecurePa$$"):
        session_token = sha256(f"{login}{password}{app.secret_key}{str(app.counter)}".encode()).hexdigest()
        if len(app.access_tokens)==3:
            app.access_tokens.remove(app.access_tokens[0])
        app.access_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
        app.counter+=1
        response.status_code = 201
    else:
        response.status_code = 401


@app.post("/login_token")
def login(response: Response,credentials: HTTPBasicCredentials = Depends(security)):
    login = credentials.username
    password = credentials.password
    if (login=="4dm1n" ) & (password=="NotSoSecurePa$$"):
        session_token = sha256(f"{login}{password}{app.secret_key}{str(app.counter)}".encode()).hexdigest()
        if len(app.access_tokens1)==3:
            app.access_tokens1.remove(app.access_tokens1[0])
        app.access_tokens1.append(session_token)
        response.status_code = 201
        app.counter+=1
        return {"token": session_token}
    else:
        response.status_code = 401

@app.get("/welcome_session")
def welcome(*, response: Response, session_token: str = Cookie(None), format:str=""):
    if (session_token in app.access_tokens1)|(session_token in app.access_tokens):
        response.status_code = 200
        if format=="json":
            return {"message": "Welcome!"}
        elif format=="html":
            return HTMLResponse(status_code=200, content="""<h1>Welcome!</h1>""")
        else:
            return PlainTextResponse(status_code=200,content="Welcome!")
    else:
        esponse.status_code = 401


@app.get("/welcome_token")
def welcome(response: Response,token: str = '', format:str=""):
    if (token in app.access_tokens)|(token in app.access_tokens1):
        response.status_code = 200
        if format=="json":
            return {"message": "Welcome!"}
        elif format=="html":
            return HTMLResponse(status_code=200, content="""<h1>Welcome!</h1>""")
        else:
            return PlainTextResponse(status_code=200,content="Welcome!")
    else:
        response.status_code = 401


@app.delete("/logout_session")
def fun(*, response: Response, session_token: str = Cookie(None), format:str=""):
    if (session_token in app.access_tokens1):
        app.access_tokens1.remove(session_token)
        rr = RedirectResponse('/logged_out?format={format}', status_code=303)
        return rr
    elif(session_token in app.access_tokens):
        app.access_tokens.remove(session_token)
        rr = RedirectResponse('/logged_out?format={format}', status_code=303)
        return rr
    else:
        esponse.status_code = 401

@app.delete("/logout_token")
def fun(response: Response,token: str = '', format:str=""):
    if (token in app.access_tokens1):
        app.access_tokens1.remove(token)
        rr = RedirectResponse(f'/logged_out?format={format}', status_code=303)
        return rr
    elif(token in app.access_tokens):
        app.access_tokens.remove(token)
        rr = RedirectResponse(f'/logged_out?format={format}', status_code=303)
        return rr
    else:
        response.status_code = 401

@app.get("/logged_out")
def fun(response: Response, format:str=""):
    if format=="json":
        response.status_code = 200
        return {"message": "Logged out!"}
    elif format=="html":
        return HTMLResponse(status_code=200, content="""<h1>Logged out!</h1>""")
    else:
        return PlainTextResponse(status_code=200,content="Logged out!")

