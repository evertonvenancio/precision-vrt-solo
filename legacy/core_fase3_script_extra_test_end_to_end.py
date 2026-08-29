# test_end_to_end.py
# Testes end-to-end do pipeline VRT completo
# VERSÃO 3.3 - Testa: DB -> Pipeline -> Export -> Financeiro

import os
import sys
import shutil
from datetime import datetime

# Garantir que estamos no diretório do projeto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from db_schema import init_db, get_connection
from vrt_pipeline import VRTPipeline
from export_manager import ExportManager
from financeiro_manager import FinanceiroManager

class TestPipelineEndToEnd:
    def __init__(self):
        self.db_path = os.path.join(PROJECT_DIR, 'precision_vrt.db')
        self.test_results = []
        
    def setup(self):
        """Prepara ambiente de teste."""
        logging.info("=" * 60)
        logging.info("🧪 INICIANDO TESTES END-TO-END VRT v3.3")
        logging.info("=" * 60)
        
        # Backup do banco existente
        if os.path.exists(self.db_path):
            backup = self.db_path + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(self.db_path, backup)
            logging.info(f"[SETUP] Backup criado: {backup}")
        
        # Inicializar DB limpo
        init_db()
        self._seed_dados_teste()
        
    def _seed_dados_teste(self):
        """Insere dados mínimos para teste."""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Cliente teste
        cursor.execute('''
            INSERT INTO clientes (nome, cpf_cnpj, telefone, email, cidade, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Fazenda Teste Silva', '12.345.678/0001-90', '(11) 98765-4321', 
              'teste@fazenda.com', 'Ribeirão Preto', 'SP'))
        self.cliente_id = cursor.lastrowid
        
        # Fazenda teste
        cursor.execute('''
            INSERT INTO fazendas (cliente_id, nome, hectares_total, localizacao)
            VALUES (?, ?, ?, ?)
        ''', (self.cliente_id, 'Fazenda Boa Vista', 150.5, 'Municipio Teste'))
        self.fazenda_id = cursor.lastrowid
        
        # Talhão teste
        cursor.execute('''
            INSERT INTO talhoes (fazenda_id, nome, hectares)
            VALUES (?, ?, ?)
        ''', (self.fazenda_id, 'Talhão 01 - Norte', 45.0))
        self.talhao_id = cursor.lastrowid
        
        # Equipe teste
        cursor.execute('''
            INSERT INTO equipe (nome, funcao, comissao_percentual, email)
            VALUES (?, ?, ?, ?)
        ''', ('Eng. Agrônomo Teste', 'Consultor Técnico', 5.0, 'agronomo@techagri.com'))
        self.equipe_id = cursor.lastrowid
        
        # Config export
        cursor.execute('''
            UPDATE config_export SET 
                empresa_nome = 'Tech & Agri VRT - TESTE',
                empresa_cnpj = '98.765.432/0001-10',
                cor_primaria = '#1565C0'
            WHERE id = 1
        ''')
        
        conn.commit()
        conn.close()
        logging.info(f"[SEED] Cliente #{self.cliente_id}, Fazenda #{self.fazenda_id}, Talhão #{self.talhao_id}")
    
    def _criar_dados_teste_vetorial(self):
        """Cria shapefile de teste com pontos de amostragem."""
        try:
            import geopandas as gpd
            from shapely.geometry import Point
            import numpy as np
            
            np.random.seed(42)
            n_points = 50
            
            # Gerar pontos em grid
            x = np.random.uniform(-47.8, -47.7, n_points)
            y = np.random.uniform(-21.2, -21.1, n_points)
            
            # Simular nutrientes
            n = np.random.normal(40, 15, n_points)
            p = np.random.normal(15, 8, n_points)
            k = np.random.normal(120, 40, n_points)
            ph = np.random.normal(5.5, 0.8, n_points)
            
            gdf = gpd.GeoDataFrame({
                'id': range(1, n_points + 1),
                'n': n,
                'p': p,
                'k': k,
                'ph': ph,
                'mo': np.random.normal(3, 1, n_points),
                'geometry': [Point(xi, yi) for xi, yi in zip(x, y)]
            }, crs='EPSG:4326')
            
            temp_dir = os.path.join(PROJECT_DIR, 'temp_test')
            os.makedirs(temp_dir, exist_ok=True)
            path = os.path.join(temp_dir, 'amostragem_teste.shp')
            gdf.to_file(path, driver='ESRI Shapefile', encoding='utf-8')
            
            return path
            
        except ImportError:
            # Fallback: criar CSV simples
            temp_dir = os.path.join(PROJECT_DIR, 'temp_test')
            os.makedirs(temp_dir, exist_ok=True)
            path = os.path.join(temp_dir, 'amostragem_teste.csv')
            
            import csv
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'n', 'p', 'k', 'ph', 'lat', 'lon'])
                for i in range(50):
                    writer.writerow([i+1, 40, 15, 120, 5.5, -21.15, -47.75])
            
            return path
    
    def test_01_pipeline_processamento(self):
        """TESTE 1: Pipeline processa amostragem e salva no DB."""
        logging.info("\n📋 TESTE 1: Pipeline de Processamento VRT")
        logging.info("-" * 50)
        
        arquivo_teste = self._criar_dados_teste_vetorial()
        logging.info(f"[INFO] Arquivo de teste: {arquivo_teste}")
        
        pipeline = VRTPipeline(n_zonas=4)
        ok, msg, rec_id = pipeline.processar_amostragem(
            arquivo_entrada=arquivo_teste,
            cliente_id=self.cliente_id,
            fazenda_id=self.fazenda_id,
            talhao_id=self.talhao_id,
            cultura='Soja',
            safra='2026/2027',
            responsavel_tecnico_id=self.equipe_id
        )
        
        self.test_results.append(('Pipeline Processamento', ok, msg))
        logging.info(f"{'✅' if ok else '❌'} {msg}")
        
        if ok and rec_id:
            self.recomendacao_id = rec_id
            
            # Verificar no DB
            rec = pipeline.get_recomendacao(rec_id)
            assert rec is not None, "Recomendação não encontrada no DB"
            assert len(rec['itens']) > 0, "Nenhuma zona salva"
            logging.info(f"   → {len(rec['itens'])} zonas salvas no banco")
            return True
        return False
    
    def test_02_export_pdf(self):
        """TESTE 2: Exportação PDF com branding."""
        logging.info("\n📋 TESTE 2: Exportação PDF")
        logging.info("-" * 50)
        
        if not hasattr(self, 'recomendacao_id'):
            logging.info("⚠️ Pulando: recomendação não criada")
            return False
        
        em = ExportManager()
        ok, msg, path = em.exportar_pdf(self.recomendacao_id)
        
        self.test_results.append(('Export PDF', ok, msg))
        logging.info(f"{'✅' if ok else '❌'} {msg}")
        
        if ok and path:
            assert os.path.exists(path), "Arquivo PDF não foi criado"
            size = os.path.getsize(path)
            assert size > 0, "PDF vazio"
            logging.info(f"   → Tamanho: {size} bytes")
            return True
        return False
    
    def test_03_export_shapefile(self):
        """TESTE 3: Exportação Shapefile."""
        logging.info("\n📋 TESTE 3: Exportação Shapefile")
        logging.info("-" * 50)
        
        if not hasattr(self, 'recomendacao_id'):
            logging.info("⚠️ Pulando: recomendação não criada")
            return False
        
        em = ExportManager()
        ok, msg, path = em.exportar_shapefile(self.recomendacao_id)
        
        self.test_results.append(('Export Shapefile', ok, msg))
        logging.info(f"{'✅' if ok else '❌'} {msg}")
        return ok
    
    def test_04_export_csv(self):
        """TESTE 4: Exportação CSV."""
        logging.info("\n📋 TESTE 4: Exportação CSV")
        logging.info("-" * 50)
        
        if not hasattr(self, 'recomendacao_id'):
            logging.info("⚠️ Pulando: recomendação não criada")
            return False
        
        em = ExportManager()
        ok, msg, path = em.exportar_csv(self.recomendacao_id)
        
        self.test_results.append(('Export CSV', ok, msg))
        logging.info(f"{'✅' if ok else '❌'} {msg}")
        return ok
    
    def test_05_financeiro_orcamento(self):
        """TESTE 5: Criação de orçamento a partir da recomendação."""
        logging.info("\n📋 TESTE 5: Financeiro - Orçamento")
        logging.info("-" * 50)
        
        if not hasattr(self, 'recomendacao_id'):
            logging.info("⚠️ Pulando: recomendação não criada")
            return False
        
        fm = FinanceiroManager()
        
        # Buscar dados da recomendação para calcular custos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(custo_estimado) as total_insumos,
                   SUM(area_hectares) as total_area
            FROM recomendacoes_itens 
            WHERE recomendacao_id = ?
        ''', (self.recomendacao_id,))
        row = cursor.fetchone()
        conn.close()
        
        custo_insumos = row['total_insumos'] or 15000.0
        area_total = row['total_area'] or 45.0
        
        ok, msg, orc_id = fm.criar_orcamento(
            cliente_id=self.cliente_id,
            descricao=f"VRT Soja 2026 - Rec #{self.recomendacao_id}",
            recomendacao_id=self.recomendacao_id,
            talhao_id=self.talhao_id,
            custo_insumos=custo_insumos,
            custo_mao_obra=area_total * 45.0,
            custo_equipamentos=2000.0,
            custo_transporte=1200.0,
            custo_administrativo=800.0,
            desconto_percentual=5.0,
            comissao_equipe_id=self.equipe_id,
            responsavel_tecnico_id=self.equipe_id
        )
        
        self.test_results.append(('Financeiro Orçamento', ok, msg))
        logging.info(f"{'✅' if ok else '❌'} {msg}")
        
        if ok and orc_id:
            self.orcamento_id = orc_id
            
            # Aprovar e faturar
            ok2, msg2 = fm.aprovar_orcamento(orc_id)
            logging.info(f"   → Aprovação: {'✅' if ok2 else '❌'} {msg2}")
            
            ok3, msg3, fat_id = fm.faturar_orcamento(
                orc_id, 
                numero_nota="0001", 
                metodo_pagamento="PIX"
            )
            logging.info(f"   → Faturamento: {'✅' if ok3 else '❌'} {msg3}")
            
            if fat_id:
                ok4, msg4 = fm.marcar_pago(fat_id)
                logging.info(f"   → Pagamento: {'✅' if ok4 else '❌'} {msg4}")
            
            # Resumo
            resumo = fm.resumo_financeiro()
            logging.info(f"   → Resumo: Orçado R$ {resumo['total_orcado']:.2f} | "
                  f"Faturado R$ {resumo['total_faturado']:.2f} | "
                  f"Pago R$ {resumo['total_pago']:.2f}")
            return True
        return False
    
    def test_06_consultas_integradas(self):
        """TESTE 6: Consultas integradas."""
        logging.info("\n📋 TESTE 6: Consultas Integradas")
        logging.info("-" * 50)
        
        pipeline = VRTPipeline()
        recs = pipeline.listar_recomendacoes(cliente_id=self.cliente_id)
        logging.info(f"   → {len(recs)} recomendações do cliente")
        
        fm = FinanceiroManager()
        orcs = fm.listar_orcamentos(cliente_id=self.cliente_id)
        logging.info(f"   → {len(orcs)} orçamentos do cliente")
        
        fats = fm.listar_faturamentos(cliente_id=self.cliente_id)
        logging.info(f"   → {len(fats)} faturamentos do cliente")
        
        self.test_results.append(('Consultas Integradas', True, f"{len(recs)} recs, {len(orcs)} orcs, {len(fats)} fats"))
        return True
    
    def run_all(self):
        """Executa todos os testes."""
        self.setup()
        
        tests = [
            self.test_01_pipeline_processamento,
            self.test_02_export_pdf,
            self.test_03_export_shapefile,
            self.test_04_export_csv,
            self.test_05_financeiro_orcamento,
            self.test_06_consultas_integradas,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logging.info(f"❌ ERRO CRÍTICO em {test.__name__}: {e}")
                self.test_results.append((test.__name__, False, str(e)))
        
        # Resumo
        logging.info("\n" + "=" * 60)
        logging.info("📊 RESUMO DOS TESTES")
        logging.info("=" * 60)
        
        passed = sum(1 for _, ok, _ in self.test_results if ok)
        total = len(self.test_results)
        
        for nome, ok, msg in self.test_results:
            status = "✅ PASSOU" if ok else "❌ FALHOU"
            logging.info(f"{status} | {nome}")
            if not ok:
                logging.info(f"      → {msg}")
        
        logging.info(f"\n🎯 Resultado: {passed}/{total} testes passaram")
        logging.info("=" * 60)
        
        # Limpeza
        temp_dir = os.path.join(PROJECT_DIR, 'temp_test')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logging.info(f"[CLEANUP] Temp removido: {temp_dir}")
        
        return passed == total

if __name__ == "__main__":
    tester = TestPipelineEndToEnd()
    sucesso = tester.run_all()
    sys.exit(0 if sucesso else 1)

