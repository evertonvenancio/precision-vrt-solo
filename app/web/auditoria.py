"""
Precision VRT Solo — Rotas do Módulo Auditoria

Endpoints HTTP para consulta de auditoria.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from db.database import get_db
from app.services.auditoria_service import AuditoriaPersistenteService
from core.seguranca.auth import get_current_user_id, get_current_user_nome, require_permission, Permission
from core.seguranca.auditoria import TipoAcao, ModuloSistema

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def pagina_auditoria(request: Request):
    """
    Página de auditoria - interface visual.
    """
    return templates.TemplateResponse(
        request=request,
        name="auditoria.html",
        context={}
    )


@router.get("/audit/api")
async def obter_auditoria_api(
    request: Request,
    db=Depends(get_db),
    usuario: Optional[str] = Query(None, description="Filtrar por usuário"),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo"),
    tipo_acao: Optional[str] = Query(None, description="Filtrar por tipo de ação"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    limite: int = Query(100, description="Limite de registros", le=1000)
):
    """
    API para consulta de auditoria.
    Requer permissão de auditoria.
    """
    try:
        # Verificar permissão
        require_permission(Permission.AUDITORIA_READ)
        
        # Obter usuário atual
        usuario_atual_id = get_current_user_id()
        usuario_atual_nome = get_current_user_nome()
        
        # Converter datas
        data_inicio_dt = None
        data_fim_dt = None
        
        if data_inicio:
            data_inicio_dt = datetime.fromisoformat(data_inicio + "T00:00:00")
        
        if data_fim:
            data_fim_dt = datetime.fromisoformat(data_fim + "T23:59:59")
        
        # Filtrar por usuário (se não for admin)
        usuario_filtro = None
        if usuario and usuario != usuario_atual_nome:
            # Somente admins podem ver outros usuários
            require_permission(Permission.ADMIN)
        
        # Montar filtros
        modulo_enum = None
        if modulo:
            try:
                modulo_enum = ModuloSistema(modulo)
            except ValueError:
                raise HTTPException(status_code=400, detail="Módulo inválido")
        
        tipo_acao_enum = None
        if tipo_acao:
            try:
                tipo_acao_enum = TipoAcao(tipo_acao)
            except ValueError:
                raise HTTPException(status_code=400, detail="Tipo de ação inválido")
        
        # Obter registros
        auditoria_service = AuditoriaPersistenteService(db)
        registros = auditoria_service.obter_registros(
            usuario_id=usuario_filtro,
            modulo=modulo_enum,
            tipo_acao=tipo_acao_enum,
            data_inicio=data_inicio_dt,
            data_fim=data_fim_dt,
            limite=limite
        )
        
        return {
            "success": True,
            "data": registros,
            "total": len(registros),
            "filtros": {
                "usuario": usuario,
                "modulo": modulo,
                "tipo_acao": tipo_acao,
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar auditoria: {str(e)}")


@router.get("/audit/estatisticas")
async def obter_estatisticas_auditoria(
    db=Depends(get_db),
    periodo_dias: int = Query(30, description="Período em dias", ge=1, le=365)
):
    """
    Obtém estatísticas da auditoria.
    """
    try:
        require_permission(Permission.AUDITORIA_READ)
        
        auditoria_service = AuditoriaPersistenteService(db)
        estatisticas = auditoria_service.obter_estatisticas(periodo_dias=periodo_dias)
        
        return {
            "success": True,
            "data": estatisticas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@router.get("/audit/exportar")
async def exportar_auditoria(
    request: Request,
    db=Depends(get_db),
    formato: str = Query("csv", description="Formato de exportação"),
    usuario: Optional[str] = Query(None),
    modulo: Optional[str] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None)
):
    """
    Exporta registros de auditoria.
    """
    try:
        require_permission(Permission.AUDITORIA_EXPORT)
        
        # Obter registros
        auditoria_service = AuditoriaPersistenteService(db)
        registros = auditoria_service.obter_registros(
            usuario_id=None,  # Permitir exportação de todos (com permissão)
            modulo=ModuloSistema(modulo) if modulo else None,
            data_inicio=datetime.fromisoformat(data_inicio + "T00:00:00") if data_inicio else None,
            data_fim=datetime.fromisoformat(data_fim + "T23:59:59") if data_fim else None,
            limite=10000  # Limite maior para exportação
        )
        
        # Formatar para exportação
        dados_exportacao = []
        for registro in registros:
            dados_exportacao.append({
                "ID": registro["id"],
                "Timestamp": registro["timestamp"],
                "Tipo Ação": registro["tipo_acao"],
                "Módulo": registro["modulo"],
                "Usuário": registro["usuario_nome"],
                "Ação": registro["acao"],
                "Recurso ID": registro["recurso_id"],
                "Recurso Tipo": registro["recurso_tipo"],
                "IP Origem": registro["ip_origem"],
                "Sucesso": "Sim" if registro["sucesso"] else "Não",
                "Mensagem": registro["mensagem"] or "",
                "Detalhes": registro["detalhes"] or ""
            })
        
        # Chamar service de exportação
        from app.services.exportacao_service import ExportacaoService
        export_service = ExportacaoService()
        
        resultado = export_service.exportar_dados(
            dados_originais=dados_exportacao,
            formatos=[formato.upper()],
            nome_arquivo_base="auditoria_export"
        )
        
        return {
            "success": True,
            "message": "Exportação concluída",
            "arquivos": resultado.get("arquivos_exportados", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar auditoria: {str(e)}")
