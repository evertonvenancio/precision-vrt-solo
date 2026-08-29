# vrt_pipeline.py
# Pipeline completo de processamento VRT com persistência no banco
# VERSÃO 3.3 - Integração DB + Branding corrigido

import os
import json
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping
from sklearn.cluster import KMeans
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from db_schema import get_connection

class VRTPipeline:
    def __init__(self, 
                 n_zonas: int = 5,
                 insumo_base_kg_ha: float = 200.0,
                 preco_insumo_kg: float = 8.50,
                 custo_aplicacao_ha: float = 45.0):
        
        self.n_zonas = n_zonas
        self.insumo_base_kg_ha = insumo_base_kg_ha
        self.preco_insumo_kg = preco_insumo_kg
        self.custo_aplicacao_ha = custo_aplicacao_ha
        self.resultado = None
        self.metadata = {}
        
    def processar_amostragem(self, 
                             arquivo_entrada: str,
                             cliente_id: int,
                             fazenda_id: Optional[int] = None,
                             talhao_id: Optional[int] = None,
                             cultura: str = "Soja",
                             safra: str = "2026/2027",
                             responsavel_tecnico_id: Optional[int] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Pipeline completo: processa amostragem, gera zonas VRT e salva no DB.
        Retorna: (sucesso, mensagem, recomendacao_id)
        """
        try:
            # 1. Validar arquivo
            if not os.path.exists(arquivo_entrada):
                return False, f"Arquivo não encontrado: {arquivo_entrada}", None
            
            # 2. Carregar e processar dados
            sucesso_proc, msg_proc = self._processar_dados(arquivo_entrada)
            if not sucesso_proc:
                return False, f"Erro no processamento: {msg_proc}", None
            
            # 3. Salvar no banco de dados
            rec_id = self._salvar_recomendacao_no_db(
                cliente_id=cliente_id,
                fazenda_id=fazenda_id,
                talhao_id=talhao_id,
                cultura=cultura,
                safra=safra,
                arquivo_entrada=arquivo_entrada,
                responsavel_tecnico_id=responsavel_tecnico_id
            )
            
            if not rec_id:
                return False, "Erro ao salvar recomendação no banco de dados", None
            
            # 4. Salvar arquivos de saída (SHP + TIFF)
            self._salvar_arquivos_saida(rec_id)
            
            return True, f"Recomendação VRT #{rec_id} processada e salva com sucesso", rec_id
            
        except Exception as e:
            return False, f"Erro no pipeline: {str(e)}", None
    
    def _processar_dados(self, arquivo_entrada: str) -> Tuple[bool, str]:
        """Processa o arquivo de amostragem e gera zonas de manejo."""
        try:
            # Detectar tipo de arquivo
            ext = os.path.splitext(arquivo_entrada)[1].lower()
            
            if ext in ['.shp', '.geojson', '.json']:
                # Vetorial
                gdf = gpd.read_file(arquivo_entrada)
                self.resultado = self._processar_vetorial(gdf)
            elif ext in ['.tif', '.tiff']:
                # Raster
                self.resultado = self._processar_raster(arquivo_entrada)
            else:
                return False, f"Formato não suportado: {ext}"
            
            return True, "Processamento concluído"
            
        except Exception as e:
            return False, str(e)
    
    def _processar_vetorial(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Processa dados vetoriais (pontos de amostragem)."""
        # Verificar colunas necessárias
        col_nutrientes = [c for c in gdf.columns if c.lower() in [
            'n', 'p', 'k', 'ph', 'mo', 'mat_org', 'fosforo', 'potassio', 'nitrogenio'
        ]]
        
        if not col_nutrientes:
            # Usar colunas numéricas disponíveis
            col_nutrientes = gdf.select_dtypes(include=[np.number]).columns.tolist()
            col_nutrientes = [c for c in col_nutrientes if c not in ['lat', 'lon', 'x', 'y', 'id']]
        
        if len(col_nutrientes) == 0:
            raise ValueError("Nenhuma coluna de nutrientes encontrada no arquivo vetorial")
        
        # Extrair coordenadas e valores
        coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        valores = gdf[col_nutrientes].fillna(0).values
        
        # Normalizar
        valores_norm = (valores - valores.mean(axis=0)) / (valores.std(axis=0) + 1e-8)
        
        # Clustering K-Means
        kmeans = KMeans(n_clusters=self.n_zonas, random_state=42, n_init=10)
        labels = kmeans.fit_predict(valores_norm)
        
        # Calcular estatísticas por zona
        zonas = []
        for i in range(self.n_zonas):
            mask = labels == i
            zona_gdf = gdf[mask].copy()
            
            if len(zona_gdf) == 0:
                continue
            
            # Calcular médias
            medias = zona_gdf[col_nutrientes].mean().to_dict()
            
            # Calcular área aproximada (convex hull)
            if len(zona_gdf) > 2:
                geom = zona_gdf.unary_union.convex_hull
            else:
                geom = zona_gdf.unary_union.buffer(50)  # 50m buffer
            
            area_ha = geom.area / 10000.0
            
            # Dosagem baseada na média de nutrientes
            indice_fertilidade = np.mean(list(medias.values()))
            dosagem = self.insumo_base_kg_ha * (1 + (indice_fertilidade - 50) / 100)
            dosagem = max(50, min(400, dosagem))  # Clamp entre 50-400 kg/ha
            
            custo = (dosagem * self.preco_insumo_kg + self.custo_aplicacao_ha) * area_ha
            
            zonas.append({
                'zona_id': i + 1,
                'classe': f"Zona {i+1}",
                'area_hectares': round(area_ha, 2),
                'dosagem_kg_ha': round(dosagem, 2),
                'insumo_sugerido': 'NPK 20-05-20' if indice_fertilidade < 50 else 'NPK 10-30-20',
                'custo_estimado': round(custo, 2),
                'produtividade_estimada': round(3.0 + (indice_fertilidade / 100), 2),
                'estatisticas': medias,
                'geometria': mapping(geom)
            })
        
        self.metadata = {
            'col_nutrientes': col_nutrientes,
            'n_pontos': len(gdf),
            'n_zonas': len(zonas),
            'data_processamento': datetime.now().isoformat()
        }
        
        return {
            'zonas': zonas,
            'gdf_original': gdf,
            'labels': labels,
            'centroides': kmeans.cluster_centers_.tolist()
        }
    
    def _processar_raster(self, arquivo_raster: str) -> Dict:
        """Processa dados raster (imagem de satélite/drone)."""
        with rasterio.open(arquivo_raster) as src:
            bandas = src.read()
            profile = src.profile
            transform = src.transform
            
            # Usar NDVI ou primeira banda
            if bandas.shape[0] >= 4:
                # Calcular NDVI: (NIR - Red) / (NIR + Red)
                red = bandas[2].astype(float)
                nir = bandas[3].astype(float)
                ndvi = np.divide(nir - red, nir + red, out=np.zeros_like(red), where=(nir+red)!=0)
                dados = ndvi
            else:
                dados = bandas[0].astype(float)
            
            # Mascarar valores inválidos
            dados = np.where(dados > -999, dados, np.nan)
            
            # Reamostrar para reduzir complexidade (máx 1000x1000)
            from scipy.ndimage import zoom
            max_dim = 1000
            if dados.shape[0] > max_dim or dados.shape[1] > max_dim:
                zoom_factor = max_dim / max(dados.shape)
                dados = zoom(dados, zoom_factor, order=1)
                # Atualizar transform
                transform = rasterio.Affine(
                    transform.a / zoom_factor, transform.b, transform.c,
                    transform.d, transform.e / zoom_factor, transform.f
                )
            
            # Flatten válidos
            valid_mask = ~np.isnan(dados)
            dados_flat = dados[valid_mask].reshape(-1, 1)
            
            if len(dados_flat) == 0:
                raise ValueError("Nenhum dado válido encontrado no raster")
            
            # K-Means
            n_clusters = min(self.n_zonas, len(dados_flat))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels_flat = kmeans.fit_predict(dados_flat)
            
            # Reconstruir matriz de labels
            labels = np.full(dados.shape, -1, dtype=int)
            labels[valid_mask] = labels_flat
            
            # Extrair shapes por zona
            zonas = []
            for i in range(n_clusters):
                mask = (labels == i).astype(np.uint8)
                
                # Shapes
                shapes_gen = shapes(mask, mask=mask, transform=transform)
                geometrias = [shape(geom) for geom, val in shapes_gen if val == 1]
                
                if not geometrias:
                    continue
                
                from shapely.ops import unary_union
                geom = unary_union(geometrias)
                
                # Simplificar
                geom = geom.simplify(5.0)
                area_ha = geom.area / 10000.0
                
                # Dosagem baseada no valor médio da zona
                zona_vals = dados_flat[labels_flat == i]
                media_zona = float(np.mean(zona_vals))
                
                dosagem = self.insumo_base_kg_ha * (1 + media_zona)
                dosagem = max(50, min(400, dosagem))
                
                custo = (dosagem * self.preco_insumo_kg + self.custo_aplicacao_ha) * area_ha
                
                zonas.append({
                    'zona_id': i + 1,
                    'classe': f"Zona {i+1}",
                    'area_hectares': round(area_ha, 2),
                    'dosagem_kg_ha': round(dosagem, 2),
                    'insumo_sugerido': 'NPK 20-05-20' if media_zona < 0.3 else 'NPK 10-30-20',
                    'custo_estimado': round(custo, 2),
                    'produtividade_estimada': round(2.5 + media_zona * 2, 2),
                    'estatisticas': {'media_ndvi': round(media_zona, 4)},
                    'geometria': mapping(geom)
                })
            
            self.metadata = {
                'tipo': 'raster',
                'shape_original': bandas.shape,
                'n_zonas': len(zonas),
                'data_processamento': datetime.now().isoformat()
            }
            
            return {
                'zonas': zonas,
                'raster_profile': profile,
                'labels': labels,
                'centroides': kmeans.cluster_centers_.tolist()
            }
    
    def _salvar_recomendacao_no_db(self,
                                   cliente_id: int,
                                   fazenda_id: Optional[int],
                                   talhao_id: Optional[int],
                                   cultura: str,
                                   safra: str,
                                   arquivo_entrada: str,
                                   responsavel_tecnico_id: Optional[int]) -> Optional[int]:
        """
        Persiste a recomendação VRT no banco de dados.
        Retorna o ID da recomendação ou None em caso de erro.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 1. Inserir recomendação principal
            cursor.execute('''
                INSERT INTO recomendacoes_vrt (
                    cliente_id, fazenda_id, talhao_id, cultura, safra,
                    data_amostragem, data_processamento, status,
                    arquivo_entrada, estatisticas_json, observacoes,
                    responsavel_tecnico_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cliente_id,
                fazenda_id,
                talhao_id,
                cultura,
                safra,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                'concluido',
                arquivo_entrada,
                json.dumps(self.metadata, ensure_ascii=False),
                f"Processamento automático. {self.metadata.get('n_zonas', 0)} zonas geradas.",
                responsavel_tecnico_id
            ))
            
            recomendacao_id = cursor.lastrowid
            
            # 2. Inserir itens (zonas)
            for zona in self.resultado['zonas']:
                cursor.execute('''
                    INSERT INTO recomendacoes_itens (
                        recomendacao_id, zona_id, classe_zona, area_hectares,
                        dosagem_kg_ha, insumo_sugerido, custo_estimado,
                        produtividade_estimada, geometria_geojson
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recomendacao_id,
                    zona['zona_id'],
                    zona['classe'],
                    zona['area_hectares'],
                    zona['dosagem_kg_ha'],
                    zona['insumo_sugerido'],
                    zona['custo_estimado'],
                    zona['produtividade_estimada'],
                    json.dumps(zona['geometria'], ensure_ascii=False)
                ))
            
            conn.commit()
            conn.close()
            
            self.metadata['recomendacao_id'] = recomendacao_id
            return recomendacao_id
            
        except Exception as e:
            logging.info(f"[ERRO DB] Falha ao salvar recomendação: {e}")
            return None
    
    def _salvar_arquivos_saida(self, recomendacao_id: int):
        """Salva os arquivos shapefile e TIFF de saída."""
        output_dir = os.path.join(os.path.dirname(__file__), 'output', f'rec_{recomendacao_id}')
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar GeoDataFrame das zonas
        zonas_data = []
        for zona in self.resultado['zonas']:
            zonas_data.append({
                'zona_id': zona['zona_id'],
                'classe': zona['classe'],
                'area_ha': zona['area_hectares'],
                'dosagem': zona['dosagem_kg_ha'],
                'insumo': zona['insumo_sugerido'],
                'custo': zona['custo_estimado'],
                'geometry': shape(zona['geometria'])
            })
        
        gdf_zonas = gpd.GeoDataFrame(zonas_data, crs='EPSG:4326')
        
        # Salvar Shapefile
        shp_path = os.path.join(output_dir, f'zonas_vrt_{recomendacao_id}.shp')
        gdf_zonas.to_file(shp_path, driver='ESRI Shapefile', encoding='utf-8')
        
        # Salvar GeoJSON também
        geojson_path = os.path.join(output_dir, f'zonas_vrt_{recomendacao_id}.geojson')
        gdf_zonas.to_file(geojson_path, driver='GeoJSON', encoding='utf-8')
        
        # Atualizar DB com caminhos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE recomendacoes_vrt 
            SET arquivo_vrt_shp = ?, arquivo_vrt_tiff = ?
            WHERE id = ?
        ''', (shp_path, geojson_path, recomendacao_id))
        conn.commit()
        conn.close()
        
        logging.info(f"[SAÍDA] Arquivos salvos em: {output_dir}")
    
    def get_recomendacao(self, recomendacao_id: int) -> Optional[Dict]:
        """Recupera uma recomendação completa do banco."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recomendacoes_vrt WHERE id = ?', (recomendacao_id,))
        rec = cursor.fetchone()
        
        if not rec:
            conn.close()
            return None
        
        rec_dict = dict(rec)
        
        # Buscar itens
        cursor.execute('''
            SELECT * FROM recomendacoes_itens WHERE recomendacao_id = ?
        ''', (recomendacao_id,))
        itens = [dict(row) for row in cursor.fetchall()]
        rec_dict['itens'] = itens
        
        conn.close()
        return rec_dict
    
    def listar_recomendacoes(self, cliente_id: Optional[int] = None) -> List[Dict]:
        """Lista recomendações com filtros opcionais."""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM recomendacoes_vrt WHERE 1=1'
        params = []
        
        if cliente_id:
            query += ' AND cliente_id = ?'
            params.append(cliente_id)
        
        query += ' ORDER BY data_processamento DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

if __name__ == "__main__":
    from db_schema import init_db
    init_db()
    
    # Teste básico
    pipeline = VRTPipeline(n_zonas=3)
    logging.info("[INFO] VRTPipeline inicializado. Use processar_amostragem() para processar dados.")

