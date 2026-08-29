# Sistema de Persistência do Dashboard
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class DashboardPersistenceService:
    """Serviço para persistir configurações do Dashboard"""
    
    def __init__(self):
        self.config_file = "C:/precision_vrt_solo/app/data/dashboard_configs.json"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Criar diretórios necessários"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
    def load_user_config(self, user_id: str) -> Dict[str, Any]:
        """Carregar configuração do usuário"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
                    
                user_config = all_configs.get(user_id, {})
                return user_config
        except Exception as e:
            print(f"Error loading user config: {e}")
            
        return self.get_default_config()
    
    def save_user_config(self, user_id: str, config: Dict[str, Any]) -> bool:
        """Salvar configuração do usuário"""
        try:
            # Carregar configurações existentes
            all_configs = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            
            # Atualizar configuração do usuário
            all_configs[user_id] = {
                **config,
                'last_updated': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            # Salvar arquivo
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Error saving user config: {e}")
            return False
    
    def reset_user_config(self, user_id: str) -> bool:
        """Resetar configuração do usuário para padrão"""
        default_config = self.get_default_config()
        return self.save_user_config(user_id, default_config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Obter configuração padrão"""
        return {
            'widgets': [
                {
                    'id': 'clientes',
                    'title': 'Clientes',
                    'description': 'Visualizar clientes relacionados ao trabalho',
                    'icon': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
                    'color': '3b82f6',
                    'permission': 'clientes:read',
                    'category': 'indicadores',
                    'state': 'loaded',
                    'has_permission': True,
                    'minimized': False,
                    'size': 'medium'
                },
                {
                    'id': 'fazendas',
                    'title': 'Fazendas',
                    'description': 'Áreas e fazendas do usuário',
                    'icon': 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
                    'color': '10b981',
                    'permission': 'fazendas:read',
                    'category': 'indicadores',
                    'state': 'loaded',
                    'has_permission': True,
                    'minimized': False,
                    'size': 'medium'
                }
            ],
            'layout': {},
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_user_widgets(self, user_id: str, user_permissions: List[str]) -> List[Dict[str, Any]]:
        """Obter widgets disponíveis para o usuário"""
        config = self.load_user_config(user_id)
        widgets = config.get('widgets', [])
        
        # Filtrar widgets por permissão
        filtered_widgets = []
        for widget in widgets:
            if widget.get('permission') in user_permissions:
                widget['has_permission'] = True
                filtered_widgets.append(widget)
            else:
                widget['has_permission'] = False
                
        return filtered_widgets
    
    def update_widget_state(self, user_id: str, widget_id: str, state: str) -> bool:
        """Atualizar estado de um widget"""
        config = self.load_user_config(user_id)
        widgets = config.get('widgets', [])
        
        for widget in widgets:
            if widget['id'] == widget_id:
                widget['state'] = state
                widget['last_updated'] = datetime.now().isoformat()
                return self.save_user_config(user_id, config)
        
        return False
    
    def get_widget_data(self, user_id: str, widget_id: str) -> Dict[str, Any]:
        """Obter dados de um widget específico"""
        # Simulação de dados de widgets
        widget_data = {
            'clientes': {
                'total': 15,
                'recent': 3,
                'trend': 'up',
                'data': [
                    {'name': 'Cliente A', 'value': 50000, 'change': 10},
                    {'name': 'Cliente B', 'value': 30000, 'change': 5},
                    {'name': 'Cliente C', 'value': 45000, 'change': -2}
                ]
            },
            'fazendas': {
                'total': 8,
                'area_total': '1,250 ha',
                'processadas': 3,
                'trend': 'stable',
                'data': [
                    {'name': 'Fazenda Alfa', 'area': '250 ha', 'status': 'processando'},
                    {'name': 'Fazenda Beta', 'area': '320 ha', 'status': 'agendado'},
                    {'name': 'Fazenda Gama', 'area': '410 ha', 'status': 'concluído'}
                ]
            },
            'processamentos': {
                'total': 12,
                'andamento': 5,
                'concluido': 7,
                'trend': 'up',
                'data': [
                    {'id': 1, 'name': 'Processamento A', 'status': 'andamento', 'progress': 75},
                    {'id': 2, 'name': 'Processamento B', 'status': 'agendado', 'progress': 0},
                    {'id': 3, 'name': 'Processamento C', 'status': 'concluido', 'progress': 100}
                ]
            },
            'prescricoes': {
                'total': 24,
                'recentes': 4,
                'trend': 'up',
                'data': [
                    {'id': 1, 'name': 'Prescrição XPTO', 'status': 'concluida', 'data': '2024-01-15'},
                    {'id': 2, 'name': 'Prescrição ABC', 'status': 'andamento', 'data': '2024-01-20'},
                    {'id': 3, 'name': 'Prescrição DEF', 'status': 'agendada', 'data': '2024-01-25'}
                ]
            },
            'recebimentos': {
                'total': 185000,
                'mes_atual': 45000,
                'trend': 'up',
                'data': [
                    {'id': 1, 'name': 'Recebimento 001', 'value': 25000, 'date': '2024-01-15', 'status': 'pago'},
                    {'id': 2, 'name': 'Recebimento 002', 'value': 20000, 'date': '2024-01-16', 'status': 'pago'},
                    {'id': 3, 'name': 'Recebimento 003', 'value': 30000, 'date': '2024-01-17', 'status': 'pendente'}
                ]
            },
            'pagamentos': {
                'total': 125000,
                'pendente': 35000,
                'trend': 'down',
                'data': [
                    {'id': 1, 'name': 'Pagamento 001', 'value': 15000, 'date': '2024-01-15', 'status': 'pendente'},
                    {'id': 2, 'name': 'Pagamento 002', 'value': 20000, 'date': '2024-01-16', 'status': 'pendente'},
                    {'id': 3, 'name': 'Pagamento 003', 'value': 25000, 'date': '2024-01-17', 'status': 'concluido'}
                ]
            },
            'atividades': {
                'total': 28,
                'hoje': 4,
                'trend': 'stable',
                'data': [
                    {'id': 1, 'description': 'Processamento concluído', 'user': ' João Silva', 'time': '2 horas atrás'},
                    {'id': 2, 'description': 'Nova prescrição criada', 'user': ' Maria Santos', 'time': '3 horas atrás'},
                    {'id': 3, 'description': 'Atualização de cadastro', 'user': ' Carlos Oliveira', 'time': '5 horas atrás'}
                ]
            },
            'agenda': {
                'total': 6,
                'hoje': 2,
                'trend': 'up',
                'data': [
                    {'id': 1, 'title': 'Reunião com cliente', 'date': '2024-01-20', 'time': '10:00'},
                    {'id': 2, 'title': 'Coleta de amostras', 'date': '2024-01-21', 'time': '14:00'},
                    {'id': 3, 'title': 'Análise de resultados', 'date': '2024-01-22', 'time': '09:00'}
                ]
            },
            'usuarios': {
                'total': 12,
                'ativos': 10,
                'trend': 'stable',
                'data': [
                    {'id': 1, 'name': 'João Silva', 'role': 'Consultor', 'status': 'ativo'},
                    {'id': 2, 'name': 'Maria Santos', 'role': 'Financeiro', 'status': 'ativo'},
                    {'id': 3, 'name': 'Carlos Oliveira', 'role': 'Técnico', 'status': 'inativo'}
                ]
            },
            'alertas': {
                'total': 5,
                'criticos': 2,
                'trend': 'down',
                'data': [
                    {'id': 1, 'title': 'Falha no sistema', 'severity': 'critico', 'time': '1 hora atrás'},
                    {'id': 2, 'title': 'Backup pendente', 'severity': 'warning', 'time': '2 horas atrás'},
                    {'id': 3, 'title': 'Atualização disponível', 'severity': 'info', 'time': '3 horas atrás'}
                ]
            }
        }
        
        return widget_data.get(widget_id, {
            'total': 0,
            'message': 'Dados não disponíveis',
            'data': []
        })
    
    def export_config(self, user_id: str) -> Dict[str, Any]:
        """Exportar configuração do usuário"""
        config = self.load_user_config(user_id)
        
        # Remover informações sensíveis
        safe_config = config.copy()
        if 'widgets' in safe_config:
            for widget in safe_config['widgets']:
                if 'permission' in widget:
                    widget['permission'] = '***'
                    
        return safe_config
    
    def import_config(self, user_id: str, config: Dict[str, Any]) -> bool:
        """Importar configuração para o usuário"""
        try:
            # Validar configuração
            if not self.validate_config(config):
                return False
                
            return self.save_user_config(user_id, config)
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validar configuração"""
        required_fields = ['widgets', 'layout']
        
        for field in required_fields:
            if field not in config:
                return False
                
        # Validar widgets
        for widget in config['widgets']:
            required_widget_fields = ['id', 'title', 'description']
            for field in required_widget_fields:
                if field not in widget:
                    return False
                    
        return True
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obter estatísticas do usuário"""
        config = self.load_user_config(user_id)
        widgets = config.get('widgets', [])
        
        stats = {
            'total_widgets': len(widgets),
            'active_widgets': len([w for w in widgets if not w.get('minimized', False)]),
            'minimized_widgets': len([w for w in widgets if w.get('minimized', False)]),
            'categories': {},
            'permissions': {}
        }
        
        # Calcular estatísticas por categoria
        for widget in widgets:
            category = widget.get('category', 'general')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            permission = widget.get('permission', 'unknown')
            stats['permissions'][permission] = stats['permissions'].get(permission, 0) + 1
            
        return stats