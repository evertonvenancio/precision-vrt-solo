"""Router FastAPI para o Modulo Extrator de Solucao.

Endpoints para gerenciamento de pontos de monitoramento, leituras,
diagnostico nutricional, upload de CSV e curvas nutritivas.
"""

import logging
import io
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy.orm import Session
import pandas as pd

from db.database import get_db

from models.extrator import PontoExtrator, LeituraExtrator, CurvaNutritiva
from schemas.extrator import (
    PontoExtratorCreate, PontoExtratorUpdate, PontoExtratorResponse,
    LeituraExtratorCreate, LeituraExtratorResponse,
    UploadCSVResponse, HistoricoResponse, DiagnosticoCompleto,
    CurvaNutritivaCreate, CurvaNutritivaResponse
)
from app.services.extrator_service import ExtratorService, mapear_colunas_csv

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/extrator",
    tags=["Extrator"],
)


# =========================================================================
# Pontos de Monitoramento
# =========================================================================

@router.post(
    "/pontos",
    response_model=PontoExtratorResponse,
    status_code=201,
    summary="Criar ponto de monitoramento",
)
def criar_ponto(
    ponto: PontoExtratorCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PontoExtratorResponse:
    """Cria um novo ponto de monitoramento (extrator/capsula)."""
    logger.info("Criando ponto de monitoramento: %s", ponto.codigo)

    try:
        novo_ponto = PontoExtrator(**ponto.model_dump())
        db.add(novo_ponto)
        db.commit()
        db.refresh(novo_ponto)
        logger.info("Ponto criado com sucesso: ID=%s", novo_ponto.id)
        return PontoExtratorResponse.model_validate(novo_ponto)
    except Exception as e:
        db.rollback()
        logger.error("Erro ao criar ponto %s: %s", ponto.codigo, e)
        raise HTTPException(status_code=500, detail=f"Erro ao criar ponto: {str(e)}")


@router.get(
    "/pontos",
    response_model=list[PontoExtratorResponse],
    summary="Listar pontos de monitoramento",
)
def listar_pontos(
    db: Annotated[Session, Depends(get_db)],
    ativo: Optional[bool] = Query(default=True, description="Filtrar por ativos"),
    cultura: Optional[str] = Query(default=None, description="Filtrar por cultura"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[PontoExtratorResponse]:
    """Lista todos os pontos de monitoramento cadastrados."""
    logger.info("Listando pontos de monitoramento | ativo=%s cultura=%s skip=%d limit=%d", ativo, cultura, skip, limit)

    try:
        query = db.query(PontoExtrator)
        if ativo is not None:
            query = query.filter(PontoExtrator.ativo == ativo)
        if cultura:
            query = query.filter(PontoExtrator.cultura.ilike(f"%{cultura}%"))

        pontos = query.offset(skip).limit(limit).all()
        logger.info("%d pontos encontrados", len(pontos))
        return [PontoExtratorResponse.model_validate(p) for p in pontos]
    except Exception as e:
        logger.error("Erro ao listar pontos: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao listar pontos: {str(e)}")


@router.get(
    "/pontos/{ponto_id}",
    response_model=PontoExtratorResponse,
    summary="Obter ponto por ID",
)
def obter_ponto(
    ponto_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> PontoExtratorResponse:
    """Retorna os dados de um ponto de monitoramento especifico."""
    logger.info("Buscando ponto ID: %s", ponto_id)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")
        return PontoExtratorResponse.model_validate(ponto)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar ponto %s: %s", ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ponto: {str(e)}")


@router.patch(
    "/pontos/{ponto_id}",
    response_model=PontoExtratorResponse,
    summary="Atualizar ponto de monitoramento",
)
def atualizar_ponto(
    ponto_id: str,
    dados: PontoExtratorUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> PontoExtratorResponse:
    """Atualiza parcialmente um ponto de monitoramento."""
    logger.info("Atualizando ponto ID: %s", ponto_id)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado para atualizacao: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")

        dados_dict = dados.model_dump(exclude_unset=True)
        for campo, valor in dados_dict.items():
            setattr(ponto, campo, valor)

        db.commit()
        db.refresh(ponto)
        logger.info("Ponto atualizado com sucesso: %s", ponto_id)
        return PontoExtratorResponse.model_validate(ponto)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro ao atualizar ponto %s: %s", ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar ponto: {str(e)}")


@router.delete(
    "/pontos/{ponto_id}",
    status_code=204,
    summary="Remover ponto de monitoramento",
)
def remover_ponto(
    ponto_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Remove (soft-delete) um ponto de monitoramento."""
    logger.info("Removendo ponto ID: %s", ponto_id)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado para remocao: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")

        ponto.ativo = False
        db.commit()
        logger.info("Ponto removido (soft-delete): %s", ponto_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro ao remover ponto %s: %s", ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao remover ponto: {str(e)}")


# =========================================================================
# Leituras
# =========================================================================

@router.post(
    "/leituras",
    response_model=LeituraExtratorResponse,
    status_code=201,
    summary="Registrar leitura",
)
def criar_leitura(
    leitura: LeituraExtratorCreate,
    db: Annotated[Session, Depends(get_db)],
) -> LeituraExtratorResponse:
    """Registra uma nova leitura de solucao de um ponto de monitoramento."""
    logger.info("Registrando leitura para ponto ID: %s", leitura.ponto_id)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == leitura.ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado para leitura: %s", leitura.ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")

        nova_leitura = LeituraExtrator(**leitura.model_dump())
        db.add(nova_leitura)
        db.commit()
        db.refresh(nova_leitura)
        logger.info("Leitura criada com sucesso: ID=%s", nova_leitura.id)
        return LeituraExtratorResponse.model_validate(nova_leitura)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro ao criar leitura para ponto %s: %s", leitura.ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao criar leitura: {str(e)}")


@router.get(
    "/leituras",
    response_model=list[LeituraExtratorResponse],
    summary="Listar leituras",
)
def listar_leituras(
    db: Annotated[Session, Depends(get_db)],
    ponto_id: Optional[str] = Query(default=None, description="Filtrar por ponto"),
    data_inicio: Optional[str] = Query(default=None, description="Data inicial (AAAA-MM-DD)"),
    data_fim: Optional[str] = Query(default=None, description="Data final (AAAA-MM-DD)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[LeituraExtratorResponse]:
    """Lista leituras registradas, com filtros opcionais."""
    logger.info("Listando leituras | ponto=%s data_inicio=%s data_fim=%s", ponto_id, data_inicio, data_fim)

    try:
        query = db.query(LeituraExtrator)
        if ponto_id:
            query = query.filter(LeituraExtrator.ponto_id == ponto_id)
        if data_inicio:
            query = query.filter(LeituraExtrator.data_leitura >= data_inicio)
        if data_fim:
            query = query.filter(LeituraExtrator.data_leitura <= data_fim)

        leituras = query.order_by(LeituraExtrator.data_leitura.desc()).offset(skip).limit(limit).all()
        logger.info("%d leituras encontradas", len(leituras))
        return [LeituraExtratorResponse.model_validate(l) for l in leituras]
    except Exception as e:
        logger.error("Erro ao listar leituras: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao listar leituras: {str(e)}")


@router.get(
    "/leituras/{leitura_id}",
    response_model=LeituraExtratorResponse,
    summary="Obter leitura por ID",
)
def obter_leitura(
    leitura_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> LeituraExtratorResponse:
    """Retorna os dados de uma leitura especifica."""
    logger.info("Buscando leitura ID: %s", leitura_id)

    try:
        leitura = db.query(LeituraExtrator).filter(LeituraExtrator.id == leitura_id).first()
        if not leitura:
            logger.warning("Leitura nao encontrada: %s", leitura_id)
            raise HTTPException(status_code=404, detail="Leitura nao encontrada")
        return LeituraExtratorResponse.model_validate(leitura)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar leitura %s: %s", leitura_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar leitura: {str(e)}")


@router.post(
    "/leituras/upload-csv",
    response_model=UploadCSVResponse,
    summary="Upload de leituras via CSV",
)
def upload_csv_leituras(
    arquivo: Annotated[UploadFile, File(..., description="Arquivo CSV com leituras")],
    db: Annotated[Session, Depends(get_db)],
    ponto_id: Optional[str] = Query(default=None, description="Ponto padrao se nao houver coluna no CSV"),
) -> UploadCSVResponse:
    """Importa leituras em lote a partir de um arquivo CSV."""
    logger.info("Recebendo upload de CSV: %s", arquivo.filename)

    try:
        conteudo = arquivo.file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(conteudo))
        logger.info("CSV carregado: %d linhas, %d colunas", len(df), len(df.columns))

        mapeamento = mapear_colunas_csv(list(df.columns))
        logger.info("Mapeamento de colunas: %s", mapeamento)

        if not mapeamento:
            logger.error("Nenhuma coluna reconhecida no CSV")
            raise HTTPException(status_code=422, detail="Nenhuma coluna reconhecida no CSV. Colunas esperadas: ph, ce, no3, k, ca, mg, po4, so4, b, fe, mn, zn, cu, data, ponto_id")

        leituras_inseridas = 0
        leituras_erro = 0
        erros = []

        for idx, row in df.iterrows():
            try:
                dados_leitura = {}
                for col_csv, campo_modelo in mapeamento.items():
                    valor = row[col_csv]
                    if pd.notna(valor):
                        dados_leitura[campo_modelo] = valor

                if ponto_id and "ponto_id" not in dados_leitura:
                    dados_leitura["ponto_id"] = ponto_id

                if "ponto_id" not in dados_leitura:
                    leituras_erro += 1
                    erros.append(f"Linha {idx+1}: ponto_id nao informado")
                    continue

                ponto = db.query(PontoExtrator).filter(PontoExtrator.id == dados_leitura["ponto_id"]).first()
                if not ponto:
                    leituras_erro += 1
                    erros.append(f"Linha {idx+1}: ponto_id {dados_leitura['ponto_id']} nao encontrado")
                    continue

                nova_leitura = LeituraExtrator(**dados_leitura)
                db.add(nova_leitura)
                leituras_inseridas += 1
            except Exception as e:
                leituras_erro += 1
                erros.append(f"Linha {idx+1}: {str(e)}")
                logger.warning("Erro na linha %d: %s", idx+1, e)

        db.commit()
        logger.info("Upload CSV concluido: %d inseridas, %d erros", leituras_inseridas, leituras_erro)

        return UploadCSVResponse(
            total_linhas=len(df),
            leituras_inseridas=leituras_inseridas,
            leituras_erro=leituras_erro,
            erros=erros[:20],
            colunas_reconhecidas=list(mapeamento.values()),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro no upload CSV %s: %s", arquivo.filename, e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar CSV: {str(e)}")


# =========================================================================
# Diagnostico
# =========================================================================

@router.get(
    "/diagnostico/{ponto_id}",
    response_model=DiagnosticoCompleto,
    summary="Diagnostico nutricional completo",
)
def diagnostico_ponto(
    ponto_id: str,
    db: Annotated[Session, Depends(get_db)],
    leitura_id: Optional[str] = Query(default=None, description="ID especifico da leitura; usa a mais recente se omitido"),
) -> DiagnosticoCompleto:
    """Executa diagnostico nutricional completo com recomendacoes de sais."""
    logger.info("Gerando diagnostico para ponto ID: %s | leitura_id=%s", ponto_id, leitura_id)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado para diagnostico: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")

        if leitura_id:
            leitura = db.query(LeituraExtrator).filter(
                LeituraExtrator.id == leitura_id,
                LeituraExtrator.ponto_id == ponto_id
            ).first()
        else:
            leitura = db.query(LeituraExtrator).filter(
                LeituraExtrator.ponto_id == ponto_id
            ).order_by(LeituraExtrator.data_leitura.desc()).first()

        if not leitura:
            logger.warning("Nenhuma leitura encontrada para ponto: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este ponto")

        curva = db.query(CurvaNutritiva).filter(
            CurvaNutritiva.cultura == ponto.cultura,
            CurvaNutritiva.fase_fenologica == ponto.fase_fenologica
        ).first()

        if not curva:
            logger.warning("Curva nutritiva nao encontrada para cultura=%s fase=%s", ponto.cultura, ponto.fase_fenologica)
            raise HTTPException(
                status_code=404,
                detail=f"Curva nutritiva nao encontrada para cultura={ponto.cultura} fase={ponto.fase_fenologica}"
            )

        historico = db.query(LeituraExtrator).filter(
            LeituraExtrator.ponto_id == ponto_id
        ).order_by(LeituraExtrator.data_leitura.desc()).limit(10).all()

        service = ExtratorService(db)
        diagnostico = service.gerar_diagnostico_completo(leitura, curva, historico)
        logger.info("Diagnostico gerado com sucesso para ponto: %s", ponto_id)
        return diagnostico

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao gerar diagnostico para ponto %s: %s", ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar diagnostico: {str(e)}")


# =========================================================================
# Historico
# =========================================================================

@router.get(
    "/historico/{ponto_id}",
    response_model=HistoricoResponse,
    summary="Historico temporal de leituras",
)
def historico_ponto(
    ponto_id: str,
    db: Annotated[Session, Depends(get_db)],
    dias: int = Query(default=90, ge=7, le=730, description="Janela temporal em dias"),
) -> HistoricoResponse:
    """Retorna serie historica de leituras com analise estatistica."""
    logger.info("Gerando historico para ponto ID: %s (ultimos %d dias)", ponto_id, dias)

    try:
        ponto = db.query(PontoExtrator).filter(PontoExtrator.id == ponto_id).first()
        if not ponto:
            logger.warning("Ponto nao encontrado para historico: %s", ponto_id)
            raise HTTPException(status_code=404, detail="Ponto de monitoramento nao encontrado")

        from datetime import date, timedelta
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)

        leituras = db.query(LeituraExtrator).filter(
            LeituraExtrator.ponto_id == ponto_id,
            LeituraExtrator.data_leitura >= data_inicio,
            LeituraExtrator.data_leitura <= data_fim
        ).order_by(LeituraExtrator.data_leitura).all()

        service = ExtratorService(db)
        historico = service.calcular_historico(ponto, leituras, data_inicio, data_fim)
        logger.info("Historico gerado com sucesso: %d leituras", len(leituras))
        return historico

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao gerar historico para ponto %s: %s", ponto_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar historico: {str(e)}")


# =========================================================================
# Curvas Nutritivas
# =========================================================================

@router.post(
    "/curvas",
    response_model=CurvaNutritivaResponse,
    status_code=201,
    summary="Cadastrar curva nutritiva",
)
def criar_curva(
    curva: CurvaNutritivaCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CurvaNutritivaResponse:
    """Cadastra uma nova curva nutritiva de referencia para uma cultura/fase."""
    logger.info("Cadastrando curva nutritiva: %s / %s", curva.cultura, curva.fase_fenologica.value if hasattr(curva.fase_fenologica, 'value') else curva.fase_fenologica)

    try:
        nova_curva = CurvaNutritiva(**curva.model_dump())
        db.add(nova_curva)
        db.commit()
        db.refresh(nova_curva)
        logger.info("Curva nutritiva criada com sucesso: ID=%s", nova_curva.id)
        return CurvaNutritivaResponse.model_validate(nova_curva)
    except Exception as e:
        db.rollback()
        logger.error("Erro ao criar curva nutritiva: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao criar curva nutritiva: {str(e)}")


@router.get(
    "/curvas",
    response_model=list[CurvaNutritivaResponse],
    summary="Listar curvas nutritivas",
)
def listar_curvas(
    db: Annotated[Session, Depends(get_db)],
    cultura: Optional[str] = Query(default=None, description="Filtrar por cultura"),
    fase: Optional[str] = Query(default=None, description="Filtrar por fase fenologica"),
) -> list[CurvaNutritivaResponse]:
    """Lista curvas nutritivas cadastradas."""
    logger.info("Listando curvas nutritivas | cultura=%s fase=%s", cultura, fase)

    try:
        query = db.query(CurvaNutritiva)
        if cultura:
            query = query.filter(CurvaNutritiva.cultura.ilike(f"%{cultura}%"))
        if fase:
            query = query.filter(CurvaNutritiva.fase_fenologica.ilike(f"%{fase}%"))

        curvas = query.all()
        logger.info("%d curvas encontradas", len(curvas))
        return [CurvaNutritivaResponse.model_validate(c) for c in curvas]
    except Exception as e:
        logger.error("Erro ao listar curvas: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao listar curvas: {str(e)}")


@router.get(
    "/curvas/{curva_id}",
    response_model=CurvaNutritivaResponse,
    summary="Obter curva nutritiva por ID",
)
def obter_curva(
    curva_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> CurvaNutritivaResponse:
    """Retorna os dados de uma curva nutritiva especifica."""
    logger.info("Buscando curva nutritiva ID: %s", curva_id)

    try:
        curva = db.query(CurvaNutritiva).filter(CurvaNutritiva.id == curva_id).first()
        if not curva:
            logger.warning("Curva nutritiva nao encontrada: %s", curva_id)
            raise HTTPException(status_code=404, detail="Curva nutritiva nao encontrada")
        return CurvaNutritivaResponse.model_validate(curva)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar curva %s: %s", curva_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar curva: {str(e)}")