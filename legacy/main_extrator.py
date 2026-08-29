import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import Base, engine, get_db
from core.seguranca import hash_senha, carregar_permissoes_usuario, verificar_senha_popup, registrar_auditoria
from models.usuario import Usuario
from models.prescricao import Prescricao
from models.financeiro import Orcamento

# Importacao dos Routers da API
from api.v1.endpoints import (
    ativos, bulk_blend, clima, compactacao, comunicacao, conhecimento, 
    extrator, fiscal, laudos_export, vendas
)

app = FastAPI(title="Precision VRT Solo API", version="1.0.0")

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Inclusao dos Routers da API (Backend)
app.include_router(ativos.router, prefix="/api/v1")
app.include_router(bulk_blend.router, prefix="/api/v1")
app.include_router(clima.router, prefix="/api/v1")
app.include_router(compactacao.router, prefix="/api/v1")
app.include_router(comunicacao.router, prefix="/api/v1")
app.include_router(conhecimento.router, prefix="/api/v1")
app.include_router(extrator.router, prefix="/api/v1")
app.include_router(fiscal.router, prefix="/api/v1")
app.include_router(laudos_export.router, prefix="/api/v1")
app.include_router(vendas.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    logging.info("Iniciando criacao de tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)

    from db.database import SessionLocal
    db = SessionLocal()
    if not db.query(Usuario).filter(Usuario.login == "admin").first():
        novo_admin = Usuario(id=str(uuid.uuid4()), login="admin", senha_hash=hash_senha("admin123"))
        db.add(novo_admin)
        db.commit()
        logging.info("Usuario admin criado.")
    db.close()
    logging.info("Tabelas verificadas/criadas com sucesso.")

def get_permissoes(db: Session) -> dict:
    user = db.query(Usuario).filter(Usuario.login == "admin").first()
    if user:
        return carregar_permissoes_usuario(user.id)
    return {}

# =========================================================================
# ROTAS DO FRONTEND (Telas do Sistema)
# =========================================================================

@app.get("/")
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    area_total = db.query(func.sum(Cliente.area_total_hectares)).filter(Cliente.ativo == True).scalar() or 0.0
    area_tratada = db.query(func.sum(Prescricao.area_hectares)).scalar() or 0.0
    oportunidade = float(area_total) - float(area_tratada)
    total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()
    hoje = datetime.now().strftime("-%m-%d")
    aniversariantes = db.query(Cliente).filter(Cliente.data_nascimento.like(f"%{hoje}"), Cliente.ativo == True).all()
    context = {
        "request": request, "area_total": float(area_total), "area_tratada": float(area_tratada),
        "oportunidade": oportunidade, "total_clientes": total_clientes,
        "aniversariantes": aniversariantes, "permissoes": get_permissoes(db)
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def processar_login(request: Request, usuario: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.login == usuario).first()
    if not user or user.senha_hash != hash_senha(senha):
        raise HTTPException(status_code=400, detail="Usuario ou senha invalidos")
    return RedirectResponse(url="/", status_code=303)

# --- CRM & COMERCIAL ---
@app.get("/financeiro")
async def financeiro_page(request: Request, db: Session = Depends(get_db)):
    orcamentos = db.query(Orcamento).order_by(Orcamento.criado_em.desc()).all()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"orcamentos": orcamentos, "permissoes": get_permissoes(db)})

@app.get("/financeiro/novo-orcamento")
async def novo_orcamento_page(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.ativo == True).order_by(Cliente.nome).all()
    return templates.TemplateResponse(request=request, name="novo_orcamento.html", context={"clientes": clientes, "permissoes": get_permissoes(db)})

@app.post("/financeiro/novo-orcamento")
async def salvar_orcamento(request: Request, db: Session = Depends(get_db)):
    return JSONResponse(status_code=200, content={"success": True, "redirect": "/financeiro"})

# --- CADASTROS GERAIS ---
@app.get("/clientes")
async def clientes_page(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.ativo == True).order_by(Cliente.nome).all()
    return templates.TemplateResponse(request=request, name="clientes.html", context={"clientes": clientes, "permissoes": get_permissoes(db)})

@app.get("/clientes/novo")
async def novo_cliente_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={"cliente": None, "permissoes": get_permissoes(db)})

@app.post("/novo-cliente")
async def salvar_cliente(request: Request, nome: str = Form(...), cpf_cnpj: str = Form(...), telefone: str = Form(...), email: str = Form(...), cidade: str = Form(...), estado: str = Form(...), area_total_hectares: float = Form(0), db: Session = Depends(get_db)):
    if db.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj).first():
        return JSONResponse(status_code=400, content={"detail": "CPF/CNPJ ja cadastrado no sistema."})
    novo = Cliente(nome=nome, cpf_cnpj=cpf_cnpj, telefone=telefone, email=email, cidade=cidade, estado=estado, area_total_hectares=area_total_hectares)
    db.add(novo)
    db.commit()
    return JSONResponse(status_code=200, content={"success": True, "redirect": "/clientes"})

@app.get("/clientes/{cliente_id}/editar")
async def editar_cliente_page(cliente_id: str, request: Request, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={"cliente": cliente, "permissoes": get_permissoes(db)})

@app.post("/clientes/{cliente_id}/editar")
async def processar_edicao_cliente(cliente_id: str, request: Request, nome: str = Form(...), cpf_cnpj: str = Form(...), telefone: str = Form(...), email: str = Form(...), cidade: str = Form(...), estado: str = Form(...), area_total_hectares: float = Form(0), db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        return JSONResponse(status_code=404, content={"detail": "Cliente nao encontrado."})
    if db.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj, Cliente.id != cliente_id).first():
        return JSONResponse(status_code=400, content={"detail": "CPF/CNPJ ja cadastrado para outro cliente."})
    cliente.nome = nome
    cliente.cpf_cnpj = cpf_cnpj
    cliente.telefone = telefone
    cliente.email = email
    cliente.cidade = cidade
    cliente.estado = estado
    cliente.area_total_hectares = area_total_hectares
    db.commit()
    return JSONResponse(status_code=200, content={"success": True, "redirect": "/clientes"})

@app.post("/clientes/{cliente_id}/excluir")
async def excluir_cliente(cliente_id: str, senha: str = Form(...), justificativa: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.login == "admin").first()
    if not user:
        return JSONResponse(status_code=403, content={"detail": "Usuario nao encontrado."})

    if not verificar_senha_popup(user.id, senha):
        return JSONResponse(status_code=403, content={"detail": "Senha incorreta."})

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        return JSONResponse(status_code=404, content={"detail": "Cliente nao encontrado."})

    cliente.ativo = False
    db.commit()
    registrar_auditoria(user.id, "EXCLUSAO_CLIENTE", f"Cliente {cliente.nome} (ID: {cliente_id}) excluido.", justificativa)
    return JSONResponse(status_code=200, content={"success": True, "redirect": "/clientes"})

@app.get("/cadastros/precos")
async def tabela_precos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="tabela_precos.html", context={"permissoes": get_permissoes(db)})

# --- MANEJO & PRESCRICAO ---
@app.get("/prescricao")
async def prescricao_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="prescricao.html", context={"permissoes": get_permissoes(db)})

@app.get("/prescricao/nova")
async def prescricao_nova_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="prescricao_nova.html", context={"permissoes": get_permissoes(db)})

@app.get("/compactacao")
async def compactacao_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="compactacao.html", context={"permissoes": get_permissoes(db)})

@app.get("/compactacao/nova")
async def compactacao_nova_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="compactacao_nova.html", context={"permissoes": get_permissoes(db)})

@app.get("/extrator")
async def extrator_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="extrator.html", context={"permissoes": get_permissoes(db)})

@app.get("/extrator/novo-ponto")
async def novo_ponto_extrator_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="novo_ponto_extrator.html", context={"permissoes": get_permissoes(db)})

# --- INTELIGENCIA AGRONOMICA ---
@app.get("/clima")
async def clima_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="clima.html", context={"permissoes": get_permissoes(db)})

@app.get("/cruzamento")
async def cruzamento_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="cruzamento.html", context={"permissoes": get_permissoes(db)})

# --- GESTAO FINANCEIRA ---
@app.get("/financeiro/caixa")
async def caixa_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"permissoes": get_permissoes(db)})

@app.get("/ativos")
async def ativos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="ativos.html", context={"permissoes": get_permissoes(db)})

@app.get("/ativos/novo")
async def novo_ativo_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="novo_ativo.html", context={"permissoes": get_permissoes(db)})

# --- GENTE & GESTAO ---
@app.get("/equipe")
async def equipe_page(request: Request, db: Session = Depends(get_db)):
    funcionarios = db.query(Funcionario).order_by(Funcionario.nome_completo).all()
    return templates.TemplateResponse(request=request, name="equipe.html", context={"funcionarios": funcionarios, "permissoes": get_permissoes(db)})

@app.get("/equipe/novo-funcionario")
async def novo_funcionario_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="novo_funcionario.html", context={"permissoes": get_permissoes(db)})

# --- CONFIGURACOES ---
@app.get("/configuracoes")
async def configuracoes_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="configuracoes.html", context={"permissoes": get_permissoes(db)})

from fastapi.responses import HTMLResponse

@app.get("/nematoides")
async def nematoides_page(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse("<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Nematoides</h1><p class='text-gray-500 dark:text-gray-400'>Modulo em construcao. Aguarde as proximas atualizacoes.</p></div>")

@app.get("/base-tecnica/culturas")
async def culturas_page(request: Request, db: Session = Depends(get_db)):
    try:
        return templates.TemplateResponse(request=request, name="base_tecnica.html", context={"titulo_pagina": "Culturas", "permissoes": get_permissoes(db)})
    except:
        return HTMLResponse("<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Culturas</h1><p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>")

@app.get("/base-tecnica/metodologias")
async def metodologias_page(request: Request, db: Session = Depends(get_db)):
    try:
        return templates.TemplateResponse(request=request, name="base_tecnica.html", context={"titulo_pagina": "Metodologias e Formulas", "permissoes": get_permissoes(db)})
    except:
        return HTMLResponse("<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Metodologias e Formulas</h1><p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>")

@app.get("/base-tecnica/bibliografia")
async def bibliografia_page(request: Request, db: Session = Depends(get_db)):
    try:
        return templates.TemplateResponse(request=request, name="base_tecnica.html", context={"titulo_pagina": "Bibliografia e Legislacao", "permissoes": get_permissoes(db)})
    except:
        return HTMLResponse("<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Bibliografia e Legislacao</h1><p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>")

@app.get("/equipe/permissoes")
async def permissoes_page(request: Request, db: Session = Depends(get_db)):
    return HTMLResponse("<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Permissoes de Acesso</h1><p class='text-gray-500 dark:text-gray-400'>Modulo em construcao. Aqui o gestor configurara os acessos.</p></div>")

@app.get("/bulk_blend")
async def bulk_blend_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="bulk_blend.html", context={"permissoes": get_permissoes(db)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
