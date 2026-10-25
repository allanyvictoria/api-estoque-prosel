from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.categoria import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
)
from app.services import categoria_service
from fastapi import Query

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar uma nova categoria",
    responses={
        400: {"description": "Requisição inválida: Dados de entrada incorretos."},
        409: {"description": "Conflito: Já existe uma categoria com este nome."},
    },
)
def criar_categoria(schema: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_service.criar(db, schema)


@router.get(
    "",
    response_model=list[CategoriaResponse],
    summary="Listar categorias com paginação",
)
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return categoria_service.listar(db, skip=skip, limit=limit)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Buscar categoria por ID",
    responses={404: {"description": "Não encontrado: Categoria não existe."}},
)
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return categoria_service.buscar_por_id(db, categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Atualizar categoria existente",
    responses={
        400: {"description": "Requisição inválida: Dados de entrada incorretos."},
        404: {"description": "Não encontrado: Categoria não existe."},
        409: {"description": ("Conflito: O novo nome já pertence a outra categoria.")},
    },
)
def atualizar_categoria(
    categoria_id: int, schema: CategoriaUpdate, db: Session = Depends(get_db)
):
    return categoria_service.atualizar(db, categoria_id, schema)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria",
    responses={
        404: {"description": "Não encontrado: Categoria não existe."},
        409: {
            "description": ("Conflito: Existem produtos vinculados a esta categoria.")
        },
    },
)
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria_service.excluir(db, categoria_id)
    return None
