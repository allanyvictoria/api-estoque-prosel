import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _validar_cnpj(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) != 14 or digitos == digitos[0] * 14:
        raise ValueError("CNPJ deve conter 14 dígitos válidos.")

    def digito_verificador(base: str, pesos: list[int]) -> str:
        resto = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    d1 = digito_verificador(digitos[:12], pesos1)
    d2 = digito_verificador(digitos[:12] + d1, pesos2)
    if digitos[12:] != d1 + d2:
        raise ValueError("CNPJ inválido (dígitos verificadores não conferem).")
    return digitos


class FornecedorCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150)
    cnpj: str
    telefone: str = Field(..., min_length=8, max_length=20)
    email: EmailStr

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("cnpj")
    @classmethod
    def normalizar_cnpj(cls, valor: str) -> str:
        return _validar_cnpj(valor)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.lower()


class FornecedorUpdate(FornecedorCreate):
    pass


class FornecedorResponse(BaseModel):
    id: int
    nome: str
    cnpj: str
    telefone: str
    email: str

    model_config = ConfigDict(from_attributes=True)
