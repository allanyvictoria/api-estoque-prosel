from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.fornecedor import (
    FornecedorCreate,
    FornecedorResponse,
    FornecedorUpdate,
)
from app.services import fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

ERRO_400 = {"description": "Dados inválidos (ex.: CNPJ ou e-mail mal formatado)."}
ERRO_404 = {"description": "Fornecedor não encontrado."}
ERRO_409 = {"description": "CNPJ ou e-mail já cadastrado, ou fornecedor com produtos."}


@router.post(
    "",
    response_model=FornecedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar fornecedor",
    responses={400: ERRO_400, 409: ERRO_409},
)
def criar_fornecedor(schema: FornecedorCreate, db: Session = Depends(get_db)):
    return fornecedor_service.criar(db, schema)


@router.get(
    "",
    response_model=list[FornecedorResponse],
    summary="Listar fornecedores com paginação",
    responses={400: ERRO_400},
)
def listar_fornecedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return fornecedor_service.listar(db, skip=skip, limit=limit)


@router.get(
    "/{fornecedor_id}",
    response_model=FornecedorResponse,
    summary="Buscar fornecedor por ID",
    responses={404: ERRO_404},
)
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    return fornecedor_service.buscar_por_id(db, fornecedor_id)


@router.put(
    "/{fornecedor_id}",
    response_model=FornecedorResponse,
    summary="Atualizar fornecedor",
    responses={400: ERRO_400, 404: ERRO_404, 409: ERRO_409},
)
def atualizar_fornecedor(
    fornecedor_id: int, schema: FornecedorUpdate, db: Session = Depends(get_db)
):
    return fornecedor_service.atualizar(db, fornecedor_id, schema)


@router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir fornecedor",
    responses={404: ERRO_404, 409: ERRO_409},
)
def excluir_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor_service.excluir(db, fornecedor_id)
