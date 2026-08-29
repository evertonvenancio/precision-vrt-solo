import sys

logging.info("=" * 70)
logging.info("DIAGNOSTICO NO CONTEXTO DO app.py")
logging.info("=" * 70)

# Passo 1: Estado ANTES do sys.path.insert
logging.info("\n[1] sys.path ANTES do insert:")
for i, p in enumerate(sys.path[:3]):
    logging.info(f"    [{i}] {p}")

# Passo 2: Inserir path (igual ao app.py)
sys.path.insert(0, r"C:\precision_vrt_solo")
logging.info("\n[2] sys.path DEPOIS do insert:")
for i, p in enumerate(sys.path[:3]):
    logging.info(f"    [{i}] {p}")

# Passo 3: Verificar se db_schema ja foi importado (cache)
logging.info("\n[3] Modulos ja carregados:")
if 'db_schema' in sys.modules:
    logging.info("    ALERTA: db_schema JA ESTA em sys.modules!")
    logging.info(f"    Origem: {sys.modules['db_schema'].__file__}")
    logging.info(f"    Atributos: {[a for a in dir(sys.modules['db_schema']) if not a.startswith('_')]}")
else:
    logging.info("    db_schema ainda nao foi importado (OK)")

# Passo 4: Tentar importar IGUAL ao app.py
logging.info("\n[4] Tentando: from db_schema import init_db, get_connection, check_integrity")
try:
    from db_schema import init_db, get_connection, check_integrity
    logging.info("    ✓ SUCESSO!")
    import db_schema
    logging.info(f"    Arquivo: {db_schema.__file__}")
except ImportError as e:
    logging.info(f"    ✗ FALHA: {e}")
    
    # Tentar importar o modulo inteiro
    logging.info("\n[4.1] Tentando import db_schema...")
    try:
        import db_schema
        logging.info("    ✓ Modulo importado!")
        logging.info(f"    Arquivo: {db_schema.__file__}")
        logging.info(f"    Atributos: {[a for a in dir(db_schema) if not a.startswith('_')]}")
        if hasattr(db_schema, 'check_integrity'):
            logging.info("    ✓ check_integrity EXISTE no modulo!")
        else:
            logging.info("    ✗ check_integrity NAO EXISTE no modulo!")
    except Exception as e2:
        logging.info(f"    ✗ Tambem falhou: {e2}")
        
        # Tentar import com importlib
        logging.info("\n[4.2] Tentando com importlib...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("db_schema", r"C:\precision_vrt_solo\db_schema.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            logging.info("    ✓ Carregado via importlib!")
            logging.info(f"    Atributos: {[a for a in dir(mod) if not a.startswith('_')]}")
        else:
            logging.info("    ✗ Nao conseguiu criar spec")

