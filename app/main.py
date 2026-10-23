from fastapi import FastAPI

app = FastAPI(title="API Estoque Prosel", version="1.0.0", description="API para gerenciamento de estoque de uma loja de variedades: produtos, fornecedores, categorias e movimentações.")

@app.get("/health")
def health_check():
    return {"status": "ok"}