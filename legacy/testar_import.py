# Script de validacao - check_integrity
# Executar: python C:\precision_vrt_solo\testar_import.py

import sys
import os

logging.info("=" * 60)
logging.info("TESTE DE IMPORTACAO: check_integrity")
logging.info("=" * 60)

# Mostrar sys.path
logging.info("\n[1] PYTHONPATH atual:")
for i, p in enumerate(sys.path):
    logging.info(f"  [{i}] {p}")

# Verificar se o diretorio do projeto esta no path
projeto_dir = r"C:\precision_vrt_solo"
if projeto_dir not in sys.path:
    logging.info(f"\n[!] ALERTA: {projeto_dir} nao esta no sys.path!")
    sys.path.insert(0, projeto_dir)
    logging.info("  -> Inserido na posicao 0")

# Tentar importar
logging.info("\n[2] Tentando importar check_integrity...")
try:
    from db_schema import init_db, get_connection, check_integrity
    logging.info("  ✓ SUCESSO: check_integrity importado!")
    logging.info(f"  ✓ Origem: {check_integrity.__module__}")
    logging.info(f"  ✓ Arquivo: {check_integrity.__code__.co_filename}")
except ImportError as e:
    logging.info(f"  ✗ FALHA: {e}")
    logging.info("\n[2.1] Verificando o que existe em db_schema...")
    try:
        import db_schema
        logging.info(f"  -> db_schema carregado de: {db_schema.__file__}")
        logging.info(f"  -> Atributos disponiveis: {[a for a in dir(db_schema) if not a.startswith('_')]}")
    except Exception as e2:
        logging.info(f"  -> ERRO ao carregar db_schema: {e2}")
    sys.exit(1)

# Verificar se e o arquivo correto
logging.info("\n[3] Validacao do arquivo-fonte:")
import db_schema
expected_file = os.path.join(projeto_dir, "db_schema.py")
actual_file = os.path.abspath(db_schema.__file__)

logging.info(f"  Esperado: {expected_file}")
logging.info(f"  Atual:    {actual_file}")

if expected_file.lower() == actual_file.lower():
    logging.info("  ✓ ARQUIVO CORRETO!")
else:
    logging.info("  ✗ ARQUIVO DIFERENTE! Possivel conflito de importacao.")

# Testar a funcao
logging.info("\n[4] Testando check_integrity()...")
try:
    ok, msg, erros = check_integrity()
    logging.info(f"  Resultado: {ok}")
    logging.info(f"  Mensagem: {msg}")
    if erros:
        logging.info(f"  Erros: {erros}")
except Exception as e:
    logging.info(f"  ✗ Erro na execucao: {e}")

logging.info("\n" + "=" * 60)
logging.info("TESTE CONCLUIDO")
logging.info("=" * 60)

