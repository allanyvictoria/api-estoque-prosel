from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def criar(db: Session, schema: CategoriaCreate) -> Categoria:
    # Verifica se já existe uma categoria com o mesmo nome
    stmt = select(Categoria).where(Categoria.nome == schema.nome)
    existente = db.scalar(stmt)

    if existente:
        raise ConflictError(
            f"Já existe uma categoria cadastrada com o nome '{schema.nome}'."
        )

    nova_categoria = Categoria(nome=schema.nome)
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Categoria]:
    stmt = select(Categoria).offset(skip).limit(limit).order_by(Categoria.id)
    return list(db.scalars(stmt).all())


def atualizar(db: Session, categoria_id: int, schema: CategoriaUpdate) -> Categoria:
    categoria = buscar_por_id(db, categoria_id)

    # Só checa duplicidade se o nome mudou, senão a própria categoria bloquearia a si mesma.
    if schema.nome != categoria.nome:
        stmt = select(Categoria).where(Categoria.nome == schema.nome)
        if db.scalar(stmt):
            raise ConflictError(
                f"Já existe outra categoria cadastrada com o nome '{schema.nome}'."
            )
        categoria.nome = schema.nome

    db.commit()
    db.refresh(categoria)
    return categoria


def excluir(db: Session, categoria_id: int) -> None:
    categoria = buscar_por_id(db, categoria_id)

    # Checamos antes para devolver mensagem clara;
    # o RESTRICT da FK é a última barreira se duas requisições chegarem juntas
    stmt_produto = select(Produto).where(Produto.categoria_id == categoria_id).limit(1)
    if db.scalar(stmt_produto):
        raise ConflictError(
            f"Não é possível excluir a categoria {categoria_id} pois existem"
            " produtos vinculados a ela."
        )

    db.delete(categoria)
    db.commit()


def buscar_por_id(db: Session, categoria_id: int) -> Categoria:
    stmt = select(Categoria).where(Categoria.id == categoria_id).limit(1)
    categoria = db.scalar(stmt)

    if not categoria:
        raise NotFoundError(f"Categoria {categoria_id} não encontrada.")

    return categoria
