from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)


class CategoriaUpdate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)


class CategoriaResponse(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)
