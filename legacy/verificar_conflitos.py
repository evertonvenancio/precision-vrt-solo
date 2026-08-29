import sys
import os

logging.info("=" * 60)
logging.info("VERIFICACAO DE CONFLITOS DE MODULO")
logging.info("=" * 60)

# Mostrar todos os caminhos onde Python busca modulos
logging.info("\n[1] sys.path (ordem de busca):")
for i, p in enumerate(sys.path):
    marker = " <-- PROJETO" if "precision_vrt" in p.lower() else ""
    exists = "OK" if os.path.exists(p) else "NAO EXISTE"
    logging.info(f"    [{i}] [{exists}] {p}{marker}")

# Verificar se existe db_schema em qualquer lugar do path
logging.info("\n[2] Buscando 'db_schema' em todo sys.path...")
for p in sys.path:
    if not os.path.isdir(p):
        continue
    candidate = os.path.join(p, "db_schema.py")
    if os.path.exists(candidate):
        size = os.path.getsize(candidate)
        mtime = os.path.getmtime(candidate)
        logging.info(f"    ENCONTRADO: {candidate}")
        logging.info(f"              Tamanho: {size} bytes, Modificado: {mtime}")

# Verificar se existe db_schema como pacote (pasta)
logging.info("\n[3] Buscando pacote 'db_schema' em todo sys.path...")
for p in sys.path:
    if not os.path.isdir(p):
        continue
    candidate = os.path.join(p, "db_schema")
    if os.path.isdir(candidate):
        init = os.path.join(candidate, "__init__.py")
        has_init = os.path.exists(init)
        logging.info(f"    PACOTE: {candidate} (tem __init__.py: {has_init})")

# Verificar PYTHONPATH
logging.info(f"\n[4] PYTHONPATH: {os.environ.get('PYTHONPATH', 'NAO DEFINIDO')}")

# Verificar se ha .pth files problematicos
logging.info("\n[5] Arquivos .pth no site-packages...")
import site
for p in site.getsitepackages():
    if os.path.exists(p):
        pth_files = [f for f in os.listdir(p) if f.endswith('.pth')]
        for f in pth_files:
            content = open(os.path.join(p, f)).read().strip()
            if 'precision_vrt' in content.lower():
                logging.info(f"    ALERTA: {f} -> {content}")

