from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.categoria import Categoria
from app.models.fornecedor import Fornecedor
from app.models.movimentacao import Movimentacao
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


def _garantir_sku_livre(db: Session, sku: str) -> None:
    if db.scalar(select(Produto.id).where(Produto.sku == sku).limit(1)) is not None:
        raise ConflictError(f"Já existe um produto cadastrado com o SKU '{sku}'.")


def _validar_relacionamentos(
    db: Session, categoria_id: int, fornecedor_id: int
) -> None:
    # Validamos aqui para responder 404 claro, em vez de deixar a FK estourar no banco.
    if db.get(Categoria, categoria_id) is None:
        raise NotFoundError(f"Categoria {categoria_id} não encontrada.")
    if db.get(Fornecedor, fornecedor_id) is None:
        raise NotFoundError(f"Fornecedor {fornecedor_id} não encontrado.")


def criar(db: Session, schema: ProdutoCreate) -> Produto:
    _garantir_sku_livre(db, schema.sku)
    _validar_relacionamentos(db, schema.categoria_id, schema.fornecedor_id)
    # O produto nasce com estoque 0 (padrão do model): o saldo só muda por movimentação,
    # para que o histórico de auditoria sempre explique a quantidade atual.
    produto = Produto(**schema.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nome: str | None = None,
    categoria_id: int | None = None,
    fornecedor_id: int | None = None,
) -> list[Produto]:
    stmt = select(Produto)
    if nome:
        stmt = stmt.where(Produto.nome.ilike(f"%{nome}%"))
    if categoria_id is not None:
        stmt = stmt.where(Produto.categoria_id == categoria_id)
    if fornecedor_id is not None:
        stmt = stmt.where(Produto.fornecedor_id == fornecedor_id)
    stmt = stmt.order_by(Produto.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def listar_estoque_minimo(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Produto]:
    # "No mínimo ou abaixo" => quantidade <= estoque_minimo (o enunciado inclui a igualdade).
    stmt = (
        select(Produto)
        .where(Produto.quantidade_em_estoque <= Produto.estoque_minimo)
        .order_by(Produto.quantidade_em_estoque, Produto.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def buscar_por_id(db: Session, produto_id: int) -> Produto:
    produto = db.scalar(select(Produto).where(Produto.id == produto_id).limit(1))
    if not produto:
        raise NotFoundError(f"Produto {produto_id} não encontrado.")
    return produto


def atualizar(db: Session, produto_id: int, schema: ProdutoUpdate) -> Produto:
    produto = buscar_por_id(db, produto_id)
    if schema.sku != produto.sku:
        _garantir_sku_livre(db, schema.sku)
    _validar_relacionamentos(db, schema.categoria_id, schema.fornecedor_id)
    # O schema não tem quantidade_em_estoque, então editar o produto nunca burla a auditoria.
    for campo, valor in schema.model_dump().items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def excluir(db: Session, produto_id: int) -> None:
    produto = buscar_por_id(db, produto_id)
    # Produto com histórico não pode sumir: apagar levaria junto a trilha de auditoria.
    # Por isso a FK de movimentações usa RESTRICT e aqui devolvemos um 409 claro.
    tem_movimentacao = db.scalar(
        select(Movimentacao.id).where(Movimentacao.produto_id == produto_id).limit(1)
    )
    if tem_movimentacao is not None:
        raise ConflictError(
            f"Não é possível excluir o produto {produto_id}: "
            "ele possui movimentações de estoque registradas."
        )
    db.delete(produto)
    db.commit()
