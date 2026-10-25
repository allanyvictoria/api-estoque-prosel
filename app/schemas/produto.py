from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    preco_custo: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    preco_venda: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    estoque_minimo: int = Field(0, ge=0)
    categoria_id: int
    fornecedor_id: int

    model_config = ConfigDict(str_strip_whitespace=True)


class ProdutoUpdate(ProdutoCreate):
    pass


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    sku: str
    preco_custo: Decimal
    preco_venda: Decimal
    quantidade_em_estoque: int
    estoque_minimo: int
    data_cadastro: datetime
    categoria_id: int
    fornecedor_id: int

    model_config = ConfigDict(from_attributes=True)
