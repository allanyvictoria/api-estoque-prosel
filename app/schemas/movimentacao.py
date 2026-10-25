from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.movimentacao import TipoMovimentacao


class MovimentacaoCreate(BaseModel):
    tipo: TipoMovimentacao
    produto_id: int
    quantidade: int = Field(..., gt=0)


class MovimentacaoResponse(BaseModel):
    id: int
    tipo: TipoMovimentacao
    produto_id: int
    quantidade: int
    data: datetime

    model_config = ConfigDict(from_attributes=True)
