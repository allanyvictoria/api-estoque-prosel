from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.movimentacao import Movimentacao, TipoMovimentacao
from app.models.produto import Produto
from app.schemas.movimentacao import MovimentacaoCreate


def criar(db: Session, schema: MovimentacaoCreate) -> Movimentacao:
    try:
        # with_for_update() faz um SELECT ... FOR UPDATE (lock pessimista): outra requisição
        # sobre o mesmo produto espera esta transação terminar. Sem isso, duas saídas
        # simultâneas leriam o mesmo saldo e poderiam deixar o estoque negativo.
        produto = db.scalar(
            select(Produto).where(Produto.id == schema.produto_id).with_for_update()
        )
        if produto is None:
            raise NotFoundError(f"Produto {schema.produto_id} não encontrado.")

        if schema.tipo == TipoMovimentacao.SAIDA:
            if schema.quantidade > produto.quantidade_em_estoque:
                raise BusinessRuleError(
                    f"Estoque insuficiente: disponível {produto.quantidade_em_estoque}, "
                    f"solicitado {schema.quantidade}.",
                    codigo="ESTOQUE_INSUFICIENTE",
                )
            produto.quantidade_em_estoque -= schema.quantidade
        else:
            produto.quantidade_em_estoque += schema.quantidade

        movimentacao = Movimentacao(**schema.model_dump())
        db.add(movimentacao)

        # Registro e atualização do saldo no MESMO commit: ou os dois acontecem, ou nenhum.
        # Assim o histórico nunca diverge do estoque real.
        db.commit()
        db.refresh(movimentacao)
        return movimentacao
    except Exception:
        db.rollback()  # desfaz tudo e libera o lock do produto
        raise


def buscar_por_id(db: Session, movimentacao_id: int) -> Movimentacao:
    movimentacao = db.scalar(
        select(Movimentacao).where(Movimentacao.id == movimentacao_id).limit(1)
    )
    if not movimentacao:
        raise NotFoundError(f"Movimentação {movimentacao_id} não encontrada.")
    return movimentacao


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    fornecedor_id: int | None = None,
    produto_id: int | None = None,
    tipo: TipoMovimentacao | None = None,
) -> list[Movimentacao]:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise BusinessRuleError("data_inicio não pode ser posterior a data_fim.")

    stmt = select(Movimentacao)
    if fornecedor_id is not None:
        # O fornecedor não é coluna da movimentação: chegamos nele via Produto.
        stmt = stmt.join(Produto, Produto.id == Movimentacao.produto_id).where(
            Produto.fornecedor_id == fornecedor_id
        )
    if produto_id is not None:
        stmt = stmt.where(Movimentacao.produto_id == produto_id)
    if tipo is not None:
        stmt = stmt.where(Movimentacao.tipo == tipo)
    if data_inicio is not None:
        stmt = stmt.where(Movimentacao.data >= data_inicio)
    if data_fim is not None:
        # "< dia seguinte" para incluir o dia final inteiro, e não só 00:00.
        stmt = stmt.where(Movimentacao.data < data_fim + timedelta(days=1))

    stmt = (
        stmt.order_by(Movimentacao.data.desc(), Movimentacao.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())
