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
import sqlite3

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

@app.get("/welcome_session",status_code=401)
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


@app.get("/welcome_token",status_code=401)
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
        response.status_code = 401

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


@app.get("/categories", status_code=200)
def root():
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        names = cursor.execute("SELECT CategoryName FROM Categories ORDER BY Categories.CategoryId").fetchall()
        ids= cursor.execute("SELECT CategoryID FROM Categories ORDER BY Categories.CategoryId").fetchall()
        lista=[]
        for i in range(len(names)):
            lista.append({"id": ids[i][0], "name": names[i][0]})
        return {"categories": lista}


@app.get("/customers", status_code=200)
def root():
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        names = cursor.execute("SELECT CompanyName FROM Customers ORDER BY Customers.CustomerID").fetchall()
        ids= cursor.execute("SELECT CustomerID FROM Customers ORDER BY Customers.CustomerID ").fetchall()
        address = cursor.execute("SELECT Address FROM Customers ORDER BY Customers.CustomerID").fetchall()
        code = cursor.execute("SELECT PostalCode FROM Customers ORDER BY Customers.CustomerID").fetchall()
        city = cursor.execute("SELECT City FROM Customers ORDER BY Customers.CustomerID").fetchall()
        country = cursor.execute("SELECT Country FROM Customers ORDER BY Customers.CustomerID").fetchall()
        lista=[]
        for i in range(len(names)):
            # if i == 84:
            #     i=83
            # elif i==85:
            #     i=84
            # elif i==86:
            #     i=85
            # elif i==83:
            #     i=86
            if (address[i][0] and code[i][0])and(city[i][0] and country[i][0]):
                full = address[i][0]+" " + code[i][0] + " " + city[i][0]+" "+country[i][0]
            else:
                full=None
            lista.append({"id": ids[i][0], "name": names[i][0], "full_address":full})
        return {"customers": lista}

@app.get("/products/{id}")
def root(response: Response,id:int):
    idi=id
    with sqlite3.connect("northwind.db") as connection:
        connection.text_factory = lambda b: b.decode(errors="ignore")
        cursor = connection.cursor()
        name = cursor.execute("SELECT ProductName FROM Products WHERE ProductID = ?",(idi,)).fetchall()
        if name:
            response.status_code =200
            return {"id": idi, "name": name[0][0]}
        else:
            response.status_code = 404

@app.get("/employees")
def root(limit:int, offset:int, order:str,response: Response):
    if order=="first_name":
        a="FirstName"
    elif order=="last_name":
        a="LastName"
    elif order=="city":
        a="City"
        print("ddddddd")
    else:
        response.status_code = 400
        a="EmployeeID"
    if a:
        with sqlite3.connect("northwind.db") as connection:
            connection.text_factory = lambda b: b.decode(errors="ignore")
            cursor = connection.cursor()
            data = cursor.execute(f"""SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY {a} LIMIT {limit} OFFSET {offset} ;""").fetchall()
            lista=[]
            for i in range(len(data)):
                lista.append({"id": data[i][0], "last_name": data[i][1], "first_name":data[i][2], "city":data[i][3] })
            return {"employees": lista}
