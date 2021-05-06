from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
    
@app.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"