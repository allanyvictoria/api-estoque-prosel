import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configura o logger para registrar os erros internos no servidor
logger = logging.getLogger(__name__)


# 1. Classe Base de Exceção de Negócio
class AppError(Exception):

  def __init__(
      self,
      mensagem: str,
      codigo: str = "ERRO_INTERNO",
      status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
  ):
    self.mensagem = mensagem
    self.codigo = codigo
    self.status_code = status_code
    super().__init__(self.mensagem)


# 2. Subclasses de Exceções de Negócio
class NotFoundError(AppError):

  def __init__(self, mensagem: str, codigo: str = "NAO_ENCONTRADO"):
    super().__init__(
        mensagem=mensagem, codigo=codigo, status_code=status.HTTP_404_NOT_FOUND
    )


class ConflictError(AppError):

  def __init__(self, mensagem: str, codigo: str = "CONFLITO"):
    super().__init__(
        mensagem=mensagem, codigo=codigo, status_code=status.HTTP_409_CONFLICT
    )


class BusinessRuleError(AppError):

  def __init__(self, mensagem: str, codigo: str = "REGRA_DE_NEGOCIO"):
    super().__init__(
        mensagem=mensagem,
        codigo=codigo,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# 3. Função para Registrar os Handlers no FastAPI
def registrar_handlers(app: FastAPI):

  @app.exception_handler(AppError)
  async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": exc.codigo, "mensagem": exc.mensagem},
    )

  @app.exception_handler(RequestValidationError)
  async def validation_error_handler(
      request: Request, exc: RequestValidationError
  ):
    # Formata os erros de validação do Pydantic para o padrão do projeto (400)
    detalhes = []
    for error in exc.errors():
      campo = " -> ".join(str(loc) for loc in error["loc"])
      msg = error["msg"]
      detalhes.append(f"{campo}: {msg}")

    mensagem_formatada = "Dados inválidos: " + "; ".join(detalhes)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"erro": "DADOS_INVALIDOS", "mensagem": mensagem_formatada},
    )

  @app.exception_handler(StarletteHTTPException)
  async def starlette_http_exception_handler(
      request: Request, exc: StarletteHTTPException
  ):
    codigo = (
        "NAO_ENCONTRADO"
        if exc.status_code == 404
        else "METODO_NAO_PERMITIDO"
        if exc.status_code == 405
        else "ERRO_HTTP"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": codigo, "mensagem": exc.detail},
    )

  @app.exception_handler(IntegrityError)
  async def sqlalchemy_integrity_error_handler(
      request: Request, exc: IntegrityError
  ):
    logger.exception("Erro de integridade no banco de dados")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "erro": "VIOLACAO_INTEGRIDADE",
            "mensagem": "Conflito de dados: violação de restrição no banco.",
        },
    )

  @app.exception_handler(Exception)
  async def generic_exception_handler(request: Request, exc: Exception):
    # Loga o erro real no servidor para fins de auditoria/debugging
    logger.exception("Erro interno não tratado no servidor")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "erro": "ERRO_INTERNO",
            "mensagem": "Erro interno do servidor.",
        },
    )