from fastapi import FastAPI


app = FastAPI()

@app.get("/buscarVoos")
def home():
    
    return ""


@app.post("/cadastrarVoo")
def cadastrar_voo():
   
    
    return {"error": "Erro ao cadastrar voo"}