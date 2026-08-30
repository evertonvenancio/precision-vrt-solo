"""
Precision VRT Solo — Rotas do Módulo Relatórios

Endpoints HTTP para geração e exportação de relatórios.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path
import tempfile
import os

from db.database import get_db
from app.services.report_service import ReportService
from app.services.nematoides_service import NematoidesService
from core.seguranca.auth import get_current_user_id, get_current_user_nome, require_permission
from core.seguranca.auth import Permission
from core.seguranca.auditoria import TipoAcao, ModuloSistema

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def pagina_relatorios(request: Request):
    """
    Página principal de relatórios - interface visual.
    """
    return templates.TemplateResponse(
        request=request,
        name="relatorios.html",
        context={
            "relatorios_disponiveis": ReportService(None).obter_relatorios_disponiveis()
        }
    )


@router.get("/relatorios/gerar/{relatorio_id}")
async def gerar_relatorio_api(
    relatorio_id: str,
    request: Request,
    db=Depends(get_db),
    formatos: Optional[str] = Query("csv", description="Formatos de exportação (csv,excel,pdf)"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Status"),
    cidade: Optional[str] = Query(None, description="Cidade"),
    estado: Optional[str] = Query(None, description="Estado")
):
    """
    Gera relatório específico.
    Requer permissão correspondente.
    """
    try:
        # Verificar permissão
        permissoes_relatorios = {
            'clientes': Permission.RELATORIOS_CLIENTES,
            'financeiro': Permission.RELATORIOS_FINANCEIRO,
            'operacional': Permission.RELATORIOS_OPERACIONAL
        }
        
        permissao = permissoes_relatorios.get(relatorio_id)
        if not permissao:
            raise HTTPException(status_code=400, detail="Relatório inválido")
        
        require_permission(permissao)
        
        # Montar filtros
        filtros = {}
        if data_inicio:
            filtros['data_inicio'] = data_inicio
        if data_fim:
            filtros['data_fim'] = data_fim
        if status:
            filtros['status'] = status
        if cidade:
            filtros['cidade'] = cidade
        if estado:
            filtros['estado'] = estado
        
        # Gerar relatório
        report_service = ReportService(db)
        formatos_list = formatos.split(',') if formatos else ['csv']
        
        if relatorio_id == 'clientes':
            resultado = report_service.gerar_relatorio_clientes(filtros, formatos_list)
        elif relatorio_id == 'financeiro':
            resultado = report_service.gerar_relatorio_financeiro(filtros, formatos_list)
        elif relatorio_id == 'operacional':
            resultado = report_service.gerar_relatorio_operacional(filtros, formatos_list)
        else:
            raise HTTPException(status_code=400, detail="Relatório inválido")
        
        # Registrar auditoria
        if resultado['success']:
            from app.services.auditoria_service import AuditoriaPersistenteService
            
            auditoria_service = AuditoriaPersistenteService(db)
            auditoria_service.registrar_operacao(
                tipo_acao=TipoAcao.EXPORTAR,
                modulo=ModuloSistema.CONFIGURACOES,
                usuario_id=get_current_user_id(),
                usuario_nome=get_current_user_nome(),
                acao=f"relatorio_{relatorio_id}",
                sucesso=True,
                detalhes={
                    'relatorio': relatorio_id,
                    'formatos': formatos_list,
                    'filtros': filtros,
                    'registros': resultado['data']['total_registros']
                }
            )
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


@router.get("/relatorios/visualizar/{relatorio_id}")
async def visualizar_relatorio(
    request: Request,
    relatorio_id: str,
    db=Depends(get_db),
    **filtros
):
    """
    Visualização prévia do relatório sem exportação.
    """
    try:
        # Verificar permissão
        permissoes_relatorios = {
            'clientes': Permission.RELATORIOS_CLIENTES,
            'financeiro': Permission.RELATORIOS_FINANCEIRO,
            'operacional': Permission.RELATORIOS_OPERACIONAL
        }
        
        permissao = permissoes_relatorios.get(relatorio_id)
        if not permissao:
            raise HTTPException(status_code=400, detail="Relatório inválido")
        
        require_permission(permissao)
        
        # Gerar relatório sem exportação
        report_service = ReportService(db)
        
        if relatorio_id == 'clientes':
            resultado = report_service.gerar_relatorio_clientes(filtros, [])
        elif relatorio_id == 'financeiro':
            resultado = report_service.gerar_relatorio_financeiro(filtros, [])
        elif relatorio_id == 'operacional':
            resultado = report_service.gerar_relatorio_operacional(filtros, [])
        else:
            raise HTTPException(status_code=400, detail="Relatório inválido")
        
        # Registrar auditoria
        if resultado['success']:
            from app.services.auditoria_service import AuditoriaPersistenteService
            
            auditoria_service = AuditoriaPersistenteService(db)
            auditoria_service.registrar_operacao(
                tipo_acao=TipoAcao.CALCULAR,
                modulo=ModuloSistema.CONFIGURACOES,
                usuario_id=get_current_user_id(),
                usuario_nome=get_current_user_nome(),
                acao=f"preview_relatorio_{relatorio_id}",
                sucesso=True,
                detalhes={
                    'relatorio': relatorio_id,
                    'filtros': filtros,
                    'registros': resultado['data']['total_registros']
                }
            )
        
        return templates.TemplateResponse(
            request=request,
            name="relatorio_preview.html",
            context={
                "relatorio": resultado['data'],
                "relatorio_id": relatorio_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao visualizar relatório: {str(e)}")


@router.get("/relatorios/tipos")
async def obter_tipos_relatorios():
    """
    Retorna tipos de relatórios disponíveis.
    """
    try:
        report_service = ReportService(None)
        relatorios = report_service.obter_relatorios_disponiveis()
        
        return {
            "success": True,
            "data": relatorios
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter tipos de relatórios: {str(e)}")
