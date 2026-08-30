#!/usr/bin/env python3
"""
Script para migrar todas as rotas web de HTTPBearer para cookie-based auth.
"""
import re
from pathlib import Path

web_dir = Path("app/web")
files_to_fix = [
    "agenda.py", "ativos.py", "auditoria.py", "bulk_blend.py", "cadastros.py",
    "caixa.py", "clima.py", "compactacao.py", "comunicacao.py", "configuracoes.py",
    "conhecimento.py", "cruzamento.py", "empresas.py", "equipe.py", "extrator.py",
    "fertirrigacao.py", "financeiro.py", "fornecedores.py", "monitoramento.py",
    "nematoides.py", "patrimonio.py", "permissoes.py", "prescricao.py",
    "produtos.py", "relatorios.py", "sensoriamento.py", "tabela_precos.py",
    "upload.py", "usuarios.py"
]

def fix_file(filepath):
    content = filepath.read_text(encoding='utf-8')
    original = content

    # 1. Remover imports de HTTPBearer/HTTPAuthorizationCredentials
    content = re.sub(
        r"from fastapi\.security import HTTPAuthorizationCredentials, HTTPBearer\n",
        "",
        content
    )
    content = re.sub(
        r"from fastapi\.security import HTTPBearer, HTTPAuthorizationCredentials\n",
        "",
        content
    )
    content = re.sub(
        r"from fastapi\.security import HTTPBearer\n",
        "",
        content
    )
    content = re.sub(
        r"from core\.authorization\.dependencies import require_permission, get_user_permissions\n",
        "",
        content
    )
    content = re.sub(
        r"from core\.authorization\.dependencies import require_permission\n",
        "",
        content
    )

    # 2. Remover security = HTTPBearer()
    content = re.sub(r"security = HTTPBearer\(\)\n", "", content)

    # 3. Adicionar import da nova dependência se não existir
    if "from app.web.auth_dependencies import require_permission_web" not in content:
        # Inserir após "router = APIRouter()" ou antes do primeiro @router
        if "router = APIRouter()" in content:
            content = content.replace(
                "router = APIRouter()",
                "router = APIRouter()\nfrom app.web.auth_dependencies import require_permission_web  # autenticação via cookie"
            )

    # 4. Substituir usuario: dict = Depends(require_permission("...")) por user: dict = Depends(require_permission_web("..."))
    content = re.sub(
        r'usuario: dict = Depends\(require_permission\("([^"]+)"\)\)',
        r'user: dict = Depends(require_permission_web("\1"))',
        content
    )

    # 5. Substituir referencias a "usuario" por "user" no context
    content = re.sub(
        r'"usuario": usuario',
        r'"usuario": user',
        content
    )
    content = re.sub(
        r'"permissoes": usuario\.get\("permissions", \[\]\)',
        r'"permissoes": user.get("permissions", [])',
        content
    )

    # 6. Substituir service = Service(db, usuario) por service = Service(db, user)
    content = re.sub(
        r'service = (\w+)\(db, usuario\)',
        r'service = \1(db, user)',
        content
    )

    # 7. Substituir usuario["id"] por user["id"]
    content = re.sub(r'usuario\["id"\]', r'user["id"]', content)

    # 8. Corrigir imports de SessionLocal se não estiver usando get_db
    if "from db.database import SessionLocal" in content and "from db.database import get_db" not in content:
        content = content.replace(
            "from db.database import SessionLocal",
            "from db.database import SessionLocal, get_db"
        )

    # 9. Corrigir db = SessionLocal() -> db: Session = Depends(get_db) se houver
    # Mas isso é mais complexo, deixo como está por enquanto

    if content != original:
        filepath.write_text(content, encoding='utf-8')
        print(f"[OK] Fixed: {filepath.name}")
        return True
    else:
        print(f"[--] No changes: {filepath.name}")
        return False

print("[FIX] Iniciando migração das rotas web...")
for fname in files_to_fix:
    f = web_dir / fname
    if f.exists():
        fix_file(f)
    else:
        print(f"[XX] Not found: {fname}")

print("\n[OK] Migração concluída!")