import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.geo_parser_service import parse_upload
from app.services.compactacao_service import CompactacaoService
from schemas.compactacao import AnaliseCompactacaoCreate, ResumoEstatistico, FlagEscarificacao
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compactacao", tags=["Compactacao"])


@router.post("/upload")
async def upload_compactacao(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recebe arquivo de pontos georreferenciados (CSV, XLSX, SHP)
    para analise de compactacao do solo.
    """
    logger.info("[COMPACTACAO_UPLOAD] Recebido arquivo: %s", file.filename)

    try:
        resultado = await parse_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO_UPLOAD] Erro no parse do arquivo %s", file.filename)
        raise HTTPException(status_code=422, detail=f"Erro ao processar arquivo: {str(e)}")

    tipo = resultado.get("tipo")
    gdf = resultado.get("gdf")
    crs = resultado.get("crs")
    registros = resultado.get("registros", 0)
    origem = resultado.get("origem", "desconhecido")

    logger.info(
        "[COMPACTACAO_UPLOAD] Parse concluido: tipo=%s | origem=%s | registros=%d | CRS=%s",
        tipo, origem, registros, crs
    )

    # Compactacao aceita apenas pontos
    if tipo != "pontos":
        logger.error("[COMPACTACAO_UPLOAD] Tipo invalido para compactacao: %s (esperado: pontos)", tipo)
        raise HTTPException(
            status_code=422,
            detail=f"Compactacao aceita apenas arquivos de pontos (amostras). Recebido: {tipo}"
        )

    logger.info("[COMPACTACAO_UPLOAD] Pontos validados. Enviando para analise de compactacao.")

    # Processar dados com o serviço de compactação
    try:
        # Converter dados do GeoDataFrame para schema
        pontos_data = []
        for _, row in gdf.iterrows():
            ponto_data = {
                "identificador_ponto": row.get("ponto_id", f"Ponto_{i+1}"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "camadas": []
            }
            
            # Adicionar camadas com base nas colunas de resistência
            profundidades = [(0, 10), (10, 20), (20, 30), (30, 40)]
            for inicio, fim in profundidades:
                coluna_rp = f"rp_{inicio}_{fim}"
                if coluna_rp in row and pd.notna(row[coluna_rp]):
                    camada_data = {
                        "profundidade_inicio": inicio,
                        "profundidade_fim": fim,
                        "resistencia_mpa": float(row[coluna_rp])
                    }
                    ponto_data["camadas"].append(camada_data)
            
            if ponto_data["camadas"]:  # Apenas pontos com camadas
                pontos_data.append(ponto_data)
        
        if not pontos_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhum ponto com dados de resistência válido encontrado"
            )
        
        # Criar análise de compactação
        analise_data = AnaliseCompactacaoCreate(
            pontos=pontos_data,
            arquivo_csv_origem=file.filename,
            data_coleta=datetime.utcnow()
        )
        
        compactacao_service = CompactacaoService(db)
        analise = compactacao_service.criar_analise_compactacao(
            analise_data=analise_data
        )
        
        # Gerar resumo estatístico
        resumo = compactacao_service.gerar_resumo_estatistico(analise.id)
        
        # Gerar flags de escarificação
        flags = compactacao_service.gerar_flags_escarificacao(analise.id)
        
        return {
            "status": "sucesso",
            "analise_id": analise.id,
            "tipo": "pontos",
            "mensagem": "Amostras de compactacao recebidas e analisadas com sucesso.",
            "registros": len(pontos_data),
            "crs": crs,
            "colunas": list(gdf.columns),
            "origem": origem,
            "resumo_estatistico": resumo,
            "flags_escarificacao": flags,
            "classificacao_geral": analise.classificacao_geral,
            "necessita_escarificacao": analise.necessita_escarificacao
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO_UPLOAD] Erro ao processar analise de compactacao: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Erro ao processar análise de compactação: {str(e)}"
        )


@router.post("/analise", response_model=dict)
async def criar_analise_compactacao(
    analise_data: AnaliseCompactacaoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova análise de compactação manualmente.
    
    Permite criar análises sem upload de arquivo, com dados estruturados.
    """
    logger.info("[COMPACTACAO] Criando análise manualmente")
    
    try:
        compactacao_service = CompactacaoService(db)
        analise = compactacao_service.criar_analise_compactacao(
            analise_data=analise_data
        )
        
        # Gerar resumo
        resumo = compactacao_service.gerar_resumo_estatistico(analise.id)
        
        return {
            "status": "sucesso",
            "analise_id": analise.id,
            "mensagem": "Análise de compactação criada com sucesso.",
            "resumo_estatistico": resumo,
            "classificacao_geral": analise.classificacao_geral,
            "necessita_escarificacao": analise.necessita_escarificacao
        }
        
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao criar análise manual: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Erro ao criar análise: {str(e)}"
        )


@router.get("/analise/{analise_id}", response_model=dict)
async def buscar_analise_compactacao(
    analise_id: str,
    db: Session = Depends(get_db)
):
    """
    Busca uma análise de compactação por ID.
    
    Retorna detalhes completos da análise com pontos e camadas.
    """
    logger.info("[COMPACTACAO] Buscando análise: %s", analise_id)
    
    try:
        compactacao_service = CompactacaoService(db)
        analise = compactacao_service.buscar_analise_por_id(analise_id)
        
        if not analise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada"
            )
        
        return {
            "status": "sucesso",
            "analise": analise,
            "mensagem": "Análise encontrada com sucesso."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao buscar análise: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar análise: {str(e)}"
        )


@router.get("/analises", response_model=dict)
async def listar_analises_compactacao(
    propriedade_id: int = None,
    talhao_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista análises de compactação com filtros opcionais.
    
    Permite filtrar por propriedade e/ou talhão.
    """
    logger.info("[COMPACTACAO] Listando análises")
    
    try:
        compactacao_service = CompactacaoService(db)
        analises = compactacao_service.listar_analises(
            propriedade_id=propriedade_id,
            talhao_id=talhao_id,
            limit=limit
        )
        
        return {
            "status": "sucesso",
            "analises": analises,
            "total": len(analises),
            "mensagem": f"Encontradas {len(analises)} análises"
        }
        
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao listar análises: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar análises: {str(e)}"
        )


@router.get("/analise/{analise_id}/resumo", response_model=dict)
async def gerar_resumo_analise(
    analise_id: str,
    db: Session = Depends(get_db)
):
    """
    Gera resumo estatístico de uma análise de compactação.
    
    Retorna estatísticas consolidadas e recomendações.
    """
    logger.info("[COMPACTACAO] Gerando resumo para análise: %s", analise_id)
    
    try:
        compactacao_service = CompactacaoService(db)
        resumo = compactacao_service.gerar_resumo_estatistico(analise_id)
        
        if not resumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada ou sem dados"
            )
        
        return {
            "status": "sucesso",
            "resumo": resumo,
            "mensagem": "Resumo estatístico gerado com sucesso."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao gerar resumo: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar resumo: {str(e)}"
        )


@router.get("/analise/{analise_id}/flags", response_model=dict)
async def gerar_flags_escarificacao(
    analise_id: str,
    db: Session = Depends(get_db)
):
    """
    Gera flags de alerta para pontos que necessitam escarificação.
    
    Identifica pontos com restrições ou impedimentos severos.
    """
    logger.info("[COMPACTACAO] Gerando flags para análise: %s", analise_id)
    
    try:
        compactacao_service = CompactacaoService(db)
        flags = compactacao_service.gerar_flags_escarificacao(analise_id)
        
        return {
            "status": "sucesso",
            "flags": flags,
            "total_flags": len(flags),
            "mensagem": f"Geradas {len(flags)} flags de alerta"
        }
        
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao gerar flags: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar flags: {str(e)}"
        )


@router.put("/analise/{analise_id}", response_model=dict)
async def atualizar_analise_compactacao(
    analise_id: str,
    analise_data: dict,
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de uma análise de compactação existente.
    
    Permite atualizar observações, talhão e propriedade.
    """
    logger.info("[COMPACTACAO] Atualizando análise: %s", analise_id)
    
    try:
        from schemas.compactacao import AnaliseCompactacaoUpdate
        
        # Converter dados para schema
        update_data = AnaliseCompactacaoUpdate(**analise_data)
        
        compactacao_service = CompactacaoService(db)
        analise = compactacao_service.atualizar_analise(analise_id, update_data)
        
        if not analise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada"
            )
        
        return {
            "status": "sucesso",
            "analise_id": analise.id,
            "mensagem": "Análise atualizada com sucesso."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao atualizar análise: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Erro ao atualizar análise: {str(e)}"
        )


@router.delete("/analise/{analise_id}", response_model=dict)
async def deletar_analise_compactacao(
    analise_id: str,
    db: Session = Depends(get_db)
):
    """
    Deleta uma análise de compactação e todos os seus dados relacionados.
    
    Operação irreversível - remove análise, pontos e camadas.
    """
    logger.info("[COMPACTACAO] Deletando análise: %s", analise_id)
    
    try:
        compactacao_service = CompactacaoService(db)
        sucesso = compactacao_service.deletar_analise(analise_id)
        
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada"
            )
        
        return {
            "status": "sucesso",
            "analise_id": analise_id,
            "mensagem": "Análise deletada com sucesso."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[COMPACTACAO] Erro ao deletar análise: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar análise: {str(e)}"
        )