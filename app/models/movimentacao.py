from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Numeric, func
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base

class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"
    __table_args__ = (CheckConstraint("quantidade >= 0"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[TipoMovimentacao] = mapped_column(String(50), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id", ondelete="RESTRICT"), nullable=False)
    quantidade: Mapped[int] = mapped_column(nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)