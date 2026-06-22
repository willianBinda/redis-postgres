from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ClienteCreate(BaseModel):
    id: int
    cpf: str
    nome: str
    endereco: str
    cidade: str
    uf: str
    email: str


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    email: Optional[str] = None


class ProdutoCreate(BaseModel):
    id: int
    produto: str
    valor: float
    quantidade: int
    tipo: str


class ProdutoUpdate(BaseModel):
    produto: Optional[str] = None
    valor: Optional[float] = None
    quantidade: Optional[int] = None
    tipo: Optional[str] = None


class CompraCreate(BaseModel):
    id: int
    id_produto: int
    data: date
    id_cliente: int


class CompraUpdate(BaseModel):
    id_produto: Optional[int] = None
    data: Optional[date] = None
    id_cliente: Optional[int] = None


class InteresseCreate(BaseModel):
    cpf: str
    nome: str
    interesses: List[str]


class InteresseUpdate(BaseModel):
    nome: Optional[str] = None
    interesses: Optional[List[str]] = None


class PessoaCreate(BaseModel):
    id: int
    cpf: str
    nome: str


class AmizadeCreate(BaseModel):
    cpf_origem: str
    cpf_destino: str
