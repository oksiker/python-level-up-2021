from fastapi import FastAPI, Response, status
import hashlib
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
from pydantic import BaseModel
from datetime import timedelta

app = FastAPI()
app.counter = 0
app.dicti = {}

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
    letters =0;
    for i in item.name:
        if item.name[i].isalpha():
            letters += 1
    for i in item.surname:
        if item.surname[i].isalpha():
            letters += 1
    
    register_date = datetime.today()
    json= {
        "id": app.counter,
        "name": item.name,
        "surname": item.surname,
        "register_date": register_date.strftime('%Y-%m-%d'),
        "vaccination_date": (register_date + timedelta(days=letters).strftime('%Y-%m-%d'))
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

    
