from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from app.services import produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos"])

ERRO_400 = {"description": "Dados inválidos."}
ERRO_404 = {"description": "Produto, categoria ou fornecedor não encontrado."}
ERRO_409 = {"description": "SKU já cadastrado ou produto com movimentações."}


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto (nasce com estoque 0)",
    responses={400: ERRO_400, 404: ERRO_404, 409: ERRO_409},
)
def criar_produto(schema: ProdutoCreate, db: Session = Depends(get_db)):
    return produto_service.criar(db, schema)


@router.get(
    "",
    response_model=list[ProdutoResponse],
    summary="Listar produtos com filtros e paginação",
    responses={400: ERRO_400},
)
def listar_produtos(
    nome: str | None = Query(None, description="Busca parcial pelo nome"),
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return produto_service.listar(
        db,
        skip=skip,
        limit=limit,
        nome=nome,
        categoria_id=categoria_id,
        fornecedor_id=fornecedor_id,
    )


# Precisa vir ANTES de "/{produto_id}", senão "estoque-minimo" seria lido como um ID.
@router.get(
    "/estoque-minimo",
    response_model=list[ProdutoResponse],
    summary="Produtos com estoque no mínimo ou abaixo dele",
    responses={400: ERRO_400},
)
def listar_estoque_minimo(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return produto_service.listar_estoque_minimo(db, skip=skip, limit=limit)


@router.get(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Buscar produto por ID",
    responses={404: ERRO_404},
)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    return produto_service.buscar_por_id(db, produto_id)


@router.put(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar produto (não altera o saldo de estoque)",
    responses={400: ERRO_400, 404: ERRO_404, 409: ERRO_409},
)
def atualizar_produto(
    produto_id: int, schema: ProdutoUpdate, db: Session = Depends(get_db)
):
    return produto_service.atualizar(db, produto_id, schema)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto sem movimentações",
    responses={404: ERRO_404, 409: ERRO_409},
)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto_service.excluir(db, produto_id)
