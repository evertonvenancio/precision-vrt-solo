import sys
sys.path.insert(0, r'C:\precision_vrt_solo')
from db_schema import init_db, check_integrity
init_db()
ok, msg, erros = check_integrity()
logging.info("[CHECK] " + msg)
if erros:
    for e in erros:
        logging.info("  ERRO: " + str(e))
else:
    logging.info("[CHECK] Sistema OK - Sem erros de integridade")

