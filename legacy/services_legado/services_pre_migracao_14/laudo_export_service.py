"""Servico de exportacao de laudos com validacao de seguranca.

Responsavel por gerar e servir arquivos de laudo (PDF, CSV, Shapefile),
garantindo que nenhum path traversal seja possivel.
"""

import logging
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

# Diretorio base seguro para exportacoes
BASE_EXPORT_DIR = Path("storage/exports").resolve()


def _validar_caminho_seguro(nome_arquivo: str) -> Path:
    """Valida que o caminho solicitado nao sai do diretorio base.

    Args:
        nome_arquivo: Nome ou caminho relativo do arquivo solicitado.

    Returns:
        Path absoluto validado dentro de BASE_EXPORT_DIR.

    Raises:
        HTTPException 404: Se o caminho tentar sair do diretorio base.
    """
    # Normalizar o caminho e resolver links simbolicos
    caminho_solicitado = (BASE_EXPORT_DIR / nome_arquivo).resolve()

    # Verificar se o caminho resolvido ainda esta dentro do diretorio base
    try:
        caminho_solicitado.relative_to(BASE_EXPORT_DIR)
    except ValueError:
        logger.warning(
            "Tentativa de path traversal bloqueada: %s (base: %s)",
            nome_arquivo, BASE_EXPORT_DIR
        )
        raise HTTPException(
            status_code=404,
            detail="Arquivo nao encontrado ou acesso negado."
        )

    return caminho_solicitado


def obter_caminho_laudo(nome_arquivo: str) -> Path:
    """Retorna o caminho absoluto de um laudo apos validacao de seguranca.

    Args:
        nome_arquivo: Nome do arquivo de laudo (ex: "laudo_123.pdf").

    Returns:
        Path absoluto validado.

    Raises:
        HTTPException 404: Se o arquivo nao existir ou for invalido.
    """
    caminho = _validar_caminho_seguro(nome_arquivo)

    if not caminho.exists():
        logger.warning("Laudo nao encontrado: %s", caminho)
        raise HTTPException(status_code=404, detail="Laudo nao encontrado.")

    if not caminho.is_file():
        logger.warning("Caminho nao e um arquivo: %s", caminho)
        raise HTTPException(status_code=404, detail="Recurso invalido.")

    logger.info("Laudo validado e localizado: %s", caminho)
    return caminho


def listar_laudos_disponiveis() -> list[dict]:
    """Lista todos os laudos disponiveis no diretorio base.

    Returns:
        Lista de dicts com nome, tamanho e data de modificacao.
    """
    laudos = []
    if not BASE_EXPORT_DIR.exists():
        logger.warning("Diretorio de exportacoes nao existe: %s", BASE_EXPORT_DIR)
        return laudos

    for arquivo in BASE_EXPORT_DIR.iterdir():
        if arquivo.is_file():
            laudos.append({
                "nome": arquivo.name,
                "tamanho_bytes": arquivo.stat().st_size,
                "modificado_em": arquivo.stat().st_mtime,
            })

    logger.info("%d laudos listados em %s", len(laudos), BASE_EXPORT_DIR)
    return laudos


class LaudoExportService:
    """Servico de geracao de laudos PDF e cartoes de cabine."""

    def __init__(self):
        self.export_dir = BASE_EXPORT_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def gerar_pdf_profissional(self, dados: dict, nome_arquivo: str) -> Path:
        """Gera um laudo PDF profissional com os dados da prescricao.

        Args:
            dados: Dicionario com geojson, perfis, prescricoes, etc.
            nome_arquivo: Nome do arquivo de saida (ex: "Cliente_Talhao_21-06-2026.pdf").

        Returns:
            Path: Caminho absoluto do arquivo PDF gerado.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except ImportError:
            logger.error("ReportLab nao instalado. Instale com: pip install reportlab")
            raise HTTPException(status_code=500, detail="Biblioteca de geracao de PDF nao disponivel.")

        caminho_pdf = self.export_dir / nome_arquivo

        c = canvas.Canvas(str(caminho_pdf), pagesize=A4)
        largura, altura = A4

        # Cabecalho
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, altura - 2 * cm, "Laudo Tecnico - Precision VRT Solo")

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, altura - 2.8 * cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Dados do talhao
        y = altura - 4 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Dados do Talhao")
        c.line(2 * cm, y - 0.3 * cm, largura - 2 * cm, y - 0.3 * cm)

        c.setFont("Helvetica", 10)
        y -= 1 * cm
        c.drawString(2 * cm, y, f"Cliente: {dados.get('cliente_nome', 'N/A')}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Talhao: {dados.get('talhao_nome', 'N/A')}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Area Total: {dados.get('area_total_ha', 0):.2f} ha")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Numero de Zonas: {dados.get('n_zonas', 0)}")

        # Perfis por zona
        y -= 1.5 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Diagnostico por Zona")
        c.line(2 * cm, y - 0.3 * cm, largura - 2 * cm, y - 0.3 * cm)

        perfis = dados.get('perfis', {})
        c.setFont("Helvetica", 9)
        y -= 1 * cm

        for zona_id, perfil in perfis.items():
            if y < 3 * cm:
                c.showPage()
                y = altura - 2 * cm
                c.setFont("Helvetica", 9)

            c.setFont("Helvetica-Bold", 10)
            c.drawString(2 * cm, y, f"Zona {zona_id}")
            y -= 0.6 * cm
            c.setFont("Helvetica", 9)

            for attr, valor in perfil.items():
                if valor is not None:
                    c.drawString(2.5 * cm, y, f"  {attr}: {valor:.2f}")
                    y -= 0.5 * cm
            y -= 0.3 * cm

        # Prescricoes
        if y < 5 * cm:
            c.showPage()
            y = altura - 2 * cm

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Prescricao Recomendada")
        c.line(2 * cm, y - 0.3 * cm, largura - 2 * cm, y - 0.3 * cm)

        prescricoes = dados.get('prescricoes', {})
        c.setFont("Helvetica", 9)
        y -= 1 * cm

        for zona_id, presc in prescricoes.items():
            if y < 3 * cm:
                c.showPage()
                y = altura - 2 * cm
                c.setFont("Helvetica", 9)

            c.setFont("Helvetica-Bold", 10)
            c.drawString(2 * cm, y, f"Zona {zona_id}")
            y -= 0.6 * cm
            c.setFont("Helvetica", 9)

            for insumo, qtd in presc.items():
                c.drawString(2.5 * cm, y, f"  {insumo}: {qtd:.2f}")
                y -= 0.5 * cm
            y -= 0.3 * cm

        # Rodape
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2 * cm, 1.5 * cm, "Precision VRT Solo - Sistema de Gestao Agronomica")
        c.drawString(2 * cm, 1 * cm, "Este laudo e de responsabilidade do consultor que o emitiu.")

        c.save()
        logger.info("Laudo PDF gerado: %s", caminho_pdf)
        return caminho_pdf

    def gerar_cartao_cabine(self, dados: dict, nome_arquivo: str) -> Path:
        """Gera um cartao de cabine A5 com os dados da prescricao.

        Args:
            dados: Dicionario com geojson, perfis, prescricoes, etc.
            nome_arquivo: Nome do arquivo de saida (ex: "Cliente_Talhao_21-06-2026_cartao.pdf").

        Returns:
            Path: Caminho absoluto do arquivo PDF gerado.
        """
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except ImportError:
            logger.error("ReportLab nao instalado. Instale com: pip install reportlab")
            raise HTTPException(status_code=500, detail="Biblioteca de geracao de PDF nao disponivel.")

        caminho_pdf = self.export_dir / nome_arquivo

        c = canvas.Canvas(str(caminho_pdf), pagesize=A5)
        largura, altura = A5

        # Cabecalho compacto
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1.5 * cm, altura - 1.5 * cm, "Cartao de Cabine")

        c.setFont("Helvetica", 8)
        c.drawString(1.5 * cm, altura - 2 * cm, f"{dados.get('cliente_nome', 'N/A')} - {dados.get('talhao_nome', 'N/A')}")
        c.drawString(1.5 * cm, altura - 2.4 * cm, f"{datetime.now().strftime('%d/%m/%Y')}")

        # Tabela resumida de prescricoes
        y = altura - 3.5 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1.5 * cm, y, "Zona | Calcario | N | P2O5 | K2O")
        c.line(1.5 * cm, y - 0.2 * cm, largura - 1.5 * cm, y - 0.2 * cm)

        y -= 0.8 * cm
        c.setFont("Helvetica", 8)
        prescricoes = dados.get('prescricoes', {})
        for zona_id, presc in prescricoes.items():
            linha = f"  {zona_id}   | {presc.get('calcario', 0):.1f} | {presc.get('n', 0):.0f} | {presc.get('p2o5', 0):.0f} | {presc.get('k2o', 0):.0f}"
            c.drawString(1.5 * cm, y, linha)
            y -= 0.5 * cm

        # Rodape
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(1.5 * cm, 1 * cm, "Precision VRT Solo")

        c.save()
        logger.info("Cartao de cabine gerado: %s", caminho_pdf)
        return caminho_pdf
