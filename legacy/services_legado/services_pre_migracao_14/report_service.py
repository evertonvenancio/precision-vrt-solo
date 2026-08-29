"""
Precision VRT Solo — Serviço de Relatórios

Responsável por gerar relatórios reais a partir de dados do sistema.
Utiliza a infraestrutura de exportação existente.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text

from db.database import get_db
from services.exportacao_service import ExportacaoService
from services.clientes_service import ClientesService
from services.dashboard_service import DashboardService


class ReportService:
    """
    Serviço de relatórios que gera relatórios reais a partir de dados do sistema.
    Não contém lógica de negócio, apenas prepara dados para relatório.
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Import dinâmico para evitar problemas de importação circular
    
    def gerar_relatorio_clientes(self,
                               filtros: Optional[Dict[str, Any]] = None,
                               formatos: List[str] = None) -> Dict[str, Any]:
        """
        Gera relatório de clientes com dados reais.
        
        Args:
            filtros: Dicionário com filtros opcionais
            formatos: Lista de formatos para exportação
            
        Returns:
            Resultado da geração do relatório
        """
        try:
            if formatos is None:
                formatos = ['CSV']
            
            # Obter dados reais de clientes
            clientes_service = ClientesService(self.db)
            clientes = clientes_service.listar()
            
            # Aplicar filtros se existirem
            if filtros:
                clientes = self._aplicar_filtros_clientes(clientes, filtros)
            
            # Preparar dados para relatório
            relatorio_data = {
                'titulo': 'Relatório de Clientes',
                'gerado_em': datetime.now().isoformat(),
                'total_registros': len(clientes),
                'periodo': {
                    'inicio': None,
                    'fim': None
                },
                'dados': []
            }
            
            # Transformar dados para formato de relatório
            for cliente in clientes:
                relatorio_data['dados'].append({
                    'ID': cliente['id'],
                    'Nome': cliente['nome'],
                    'CPF/CNPJ': cliente['cpf_cnpj'],
                    'Email': cliente['email'],
                    'Telefone': cliente['telefone'],
                    'Cidade': cliente['cidade'],
                    'Estado': cliente['estado'],
                    'Área Total (ha)': cliente['area_total_hectares'],
                    'Status': 'Ativo' if cliente['ativo'] else 'Inativo',
                    'Criado Em': cliente['criado_em']
                })
            
            # Se não houver dados, manter estrutura
            if not relatorio_data['dados']:
                relatorio_data['dados'] = [{
                    'ID': '',
                    'Nome': 'Nenhum cliente encontrado',
                    'CPF/CNPJ': '',
                    'Email': '',
                    'Telefone': '',
                    'Cidade': '',
                    'Estado': '',
                    'Área Total (ha)': 0,
                    'Status': '',
                    'Criado Em': ''
                }]
                relatorio_data['total_registros'] = 0
            
            # Gerar exportação
            if formatos:
                from services.exportacao_service import ExportacaoService
                export_service = ExportacaoService()
                resultado_export = export_service.exportar_multiplos(
                    dados_originais=relatorio_data,
                    formatos=formatos,
                    nome_arquivo_base="relatorio_clientes"
                )
            
                return {
                    'success': True,
                    'data': relatorio_data,
                    'exportacao': resultado_export,
                    'mensagem': f'Relatório gerado com sucesso. {relatorio_data["total_registros"]} registros encontrados.'
                }
            
            return {
                'success': True,
                'data': relatorio_data,
                'mensagem': f'Relatário preparado. {relatorio_data["total_registros"]} registros encontrados.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mensagem': f'Erro ao gerar relatório de clientes: {str(e)}'
            }
    
    def gerar_relatorio_financeiro(self,
                                 filtros: Optional[Dict[str, Any]] = None,
                                 formatos: List[str] = None) -> Dict[str, Any]:
        """
        Gera relatório financeiro com dados reais.
        """
        try:
            if formatos is None:
                formatos = ['CSV']
            
            # Query para dados financeiros reais
            query_orcamentos = text("""
                SELECT 
                    o.id, o.cliente_id, o.data_emissao, o.valor_total_liquido as valor_total, o.status,
                    c.nome as cliente_nome, c.cpf_cnpj
                FROM orcamentos o
                LEFT JOIN clientes c ON o.cliente_id = c.id
                WHERE o.status IS NOT NULL
            """)
            
            if filtros:
                conditions = []
                if 'data_inicio' in filtros:
                    conditions.append(f"o.data_emissao >= '{filtros['data_inicio']}'")
                if 'data_fim' in filtros:
                    conditions.append(f"o.data_emissao <= '{filtros['data_fim']}'")
                if 'status' in filtros:
                    conditions.append(f"o.status = '{filtros['status']}'")
                
                if conditions:
                    query_orcamentos = text(str(query_orcamentos) + " AND " + " AND ".join(conditions))
            
            result = self.db.execute(query_orcamentos)
            orcamentos = result.fetchall()
            
            # Preparar dados para relatório
            relatorio_data = {
                'titulo': 'Relatório Financeiro - Orçamentos',
                'gerado_em': datetime.now().isoformat(),
                'total_registros': len(orcamentos),
                'periodo': {
                    'inicio': filtros.get('data_inicio') if filtros else None,
                    'fim': filtros.get('data_fim') if filtros else None
                },
                'dados': []
            }
            
            total_geral = 0
            for orcamento in orcamentos:
                total_geral += orcamento[3]  # valor_total
                
                relatorio_data['dados'].append({
                    'ID Orçamento': orcamento[0],
                    'Cliente ID': orcamento[1],
                    'Cliente Nome': orcamento[6] if len(orcamento) > 6 else '',
                    'CPF/CNPJ': orcamento[7] if len(orcamento) > 7 else '',
                    'Data Emissão': orcamento[2],
                    'Valor Total': f"R$ {orcamento[3]:,.2f}",
                    'Status': orcamento[4],
                    'Valor Numérico': orcamento[3]
                })
            
            # Adicionar totais
            relatorio_data['totais'] = {
                'total_orcamentos': len(orcamentos),
                'valor_total': f"R$ {total_geral:,.2f}",
                'valor_medio': f"R$ {total_geral/len(orcamentos):,.2f}" if orcamentos else "R$ 0,00"
            }
            
            # Se não houver dados
            if not relatorio_data['dados']:
                relatorio_data['dados'] = [{
                    'ID Orçamento': '',
                    'Cliente ID': '',
                    'Cliente Nome': 'Nenhum orçamento encontrado',
                    'CPF/CNPJ': '',
                    'Data Emissão': '',
                    'Valor Total': 'R$ 0,00',
                    'Status': '',
                    'Valor Numérico': 0
                }]
                relatorio_data['totais'] = {
                    'total_orcamentos': 0,
                    'valor_total': 'R$ 0,00',
                    'valor_medio': 'R$ 0,00'
                }
                relatorio_data['total_registros'] = 0
            
            # Gerar exportação
            if formatos:
                from services.exportacao_service import ExportacaoService
                export_service = ExportacaoService()
                resultado_export = export_service.exportar_multiplos(
                    dados_originais=relatorio_data,
                    formatos=formatos,
                    nome_arquivo_base="relatorio_financeiro"
                )
                
                return {
                    'success': True,
                    'data': relatorio_data,
                    'exportacao': resultado_export,
                    'mensagem': f'Relatório financeiro gerado com sucesso. {relatorio_data["total_registros"]} orçamentos encontrados.'
                }
            
            return {
                'success': True,
                'data': relatorio_data,
                'mensagem': f'Relatário financeiro preparado. {relatorio_data["total_registros"]} orçamentos encontrados.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mensagem': f'Erro ao gerar relatório financeiro: {str(e)}'
            }
    
    def gerar_relatorio_operacional(self,
                                  filtros: Optional[Dict[str, Any]] = None,
                                  formatos: List[str] = None) -> Dict[str, Any]:
        """
        Gera relatório operacional com dados reais (prescrições, análises, etc.).
        """
        try:
            if formatos is None:
                formatos = ['CSV']
            
            # Query para prescrições reais
            query_prescricoes = text("""
                SELECT 
                    p.id, p.cliente_id, p.criado_em as data_criacao, p.status, p.area_hectares as area_total,
                    c.nome as cliente_nome
                FROM prescricao p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                WHERE p.status IS NOT NULL
            """)
            
            result = self.db.execute(query_prescricoes)
            prescricoes = result.fetchall()
            
            # Preparar dados para relatório
            relatorio_data = {
                'titulo': 'Relatório Operacional - Prescrições',
                'gerado_em': datetime.now().isoformat(),
                'total_registros': len(prescricoes),
                'periodo': {
                    'inicio': None,
                    'fim': None
                },
                'dados': []
            }
            
            total_area = 0
            for prescricao in prescricoes:
                total_area += prescricao[4]  # area_total
                
                relatorio_data['dados'].append({
                    'ID Prescrição': prescricao[0],
                    'Cliente ID': prescricao[1],
                    'Cliente Nome': prescricao[5],
                    'Data Criação': prescricao[2],
                    'Status': prescricao[3],
                    'Área (ha)': prescricao[4],
                    'Valor Numérico': prescricao[4]  # Para cálculos
                })
            
            # Adicionar totais
            relatorio_data['totais'] = {
                'total_prescricoes': len(prescricoes),
                'area_total': f"{total_area:,.2f} ha",
                'area_media': f"{total_area/len(prescricoes):,.2f} ha" if prescricoes else "0,00 ha"
            }
            
            # Se não houver dados
            if not relatorio_data['dados']:
                relatorio_data['dados'] = [{
                    'ID Prescrição': '',
                    'Cliente ID': '',
                    'Cliente Nome': 'Nenhuma prescrição encontrada',
                    'Data Criação': '',
                    'Status': '',
                    'Área (ha)': '0,00',
                    'Valor Numérico': 0
                }]
                relatorio_data['totais'] = {
                    'total_prescricoes': 0,
                    'area_total': '0,00 ha',
                    'area_media': '0,00 ha'
                }
                relatorio_data['total_registros'] = 0
            
            # Gerar exportação
            if formatos:
                from services.exportacao_service import ExportacaoService
                export_service = ExportacaoService()
                resultado_export = export_service.exportar_multiplos(
                    dados_originais=relatorio_data,
                    formatos=formatos,
                    nome_arquivo_base="relatorio_operacional"
                )
                
                return {
                    'success': True,
                    'data': relatorio_data,
                    'exportacao': resultado_export,
                    'mensagem': f'Relatório operacional gerado com sucesso. {relatorio_data["total_registros"]} prescrições encontradas.'
                }
            
            return {
                'success': True,
                'data': relatorio_data,
                'mensagem': f'Relatário operacional preparado. {relatorio_data["total_registros"]} prescrições encontradas.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mensagem': f'Erro ao gerar relatório operacional: {str(e)}'
            }
    
    def _aplicar_filtros_clientes(self, clientes: List[Dict[str, Any]], filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aplica filtros aos dados de clientes.
        """
        resultados = clientes
        
        if 'status' in filtros:
            status_filtro = filtros['status']
            if status_filtro == 'ativo':
                resultados = [c for c in resultados if c['ativo'] == 1]
            elif status_filtro == 'inativo':
                resultados = [c for c in resultados if c['ativo'] == 0]
        
        if 'cidade' in filtros:
            cidade_filtro = filtros['cidade'].lower()
            resultados = [c for c in resultados if c['cidade'] and c['cidade'].lower() == cidade_filtro]
        
        if 'estado' in filtros:
            estado_filtro = filtros['estado'].upper()
            resultados = [c for c in resultados if c['estado'] and c['estado'].upper() == estado_filtro]
        
        return resultados
    
    def obter_relatorios_disponiveis(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de relatórios disponíveis.
        """
        return [
            {
                'id': 'clientes',
                'nome': 'Relatório de Clientes',
                'descricao': 'Lista completa de clientes cadastrados',
                'filtros': ['status', 'cidade', 'estado'],
                'formatos': ['CSV', 'Excel', 'PDF'],
                'permissao': 'relatorios:clientes'
            },
            {
                'id': 'financeiro',
                'nome': 'Relatório Financeiro',
                'descricao': 'Orçamentos e movimentações financeiras',
                'filtros': ['data_inicio', 'data_fim', 'status'],
                'formatos': ['CSV', 'Excel'],
                'permissao': 'relatorios:financeiro'
            },
            {
                'id': 'operacional',
                'nome': 'Relatório Operacional',
                'descricao': 'Prescrições e análises técnicas',
                'filtros': ['data_inicio', 'data_fim'],
                'formatos': ['CSV', 'Excel'],
                'permissao': 'relatorios:operacional'
            }
        ]