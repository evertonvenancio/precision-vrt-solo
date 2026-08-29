"""
Exportador Tecnico - PDF e Shapefile
"""

from datetime import datetime
from typing import List, Dict, Optional

# ============================================================
# CONFIGURACAO FUTURA
# ============================================================
CONFIG_EXPORT = {
    "logo_path": None,
    "cabecalho_linha1": "Tech & Agri VRT",
    "cabecalho_linha2": "Sistema de Prescricao de Taxa Variavel",
    "cor_primaria": "#00C853",
    "cor_texto": "#121212",
    "fonte_padrao": "Helvetica",
    "tamanho_fonte": 10,
}

# ============================================================
# PDF - ReportLab
# ============================================================
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def gerar_pdf_recomendacao(recomendacoes: List[Dict], caminho_saida: str,
                           cliente: str = "Cliente", talhao: str = "Talhao",
                           cultura: str = "", produtividade: float = 0,
                           config: Optional[Dict] = None,
                           responsavel_id: int = None,
                           responsavel_nome: str = ""):
    if not REPORTLAB_DISPONIVEL:
        raise ImportError("Instale reportlab: pip install reportlab")
    
    cfg = config or CONFIG_EXPORT
    
    doc = SimpleDocTemplate(
        caminho_saida, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    
    elementos = []
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'TituloCustom', parent=styles['Heading1'],
        fontName=cfg.get('fonte_padrao', 'Helvetica-Bold'),
        fontSize=16, textColor=colors.HexColor(cfg.get('cor_primaria', '#00C853')),
        spaceAfter=12
    )
    
    estilo_subtitulo = ParagraphStyle(
        'SubtituloCustom', parent=styles['Heading2'],
        fontName=cfg.get('fonte_padrao', 'Helvetica-Bold'),
        fontSize=12, textColor=colors.HexColor(cfg.get('cor_texto', '#121212')),
        spaceAfter=6
    )
    
    elementos.append(Paragraph(cfg.get('cabecalho_linha1', 'Tech & Agri VRT'), estilo_titulo))
    elementos.append(Paragraph(cfg.get('cabecalho_linha2', ''), styles['Normal']))
    elementos.append(Spacer(1, 0.5*cm))
    
    info_data = [
        ["Cliente:", cliente, "Data:", datetime.now().strftime("%d/%m/%Y")],
        ["Talhao:", talhao, "Cultura:", cultura.title() if cultura else "-"],
        ["Produtividade:", f"{produtividade} sc/ha", "Amostras:", str(len(recomendacoes))],
    ]
    
    if responsavel_nome:
        info_data.append(["Responsavel Tecnico:", responsavel_nome, "", ""])
    
    tabela_info = Table(info_data, colWidths=[3*cm, 5*cm, 3*cm, 3*cm])
    tabela_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f0f0')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f0f0f0')),
    ]))
    elementos.append(tabela_info)
    elementos.append(Spacer(1, 0.8*cm))
    
    elementos.append(Paragraph("Recomendacoes por Amostra", estilo_subtitulo))
    
    for rec in recomendacoes:
        elementos.append(Paragraph(
            f"<b>Amostra {rec['amostra_id']}</b> | "
            f"Lat: {rec['coordenadas']['lat']:.6f}, Lon: {rec['coordenadas']['lon']:.6f} | "
            f"Custo Total: R$ {rec['custo_total_ha']:.2f}/ha",
            styles['Normal']
        ))
        elementos.append(Spacer(1, 0.2*cm))
        
        dados = [["Tipo", "Insumo", "Dose", "Unidade", "Custo/ha"]]
        for r in rec['recomendacoes']:
            dados.append([
                r['tipo'], r['insumo'],
                f"{r['dose']:.2f}", r['unidade'],
                f"R$ {r['custo_ha']:.2f}"
            ])
        
        tabela = Table(dados, colWidths=[3*cm, 5*cm, 2.5*cm, 2*cm, 2.5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(cfg.get('cor_primaria', '#00C853'))),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.4*cm))
    
    doc.build(elementos)
    return caminho_saida


# ============================================================
# SHAPEFILE - GeoPandas
# ============================================================
try:
    import geopandas as gpd
    from shapely.geometry import Point
    SHAPEFILE_DISPONIVEL = True
except ImportError:
    SHAPEFILE_DISPONIVEL = False

def gerar_shapefile_recomendacao(recomendacoes: List[Dict], caminho_saida: str,
                                  cliente: str = "Cliente", talhao: str = "Talhao",
                                  responsavel_id: int = None):
    if not SHAPEFILE_DISPONIVEL:
        raise ImportError("Instale geopandas e shapely: pip install geopandas shapely")
    
    dados = []
    for rec in recomendacoes:
        for r in rec['recomendacoes']:
            dados.append({
                "amostra_id": rec['amostra_id'],
                "latitude": rec['coordenadas']['lat'],
                "longitude": rec['coordenadas']['lon'],
                "tipo": r['tipo'],
                "insumo": r['insumo'],
                "dose": r['dose'],
                "unidade": r['unidade'],
                "custo_ha": r['custo_ha'],
                "cliente": cliente,
                "talhao": talhao,
                "responsavel_id": responsavel_id
            })
    
    df = pd.DataFrame(dados)
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    gdf.to_file(caminho_saida)
    return caminho_saida


# ============================================================
# CSV
# ============================================================
import pandas as pd

def gerar_csv_recomendacao(recomendacoes: List[Dict], caminho_saida: str,
                           cliente: str = "Cliente", talhao: str = "Talhao",
                           responsavel_id: int = None):
    dados = []
    for rec in recomendacoes:
        for r in rec['recomendacoes']:
            dados.append({
                "amostra_id": rec['amostra_id'],
                "latitude": rec['coordenadas']['lat'],
                "longitude": rec['coordenadas']['lon'],
                "tipo": r['tipo'],
                "insumo": r['insumo'],
                "dose": r['dose'],
                "unidade": r['unidade'],
                "custo_ha": r['custo_ha'],
                "cliente": cliente,
                "talhao": talhao,
                "responsavel_id": responsavel_id
            })
    
    df = pd.DataFrame(dados)
    df.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
    return caminho_saida