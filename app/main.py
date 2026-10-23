from fastapi import FastAPI

app = FastAPI(title="API Estoque Prosel", version="1.0.0", description="API para gerenciamento de estoque de um restaurante.")

@app.get("/health")
def health_check():
    return {"status": "ok"}