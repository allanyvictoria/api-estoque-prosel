from fastapi import FastAPI
from app.core.exceptions import registrar_handlers


app = FastAPI(title="API Estoque Prosel", version="1.0.0", description="API para " \
"gerenciamento de estoque de uma loja de variedades: produtos, fornecedores, categorias e movimentações.")

registrar_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}