from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Numeric, func
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (CheckConstraint("quantidade_em_estoque >= 0"), CheckConstraint("estoque_minimo >= 0"))

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    preco_custo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_venda: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade_estoque: Mapped[int] = mapped_column(nullable=False, default=0)
    estoque_minimo: Mapped[int] = mapped_column(nullable=False, default=0)
    data_cadastro: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id", ondelete="RESTRICT"), nullable=False)