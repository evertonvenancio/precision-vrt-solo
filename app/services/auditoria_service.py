"""
Precision VRT Solo — Serviço de Auditoria Persistente

Responsável por registrar e consultar eventos auditáveis no banco de dados.
Integra a lógica existente com persistência real.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from db.database import get_db
from app.services.exportacao_service import ExportacaoService
from app.services.clientes_service import ClientesService
from app.services.dashboard_service import DashboardService
from core.seguranca.auditoria import TipoAcao, ModuloSistema, AuditorSistema, AuditoriaRegistro
from models.auditoria import AuditoriaEvento


class AuditoriaService:
    """
    Serviço de auditoria compatível com interface original.
    
    Esta classe foi adicionada para manter a compatibilidade com o contrato
    original esperado pelo sistema. A implementação delega para 
    AuditoriaPersistenteService.
    """
    
    def __init__(self, db: Session):
        self.service = AuditoriaPersistenteService(db)
    
    def registrar_operacao(self, 
                          tipo_acao: TipoAcao, 
                          modulo: ModuloSistema,
                          usuario_id: int,
                          usuario_nome: str,
                          acao: str,
                          recurso_id: Optional[str] = None,
                          recurso_tipo: Optional[str] = None,
                          ip_origem: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          sucesso: bool = True,
                          mensagem: Optional[str] = None,
                          detalhes: Optional[Dict[str, Any]] = None) -> str:
        """Delega para AuditoriaPersistenteService"""
        return self.service.registrar_operacao(
            tipo_acao=tipo_acao,
            modulo=modulo,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao=acao,
            recurso_id=recurso_id,
            recurso_tipo=recurso_tipo,
            ip_origem=ip_origem,
            user_agent=user_agent,
            sucesso=sucesso,
            mensagem=mensagem,
            detalhes=detalhes
        )
    
    def obter_registros(self,
                       usuario_id: Optional[int] = None,
                       modulo: Optional[ModuloSistema] = None,
                       tipo_acao: Optional[TipoAcao] = None,
                       recurso_id: Optional[str] = None,
                       data_inicio: Optional[datetime] = None,
                       data_fim: Optional[datetime] = None,
                       limite: int = 100) -> List[Dict[str, Any]]:
        """Delega para AuditoriaPersistenteService"""
        return self.service.obter_registros(
            usuario_id=usuario_id,
            modulo=modulo,
            tipo_acao=tipo_acao,
            recurso_id=recurso_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            limite=limite
        )
    
    def obter_estatisticas(self,
                          periodo_dias: int = 30) -> Dict[str, Any]:
        """Delega para AuditoriaPersistenteService"""
        return self.service.obter_estatisticas(periodo_dias=periodo_dias)
    
    def registrar_login(self, 
                      usuario_id: int, 
                      usuario_nome: str, 
                      ip_origem: str,
                      sucesso: bool = True,
                      mensagem: Optional[str] = None) -> str:
        """Delega para AuditoriaPersistenteService"""
        return self.service.registrar_login(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            ip_origem=ip_origem,
            sucesso=sucesso,
            mensagem=mensagem
        )
    
    def registrar_operacao_usuario(self,
                                  tipo_acao: TipoAcao,
                                  usuario_id: int,
                                  usuario_nome: str,
                                  detalhes: Dict[str, Any]) -> str:
        """Delega para AuditoriaPersistenteService"""
        return self.service.registrar_operacao_usuario(
            tipo_acao=tipo_acao,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            detalhes=detalhes
        )
    
    def registrar_operacao_cliente(self,
                                   tipo_acao: TipoAcao,
                                   usuario_id: int,
                                   usuario_nome: str,
                                   cliente_id: str,
                                   detalhes: Dict[str, Any]) -> str:
        """Delega para AuditoriaPersistenteService"""
        return self.service.registrar_operacao_cliente(
            tipo_acao=tipo_acao,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            cliente_id=cliente_id,
            detalhes=detalhes
        )


class AuditoriaPersistenteService:
    """
    Serviço de auditoria com persistência real no banco de dados.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.auditoria_logica = AuditorSistema()
    
    def registrar_operacao(self, 
                          tipo_acao: TipoAcao, 
                          modulo: ModuloSistema,
                          usuario_id: int,
                          usuario_nome: str,
                          acao: str,
                          recurso_id: Optional[str] = None,
                          recurso_tipo: Optional[str] = None,
                          ip_origem: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          sucesso: bool = True,
                          mensagem: Optional[str] = None,
                          detalhes: Optional[Dict[str, Any]] = None) -> str:
        """
        Registra operação de auditoria com persistência real.
        
        Args:
            tipo_acao: Tipo da ação (criar, alterar, excluir, etc.)
            modulo: Módulo do sistema (clientes, financeiro, etc.)
            usuario_id: ID do usuário
            usuario_nome: Nome do usuário
            acao: Descrição da ação
            recurso_id: ID do recurso afetado (opcional)
            recurso_tipo: Tipo do recurso (opcional)
            ip_origem: IP de origem (opcional)
            user_agent: User agent (opcional)
            sucesso: Se a operação teve sucesso
            mensagem: Mensagem de erro ou detalhe (opcional)
            detalhes: Dados adicionais em formato dict (opcional)
            
        Returns:
            ID do registro no banco
        """
        try:
            # Criar registro no banco
            auditoria_evento = AuditoriaEvento(
                tipo_acao=tipo_acao.value,
                modulo=modulo.value,
                usuario_id=usuario_id,
                usuario_nome=usuario_nome,
                acao=acao,
                recurso_id=recurso_id,
                recurso_tipo=recurso_tipo,
                ip_origem=ip_origem,
                user_agent=user_agent,
                sucesso=sucesso,
                mensagem=mensagem,
                detalhes=json.dumps(detalhes) if detalhes else None
            )
            
            self.db.add(auditoria_evento)
            self.db.commit()
            
            # Também registrar na estrutura lógica existente
            registro_logico = AuditoriaRegistro(
                tipo_acao=tipo_acao,
                modulo=modulo,
                usuario=usuario_nome,
                acao=acao,
                dados_antes={},  # Não armazenar dados sensíveis
                dados_depois={}  # Não armazenar dados sensíveis
            )
            
            registro_id = self.auditoria_logica.registrar_operacao(registro_logico)
            
            return str(auditoria_evento.id)
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao registrar operação de auditoria: {e}")
            raise
    
    def obter_registros(self,
                       usuario_id: Optional[int] = None,
                       modulo: Optional[ModuloSistema] = None,
                       tipo_acao: Optional[TipoAcao] = None,
                       recurso_id: Optional[str] = None,
                       data_inicio: Optional[datetime] = None,
                       data_fim: Optional[datetime] = None,
                       limite: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém registros de auditoria com filtros.
        
        Returns:
            Lista de registros formatados para API
        """
        try:
            # Construir query
            query = self.db.query(AuditoriaEvento)
            
            if usuario_id:
                query = query.filter(AuditoriaEvento.usuario_id == usuario_id)
            
            if modulo:
                query = query.filter(AuditoriaEvento.modulo == modulo.value)
            
            if tipo_acao:
                query = query.filter(AuditoriaEvento.tipo_acao == tipo_acao.value)
            
            if recurso_id:
                query = query.filter(AuditoriaEvento.recurso_id == recurso_id)
            
            if data_inicio:
                query = query.filter(AuditoriaEvento.timestamp >= data_inicio)
            
            if data_fim:
                query = query.filter(AuditoriaEvento.timestamp <= data_fim)
            
            # Ordenar por timestamp (mais recentes primeiro)
            query = query.order_by(AuditoriaEvento.timestamp.desc())
            
            # Aplicar limite
            if limite:
                query = query.limit(limite)
            
            registros = query.all()
            
            # Formatar para retorno
            resultado = []
            for registro in registros:
                resultado.append({
                    'id': registro.id,
                    'tipo_acao': registro.tipo_acao,
                    'modulo': registro.modulo,
                    'usuario_id': registro.usuario_id,
                    'usuario_nome': registro.usuario_nome,
                    'acao': registro.acao,
                    'recurso_id': registro.recurso_id,
                    'recurso_tipo': registro.recurso_tipo,
                    'ip_origem': registro.ip_origem,
                    'user_agent': registro.user_agent,
                    'sucesso': registro.sucesso,
                    'mensagem': registro.mensagem,
                    'detalhes': json.loads(registro.detalhes) if registro.detalhes else None,
                    'timestamp': registro.timestamp.isoformat() if registro.timestamp else None
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao obter registros de auditoria: {e}")
            return []
    
    def obter_estatisticas(self,
                          periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas da auditoria para um período.
        """
        try:
            data_inicio = datetime.now() - timedelta(days=periodo_dias)
            
            # Total de registros
            total_registros = self.db.query(AuditoriaEvento).filter(
                AuditoriaEvento.timestamp >= data_inicio
            ).count()
            
            # Por módulo
            por_modulo = {}
            for modulo in ModuloSistema:
                count = self.db.query(AuditoriaEvento).filter(
                    and_(
                        AuditoriaEvento.timestamp >= data_inicio,
                        AuditoriaEvento.modulo == modulo.value
                    )
                ).count()
                if count > 0:
                    por_modulo[modulo.value] = count
            
            # Por tipo de ação
            por_tipo = {}
            for tipo in TipoAcao:
                count = self.db.query(AuditoriaEvento).filter(
                    and_(
                        AuditoriaEvento.timestamp >= data_inicio,
                        AuditoriaEvento.tipo_acao == tipo.value
                    )
                ).count()
                if count > 0:
                    por_tipo[tipo.value] = count
            
            # Por usuário (top 5)
            por_usuario = {}
            usuarios_registros = self.db.query(
                AuditoriaEvento.usuario_id,
                AuditoriaEvento.usuario_nome,
                func.count(AuditoriaEvento.id).label('count')
            ).filter(
                AuditoriaEvento.timestamp >= data_inicio
            ).group_by(
                AuditoriaEvento.usuario_id,
                AuditoriaEvento.usuario_nome
            ).order_by(
                func.count(AuditoriaEvento.id).desc()
            ).limit(5).all()
            
            for user_id, user_nome, count in usuarios_registros:
                por_usuario[user_nome] = count
            
            # Taxa de sucesso
            sucesso_count = self.db.query(AuditoriaEvento).filter(
                and_(
                    AuditoriaEvento.timestamp >= data_inicio,
                    AuditoriaEvento.sucesso == True
                )
            ).count()
            
            taxa_sucesso = (sucesso_count / total_registros * 100) if total_registros > 0 else 0
            
            return {
                'periodo_dias': periodo_dias,
                'total_registros': total_registros,
                'por_modulo': por_modulo,
                'por_tipo_acao': por_tipo,
                'por_usuario': por_usuario,
                'taxa_sucesso': round(taxa_sucesso, 2)
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas de auditoria: {e}")
            # Em caso de erro, retornar None para indicar falha real
            return None
    
    def registrar_login(self, 
                      usuario_id: int, 
                      usuario_nome: str, 
                      ip_origem: str,
                      sucesso: bool = True,
                      mensagem: Optional[str] = None) -> str:
        """
        Registra evento de login.
        """
        return self.registrar_operacao(
            tipo_acao=TipoAcao.CRIAR if sucesso else TipoAcao.ALTERAR,
            modulo=ModuloSistema.USUARIOS,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao="login" if sucesso else "login_falho",
            ip_origem=ip_origem,
            sucesso=sucesso,
            mensagem=mensagem
        )
    
    def registrar_operacao_usuario(self,
                                  tipo_acao: TipoAcao,
                                  usuario_id: int,
                                  usuario_nome: str,
                                  detalhes: Dict[str, Any]) -> str:
        """
        Registra operação relacionada a usuários.
        """
        return self.registrar_operacao(
            tipo_acao=tipo_acao,
            modulo=ModuloSistema.USUARIOS,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao=detalhes.get('operacao', 'operacao_usuario'),
            recurso_id=str(detalhes.get('usuario_id')),
            recurso_tipo='usuario',
            detalhes=detalhes
        )
    
    def registrar_operacao_cliente(self,
                                   tipo_acao: TipoAcao,
                                   usuario_id: int,
                                   usuario_nome: str,
                                   cliente_id: str,
                                   detalhes: Dict[str, Any]) -> str:
        """
        Registra operação relacionada a clientes.
        """
        return self.registrar_operacao(
            tipo_acao=tipo_acao,
            modulo=ModuloSistema.USUARIOS,  # Clientes está sob Cadastros Gerais, mas auditamos por USUARIOS
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao=f"cliente_{tipo_acao.value}",
            recurso_id=cliente_id,
            recurso_tipo='cliente',
            detalhes=detalhes
        )