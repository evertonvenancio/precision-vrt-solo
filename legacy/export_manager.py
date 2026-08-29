# export_manager.py
# Gerenciador de exportações com branding configurável via DB
# VERSÃO 3.3 - Branding dinâmico do config_export

import os
from datetime import datetime
from typing import Dict, Optional
from db_schema import get_connection

# Imports condicionais para evitar erro se não instalado
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

try:
    import geopandas as gpd
    GEOPANDAS_OK = True
except ImportError:
    GEOPANDAS_OK = False

class ExportManager:
    def __init__(self):
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> Dict:
        """Carrega configurações de branding do banco."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM config_export WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return self._config_padrao()
    
    def _config_padrao(self) -> Dict:
        return {
            'empresa_nome': 'Tech & Agri VRT',
            'empresa_logo_path': None,
            'empresa_cnpj': '',
            'empresa_endereco': '',
            'empresa_telefone': '',
            'empresa_email': '',
            'cor_primaria': '#2E7D32',
            'cor_secundaria': '#1B5E20',
            'fonte_titulo': 'Helvetica-Bold',
            'fonte_corpo': 'Helvetica',
            'disclaimer': 'Mapa gerado automaticamente. Sujeito a validação técnica in loco.'
        }
    
    def atualizar_config(self, **kwargs) -> Tuple[bool, str]:
        """Atualiza configurações de branding."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            campos_permitidos = [
                'empresa_nome', 'empresa_logo_path', 'empresa_cnpj',
                'empresa_endereco', 'empresa_telefone', 'empresa_email',
                'cor_primaria', 'cor_secundaria', 'fonte_titulo',
                'fonte_corpo', 'disclaimer'
            ]
            
            updates = []
            values = []
            for campo, valor in kwargs.items():
                if campo in campos_permitidos:
                    updates.append(f"{campo} = ?")
                    values.append(valor)
            
            if not updates:
                return False, "Nenhum campo válido para atualizar"
            
            values.append(1)  # id = 1
            query = f"UPDATE config_export SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            self.config = self._carregar_config()
            return True, "Configurações atualizadas"
            
        except Exception as e:
            return False, f"Erro: {str(e)}"
    
    def exportar_pdf(self, 
                     recomendacao_id: int,
                     output_path: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Exporta relatório PDF técnico da recomendação VRT.
        """
        if not REPORTLAB_OK:
            return False, "ReportLab não instalado. Execute: pip install reportlab", None
        
        try:
            # Buscar dados da recomendação
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, c.nome as cliente_nome, c.cpf_cnpj as cliente_cnpj,
                       f.nome as fazenda_nome, t.nome as talhao_nome
                FROM recomendacoes_vrt r
                LEFT JOIN clientes c ON r.cliente_id = c.id
                LEFT JOIN fazendas f ON r.fazenda_id = f.id
                LEFT JOIN talhoes t ON r.talhao_id = t.id
                WHERE r.id = ?
            ''', (recomendacao_id,))
            rec = cursor.fetchone()
            
            if not rec:
                conn.close()
                return False, f"Recomendação #{recomendacao_id} não encontrada", None
            
            rec = dict(rec)
            
            # Buscar itens
            cursor.execute('''
                SELECT * FROM recomendacoes_itens WHERE recomendacao_id = ?
                ORDER BY zona_id
            ''', (recomendacao_id,))
            itens = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Definir output
            if not output_path:
                output_dir = os.path.join(os.path.dirname(__file__), 'output', f'rec_{recomendacao_id}')
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'relatorio_vrt_{recomendacao_id}.pdf')
            
            # Criar PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            styles = getSampleStyleSheet()
            
            # Cores do branding
            cor_prim = colors.HexColor(self.config['cor_primaria'])
            cor_sec = colors.HexColor(self.config['cor_secundaria'])
            
            # Estilos customizados
            titulo_style = ParagraphStyle(
                'TituloBranding',
                parent=styles['Heading1'],
                fontName=self.config['fonte_titulo'],
                fontSize=18,
                textColor=cor_prim,
                spaceAfter=12
            )
            
            subtitulo_style = ParagraphStyle(
                'SubtituloBranding',
                parent=styles['Heading2'],
                fontName=self.config['fonte_titulo'],
                fontSize=14,
                textColor=cor_sec,
                spaceAfter=10
            )
            
            # Elementos do documento
            elementos = []
            
            # Cabeçalho com branding
            header_data = [[
                Paragraph(f"<b>{self.config['empresa_nome']}</b><br/>"
                         f"<font size=8>{self.config['empresa_endereco'] or ''}<br/>"
                         f"CNPJ: {self.config['empresa_cnpj'] or 'N/A'} | "
                         f"Tel: {self.config['empresa_telefone'] or 'N/A'}</font>", 
                         styles['Normal']),
                Paragraph(f"<font size=8>{datetime.now().strftime('%d/%m/%Y')}</font>", 
                         styles['Normal'])
            ]]
            header_table = Table(header_data, colWidths=[14*cm, 3*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),
                ('ALIGN', (-1,0), (-1,0), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('LINEBELOW', (0,0), (-1,0), 1, cor_prim),
            ]))
            elementos.append(header_table)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Logo se existir
            if self.config['empresa_logo_path'] and os.path.exists(self.config['empresa_logo_path']):
                try:
                    img = Image(self.config['empresa_logo_path'], width=3*cm, height=2*cm)
                    elementos.append(img)
                    elementos.append(Spacer(1, 0.3*cm))
                except:
                    pass
            
            # Título
            elementos.append(Paragraph("RELATÓRIO TÉCNICO VRT", titulo_style))
            elementos.append(Spacer(1, 0.3*cm))
            
            # Info geral
            info_data = [
                ['Recomendação:', f"#{rec['id']}"],
                ['Cliente:', rec['cliente_nome'] or 'N/A'],
                ['Fazenda:', rec['fazenda_nome'] or 'N/A'],
                ['Talhão:', rec['talhao_nome'] or 'N/A'],
                ['Cultura:', rec['cultura'] or 'N/A'],
                ['Safra:', rec['safra'] or 'N/A'],
                ['Data:', rec['data_processamento'] or 'N/A'],
            ]
            info_table = Table(info_data, colWidths=[4*cm, 13*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), self.config['fonte_titulo']),
                ('FONTNAME', (1,0), (1,-1), self.config['fonte_corpo']),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f0f0')),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            elementos.append(info_table)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Tabela de zonas
            elementos.append(Paragraph("ZONAS DE MANEJO RECOMENDADAS", subtitulo_style))
            
            if itens:
                zonas_data = [['Zona', 'Área (ha)', 'Dosagem (kg/ha)', 'Insumo', 'Custo Est. (R$)']]
                total_area = 0
                total_custo = 0
                
                for item in itens:
                    zonas_data.append([
                        item['classe_zona'],
                        f"{item['area_hectares']:.2f}",
                        f"{item['dosagem_kg_ha']:.2f}",
                        item['insumo_sugerido'],
                        f"R$ {item['custo_estimado']:.2f}"
                    ])
                    total_area += item['area_hectares'] or 0
                    total_custo += item['custo_estimado'] or 0
                
                # Totais
                zonas_data.append(['TOTAL', f"{total_area:.2f}", '-', '-', f"R$ {total_custo:.2f}"])
                
                zonas_table = Table(zonas_data, colWidths=[3*cm, 3*cm, 3.5*cm, 4*cm, 3.5*cm])
                zonas_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), self.config['fonte_titulo']),
                    ('FONTNAME', (0,1), (-1,-1), self.config['fonte_corpo']),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('BACKGROUND', (0,0), (-1,0), cor_prim),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f5e9')),
                    ('FONTNAME', (0,-1), (-1,-1), self.config['fonte_titulo']),
                ]))
                elementos.append(zonas_table)
            else:
                elementos.append(Paragraph("Nenhuma zona encontrada.", styles['Normal']))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # Disclaimer
            elementos.append(Paragraph(
                f"<font size=8><i>{self.config['disclaimer']}</i></font>",
                styles['Normal']
            ))
            
            # Build
            doc.build(elementos)
            
            return True, f"PDF exportado: {output_path}", output_path
            
        except Exception as e:
            return False, f"Erro ao exportar PDF: {str(e)}", None
    
    def exportar_shapefile(self,
                           recomendacao_id: int,
                           output_path: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Exporta shapefile das zonas VRT."""
        if not GEOPANDAS_OK:
            return False, "GeoPandas não instalado. Execute: pip install geopandas pyogrio", None
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT i.*, r.cultura, r.safra
                FROM recomendacoes_itens i
                JOIN recomendacoes_vrt r ON i.recomendacao_id = r.id
                WHERE i.recomendacao_id = ?
            ''', (recomendacao_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return False, "Nenhum dado encontrado", None
            
            # Reconstruir GeoDataFrame
            import json
            from shapely.geometry import shape
            
            data = []
            for row in rows:
                row_dict = dict(row)
                geom = shape(json.loads(row_dict['geometria_geojson']))
                data.append({
                    'zona_id': row_dict['zona_id'],
                    'classe': row_dict['classe_zona'],
                    'area_ha': row_dict['area_hectares'],
                    'dosagem': row_dict['dosagem_kg_ha'],
                    'insumo': row_dict['insumo_sugerido'],
                    'custo': row_dict['custo_estimado'],
                    'produt': row_dict['produtividade_estimada'],
                    'cultura': row_dict['cultura'],
                    'safra': row_dict['safra'],
                    'geometry': geom
                })
            
            gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
            
            if not output_path:
                output_dir = os.path.join(os.path.dirname(__file__), 'output', f'rec_{recomendacao_id}')
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'zonas_vrt_{recomendacao_id}.shp')
            
            gdf.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')
            
            return True, f"Shapefile exportado: {output_path}", output_path
            
        except Exception as e:
            return False, f"Erro ao exportar Shapefile: {str(e)}", None
    
    def exportar_csv(self,
                     recomendacao_id: int,
                     output_path: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Exporta CSV com dados tabulares da recomendação."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT i.*, c.nome as cliente_nome, f.nome as fazenda_nome,
                       t.nome as talhao_nome, r.cultura, r.safra
                FROM recomendacoes_itens i
                JOIN recomendacoes_vrt r ON i.recomendacao_id = r.id
                LEFT JOIN clientes c ON r.cliente_id = c.id
                LEFT JOIN fazendas f ON r.fazenda_id = f.id
                LEFT JOIN talhoes t ON r.talhao_id = t.id
                WHERE i.recomendacao_id = ?
            ''', (recomendacao_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return False, "Nenhum dado encontrado", None
            
            import csv
            
            if not output_path:
                output_dir = os.path.join(os.path.dirname(__file__), 'output', f'rec_{recomendacao_id}')
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'dados_vrt_{recomendacao_id}.csv')
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=dict(rows[0]).keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
            
            return True, f"CSV exportado: {output_path}", output_path
            
        except Exception as e:
            return False, f"Erro ao exportar CSV: {str(e)}", None

if __name__ == "__main__":
    em = ExportManager()
    logging.info(f"[INFO] ExportManager inicializado. Empresa: {em.config['empresa_nome']}")

