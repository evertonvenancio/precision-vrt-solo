import sys
import pkgutil
import os

logging.info("=" * 70)
logging.info("BUSCA POR 'db_schema' EM TODOS OS PACOTES")
logging.info("=" * 70)

# Buscar em todos os modulos carregaveis
logging.info("\n[1] Buscando 'db_schema' em todos os pacotes...")
for importer, modname, ispkg in pkgutil.iter_modules():
    if 'db_schema' in modname:
        logging.info(f"    ENCONTRADO: {modname} (pacote: {ispkg})")
        try:
            loader = importer.find_module(modname)
            logging.info(f"      Loader: {loader}")
        except Exception as e:
            logging.info(f"      Erro: {e}")

# Verificar tambem no path completo
logging.info("\n[2] Verificando arquivos db_schema.py no sys.path...")
for p in sys.path:
    if os.path.isdir(p):
        candidate = os.path.join(p, "db_schema.py")
        if os.path.exists(candidate):
            logging.info(f"    ENCONTRADO: {candidate}")
            logging.info(f"      Tamanho: {os.path.getsize(candidate)} bytes")
            
            # Verificar se tem check_integrity
            with open(candidate, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                if 'def check_integrity' in content:
                    logging.info("      ✓ Tem check_integrity")
                else:
                    logging.info("      ✗ NAO tem check_integrity")

# Verificar se ha __pycache__/db_schema.* em algum lugar
logging.info("\n[3] Buscando db_schema.pyc em __pycache__...")
for root, dirs, files in os.walk(os.path.expanduser('~')):
    if '__pycache__' in root and any('db_schema' in f for f in files):
        for f in files:
            if 'db_schema' in f:
                logging.info(f"    ENCONTRADO: {os.path.join(root, f)}")
    # Limitar profundidade para nao demorar muito
    if root.count(os.sep) > 8:
        dirs[:] = []

