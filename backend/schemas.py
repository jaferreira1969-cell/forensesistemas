from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class OperacaoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class OperacaoCreate(OperacaoBase):
    pass

class Operacao(OperacaoBase):
    id: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)

class TelefoneBase(BaseModel):
    numero: str
    identificacao: Optional[str] = None
    foto: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    observacoes: Optional[str] = None

class Telefone(TelefoneBase):
    id: int
    operacao_id: int
    total_mensagens: int
    categoria: Optional[str] = None
    observacoes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TelefoneUpdate(BaseModel):
    identificacao: Optional[str] = None
    foto: Optional[str] = None
    categoria: Optional[str] = None
    observacoes: Optional[str] = None

class IPBase(BaseModel):
    endereco: str
    pais: Optional[str] = None
    cidade: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    provedor: Optional[str] = None

class IP(IPBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class MensagemBase(BaseModel):
    alvo: Optional[str] = None
    remetente: Optional[str] = None
    destinatario: Optional[str] = None
    porta: Optional[int] = None
    data_hora: Optional[datetime] = None
    tipo_mensagem: Optional[str] = None

class Mensagem(MensagemBase):
    id: int
    operacao_id: int
    ip_id: Optional[int] = None
    ip_rel: Optional[IP] = None

    model_config = ConfigDict(from_attributes=True)
