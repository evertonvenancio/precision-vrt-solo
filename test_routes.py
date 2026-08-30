"""
Script de teste: sobe o servidor, faz login e testa todas as rotas web.
"""
import subprocess, time, sys, json, requests

# 1. Subir servidor
print("[1] Iniciando servidor...")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(4)

# 2. Health check
try:
    r = requests.get("http://127.0.0.1:8000/health", timeout=5)
    print(f"[2] Health: {r.status_code} {r.text[:80]}")
except Exception as e:
    print(f"[2] FAIL health: {e}")
    proc.kill()
    sys.exit(1)

# 3. Login
try:
    r = requests.post("http://127.0.0.1:8000/web/auth/login",
                       data={"usuario": "admin", "senha": "admin123"},
                       allow_redirects=False, timeout=5)
    print(f"[3] Login: {r.status_code}")
    cookies = r.cookies.get_dict()
    print(f"    Cookies: {list(cookies.keys())}")
except Exception as e:
    print(f"[3] FAIL login: {e}")
    proc.kill()
    sys.exit(1)

if not cookies.get("access_token"):
    print("    ERRO: access_token não definido!")
    proc.kill()
    sys.exit(1)

session = requests.Session()
session.cookies.update(cookies)

# 4. Testar rotas web
routes = [
    "/web/dashboard/",
    "/web/clientes/",
    "/web/orcamentos/",
    "/web/vendas/",
    "/web/prescricao/",
    "/web/compactacao/",
    "/web/nematoides/",
    "/web/fertirrigacao/",
    "/web/sensoriamento/",
    "/web/monitoramento/",
    "/web/financeiro/",
    "/web/ativos/",
    "/web/comunicacao/",
    "/web/auditoria/",
    "/web/bulk_blend/",
    "/web/caixa/",
    "/web/clima/",
    "/web/conhecimento/",
    "/web/cruzamento/",
    "/web/equipes/",
    "/web/extrator/",
    "/web/permissoes/",
    "/web/tabela_precos/",
    "/web/upload/",
    "/web/configuracoes/",
    "/web/relatorios/",
]

print(f"\n[4] Testando {len(routes)} rotas web...\n")

ok = 0
fail = 0
for route in routes:
    try:
        r = session.get(f"http://127.0.0.1:8000{route}", allow_redirects=False, timeout=10)
        status = r.status_code
        has_html = "<html" in r.text.lower()[:500] or "<!DOCTYPE" in r.text[:500]
        detail = r.text[:80].replace("\n", " ") if not has_html else f"HTML ({len(r.text)} bytes)"

        if status == 200 and has_html:
            print(f"  ✅ {route} -> {status} {detail}")
            ok += 1
        elif status == 307 or status == 303:
            print(f"  ↪️ {route} -> {status} redirect to {r.headers.get('location', '?')}")
            # Follow redirect
            r2 = session.get(f"http://127.0.0.1:8000{r.headers.get('location', route)}", allow_redirects=True, timeout=10)
            has_html2 = "<html" in r2.text.lower()[:500] or "<!DOCTYPE" in r2.text[:500]
            if r2.status_code == 200 and has_html2:
                print(f"     ✅ Redirect OK ({len(r2.text)} bytes)")
                ok += 1
            else:
                print(f"     ❌ Redirect FAIL: {r2.status_code} {r2.text[:100]}")
                fail += 1
        elif status == 401:
            print(f"  ❌ {route} -> 401 UNAUTHORIZED: {r.text[:120]}")
            fail += 1
        elif status == 403:
            print(f"  ⚠️ {route} -> 403 FORBIDDEN (sem permissão): {r.text[:120]}")
            ok += 1  # 403 é válido
        elif status == 404:
            print(f"  ❌ {route} -> 404: rota não encontrada")
            fail += 1
        else:
            print(f"  ❌ {route} -> {status}: {detail}")
            fail += 1
    except Exception as e:
        print(f"  💥 {route} -> ERRO: {e}")
        fail += 1

print(f"\n{'='*50}")
print(f"RESULTADO: {ok} OK / {fail} FALHOU / {len(routes)} total")
print(f"{'='*50}")

# Cleanup
proc.terminate()
proc.wait(timeout=5)
print("\n[OK] Servidor encerrado")
