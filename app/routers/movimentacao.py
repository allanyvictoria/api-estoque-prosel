from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.movimentacao import TipoMovimentacao
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse
from app.services import movimentacao_service

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

# Não há PUT/PATCH/DELETE: os registros são imutáveis (histórico de auditoria).


@router.post(
    "",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada ou saída (atualiza o estoque na mesma transação)",
    responses={
        400: {"description": "Dados inválidos ou estoque insuficiente."},
        404: {"description": "Produto não encontrado."},
    },
)
def criar_movimentacao(schema: MovimentacaoCreate, db: Session = Depends(get_db)):
    return movimentacao_service.criar(db, schema)


@router.get(
    "",
    response_model=list[MovimentacaoResponse],
    summary="Listar histórico com filtros por período, fornecedor, produto e tipo",
    responses={400: {"description": "Filtros inválidos."}},
)
def listar_movimentacoes(
    data_inicio: date | None = Query(None, description="AAAA-MM-DD"),
    data_fim: date | None = Query(None, description="AAAA-MM-DD (inclusive)"),
    fornecedor_id: int | None = None,
    produto_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return movimentacao_service.listar(
        db,
        skip=skip,
        limit=limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
        fornecedor_id=fornecedor_id,
        produto_id=produto_id,
        tipo=tipo,
    )


@router.get(
    "/{movimentacao_id}",
    response_model=MovimentacaoResponse,
    summary="Buscar movimentação por ID",
    responses={404: {"description": "Movimentação não encontrada."}},
)
def buscar_movimentacao(movimentacao_id: int, db: Session = Depends(get_db)):
    return movimentacao_service.buscar_por_id(db, movimentacao_id)
