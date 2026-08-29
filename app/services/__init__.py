"""
Precision VRT Solo — Pacote de Serviços (Lazy Imports)
"""

import importlib

# Mapeamento: nome_exportado → (nome_do_modulo, nome_da_classe)
_LAZY_IMPORTS = {
    "AuditoriaService": ("services.auditoria_service", "AuditoriaService"),
    "AuditoriaPersistenteService": ("services.auditoria_service", "AuditoriaPersistenteService"),
    "AuthService": ("services.auth_service", "AuthService"),
    "AuthServiceReal": ("services.auth_service_real", "AuthService"),
    "ClientesService": ("services.clientes_service", "ClientesService"),
    "ClientesServiceReal": ("services.clientes_service_real", "ClientesService"),
    "DashboardService": ("services.dashboard_service", "DashboardService"),
    "FinanceiroService": ("services.financeiro_service", "FinanceiroService"),
    "FinanceiroServiceReal": ("services.financeiro_service_real", "FinanceiroService"),
    "AtivosService": ("services.ativos_service", "AtivosService"),
    "CaixaService": ("services.caixa_service", "CaixaService"),
    "ClimaService": ("services.clima_service", "ClimaService"),
    "ComissaoService": ("services.comissao_service", "ComissaoService"),
    "CompactacaoService": ("services.compactacao_service", "CompactacaoService"),
    "ComunicacaoService": ("services.comunicacao_service", "ComunicacaoService"),
    "ConfiguracoesService": ("services.configuracoes_service", "ConfiguracoesService"),
    "ConhecimentoError": ("services.conhecimento_service", "ConhecimentoError"),
    "ConhecimentoService": ("services.conhecimento_service", "ConhecimentoService"),
    "CruzamentoService": ("services.cruzamento_service", "CruzamentoService"),
    "EquipeService": ("services.equipe_service", "EquipeService"),
    "ExportacaoService": ("services.exportacao_service", "ExportacaoService"),
    "ExtratorService": ("services.extrator_service", "ExtratorService"),
    "FertirrigacaoService": ("services.fertirrigacao_service", "FertirrigacaoService"),
    "FiscalError": ("services.fiscal_service", "FiscalError"),
    "FiscalService": ("services.fiscal_service", "FiscalService"),
    "TipoArquivo": ("services.geo_parser_service", "TipoArquivo"),
    "TipoDado": ("services.geo_parser_service", "TipoDado"),
    "Metadados": ("services.geo_parser_service", "Metadados"),
    "ResultadoParse": ("services.geo_parser_service", "ResultadoParse"),
    "LaudoExportService": ("services.laudo_export_service", "LaudoExportService"),
    "MonitoramentoService": ("services.monitoramento_service", "MonitoramentoService"),
    "NematoidesService": ("services.nematoides_service", "NematoidesService"),
    "OrcamentosService": ("services.orcamentos_service", "OrcamentosService"),
    "PermissoesService": ("services.permissoes_service", "PermissoesService"),
    "ItemCalculado": ("services.precificacao_service", "ItemCalculado"),
    "ResultadoOrcamento": ("services.precificacao_service", "ResultadoOrcamento"),
    "PrecificacaoService": ("services.precificacao_service", "PrecificacaoService"),
    "PrescricaoService": ("services.prescricao_service", "PrescricaoService"),
    "PrescricaoVrtService": ("services.prescricao_vrt_service", "PrescricaoVrtService"),
    "ReportService": ("services.report_service", "ReportService"),
    "SensoriamentoService": ("services.sensoriamento_service", "SensoriamentoService"),
    "TabelaPrecosService": ("services.tabela_precos_service", "TabelaPrecosService"),
    "DetectorTipoArquivo": ("services.upload_service", "DetectorTipoArquivo"),
    "ExtratorZip": ("services.upload_service", "ExtratorZip"),
    "ProcessadorArquivos": ("services.upload_service", "ProcessadorArquivos"),
    "UploadService": ("services.upload_service", "UploadService"),
    "ExportadorService": ("services.upload_service", "ExportadorService"),
    "ValidacaoService": ("services.validacao_service", "ValidacaoService"),
    "VendasService": ("services.vendas_service", "VendasService"),
    "_ConfigSistemaAdapter": ("services.configuracoes_service", "_ConfigSistemaAdapter"),
    "ResultadoComissao": ("services.comissao_service", "ResultadoComissao"),
    "ResultadoEnvio": ("services.comunicacao_service", "ResultadoEnvio")
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    raise AttributeError(f"module 'app.services' has no attribute '{name}'")


__all__ = list(_LAZY_IMPORTS.keys())