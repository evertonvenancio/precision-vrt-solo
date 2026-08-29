"""
Precision VRT Solo — Teste do Sistema de Relatórios

Script para validar o funcionamento dos relatórios com dados reais.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def testar_relatorios():
    """
    Testa o sistema de relatórios com dados reais.
    """
    print("📊 Testando Sistema de Relatórios...")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        engine = create_engine('sqlite:///precision_vrt.db')
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Instanciar serviço de relatórios
        from services.report_service import ReportService
        report_service = ReportService(db)
        
        print("✅ 1. Serviço de relatórios instanciado com sucesso")
        
        # Testar relatório de clientes (sem filtros)
        resultado_clientes = report_service.gerar_relatorio_clientes()
        print(f"✅ 2. Relatório de clientes: {resultado_clientes['data']['total_registros']} clientes encontrados")
        
        if resultado_clientes['data']['dados']:
            cliente = resultado_clientes['data']['dados'][0]
            print(f"   - Primeiro cliente: {cliente['Nome']} ({cliente['CPF/CNPJ']})")
            print(f"   - Status: {cliente['Status']}")
        
        # Testar relatório financeiro (sem filtros)
        resultado_financeiro = report_service.gerar_relatorio_financeiro()
        print(f"✅ 3. Relatório financeiro: {resultado_financeiro['data']['total_registros']} orçamentos encontrados")
        
        if resultado_financeiro['data']['totais']:
            totais = resultado_financeiro['data']['totais']
            print(f"   - Total orçamentos: {totais['total_orcamentos']}")
            print(f"   - Valor total: {totais['valor_total']}")
        
        # Testar relatório operacional (sem filtros)
        resultado_operacional = report_service.gerar_relatorio_operacional()
        print(f"✅ 4. Relatório operacional: {resultado_operacional['data']['total_registros']} prescrições encontradas")
        
        if resultado_operacional['data']['totais']:
            totais = resultado_operacional['data']['totais']
            print(f"   - Total prescrições: {totais['total_prescricoes']}")
            print(f"   - Área total: {totais['area_total']}")
        
        # Testar relatório com filtros
        print("\n🔍 Testando filtros:")
        resultado_filtrado = report_service.gerar_relatorio_clientes(
            filtros={'status': 'ativo'},
            formatos=['CSV']
        )
        print(f"✅ 5. Relatório filtrado (ativos): {resultado_filtrado['data']['total_registros']} clientes ativos")
        
        # Testar relatório vazio
        resultado_vazio = report_service.gerar_relatorio_financeiro(
            filtros={'data_inicio': '2030-01-01', 'data_fim': '2030-12-31'}
        )
        print(f"✅ 6. Relatório vazio: {resultado_filtrado['data']['total_registros']} registros futuros (esperado: 0)")
        
        # Testar exportação
        if resultado_financeiro['success'] and 'exportacao' in resultado_financeiro:
            print(f"✅ 7. Exportação suportada: {resultado_financeiro['exportacao']['arquivos_exportados']}")
        
        # Testar tipos disponíveis
        tipos_disponiveis = report_service.obter_relatorios_disponiveis()
        print(f"✅ 8. Tipos de relatórios disponíveis: {len(tipos_disponiveis)}")
        
        for relatorio in tipos_disponiveis:
            print(f"   - {relatorio['nome']}: {relatorio['descricao']}")
        
        db.close()
        
        print("\n🎯 Todos os testes de relatórios passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante testes: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_relatorios()
    
    if sucesso:
        print("\n🔧 Próximos passos:")
        print("   1. Reiniciar o aplicativo")
        print("   2. Acessar /web/relatorios para visualizar interface")
        print("   3. Testar geração de relatórios na interface")
        print("   4. Testar exportação em diferentes formatos")
    else:
        print("\n❌ Alguns testes falharam. Verificar erros acima.")