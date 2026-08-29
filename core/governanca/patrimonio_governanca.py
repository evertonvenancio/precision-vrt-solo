"""
Precision VRT Solo — Governança de Patrimônio

Implementa controle de alterações em patrimônio.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from .fluxos_aprovacao import FluxoAprovacao, processo_aprovacao, TipoOperacao, NivelAprovacao

class TipoItemPatrimonial(Enum):
    """Tipos de itens patrimoniais."""
    MAQUINA = "maquina"
    VEICULO = "veiculo"
    EQUIPAMENTO = "equipamento"
    COMPUTADOR = "computador"
    NOTEBOOK = "notebook"
    TABLET = "tablet"
    CELULAR = "celular"
    DRONE = "drone"
    SENSOR = "sensor"
    LICENCA = "licenca"
    FERRAMENTA = "ferramenta"
    MOVEL = "movel"
    IMOBILIARIO = "imobiliario"

class CategoriaPatrimonio(Enum):
    """Categorias de patrimônio."""
    EQUIPAMENTOS = "equipamentos"
    VEHICULOS = "veiculos"
    COMPUTACAO = "computacao"
    COMUNICACAO = "comunicacao"
    SENSORES = "sensores"
    SOFTWARE = "software"
    MOVEIS = "moveis"
    IMOVEIS = "imoveis"
    FERRAMENTAS = "ferramentas"
    OUTROS = "outros"

class TipoOperacaoPatrimonio(Enum):
    """Tipos de operações patrimoniais."""
    AQUISICAO = "aquisicao"
    BAIXA = "baixa"
    TRANSFERENCIA = "transferencia"
    MANUTENCAO = "manutencao"
    DEPRECIACAO = "depreciacao"
    REVALUACAO = "reavaliacao"
    INVENTARIO = "inventario"
    REPARO = "reparo"
    CALIBRACAO = "calibracao"
    ATUALIZACAO = "atualizacao"
    ALUGUEL = "aluguel"
    VENDA = "venda"

class ItemPatrimonial:
    """
    Representa um item patrimonial.
    """
    
    def __init__(self,
                 id_item: str,
                 tipo: TipoItemPatrimonial,
                 categoria: CategoriaPatrimonio,
                 descricao: str,
                 valor: float,
                 data_aquisicao: datetime,
                 fornecedor: Optional[str] = None,
                 vida_util: Optional[int] = None,
                 depreciacao_anual: Optional[float] = None,
                 localizacao: Optional[str] = None,
                responsavel: Optional[str] = None,
                situacao: str = "ativo",
                dados_adicionais: Optional[Dict[str, Any]] = None):
        self.id_item = id_item
        self.tipo = tipo
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor
        self.data_aquisicao = data_aquisicao
        self.fornecedor = fornecedor
        self.vida_util = vida_util
        self.depreciacao_anual = depreciacao_anual
        self.localizacao = localizacao
        self.responsavel = responsavel
        self.situacao = situacao
        self.dados_adicionais = dados_adicionais or {}
        self.historico: List[Dict[str, Any]] = []
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def adicionar_historico(self, evento: str, usuario_id: str, dados: Optional[Dict[str, Any]] = None):
        """
        Adiciona evento ao histórico do item.
        """
        historico_item = {
            'evento': evento,
            'timestamp': datetime.now(),
            'usuario_id': usuario_id,
            'dados': dados or {}
        }
        
        self.historico.append(historico_item)
        self.atualizado_em = datetime.now()

class OperacaoPatrimonio:
    """
    Representa uma operação patrimonial controlada.
    """
    
    def __init__(self,
                 id_operacao: str,
                 tipo: TipoOperacaoPatrimonio,
                 itens_envolvidos: List[str],
                 descricao: str,
                 solicitante_id: str,
                 valor_total: float,
                 justificativa: str,
                 cliente_id: Optional[str] = None,
                dados_adicionais: Optional[Dict[str, Any]] = None,
                aprovadores_necessarios: int = 1,
                restricoes: Optional[Dict[str, Any]] = None):
        self.id_operacao = id_operacao
        self.tipo = tipo
        self.itens_envolvidos = itens_envolvidos
        self.descricao = descricao
        self.solicitante_id = solicitante_id
        self.valor_total = valor_total
        self.justificativa = justificativa
        self.cliente_id = cliente_id
        self.dados_adicionais = dados_adicionais or {}
        self.aprovadores_necessarios = aprovadores_necessarios
        self.restricoes = restricoes or {}
        self.criado_em = datetime.now()
        self.status = "pendente"
        self.aprovacoes: List[Dict[str, Any]] = []
        self.historico: List[Dict[str, Any]] = []
        
    def pode_ser_aprovada(self, usuario_id: str, contexto: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verifica se operação pode ser aprovada pelo usuário.
        """
        # Verificar se usuário não já aprovou
        if any(aprovacao.get('aprovador_id') == usuario_id for aprovacao in self.aprovacoes):
            return False
            
        # Verificar restrições se contexto fornecido
        if contexto:
            for chave, valor_restricao in self.restricoes.items():
                if chave in contexto:
                    if isinstance(valor_restricao, dict):
                        if 'max' in valor_restricao and contexto[chave] > valor_restricao['max']:
                            return False
                        if 'min' in valor_restricao and contexto[chave] < valor_restricao['min']:
                            return False
                        if 'permitido' in valor_restricao and contexto[chave] not in valor_restricao['permitido']:
                            return False
                    else:
                        if contexto[chave] != valor_restricao:
                            return False
                            
        return True
        
    def adicionar_aprovacao(self, 
                           aprovador_id: str, 
                           aprovado: bool, 
                           justificativa: str = "",
                           dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Adiciona aprovação à operação.
        """
        aprovacao = {
            'aprovador_id': aprovador_id,
            'data_aprovacao': datetime.now(),
            'aprovado': aprovado,
            'justificativa': justificativa,
            'dados_complementares': dados_complementares or {}
        }
        
        self.aprovacoes.append(aprovacao)
        
        # Atualizar status
        aprovacoes_positivas = sum(1 for a in self.aprovacoes if a['aprovado'])
        if aprovacoes_positivas >= self.aprovadores_necessarios:
            self.status = "aprovada"
        elif any(not a['aprovado'] for a in self.aprovacoes):
            self.status = "rejeitada"
        else:
            self.status = "em_aprovacao"
            
        # Adicionar ao histórico
        self.historico.append({
            'evento': 'aprovacao' if aprovado else 'rejeicao',
            'timestamp': datetime.now(),
            'usuario': aprovador_id,
            'justificativa': justificativa,
            'dados_complementares': dados_complementares or {}
        })
        
        return True
        
    def obter_status_completo(self) -> Dict[str, Any]:
        """
        Obtém status completo da operação.
        """
        return {
            'id_operacao': self.id_operacao,
            'tipo': self.tipo.value,
            'itens_envolvidos': self.itens_envolvidos,
            'descricao': self.descricao,
            'solicitante_id': self.solicitante_id,
            'valor_total': self.valor_total,
            'justificativa': self.justificativa,
            'cliente_id': self.cliente_id,
            'dados_adicionais': self.dados_adicionais,
            'aprovadores_necessarios': self.aprovadores_necessarios,
            'aprovacoes_recebidas': len(self.aprovacoes),
            'aprovacoes_positivas': sum(1 for a in self.aprovacoes if a['aprovado']),
            'status': self.status,
            'restricoes': self.restricoes,
            'criado_em': self.criado_em,
            'historico': self.historico
        }

class AprovadorPatrimonio:
    """
    Aprovador para operações patrimoniais.
    """
    
    def __init__(self, usuario_id: str, nivel: str, limites: Optional[Dict[str, float]] = None):
        self.usuario_id = usuario_id
        self.nivel = nivel  # tecnico, supervisor, gerente, diretor, administrador
        self.limites = limites or {}
        self.operacoes_aprovadas: List[OperacaoPatrimonio] = []
        self.operacoes_rejeitadas: List[OperacaoPatrimonio] = []
        self.operacoes_pendentes: List[str] = []
        
    def pode_aprovar(self, operacao: OperacaoPatrimonio) -> bool:
        """
        Verifica se aprovador pode aprovar operação.
        """
        # Verificar limite por tipo
        if operacao.tipo.value in self.limites:
            if operacao.valor_total > self.limites[operacao.tipo.value]:
                return False
                
        # Verificar nível geral
        if self.nivel == "tecnico" and operacao.tipo.value in ["aquisicao", "baixa", "transferencia"]:
            return False
        if self.nivel == "supervisor" and operacao.tipo.value == "transferencia":
            return False
        if self.nivel == "gerente" and operacao.tipo.value == "baixa":
            return False
        if self.nivel == "diretor" and operacao.tipo.value in ["aquisicao", "baixa"]:
            return False
            
        return True
        
    def aprovar_operacao(self, 
                        operacao: OperacaoPatrimonio, 
                        justificativa: str = "",
                        dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Aprova operação patrimonial.
        """
        if not self.pode_aprovar(operacao):
            return False
            
        sucesso = operacao.adicionar_aprovacao(
            self.usuario_id, True, justificativa, dados_complementares
        )
        
        if sucesso:
            self.operacoes_aprovadas.append(operacao)
            if operacao.id_operacao in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(operacao.id_operacao)
                
        return sucesso
        
    def rejeitar_operacao(self, 
                         operacao: OperacaoPatrimonio, 
                         justificativa: str = "",
                         dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Rejeita operação patrimonial.
        """
        sucesso = operacao.adicionar_aprovacao(
            self.usuario_id, False, justificativa, dados_complementares
        )
        
        if sucesso:
            self.operacoes_rejeitadas.append(operacao)
            if operacao.id_operacao in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(operacao.id_operacao)
                
        return sucesso

class FluxoPatrimonio:
    """
    Gerencia fluxo de aprovação para operações patrimoniais.
    """
    
    def __init__(self):
        self.operacoes: Dict[str, OperacaoPatrimonio] = {}
        self.aprovadores: Dict[str, AprovadorPatrimonio] = {}
        self.itens_patrimoniais: Dict[str, ItemPatrimonial] = {}
        self.mapeamento_tipo_operacao = {
            TipoOperacaoPatrimonio.AQUISICAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.BAIXA: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.TRANSFERENCIA: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.MANUTENCAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.DEPRECIACAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.REVALUACAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.INVENTARIO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.REPARO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.CALIBRACAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.ATUALIZACAO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.ALUGUEL: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoPatrimonio.VENDA: TipoOperacao.LIBERAR_PATRIMONIO
        }
        
    def criar_operacao(self, operacao: OperacaoPatrimonio) -> str:
        """
        Cria nova operação patrimonial.
        """
        operacao.id_operacao = f"patrimonio_{int(datetime.now().timestamp())}_{len(self.operacoes)}"
        self.operacoes[operacao.id_operacao] = operacao
        
        # Adicionar aos aprovadores pendentes
        for aprovador in self.aprovadores.values():
            if aprovador.pode_aprovar(operacao):
                aprovador.operacoes_pendentes.append(operacao.id_operacao)
                
        return operacao.id_operacao
        
    def obter_operacao(self, id_operacao: str) -> Optional[OperacaoPatrimonio]:
        """
        Obtém operação pelo ID.
        """
        return self.operacoes.get(id_operacao)
        
    def adicionar_aprovador(self, aprovador: AprovadorPatrimonio):
        """
        Adiciona aprovador ao sistema.
        """
        self.aprovadores[aprovador.usuario_id] = aprovador
        
    def adicionar_item_patrimonial(self, item: ItemPatrimonial):
        """
        Adiciona item patrimonial ao sistema.
        """
        self.itens_patrimoniais[item.id_item] = item
        
    def obter_item_patrimonial(self, id_item: str) -> Optional[ItemPatrimonial]:
        """
        Obtém item patrimonial pelo ID.
        """
        return self.itens_patrimoniais.get(id_item)
        
    def obter_fluxo_aprovacao(self, id_operacao: str) -> Optional[FluxoAprovacao]:
        """
        Obtém fluxo de aprovação correspondente.
        """
        operacao = self.obter_operacao(id_operacao)
        if not operacao:
            return None
            
        # Mapear tipo de operação
        tipo_fluxo = self.mapeamento_tipo_operacao.get(operacao.tipo)
        if not tipo_fluxo:
            return None
            
        fluxo = FluxoAprovacao(
            id_fluxo=operacao.id_operacao,
            tipo_operacao=tipo_fluxo,
            solicitante_id=operacao.solicitante_id,
            operacao_descricao=operacao.descricao,
            nivel_aprovacao=NivelAprovacao.GERENTE,
            clientes_envolvidos=[operacao.cliente_id] if operacao.cliente_id else None,
            modulo="patrimonio",
            aprovadores_necessarios=operacao.aprovadores_necessarios
        )
        
        # Adicionar aprovações existentes
        for aprovacao in operacao.aprovacoes:
            fluxo.adicionar_aprovacao(
                aprovacao['aprovador_id'], 
                aprovacao['aprovado'], 
                aprovacao['justificativa']
            )
            
        return fluxo
        
    def liberar_operacao(self, id_operacao: str) -> bool:
        """
        Libera operação após aprovação final.
        """
        operacao = self.obter_operacao(id_operacao)
        if not operacao or operacao.status != "aprovada":
            return False
            
        # Atualizar itens envolvidos
        for item_id in operacao.itens_envolvidos:
            item = self.obter_item_patrimonial(item_id)
            if item:
                item.adicionar_historico(
                    operacao.tipo.value,
                    operacao.solicitante_id,
                    {'operacao_id': operacao.id_operacao, 'dados': operacao.dados_adicionais}
                )
                
        # Registrar operação como liberada
        operacao.historico.append({
            'evento': 'liberacao',
            'timestamp': datetime.now(),
            'status': 'liberada'
        })
        
        return True

# Instância global
fluxo_patrimonio = FluxoPatrimonio()

def criar_operacao_patrimonio(tipo: TipoOperacaoPatrimonio,
                             itens_envolvidos: List[str],
                             descricao: str,
                             solicitante_id: str,
                             valor_total: float,
                             justificativa: str,
                             cliente_id: Optional[str] = None,
                             dados_adicionais: Optional[Dict[str, Any]] = None,
                             aprovadores_necessarios: int = 1,
                             restricoes: Optional[Dict[str, Any]] = None) -> str:
    """
    Função utilitária para criar operação patrimonial.
    """
    operacao = OperacaoPatrimonio(
        id_operacao="",
        tipo=tipo,
        itens_envolvidos=itens_envolvidos,
        descricao=descricao,
        solicitante_id=solicitante_id,
        valor_total=valor_total,
        justificativa=justificativa,
        cliente_id=cliente_id,
        dados_adicionais=dados_adicionais,
        aprovadores_necessarios=aprovadores_necessarios,
        restricoes=restricoes or {}
    )
    
    return fluxo_patrimonio.criar_operacao(operacao)