from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Operacao(Base):
    __tablename__ = "operacoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    telefones = relationship("Telefone", back_populates="operacao", cascade="all, delete-orphan")
    mensagens = relationship("Mensagem", back_populates="operacao", cascade="all, delete-orphan")
    comunicacoes = relationship("Comunicacao", back_populates="operacao", cascade="all, delete-orphan")

class Telefone(Base):
    __tablename__ = "telefones"

    id = Column(Integer, primary_key=True, index=True)
    operacao_id = Column(Integer, ForeignKey("operacoes.id"))
    numero = Column(String, nullable=False)
    identificacao = Column(String)  # Nome personalizado
    foto = Column(String)  # URL ou Base64 da foto
    tipo = Column(String) # 'ALVO' ou 'SECUNDARIO'
    categoria = Column(String)  # 'SUSPEITO', 'TESTEMUNHA', 'VITIMA', 'OUTRO'
    observacoes = Column(String)  # Notas de investigação
    total_mensagens = Column(Integer, default=0)

    operacao = relationship("Operacao", back_populates="telefones")
    # Relacionamentos para grafos podem ser complexos, definiremos conforme necessidade

class IP(Base):
    __tablename__ = "ips"

    id = Column(Integer, primary_key=True, index=True)
    endereco = Column(String, nullable=False, unique=True)
    pais = Column(String)
    cidade = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    provedor = Column(String)

    mensagens = relationship("Mensagem", back_populates="ip_rel")

class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    operacao_id = Column(Integer, ForeignKey("operacoes.id"), index=True)  # Índice para filtros por operação
    alvo = Column(String, index=True)  # Índice para buscas por alvo
    remetente = Column(String, index=True)  # Índice para filtros por remetente
    destinatario = Column(String, index=True)  # Índice para filtros por destinatário
    ip_id = Column(Integer, ForeignKey("ips.id"), nullable=True, index=True)  # Índice para joins com IP
    porta = Column(Integer, nullable=True)
    data_hora = Column(DateTime, index=True)  # Índice para ordenação e filtros temporais
    tipo_mensagem = Column(String)

    operacao = relationship("Operacao", back_populates="mensagens")
    ip_rel = relationship("IP", back_populates="mensagens")

class Comunicacao(Base):
    __tablename__ = "comunicacoes"

    id = Column(Integer, primary_key=True, index=True)
    operacao_id = Column(Integer, ForeignKey("operacoes.id"))
    telefone_origem = Column(String) # Armazenando o número diretamente para simplificar por enquanto
    telefone_destino = Column(String)
    quantidade = Column(Integer, default=1)

    operacao = relationship("Operacao", back_populates="comunicacoes")

class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(Integer, primary_key=True, index=True)
    operacao_id = Column(Integer, ForeignKey("operacoes.id"))
    nome = Column(String)
    hash_md5 = Column(String)
    data_upload = Column(DateTime, default=datetime.utcnow)
    alvo_numero = Column(String, nullable=True)  # Account Identifier (ex: +5534980319919)
    periodo_inicio = Column(String, nullable=True)  # Data início do período
    periodo_fim = Column(String, nullable=True)  # Data fim do período

    operacao = relationship("Operacao", back_populates="arquivos")

# Update Operacao relationship
Operacao.arquivos = relationship("Arquivo", back_populates="operacao", cascade="all, delete-orphan")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    telefone = Column(String)
    foto = Column(String)  # Base64 ou URL
    role = Column(String, default="user")  # 'admin' ou 'user'
    status = Column(String, default="pending")  # 'pending', 'active', 'blocked'
    data_criacao = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime, nullable=True)
