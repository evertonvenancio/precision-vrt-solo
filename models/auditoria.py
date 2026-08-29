"""
Precision VRT Solo — Modelo de Auditoria Persistente

Responsável pelo registro de eventos auditáveis no banco de dados.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class AuditoriaEvento(Base):
    """
    Tabela de eventos auditáveis no banco de dados.
    Registra operações relevantes do sistema.
    """
    
    __tablename__ = "auditoria_eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_acao = Column(String(50), nullable=False, index=True)  # criar, alterar, excluir, login, etc.
    modulo = Column(String(50), nullable=False, index=True)      # clientes, financeiro, usuarios, etc.
    usuario_id = Column(Integer, nullable=False, index=True)    # ID do usuário que realizou a operação
    usuario_nome = Column(String(100), nullable=False)          # Nome do usuário para consultas fáceis
    acao = Column(String(200), nullable=False)                  # Descrição da ação realizada
    recurso_id = Column(String(100), nullable=True, index=True) # ID do recurso afetado (opcional)
    recurso_tipo = Column(String(50), nullable=True)            # Tipo do recurso (cliente, orcamento, etc.)
    ip_origem = Column(String(45), nullable=True)               # IP de origem da operação
    user_agent = Column(Text, nullable=True)                     # User agent do navegador
    sucesso = Column(Boolean, nullable=False, default=True)     # Se a operação teve sucesso
    mensagem = Column(Text, nullable=True)                      # Mensagem de erro ou detalhe
    detalhes = Column(Text, nullable=True)                      # Dados adicionais em JSON
    timestamp = Column(DateTime, nullable=False, index=True, server_default=func.now())
    
    def __repr__(self):
        return f"AuditoriaEvento(id={self.id}, tipo_acao='{self.tipo_acao}', modulo='{self.modulo}', usuario='{self.usuario_nome}', timestamp='{self.timestamp}')"


class AuditoriaFiltro(Base):
    """
    Tabela para filtros e configurações de auditoria (opcional para futuro).
    """
    
    __tablename__ = "auditoria_filtros"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    nome_filtro = Column(String(100), nullable=False)
    configuracao = Column(Text, nullable=True)  # JSON com configuração do filtro
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    ultimos_usado = Column(DateTime, nullable=True)