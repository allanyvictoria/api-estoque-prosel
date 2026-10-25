from fastapi import FastAPI
from app.core.exceptions import registrar_handlers
from app.routers import categoria, fornecedor, movimentacao, produto

app = FastAPI(
    title="API Estoque Prosel",
    version="1.0.0",
    description="API para "
    "gerenciamento de estoque de uma loja de variedades: produtos, fornecedores, categorias e movimentações.",
)

registrar_handlers(app)

app.include_router(categoria.router)
app.include_router(fornecedor.router)
app.include_router(produto.router)
app.include_router(movimentacao.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
