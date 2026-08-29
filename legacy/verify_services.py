import sys
sys.path.insert(0, '.')

from app.services.orcamentos_service import OrcamentosService
print('[OK] OrcamentosService importado')

from app.services.vendas_service import VendasService
print('[OK] VendasService importado')

from app.services.auth_service import AuthService
print('[OK] AuthService importado')

from core.authorization.dependencies import PERMISSION_MAP, SIDEBAR_MENU_STRUCTURE
print(f'[OK] PERMISSION_MAP: {len(PERMISSION_MAP)} entries')
print(f'[OK] SIDEBAR_MENU_STRUCTURE: {len(SIDEBAR_MENU_STRUCTURE)} groups')
for g in SIDEBAR_MENU_STRUCTURE:
    print(f'    - {g["titulo"]}: {len(g["itens"])} itens')
