"""
MAPEADOR DE ESTRUTURA — Precision VRT Solo
Gera relatório completo da arquitetura real do projeto.
Exclui: venv/, __pycache__/, .git/, node_modules/
"""

import os
from pathlib import Path
from datetime import datetime

# CONFIGURAÇÃO
RAIZ = Path(r"C:\precision_vrt_solo")
OUTPUT = RAIZ / "RELATORIO_ARQUITETURA_REAL.txt"

EXTENSOES_RELEVANTES = {".py", ".txt", ".json", ".csv", ".xlsx", ".db", ".sql", ".md", ".yml", ".yaml", ".html", ".js", ".css"}
PASTAS_EXCLUIR = {"venv", "__pycache__", ".git", "node_modules", ".pytest_cache", ".mypy_cache", "dist", "build"}


def deve_excluir(caminho: Path) -> bool:
    """Verifica se alguma parte do caminho está na lista de exclusão."""
    for parte in caminho.parts:
        if parte.lower() in PASTAS_EXCLUIR:
            return True
    return False


def formatar_tamanho(bytes_size: int) -> str:
    if bytes_size == 0:
        return "0 B  [STUB]"
    elif bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


def classificar_arquivo(nome: str, tamanho: int) -> str:
    tags = []
    if tamanho == 0:
        tags.append("STUB_VAZIO")
    elif tamanho > 20 * 1024 and nome.endswith(".py"):
        tags.append("MONOLITO")
    elif tamanho > 50 * 1024 and nome.endswith(".py"):
        tags.append("MONOLITO_GRANDE")

    if "test" in nome.lower() and nome.endswith(".py"):
        tags.append("TESTE")
    if nome.startswith("_") and nome.endswith(".py"):
        tags.append("PRIVADO")
    if nome == "__init__.py":
        tags.append("INIT")

    return " | ".join(tags) if tags else "-"


def main():
    if not RAIZ.exists():
        print(f"ERRO: Pasta {RAIZ} não encontrada!")
        return

    linhas = []
    linhas.append("=" * 90)
    linhas.append("RELATÓRIO DE ARQUITETURA REAL — Precision VRT Solo")
    linhas.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    linhas.append(f"Raiz: {RAIZ}")
    linhas.append("=" * 90)
    linhas.append("")

    # Estatísticas globais
    total_arquivos = 0
    total_pastas = 0
    total_stubs = 0
    total_monolitos = 0
    arquivos_py = 0
    arquivos_db = 0

    # Coletar estrutura
    estrutura = {}

    for item in sorted(RAIZ.rglob("*")):
        if deve_excluir(item):
            continue

        relativo = item.relative_to(RAIZ)

        if item.is_dir():
            total_pastas += 1
            continue

        # Arquivo
        total_arquivos += 1
        ext = item.suffix.lower()
        tamanho = item.stat().st_size

        if ext == ".py":
            arquivos_py += 1
        if ext == ".db":
            arquivos_db += 1
        if tamanho == 0:
            total_stubs += 1
        if tamanho > 20 * 1024 and ext == ".py":
            total_monolitos += 1

        # Agrupar por pasta
        pasta_pai = str(relativo.parent)
        if pasta_pai not in estrutura:
            estrutura[pasta_pai] = []

        estrutura[pasta_pai].append({
            "nome": item.name,
            "tamanho": tamanho,
            "tamanho_str": formatar_tamanho(tamanho),
            "classificacao": classificar_arquivo(item.name, tamanho),
            "extensao": ext,
        })

    # Resumo executivo
    linhas.append("📊 RESUMO EXECUTIVO")
    linhas.append("-" * 90)
    linhas.append(f"Total de pastas (excluindo lixo):     {total_pastas}")
    linhas.append(f"Total de arquivos:                    {total_arquivos}")
    linhas.append(f"Arquivos Python (.py):                {arquivos_py}")
    linhas.append(f"Bancos de dados (.db):                {arquivos_db}")
    linhas.append(f"Stubs vazios (0 bytes):               {total_stubs}")
    linhas.append(f"Monolitos Python (>20KB):             {total_monolitos}")
    linhas.append("")

    # Lista por pasta
    linhas.append("📁 ESTRUTURA POR PASTA")
    linhas.append("-" * 90)

    for pasta in sorted(estrutura.keys()):
        arquivos = estrutura[pasta]
        linhas.append(f"\n[{pasta}]")
        linhas.append("-" * 80)

        for arq in sorted(arquivos, key=lambda x: x["nome"]):
            tag = f" [{arq['classificacao']}]" if arq["classificacao"] != "-" else ""
            linhas.append(f"  {arq['nome']:50s} {arq['tamanho_str']:>15s}{tag}")

    # Seção especial: arquivos soltos na raiz
    linhas.append("\n" + "=" * 90)
    linhas.append("📄 ARQUIVOS SOLTOS NA RAIZ DO PROJETO (não estão em pasta)")
    linhas.append("-" * 90)
    raiz_arquivos = estrutura.get(".", [])
    if raiz_arquivos:
        for arq in sorted(raiz_arquivos, key=lambda x: x["nome"]):
            tag = f" [{arq['classificacao']}]" if arq["classificacao"] != "-" else ""
            linhas.append(f"  {arq['nome']:50s} {arq['tamanho_str']:>15s}{tag}")
    else:
        linhas.append("  (nenhum arquivo solto na raiz)")

    # Seção especial: stubs vazios
    linhas.append("\n" + "=" * 90)
    linhas.append("⚠️  STUBS VAZIOS (0 bytes)")
    linhas.append("-" * 90)
    stubs_encontrados = []
    for pasta, arquivos in estrutura.items():
        for arq in arquivos:
            if arq["tamanho"] == 0:
                stubs_encontrados.append(f"  {pasta}/{arq['nome']}")

    if stubs_encontrados:
        for s in sorted(stubs_encontrados):
            linhas.append(s)
    else:
        linhas.append("  (nenhum stub vazio encontrado)")

    # Seção especial: monolitos
    linhas.append("\n" + "=" * 90)
    linhas.append("🐘 MONOLITOS PYTHON (>20KB)")
    linhas.append("-" * 90)
    monolitos = []
    for pasta, arquivos in estrutura.items():
        for arq in arquivos:
            if arq["tamanho"] > 20 * 1024 and arq["extensao"] == ".py":
                monolitos.append((f"{pasta}/{arq['nome']}", arq["tamanho_str"]))

    if monolitos:
        for m, t in sorted(monolitos):
            linhas.append(f"  {m:70s} {t:>15s}")
    else:
        linhas.append("  (nenhum monolito encontrado)")

    # Seção especial: possíveis serviços legados
    linhas.append("\n" + "=" * 90)
    linhas.append("🔍 PASTAS COM NOME DE SERVIÇO/MÓDULO (para análise de reaproveitamento)")
    linhas.append("-" * 90)
    pastas_servico = [
        "api", "app", "services", "modules", "pages", "frontend", 
        "relatorios", "insumos_comerciais", "utils", "models", "schemas"
    ]
    for nome in sorted(pastas_servico):
        caminho = RAIZ / nome
        if caminho.exists() and caminho.is_dir():
            qtd = sum(1 for _ in caminho.rglob("*.py") if not deve_excluir(_))
            linhas.append(f"  {nome:30s} → {qtd:4d} arquivos .py")

    linhas.append("\n" + "=" * 90)
    linhas.append("FIM DO RELATÓRIO")
    linhas.append("=" * 90)

    # Salvar
    texto = "\n".join(linhas)
    OUTPUT.write_text(texto, encoding="utf-8")
    print(f"✅ Relatório salvo em: {OUTPUT}")
    print(f"   Total de linhas: {len(linhas)}")
    print(f"   Abra o arquivo para visualizar a estrutura completa.")


if __name__ == "__main__":
    main()
