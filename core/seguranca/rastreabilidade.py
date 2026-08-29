"""
Precision VRT Solo — Rastreabilidade Global

Responsável pelo controle de alterações e histórico de dados.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from copy import deepcopy

class ItemRastreavel:
    """
    Item que pode ser rastreado.
    Apenas dados, não lógica.
    """
    
    def __init__(self, id_item: str, tipo: str, dados: Dict[str, Any]):
        self.id_item = id_item
        self.tipo = tipo
        self.dados = deepcopy(dados)
        self.versao = 1
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        self.criado_por = None
        self.atualizado_por = None
        self.status = 'ativo'
        
    def criar_nova_versao(self, dados_novos: Dict[str, Any], atualizado_por: str) -> 'ItemRastreavel':
        """
        Cria nova versão do item.
        Não executa lógica de negócio.
        """
        novo_item = ItemRastreavel(
            id_item=self.id_item,
            tipo=self.tipo,
            dados=dados_novos
        )
        novo_item.versao = self.versao + 1
        novo_item.criado_em = self.criado_em
        novo_item.criado_por = self.criado_por
        novo_item.atualizado_em = datetime.now()
        novo_item.atualizado_por = atualizado_por
        novo_item.status = self.status
        return novo_item

class HistoricoAlteracao:
    """
    Registro de alteração no histórico.
    Apenas dados, não lógica.
    """
    
    def __init__(self,
                 id_item: str,
                 versao_anterior: int,
                 versao_nova: int,
                 campos_alterados: List[str],
         valores_anteriores: Dict[str, Any],
         valores_novos: Dict[str, Any],
         alterado_por: str,
         data_alteracao: datetime,
         justificativa: Optional[str] = None):
        self.id_item = id_item
        self.versao_anterior = versao_anterior
        self.versao_nova = versao_nova
        self.campos_alterados = campos_alterados
        self.valores_anteriores = valores_anteriores
        self.valores_novos = valores_novos
        self.alterado_por = alterado_por
        self.data_alteracao = data_alteracao
        self.justificativa = justificativa
        
    def __str__(self):
        return f"HistoricoAlteracao({self.id_item}, v{self.versao_anterior}->v{self.versao_nova}, {self.alterado_por})"

class GerenciadorRastreabilidade:
    """
    Gerencia rastreabilidade de itens.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.itens: Dict[str, ItemRastreavel] = {}
        self.historico: Dict[str, List[HistoricoAlteracao]] = {}
        self.versoes: Dict[str, List[ItemRastreavel]] = {}
        
    def criar_item(self, id_item: str, tipo: str, dados: Dict[str, Any], criado_por: Optional[str] = None) -> ItemRastreavel:
        """
        Cria novo item rastreável.
        Não executa lógica de negócio.
        """
        item = ItemRastreavel(id_item, tipo, dados)
        if criado_por:
            item.criado_por = criado_por
            
        self.itens[id_item] = item
        
        # Iniciar histórico
        self.historico[id_item] = []
        self.versoes[id_item] = [item]
        
        # Registrar primeira versão
        self.registrar_alteracao(
            item=item,
            versao_anterior=0,
            versao_nova=1,
            campos_alterados=list(dados.keys()),
            valores_anteriores={},
            valores_novos=dados,
            alterado_por=criado_por or 'sistema'
        )
        
        return item
        
    def atualizar_item(self, 
                      id_item: str,
                      dados_novos: Dict[str, Any],
                      campos_alterados: Optional[List[str]] = None,
                      atualizado_por: Optional[str] = None,
                      justificativa: Optional[str] = None) -> Optional[ItemRastreavel]:
        """
        Atualiza item rastreável.
        Não executa lógica de negócio.
        """
        if id_item not in self.itens:
            return None
            
        item_atual = self.itens[id_item]
        
        # Identificar campos alterados se não fornecidos
        if campos_alterados is None:
            campos_alterados = []
            valores_anteriores = {}
            valores_novos = {}
            
            for chave, valor in dados_novos.items():
                if chave in item_atual.dados and item_atual.dados[chave] != valor:
                    campos_alterados.append(chave)
                    valores_anteriores[chave] = item_atual.dados[chave]
                    valores_novos[chave] = valor
                    
        # Criar nova versão
        novo_item = item_atual.criar_nova_versao(dados_novos, atualizado_por or 'sistema')
        
        # Atualizar referências
        self.itens[id_item] = novo_item
        self.versoes[id_item].append(novo_item)
        
        # Registrar alteração
        self.registrar_alteracao(
            item=item_atual,
            versao_anterior=item_atual.versao,
            versao_nova=novo_item.versao,
            campos_alterados=campos_alterados,
            valores_anteriores=valores_anteriores,
            valores_novos=valores_novos,
            alterado_por=atualizado_por or 'sistema',
            justificativa=justificativa
        )
        
        return novo_item
        
    def obter_item_atual(self, id_item: str) -> Optional[ItemRastreavel]:
        """
        Obtém versão atual do item.
        """
        return self.itens.get(id_item)
        
    def obter_historico(self, id_item: str) -> List[HistoricoAlteracao]:
        """
        Obtém histórico de alterações do item.
        """
        return self.historico.get(id_item, [])
        
    def obter_versoes(self, id_item: str) -> List[ItemRastreavel]:
        """
        Obtém todas as versões do item.
        """
        return self.versoes.get(id_item, [])
        
    def obter_versao_especifica(self, id_item: str, versao: int) -> Optional[ItemRastreavel]:
        """
        Obtém versão específica do item.
        """
        versoes = self.versoes.get(id_item, [])
        for v in versoes:
            if v.versao == versao:
                return v
        return None
        
    def registrar_alteracao(self,
                           item: ItemRastreavel,
                           versao_anterior: int,
                           versao_nova: int,
                           campos_alterados: List[str],
                           valores_anteriores: Dict[str, Any],
                           valores_novos: Dict[str, Any],
                           alterado_por: str,
                           justificativa: Optional[str] = None):
        """
        Registra alteração no histórico.
        """
        historico = HistoricoAlteracao(
            id_item=item.id_item,
            versao_anterior=versao_anterior,
            versao_nova=versao_nova,
            campos_alterados=campos_alterados,
            valores_anteriores=valores_anteriores,
            valores_novos=valores_novos,
            alterado_por=alterado_por,
            data_alteracao=datetime.now(),
            justificativa=justificativa
        )
        
        if item.id_item not in self.historico:
            self.historico[item.id_item] = []
        self.historico[item.id_item].append(historico)
        
    def desfazer_alteracao(self, id_item: str, versao: int, desfeito_por: str) -> bool:
        """
        Desfere alteração para versão anterior.
        Não remove registros, apenas desfaz.
        """
        versoes = self.versoes.get(id_item, [])
        if versao > 1 and versao <= len(versoes):
            versao_anterior = self.obter_versao_especifica(id_item, versao - 1)
            if versao_anterior:
                self.itens[id_item] = versao_anterior
                return True
        return False

# Instância global
gerenciador_rastreabilidade = GerenciadorRastreabilidade()

# Funções utilitárias
def criar_item_rastreavel(id_item: str,
                         tipo: str,
                         dados: Dict[str, Any],
                         criado_por: Optional[str] = None) -> ItemRastreavel:
    """
    Cria novo item rastreável.
    """
    return gerenciador_rastreabilidade.criar_item(id_item, tipo, dados, criado_por)

def atualizar_item_rastreavel(id_item: str,
                             dados_novos: Dict[str, Any],
                             campos_alterados: Optional[List[str]] = None,
                             atualizado_por: Optional[str] = None,
                             justificativa: Optional[str] = None) -> Optional[ItemRastreavel]:
    """
    Atualiza item rastreável.
    """
    return gerenciador_rastreabilidade.atualizar_item(
        id_item=id_item,
        dados_novos=dados_novos,
        campos_alterados=campos_alterados,
        atualizado_por=atualizado_por,
        justificativa=justificativa
    )

def obter_historico_item(id_item: str) -> List[HistoricoAlteracao]:
    """
    Obtém histórico de um item.
    """
    return gerenciador_rastreabilidade.obter_historico(id_item)