import sys
import ast
import os

logging.info("=" * 60)
logging.info("DIAGNOSTICO PYTHON - db_schema.py")
logging.info("=" * 60)

path = r"C:\precision_vrt_solo\db_schema.py"
logging.info(f"\n[1] Arquivo existe: {os.path.exists(path)}")
logging.info(f"    Tamanho: {os.path.getsize(path)} bytes")

# Tentar parsear como AST
logging.info("\n[2] Tentando parsear com ast.parse...")
with open(path, 'rb') as f:
    source_bytes = f.read()

# Detectar encoding
logging.info(f"\n[3] Primeiros bytes: {source_bytes[:10]}")

# Tentar UTF-8
try:
    source = source_bytes.decode('utf-8')
    logging.info("    Decodificado como UTF-8: OK")
except UnicodeDecodeError as e:
    logging.info(f"    ERRO UTF-8: {e}")
    try:
        source = source_bytes.decode('latin1')
        logging.info("    Decodificado como Latin1: OK (CUIDADO!)")
    except:
        source = source_bytes.decode('cp1252')
        logging.info("    Decodificado como CP1252: OK (CUIDADO!)")

# Parse AST
try:
    tree = ast.parse(source)
    logging.info("\n[4] AST parse: OK")
    
    # Listar todas as funcoes e classes
    funcoes = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    logging.info(f"\n[5] Funcoes encontradas: {funcoes}")
    logging.info(f"    Classes encontradas: {classes}")
    
    if 'check_integrity' in funcoes:
        logging.info("\n    ✓ check_integrity ESTA na AST!")
    else:
        logging.info("\n    ✗ check_integrity NAO esta na AST!")
        logging.info("    Possivel causa: erro de sintaxe ANTES da funcao")
        
except SyntaxError as e:
    logging.info(f"\n[4] ERRO DE SINTAXE na linha {e.lineno}:")
    logging.info(f"    {e.text}")
    logging.info(f"    {' ' * (e.offset - 1)}^")
    logging.info(f"    {e.msg}")

# Tentar import normal
logging.info("\n[6] Tentando import via __import__...")
sys.path.insert(0, r"C:\precision_vrt_solo")
try:
    import db_schema
    logging.info("    ✓ Import OK!")
    logging.info(f"    Arquivo: {db_schema.__file__}")
    logging.info(f"    Atributos: {[a for a in dir(db_schema) if not a.startswith('_')]}")
    if hasattr(db_schema, 'check_integrity'):
        logging.info("    ✓ check_integrity disponivel!")
    else:
        logging.info("    ✗ check_integrity NAO disponivel!")
except Exception as e:
    logging.info(f"    ✗ Import falhou: {type(e).__name__}: {e}")

