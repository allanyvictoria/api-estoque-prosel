from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate


def _garantir_unicidade(
    db: Session, schema: FornecedorCreate, ignorar_id: int | None = None
) -> None:
    # Checamos antes do INSERT/UPDATE para devolver uma mensagem clara;
    # o UNIQUE do banco continua sendo a última barreira.
    por_cnpj = db.scalar(select(Fornecedor).where(Fornecedor.cnpj == schema.cnpj))
    if por_cnpj and por_cnpj.id != ignorar_id:
        raise ConflictError("Já existe um fornecedor cadastrado com este CNPJ.")

    por_email = db.scalar(select(Fornecedor).where(Fornecedor.email == schema.email))
    if por_email and por_email.id != ignorar_id:
        raise ConflictError("Já existe um fornecedor cadastrado com este e-mail.")


def criar(db: Session, schema: FornecedorCreate) -> Fornecedor:
    _garantir_unicidade(db, schema)
    fornecedor = Fornecedor(**schema.model_dump())
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Fornecedor]:
    stmt = select(Fornecedor).order_by(Fornecedor.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def buscar_por_id(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = db.scalar(
        select(Fornecedor).where(Fornecedor.id == fornecedor_id).limit(1)
    )
    if not fornecedor:
        raise NotFoundError(f"Fornecedor {fornecedor_id} não encontrado.")
    return fornecedor


def atualizar(db: Session, fornecedor_id: int, schema: FornecedorUpdate) -> Fornecedor:
    fornecedor = buscar_por_id(db, fornecedor_id)
    # ignorar_id evita que o próprio fornecedor bloqueie a si mesmo.
    _garantir_unicidade(db, schema, ignorar_id=fornecedor_id)
    for campo, valor in schema.model_dump().items():
        setattr(fornecedor, campo, valor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


def excluir(db: Session, fornecedor_id: int) -> None:
    fornecedor = buscar_por_id(db, fornecedor_id)
    # Checagem prévia para dar mensagem amigável; o RESTRICT da FK é a rede de segurança.
    tem_produto = db.scalar(
        select(Produto.id).where(Produto.fornecedor_id == fornecedor_id).limit(1)
    )
    if tem_produto is not None:
        raise ConflictError(
            f"Não é possível excluir o fornecedor {fornecedor_id}: "
            "existem produtos vinculados a ele."
        )
    db.delete(fornecedor)
    db.commit()
