"""
Precision VRT Solo - Versao CLI (Linha de Comando)
Roda no terminal/cmd sem precisar de navegador.
"""

import sys
import argparse
import logging
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prescricao_vrt.interpolacao import InterpoladorSolo
from core.prescricao_vrt.zoneamento import Zoneador
from core.prescricao_vrt.prescricao import MotorPrescricao
from core.prescricao_vrt.exportacao import Exportador


def print_banner():
    logging.info("""
+==============================================================+
|           PRECISION VRT SOLO - CLI v1.0                      |
|     Prescricao de Taxa Variavel por Analise de Solo          |
+==============================================================+
    """)


def print_divider(char="=", length=60):
    logging.info(char * length)


def input_com_default(mensagem, default):
    valor = input(f"{mensagem} [{default}]: ").strip()
    return valor if valor else default


def menu_interativo():
    print_banner()
    logging.info("[CONFIG] CONFIGURACAO DOS DADOS\n")
    
    arquivo_default = "data/input/amostras_exemplo.csv"
    arquivo = input_com_default("Arquivo CSV", arquivo_default)
    
    if not Path(arquivo).exists():
        logging.info(f"[ERROR] Arquivo nao encontrado: {arquivo}")
        return None
    
    logging.info("\n[CULTURA]")
    logging.info("  [1] Milho")
    logging.info("  [2] Soja")
    logging.info("  [3] Trigo")
    logging.info("  [4] Arroz")
    logging.info("  [5] Feijao")
    logging.info("  [6] Algodao")
    logging.info("  [7] Cafe")
    logging.info("  [8] Cana-de-Acucar")
    logging.info("  [9] Sorgo")
    logging.info("  [10] Melancia")
    logging.info("  [11] Abobora")
    logging.info("  [12] Frutiferas")
    logging.info("  [13] Citros")
    cultura_opcao = input_com_default("Escolha", "1")
    culturas = {
        "1": "milho", "2": "soja", "3": "trigo", "4": "arroz", "5": "feijao",
        "6": "algodao", "7": "cafe", "8": "cana", "9": "sorgo", "10": "melancia",
        "11": "abobora", "12": "frutiferas", "13": "citrus"
    }
    cultura = culturas.get(cultura_opcao, "milho")
    
    produtividade = int(input_com_default("Produtividade alvo (sc/ha)", "80"))
    
    logging.info("\n[ZONEAMENTO]")
    n_zonas = input_com_default("Numero de zonas (auto=0)", "4")
    n_zonas = None if n_zonas == "0" else int(n_zonas)
    
    resolucao = int(input_com_default("Resolucao do mapa (m)", "10"))
    
    logging.info("\n[ATRIBUTOS] ATRIBUTOS PARA ZONEAMENTO")
    logging.info("  padrao: ph, p_mg_dm3, k_mg_dm3, mo_percent")
    atributos_str = input_com_default("Atributos (separados por virgula)", "ph, p_mg_dm3, k_mg_dm3, mo_percent")
    atributos = [a.strip() for a in atributos_str.split(",")]
    
    return {
        'arquivo': arquivo,
        'cultura': cultura,
        'produtividade': produtividade,
        'n_zonas': n_zonas,
        'resolucao': resolucao,
        'atributos': atributos
    }


def processar(config):
    print_divider()
    logging.info("[PROCESS] PROCESSANDO...")
    print_divider()
    
    logging.info("\n[1/5] Carregando dados...")
    df = pd.read_csv(config['arquivo'])
    logging.info(f"  [OK] {len(df)} amostras carregadas")
    
    colunas_necessarias = ['latitude', 'longitude'] + config['atributos']
    faltantes = [c for c in colunas_necessarias if c not in df.columns]
    
    if faltantes:
        logging.info(f"  [ERROR] Colunas faltantes: {', '.join(faltantes)}")
        return None
    
    logging.info(f"\n[2/5] Interpolando atributos (Krigagem, resolucao {config['resolucao']}m)...")
    interpolador = InterpoladorSolo(
        resolucao_m=config['resolucao'],
        variograma_model='spherical'
    )
    
    resultados_interp = interpolador.interpolar_talhao(
        df,
        x_col='longitude',
        y_col='latitude',
        atributos=config['atributos']
    )
    logging.info(f"  [OK] {len(resultados_interp['atributos'])} atributos interpolados")
    
    logging.info("\n[3/5] Criando zonas de manejo...")
    zoneador = Zoneador(n_zonas=config['n_zonas'] if config['n_zonas'] else 4)
    resultados_zona = zoneador.zonear(
        resultados_interp,
        atributos=config['atributos'],
        n_zonas=config['n_zonas']
    )
    logging.info(f"  [OK] {resultados_zona['estatisticas']['n_zonas']} zonas criadas")
    
    logging.info("\n[4/5] Calculando prescricao...")
    motor = MotorPrescricao(
        cultura=config['cultura'],
        produtividade_alvo=config['produtividade']
    )
    
    prescricoes = motor.prescrever_todas_zonas(resultados_zona['perfis'])
    resumo = prescricoes['resumo']
    
    logging.info(f"  [OK] Custo medio: R$ {resumo['custo_medio_ha']:.2f}/ha")
    logging.info(f"  [OK] Economia VRT: R$ {resumo['economia_vrt']:.2f}/ha")
    
    logging.info("\n[5/5] Exportando resultados...")
    exportador = Exportador(output_dir='data/output')
    
    gdf_zonas = exportador.raster_para_zonas_poligonos(
        resultados_zona['raster_zonas'],
        resultados_interp['grid_x'],
        resultados_interp['grid_y']
    )
    
    gdf_prescricao = exportador.adicionar_prescricao(gdf_zonas, prescricoes)
    
    nome_base = f"prescricao_{config['cultura']}_{config['produtividade']}sc"
    
    caminho_shp = exportador.exportar_shapefile(gdf_prescricao, nome_base)
    caminho_geojson = exportador.exportar_geojson(gdf_prescricao, nome_base)
    caminho_csv = exportador.exportar_csv_prescricao(prescricoes, nome_base)
    
    relatorio = exportador.gerar_relatorio_texto(
        prescricoes,
        resultados_zona['perfis'],
        nome_talhao="Talhao Processado"
    )
    caminho_relatorio = exportador.salvar_relatorio(relatorio, nome_base)
    
    logging.info(f"  [OK] Shapefile: {caminho_shp}")
    logging.info(f"  [OK] GeoJSON: {caminho_geojson}")
    logging.info(f"  [OK] CSV: {caminho_csv}")
    logging.info(f"  [OK] Relatorio: {caminho_relatorio}")
    
    return {
        'config': config,
        'df': df,
        'interpolacao': resultados_interp,
        'zoneamento': resultados_zona,
        'prescricoes': prescricoes,
        'gdf': gdf_prescricao,
        'arquivos': {
            'shapefile': caminho_shp,
            'geojson': caminho_geojson,
            'csv': caminho_csv,
            'relatorio': caminho_relatorio
        }
    }


def mostrar_resultados(resultados):
    if not resultados:
        return
    
    presc = resultados['prescricoes']
    perfis = resultados['zoneamento']['perfis']
    
    print_divider()
    logging.info("[RESULT] RESULTADO DA PRESCRICAO")
    print_divider()
    
    resumo = presc['resumo']
    logging.info(f"""
+-------------------------------------------------------------+
|  RESUMO EXECUTIVO                                           |
+-------------------------------------------------------------+
|  Cultura:          {resultados['config']['cultura'].upper():20}                     |
|  Produtividade:    {resultados['config']['produtividade']} sc/ha                    |
|  Zonas:            {resumo['n_zonas']}                                          |
|  Custo Medio:      R$ {resumo['custo_medio_ha']:>8.2f}/ha                  |
|  Custo Minimo:     R$ {resumo['custo_min_ha']:>8.2f}/ha                  |
|  Custo Maximo:     R$ {resumo['custo_max_ha']:>8.2f}/ha                  |
|  Economia VRT:     R$ {resumo['economia_vrt']:>8.2f}/ha                  |
+-------------------------------------------------------------+
    """)
    
    logging.info("[PRESCRICAO] PRESCRICAO DETALHADA POR ZONA\n")
    
    for zona_id, pres in presc['prescricoes'].items():
        perfil = perfis.get(zona_id, {})
        
        logging.info(f"+-- ZONA {zona_id + 1} {'-' * 50}")
        logging.info(f"|  pH: {perfil.get('ph', {}).get('media', 0):.2f}")
        logging.info(f"|  P: {perfil.get('p_mg_dm3', {}).get('media', 0):.1f} mg/dm3")
        logging.info(f"|  K: {perfil.get('k_mg_dm3', {}).get('media', 0):.1f} mg/dm3")
        logging.info(f"|  Calagem: {pres['calagem']['necessidade_CaCO3_t_ha']} t/ha")
        logging.info(f"|  P2O5: {pres['fosforo']['necessidade_P2O5_kg_ha']:.1f} kg/ha")
        logging.info(f"|  K2O: {pres['potassio']['necessidade_K2O_kg_ha']:.1f} kg/ha")
        logging.info(f"|  N: {pres['nitrogenio']['necessidade_N_kg_ha']:.1f} kg/ha")
        logging.info("|")
        for f in pres['fertilizantes']:
            logging.info(f"|  - {f['fertilizante']}: {f['dose_kg_ha']} kg/ha = R$ {f['custo_ha']:.2f}/ha")
        logging.info(f"|  [CUSTO] R$ {pres['custo_total_ha']:.2f}/ha")
        logging.info(f"+{'-' * 58}\n")
    
    print_divider("=")
    logging.info("[OK] ARQUIVOS GERADOS:")
    print_divider("=")
    for tipo, caminho in resultados['arquivos'].items():
        logging.info(f"  [FILE] {tipo.upper():12} -> {caminho}")
    logging.info("\nProximos passos:")
    logging.info("  1. Importar shapefile no GPS do trator")
    logging.info("  2. Enviar relatorio e CSV ao produtor")
    logging.info("  3. Validar com amostragem apos 2 anos")
    print_divider("=")


def main():
    parser = argparse.ArgumentParser(
        description='Precision VRT Solo - Prescricao de Taxa Variavel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  Interativo:           python cli.py
  Com argumentos:       python cli.py -a amostras.csv -c milho -p 80
  Ajuda:               python cli.py -h
        """
    )
    
    parser.add_argument('-a', '--arquivo', default='data/input/amostras_exemplo.csv',
                       help='Arquivo CSV com analises de solo')
    parser.add_argument('-c', '--cultura', default='milho',
                       choices=['milho', 'soja', 'trigo', 'arroz', 'feijao', 'algodao', 'cafe', 'cana', 'sorgo', 'melancia', 'abobora', 'frutiferas', 'citrus'],
                       help='Cultura')
    parser.add_argument('-p', '--produtividade', type=int, default=80,
                       help='Produtividade alvo em sc/ha')
    parser.add_argument('-z', '--zonas', type=int, default=4,
                       help='Numero de zonas (0=auto)')
    parser.add_argument('-r', '--resolucao', type=int, default=10,
                       help='Resolucao do mapa em metros')
    parser.add_argument('--atributos', default='ph,p_mg_dm3,k_mg_dm3,mo_percent',
                       help='Atributos para zoneamento, separados por virgula')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        config = menu_interativo()
    else:
        config = {
            'arquivo': args.arquivo,
            'cultura': args.cultura,
            'produtividade': args.produtividade,
            'n_zonas': None if args.zonas == 0 else args.zonas,
            'resolucao': args.resolucao,
            'atributos': args.atributos.split(',')
        }
    
    if config is None:
        logging.info("[ERROR] Configuracao invalida. Encerrando.")
        sys.exit(1)
    
    resultados = processar(config)
    
    if resultados:
        mostrar_resultados(resultados)
    else:
        logging.info("[ERROR] Erro no processamento.")
        sys.exit(1)


if __name__ == '__main__':
    main()
