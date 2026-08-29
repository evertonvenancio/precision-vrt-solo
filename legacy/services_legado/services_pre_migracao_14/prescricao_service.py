"""
Precision VRT Solo - Serviço do Módulo Prescrição
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
import json
import logging
import shutil
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes
from core.prescricao_vrt.interpolacao import InterpoladorSolo
from core.prescricao_vrt.zoneamento import Zoneador
from core.prescricao_vrt.prescricao import MotorPrescricao
from config.culturas import listar_culturas
from config.formulas import get_formula, listar_formulas
from models.cliente import Cliente

from core.utilitarios.helpers import (
    _parse_upload,
    _salvar_upload,
    _padronizar_id,
    _calcular_area_ha,
    _gdf_para_geojson,
)

# Diretórios de dados
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
UPLOAD_DIR = DATA_DIR / "uploads"
STORAGE_EXPORTS_DIR = BASE_DIR / "storage" / "exports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class PrescricaoService:
    """
    Serviço central do módulo Prescrição.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def get_contexto_nova_page(self) -> dict:
        """Monta o contexto para a página de nova prescrição."""
        clientes = self.db.query(models.cliente.Cliente).filter(Cliente.ativo == True).order_by(Cliente.nome).all()
        return {
            "clientes": clientes,
            "culturas": listar_culturas(),
            "formulas": listar_formulas(),
            "permissoes": self.buscar_permissoes(),
        }

    def processar_upload_geo(self, limite_talhao: UploadFile, amostras_solo: UploadFile) -> JSONResponse:
        """Recebe arquivos geoespaciais para processamento de prescrição VRT."""
        try:
            input_dir = Path("data/input")
            input_dir.mkdir(parents=True, exist_ok=True)

            limite_path = input_dir / f"limite_{uuid.uuid4().hex}_{limite_talhao.filename}"
            with open(limite_path, "wb") as buffer:
                shutil.copyfileobj(limite_talhao.file, buffer)

            amostras_path = input_dir / f"amostras_{uuid.uuid4().hex}_{amostras_solo.filename}"
            with open(amostras_path, "wb") as buffer:
                shutil.copyfileobj(amostras_solo.file, buffer)

            logging.info("Arquivos recebidos: limite=%s, amostras=%s", limite_path.name, amostras_path.name)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Arquivos recebidos com sucesso. Processando...",
                    "arquivos": {
                        "limite": limite_path.name,
                        "amostras": amostras_path.name
                    }
                }
            )
        except Exception as exc:
            logging.exception("Erro no upload de arquivos geoespaciais: %s", exc)
            return JSONResponse(
                status_code=500,
                content={"success": False, "detail": f"Erro ao processar arquivos: {str(exc)}"}
            )

    def processar_prescricao(
        self,
        limite_talhao: UploadFile,
        amostras_solo: UploadFile,
        cliente_id: str,
        talhao_nome: str,
        cultura: str,
        produtividade: float,
        n_zonas: int,
        metodologia: str,
    ) -> JSONResponse:
        """
        Pipeline completo de prescrição VRT.
        """
        # --- A. SALVAR UPLOADS ---
        caminho_limite = _salvar_upload(limite_talhao, UPLOAD_DIR)
        caminho_amostras = _salvar_upload(amostras_solo, UPLOAD_DIR)

        # --- B. PARSE LIMITE (GeoJSON/SHP) ---
        resultado_limite = _parse_upload(str(caminho_limite))
        gdf_pontos = resultado_limite.get("gdf_pontos")
        gdf_poligono = resultado_limite.get("gdf_poligono")

        if gdf_pontos is None or gdf_pontos.empty:
            raise HTTPException(
                status_code=400,
                detail="Arquivo limite nao contem pontos de amostragem com coordenadas."
            )

        # --- C. PARSE AMOSTRAS (CSV/XLSX) ---
        resultado_amostras = _parse_upload(str(caminho_amostras))

        if resultado_amostras.get("tipo") != "tabular":
            raise HTTPException(
                status_code=400,
                detail="Arquivo de amostras deve ser CSV ou XLSX com dados quimicos."
            )

        df_amostras = resultado_amostras["df"]

        if df_amostras is None or df_amostras.empty:
            raise HTTPException(
                status_code=400,
                detail="Arquivo de amostras esta vazio ou nao pode ser lido."
            )

        # --- D. PREPARAR DATAFRAMES PARA MERGE ---
        if "ponto_id" not in gdf_pontos.columns:
            raise HTTPException(
                status_code=400,
                detail="Coluna 'ponto_id' nao encontrada no arquivo de pontos (GeoJSON)."
            )
        if "ponto_id" not in df_amostras.columns:
            raise HTTPException(
                status_code=400,
                detail="Coluna 'ponto_id' nao encontrada no arquivo de amostras (CSV/XLSX)."
            )

        gdf_pontos["ponto_id"] = _padronizar_id(gdf_pontos["ponto_id"])
        df_amostras["ponto_id"] = _padronizar_id(df_amostras["ponto_id"])

        # --- E. MERGE ---
        df_completo = gdf_pontos.merge(df_amostras, on="ponto_id", how="inner")

        if df_completo.empty:
            raise HTTPException(
                status_code=400,
                detail="Nenhum ID do CSV correspondeu aos IDs do GeoJSON. Verifique a coluna 'ponto_id' em ambos os arquivos."
            )

        # --- F. CONVERSAO NUMERICA ---
        df_completo["latitude"] = pd.to_numeric(df_completo["latitude"], errors="coerce")
        df_completo["longitude"] = pd.to_numeric(df_completo["longitude"], errors="coerce")

        cols_excluir = {"ponto_id", "latitude", "longitude", "geometry"}
        cols_numericas = [c for c in df_completo.columns if c not in cols_excluir]
        for col in cols_numericas:
            df_completo[col] = pd.to_numeric(df_completo[col], errors="coerce")

        df_completo = df_completo.dropna(subset=["latitude", "longitude"])
        cols_vazias = df_completo.columns[df_completo.isna().all()]
        df_completo = df_completo.drop(columns=cols_vazias)

        if df_completo.empty:
            raise HTTPException(
                status_code=400,
                detail="Nenhum dado valido apos limpeza numerica das coordenadas."
            )

        # --- G. INTERPOLACAO ---
        interpolador = InterpoladorSolo()
        resultados_interpolacao = interpolador.interpolar_talhao(
            df_completo,
            x_col="longitude",
            y_col="latitude"
        )

        if not resultados_interpolacao.get("atributos"):
            raise HTTPException(
                status_code=400,
                detail="Nenhum atributo pode ser interpolado."
            )

        # --- H. ZONEAMENTO ---
        zoneador = Zoneador(n_zonas=n_zonas)
        resultado_zoneamento = zoneador.zonear(resultados_interpolacao)

        raster_zonas = getattr(resultado_zoneamento, "raster_zonas", None)
        perfis = getattr(resultado_zoneamento, "perfis", {})
        grid_x = resultados_interpolacao["grid_x"]
        grid_y = resultados_interpolacao["grid_y"]

        # --- I. VETORIZACAO ---
        from core.prescricao_vrt.exportacao import Exportador
        exportador = Exportador(str(OUTPUT_DIR))
        grid_x_1d = np.asarray(grid_x).flatten()
        grid_y_1d = np.asarray(grid_y).flatten()

        gdf_zonas = exportador.raster_para_zonas_poligonos(
            raster_zonas, grid_x_1d, grid_y_1d,
            atributos_zonas=perfis
        )

        if gdf_zonas.crs is None or gdf_zonas.crs.to_string() != "EPSG:4326":
            gdf_zonas = gdf_zonas.to_crs(epsg=4326)

        # --- J. GERAR IMAGEM PNG ---
        mapa_png_path_fisico = str(STORAGE_EXPORTS_DIR / "mapa_zonas.png")
        exportador.gerar_imagem_mapa(
            gdf_zonas=gdf_zonas,
            gdf_poligono=gdf_poligono,
            caminho_saida=mapa_png_path_fisico
        )

        mapa_png_url = "/storage/exports/mapa_zonas.png"

        # --- K. GEOJSON LIMITE ---
        if gdf_poligono is not None:
            if gdf_poligono.crs is None or gdf_poligono.crs.to_string() != "EPSG:4326":
                gdf_poligono = gdf_poligono.to_crs(epsg=4326)
        geojson_limite = _gdf_para_geojson(gdf_poligono)

        # --- L. AREA TOTAL ---
        area_total_ha = _calcular_area_ha(gdf_poligono)

        # --- M. PRESCRICAO ---
        motor = MotorPrescricao(
            cultura=cultura,
            produtividade=produtividade,
            teor_argila=20.0,
            metodo_id=metodologia
        )
        resultado_prescricao = motor.prescrever_todas_zonas(perfis)

        # --- N. NOTAS TECNICAS ---
        formula = get_formula(metodologia)
        notas_tecnicas = {
            "embasamento": formula.get("embasamento_tecnico", ""),
            "bibliografia": formula.get("bibliografia", ""),
            "referencia_legal": formula.get("referencia_legal", "")
        }

        # --- O. EXPORTACAO JSON ---
        perfis_serial = {}
        for zona_id, attrs in perfis.items():
            perfis_serial[str(zona_id)] = {}
            for attr, stats in attrs.items():
                perfis_serial[str(zona_id)][attr] = {
                    k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                    for k, v in stats.items()
                }

        estatisticas_serial = {}
        for k, v in getattr(resultado_zoneamento, "estatisticas", {}).items():
            if isinstance(v, dict):
                estatisticas_serial[k] = {
                    kk: (float(vv) if isinstance(vv, (np.floating, np.integer)) else vv)
                    for kk, vv in v.items()
                }
            elif isinstance(v, (np.floating, np.integer)):
                estatisticas_serial[k] = float(v)
            else:
                estatisticas_serial[k] = v

        atributos_usados = getattr(resultado_zoneamento, "atributos_usados", [])
        if isinstance(atributos_usados, np.ndarray):
            atributos_usados = atributos_usados.tolist()

        output_data = {
            "success": True,
            "prescricoes": resultado_prescricao["prescricoes"],
            "resumo": resultado_prescricao["resumo"],
            "estatisticas_zoneamento": estatisticas_serial,
            "atributos_usados": atributos_usados,
            "perfis_zonas": perfis_serial,
            "geojson_limite": geojson_limite,
            "area_total_ha": area_total_ha,
            "notas_tecnicas": notas_tecnicas,
            "cliente_id": cliente_id,
            "talhao_nome": talhao_nome,
            "cultura": cultura,
            "produtividade": produtividade,
            "metodologia": metodologia,
            "n_zonas": n_zonas,
            "mapa_png_path": mapa_png_url
        }

        output_path = OUTPUT_DIR / "resultado_temp.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return JSONResponse(content={
            "success": True,
            "redirect": "/prescricao/resultado"
        })

    def get_resultado_context(self, request) -> dict:
        """Monta o contexto para a página de resultado da prescrição."""
        output_path = OUTPUT_DIR / "resultado_temp.json"
        if not output_path.exists():
            clientes = self.db.query(models.cliente.Cliente).filter(Cliente.ativo == True).order_by(Cliente.nome).all()
            return {
                "request": request,
                "erro": "Nenhum resultado encontrado. Processe uma prescricao primeiro.",
                "clientes": clientes,
                "culturas": listar_culturas(),
                "formulas": listar_formulas(),
                "permissoes": self.buscar_permissoes(),
            }

        with open(output_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

        mapa_png_path = dados.get("mapa_png_path", "")

        return {
            "request": request,
            "dados": dados,
            "mapa_png_path": mapa_png_path,
            "talhao_geojson": dados.get("geojson_limite", {"type": "FeatureCollection", "features": []}),
            "permissoes": self.buscar_permissoes(),
        }
