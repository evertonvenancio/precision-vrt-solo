import logging
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import Base, engine, get_db
from core.seguranca import hash_senha, carregar_permissoes_usuario, verificar_senha_popup, registrar_auditoria
from models.usuario import Usuario
from models.prescricao import Prescricao
from models.financeiro import Orcamento
from services.geo_parser_service import GeoParserService

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
    """Wizard de 3 etapas: Configuracao, Upload, Processamento."""
    clientes = db.query(Cliente).filter(Cliente.ativo == True).order_by(Cliente.nome).all()

    # Mock de culturas e formulas (substituir por imports reais quando existirem)
    culturas = [
        ("milho", "Milho"),
        ("soja", "Soja"),
        ("trigo", "Trigo"),
        ("arroz", "Arroz"),
        ("feijao", "Feijao"),
        ("algodao", "Algodao"),
        ("cafe_arabica", "Cafe Arabica"),
        ("cafe_conilon", "Cafe Conilon"),
        ("cana", "Cana-de-acucar"),
    ]

    formulas = [
        ("interp_kmeans", "Interpolacao + K-Means"),
        ("interp_kriging", "Kriging + K-Means"),
        ("idw_cluster", "IDW + Clustering"),
        ("natural_breaks", "Quebras Naturais (Jenks)"),
    ]

    return templates.TemplateResponse(
        request=request,
        name="prescricao_nova.html",
        context={
            "request": request,
            "clientes": clientes,
            "culturas": culturas,
            "formulas": formulas,
            "permissoes": get_permissoes(db)
        }
    )

@app.post("/prescricao/processar")
async def prescricao_processar(
    request: Request,
    cliente_id: str = Form(...),
    talhao_nome: str = Form(...),
    cultura: str = Form(...),
    produtividade: float = Form(...),
    metodologia: str = Form(...),
    n_zonas: int = Form(3),
    limite_talhao: UploadFile = File(None),
    amostras_solo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Recebe dados do wizard e arquivos, processa interpolacao, zoneamento e prescricao."""
    try:
        import shutil
        import pathlib
        import pandas as pd

        # Importar modulos do core (presumindo que existem no projeto)
        from core.prescricao_vrt.interpolacao import InterpoladorSolo
        from core.prescricao_vrt.zoneamento import Zoneador
        from core.prescricao_vrt.prescricao import MotorPrescricao
        from core.prescricao_vrt.exportacao import Exportador

        input_dir = pathlib.Path("data/input")
        output_dir = pathlib.Path("data/output")
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        arquivos_salvos = {}
        limite_path = None
        amostras_path = None

        # Salvar arquivos no disco
        if limite_talhao and limite_talhao.filename:
            limite_path = input_dir / f"limite_{uuid.uuid4().hex}_{limite_talhao.filename}"
            with open(limite_path, "wb") as buffer:
                shutil.copyfileobj(limite_talhao.file, buffer)
            arquivos_salvos["limite"] = str(limite_path)

        if amostras_solo and amostras_solo.filename:
            amostras_path = input_dir / f"amostras_{uuid.uuid4().hex}_{amostras_solo.filename}"
            with open(amostras_path, "wb") as buffer:
                shutil.copyfileobj(amostras_solo.file, buffer)
            arquivos_salvos["amostras"] = str(amostras_path)

        # --- Parse universal dos arquivos ---
        # Parse amostras de solo a partir do arquivo salvo
        from fastapi import UploadFile

        # Criar UploadFile fake a partir do arquivo salvo para reutilizar o parser
        with open(amostras_path, "rb") as f_amostras:
            amostras_content = f_amostras.read()

        # Usar o parser diretamente com o conteudo em bytes
        import io
        amostras_fileobj = io.BytesIO(amostras_content)
        amostras_upload = UploadFile(filename=amostras_path.name, file=amostras_fileobj)
        resultado_amostras = GeoParserService.parse_upload(amostras_upload)
        amostras_upload.file.close()

        # Extrair DataFrame de pontos com atributos quimicos
        if resultado_amostras["tipo"] in ("pontos", "ambos"):
            df_amostras = GeoParserService.gdf_para_dataframe(resultado_amostras["gdf_pontos"])
        else:
            return JSONResponse(
                status_code=400,
                content={"detail": "Arquivo de amostras nao contem pontos de amostragem."}
            )

        # Verificar colunas obrigatorias de coordenadas
        if 'latitude' not in df_amostras.columns or 'longitude' not in df_amostras.columns:
            return JSONResponse(
                status_code=400,
                content={"detail": "Arquivo de amostras nao possui colunas de latitude e longitude."}
            )

        # Mapeamento flexivel de colunas quimicas (suporta variacoes de nomenclatura)
        mapa_atributos = {
            "ph": ["ph"],
            "p_mg_dm3": ["p_mg_dm3", "p", "fosforo", "p_mg_kg", "p_ppm"],
            "k_mg_dm3": ["k_mg_dm3", "k", "potassio", "k_mg_kg", "k_ppm"],
            "ca_mmolc": ["ca_mmolc", "ca", "calcio", "ca_cmolc"],
            "mg_mmolc": ["mg_mmolc", "mg", "magnesio", "mg_cmolc"],
            "al_mmolc": ["al_mmolc", "al", "aluminio", "al_cmolc"],
            "h_al": ["h_al", "hal", "h+al", "h_al_mmolc"],
            "sb": ["sb", "soma_bases", "soma_de_bases"],
            "ctc": ["ctc", "capacidade_troca", "t"],
            "v_percent": ["v_percent", "v_", "v%", "saturacao_bases", "saturacao"],
            "mo_percent": ["mo_percent", "mo_", "mo%", "materia_organica", "mat_org"],
            "argila": ["argila", "argila_percent", "argila_", "clay"],
            "silte": ["silte", "silte_percent", "silte_", "silt"],
            "areia": ["areia", "areia_percent", "areia_", "sand"],
            "b_mg_dm3": ["b_mg_dm3", "b", "boro", "b_ppm"],
            "cu_mg_dm3": ["cu_mg_dm3", "cu", "cobre", "cu_ppm"],
            "fe_mg_dm3": ["fe_mg_dm3", "fe", "ferro", "fe_ppm"],
            "mn_mg_dm3": ["mn_mg_dm3", "mn", "manganes", "mn_ppm"],
            "zn_mg_dm3": ["zn_mg_dm3", "zn", "zinco", "zn_ppm"],
            "s_mg_dm3": ["s_mg_dm3", "s", "enxofre", "s_ppm"],
        }

        # Encontrar colunas reais no DataFrame
        atributos_presentes = []
        colunas_reais = set(df_amostras.columns)
        for padrao, aliases in mapa_atributos.items():
            for alias in aliases:
                if alias in colunas_reais:
                    atributos_presentes.append(padrao)
                    break

        # Preparar DataFrame: remover duplicatas e garantir tipos numericos
        df_amostras = df_amostras.loc[:, ~df_amostras.columns.duplicated()]
        df_amostras['latitude'] = pd.to_numeric(df_amostras['latitude'], errors='coerce')
        df_amostras['longitude'] = pd.to_numeric(df_amostras['longitude'], errors='coerce')
        df_amostras = df_amostras.dropna(subset=['latitude', 'longitude'])

        # Determinar atributos a interpolar (todas as colunas exceto coordenadas e metadados)
        atributos = [c for c in df_amostras.columns if c not in ['latitude', 'longitude', 'id', 'talhao', 'data', 'profundidade']]

        # Interpolar todos os atributos presentes
        interpolador = InterpoladorSolo()
        rasters_interpolados = interpolador.interpolar_talhao(
            df_amostras, x_col="longitude", y_col="latitude", atributos=atributos
        )

        # --- Processar limite do talhao ---
        talhao_geojson = None

        if limite_talhao and limite_talhao.filename and limite_path:
            with open(limite_path, "rb") as f_limite:
                limite_content = f_limite.read()
            limite_fileobj = io.BytesIO(limite_content)
            limite_upload = UploadFile(filename=limite_path.name, file=limite_fileobj)
            resultado_limite = GeoParserService.parse_upload(limite_upload)
            limite_upload.file.close()
            if resultado_limite["tipo"] in ("poligono", "ambos") and resultado_limite["gdf_poligono"] is not None:
                talhao_geojson = json.loads(resultado_limite["gdf_poligono"].to_json())
        elif resultado_amostras["tipo"] == "ambos" and resultado_amostras["gdf_poligono"] is not None:
            # Se nao enviou limite separado, mas amostras tem poligono, usar como limite
            talhao_geojson = json.loads(resultado_amostras["gdf_poligono"].to_json())

        # Zoneamento com K-Means sobre os rasters interpolados
        zoneador = Zoneador(n_zonas=n_zonas, metodologia=metodologia)
        raster_zonas = zoneador.executar(rasters_interpolados)

        # Calcular perfis (media de cada atributo por zona)
        perfis = zoneador.calcular_perfis(rasters_interpolados, raster_zonas)

        # Prescricao
        motor = MotorPrescricao(cultura=cultura, produtividade=produtividade)
        prescricoes = motor.executar(perfis)

        # Exportar raster de zonas para GeoJSON
        exportador = Exportador()
        geojson_zonas = exportador.raster_para_geojson(raster_zonas, perfis)

        # Buscar nome do cliente
        cliente_obj = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        cliente_nome = cliente_obj.nome if cliente_obj else "Cliente"

        # Salvar resultado temporario
        resultado = {
            "geojson": geojson_zonas,
            "perfis": perfis,
            "prescricoes": prescricoes,
            "n_zonas": n_zonas,
            "area_total_ha": zoneador.calcular_area_total(raster_zonas),
            "talhao_geojson": None,
            "cliente_nome": cliente_nome,
            "talhao_nome": talhao_nome
        }

        # Salvar GeoJSON do talhao se encontrado
        if talhao_geojson:
            resultado["talhao_geojson"] = talhao_geojson

        resultado_path = output_dir / "resultado_temp.json"
        with open(resultado_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        logging.info(
            "Prescricao processada: cliente=%s, talhao=%s, cultura=%s, metodologia=%s, zonas=%d, atributos=%s",
            cliente_id, talhao_nome, cultura, metodologia, n_zonas, atributos_presentes
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "redirect": "/prescricao/resultado",
                "message": "Dados recebidos com sucesso. Processando prescricao..."
            }
        )
    except Exception as exc:
        logging.exception("Erro ao processar prescricao: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": f"Erro ao processar prescricao: {str(exc)}"}
        )

@app.get("/prescricao/resultado")
async def prescricao_resultado_page(request: Request, db: Session = Depends(get_db)):
    """Tela de resultado da prescricao com mapa de zonas, perfis e prescricoes."""
    import pathlib

    output_dir = pathlib.Path("data/output")
    resultado_path = output_dir / "resultado_temp.json"

    # Valores padrao (fallback)
    geojson_zonas = {
        "type": "FeatureCollection",
        "features": []
    }
    perfis = {}
    prescricoes = {}
    n_zonas = 0
    area_total_ha = 0.0
    talhao_geojson = None

    # Ler resultado processado se existir
    if resultado_path.exists():
        try:
            with open(resultado_path, "r", encoding="utf-8") as f:
                resultado = json.load(f)
            geojson_zonas = resultado.get("geojson", geojson_zonas)
            perfis = resultado.get("perfis", perfis)
            prescricoes = resultado.get("prescricoes", prescricoes)
            n_zonas = resultado.get("n_zonas", n_zonas)
            area_total_ha = resultado.get("area_total_ha", area_total_ha)
            talhao_geojson = resultado.get("talhao_geojson", talhao_geojson)
        except Exception as exc:
            logging.warning("Erro ao ler resultado_temp.json: %s", exc)

    # Fallback: dados simulados se nao houver resultado processado
    if not geojson_zonas or not geojson_zonas.get("features"):
        geojson_zonas = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"zona": 1, "n": 15.2, "p": 12.8, "k": 8.5},
                    "geometry": {"type": "Polygon", "coordinates": [[[-47.95, -15.80], [-47.92, -15.80], [-47.92, -15.77], [-47.95, -15.77], [-47.95, -15.80]]]}
                },
                {
                    "type": "Feature",
                    "properties": {"zona": 2, "n": 22.1, "p": 18.4, "k": 14.2},
                    "geometry": {"type": "Polygon", "coordinates": [[[-47.92, -15.80], [-47.89, -15.80], [-47.89, -15.77], [-47.92, -15.77], [-47.92, -15.80]]]}
                },
                {
                    "type": "Feature",
                    "properties": {"zona": 3, "n": 8.5, "p": 6.2, "k": 4.1},
                    "geometry": {"type": "Polygon", "coordinates": [[[-47.95, -15.77], [-47.92, -15.77], [-47.92, -15.74], [-47.95, -15.74], [-47.95, -15.77]]]}
                },
                {
                    "type": "Feature",
                    "properties": {"zona": 4, "n": 18.7, "p": 15.3, "k": 11.8},
                    "geometry": {"type": "Polygon", "coordinates": [[[-47.92, -15.77], [-47.89, -15.77], [-47.89, -15.74], [-47.92, -15.74], [-47.92, -15.77]]]}
                }
            ]
        }
        n_zonas = 4
        area_total_ha = 150.0
        perfis = {
            "1": {"ph": 5.8, "p_mg_dm3": 12.5, "k_mg_dm3": 85.0, "ca_mmolc": 45.2, "mg_mmolc": 18.5, "al_mmolc": 8.2, "h_al": 32.0, "sb": 63.7, "ctc": 95.7, "v_percent": 66.5, "mo_percent": 2.8, "argila": 35.0, "silte": 25.0, "areia": 40.0, "b_mg_dm3": 0.45, "cu_mg_dm3": 1.2, "fe_mg_dm3": 45.0, "mn_mg_dm3": 12.5, "zn_mg_dm3": 2.8, "s_mg_dm3": 15.0},
            "2": {"ph": 6.2, "p_mg_dm3": 18.3, "k_mg_dm3": 120.0, "ca_mmolc": 52.0, "mg_mmolc": 22.0, "al_mmolc": 5.1, "h_al": 28.0, "sb": 74.0, "ctc": 102.0, "v_percent": 72.5, "mo_percent": 3.2, "argila": 42.0, "silte": 30.0, "areia": 28.0, "b_mg_dm3": 0.62, "cu_mg_dm3": 1.8, "fe_mg_dm3": 52.0, "mn_mg_dm3": 18.0, "zn_mg_dm3": 3.5, "s_mg_dm3": 22.0},
            "3": {"ph": 5.2, "p_mg_dm3": 8.1, "k_mg_dm3": 55.0, "ca_mmolc": 38.0, "mg_mmolc": 14.0, "al_mmolc": 12.5, "h_al": 45.0, "sb": 52.0, "ctc": 97.0, "v_percent": 53.6, "mo_percent": 2.1, "argila": 28.0, "silte": 20.0, "areia": 52.0, "b_mg_dm3": 0.32, "cu_mg_dm3": 0.8, "fe_mg_dm3": 38.0, "mn_mg_dm3": 8.5, "zn_mg_dm3": 1.9, "s_mg_dm3": 10.0},
            "4": {"ph": 5.9, "p_mg_dm3": 15.0, "k_mg_dm3": 95.0, "ca_mmolc": 48.0, "mg_mmolc": 20.0, "al_mmolc": 7.0, "h_al": 30.0, "sb": 68.0, "ctc": 98.0, "v_percent": 69.4, "mo_percent": 2.9, "argila": 38.0, "silte": 22.0, "areia": 40.0, "b_mg_dm3": 0.50, "cu_mg_dm3": 1.5, "fe_mg_dm3": 48.0, "mn_mg_dm3": 15.0, "zn_mg_dm3": 3.0, "s_mg_dm3": 18.0}
        }
        prescricoes = {
            "1": {"calcario": 2.5, "gesso": 0.0, "n": 120, "p2o5": 80, "k2o": 60},
            "2": {"calcario": 1.8, "gesso": 0.0, "n": 90, "p2o5": 60, "k2o": 45},
            "3": {"calcario": 3.2, "gesso": 0.5, "n": 150, "p2o5": 100, "k2o": 80},
            "4": {"calcario": 2.2, "gesso": 0.0, "n": 110, "p2o5": 75, "k2o": 55}
        }

    # Extrair cliente_nome e talhao_nome do resultado
    cliente_nome = resultado.get("cliente_nome", "Cliente") if 'resultado' in dir() else "Cliente"
    talhao_nome = resultado.get("talhao_nome", "Talhao") if 'resultado' in dir() else "Talhao"

    # Se leu do arquivo, pegar de la
    if resultado_path.exists():
        try:
            with open(resultado_path, "r", encoding="utf-8") as f:
                resultado = json.load(f)
            cliente_nome = resultado.get("cliente_nome", "Cliente")
            talhao_nome = resultado.get("talhao_nome", "Talhao")
        except Exception:
            pass

    return templates.TemplateResponse(
        request=request,
        name="prescricao_resultado.html",
        context={
            "request": request,
            "permissoes": get_permissoes(db),
            "geojson": json.dumps(geojson_zonas),
            "perfis": perfis,
            "prescricoes": prescricoes,
            "n_zonas": n_zonas,
            "area_total_ha": area_total_ha,
            "talhao_geojson": json.dumps(talhao_geojson) if talhao_geojson else "null",
            "cliente_nome": cliente_nome,
            "talhao_nome": talhao_nome
        }
    )

@app.get("/compactacao")
async def compactacao_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="compactacao.html", context={"permissoes": get_permissoes(db)})

@app.get("/compactacao/nova")
async def compactacao_nova_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="compactacao_nova.html", context={"permissoes": get_permissoes(db)})

@app.get("/extrator")
async def extrator_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="extrator.html", context={"permissoes": get_permissoes(db)})

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


# --- GERACAO DE LAUDOS ---
@app.get("/prescricao/gerar-pdf")
async def gerar_laudo_pdf(
    request: Request,
    cliente: str = Query(...),
    talhao: str = Query(...),
    db: Session = Depends(get_db)
):
    """Gera e retorna o laudo PDF com nomenclatura dinamica."""
    from services.laudo_export_service import LaudoExportService

    nome_arquivo = f"{cliente}_{talhao}_{datetime.now().strftime('%d-%m-%Y')}.pdf"
    nome_arquivo = nome_arquivo.replace(' ', '_').replace('/', '-')

    service = LaudoExportService()

    # Ler dados do resultado temporario
    import pathlib
    resultado_path = pathlib.Path("data/output/resultado_temp.json")
    dados = {}
    if resultado_path.exists():
        with open(resultado_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

    caminho_pdf = service.gerar_pdf_profissional(dados, nome_arquivo)

    return FileResponse(
        path=caminho_pdf,
        filename=nome_arquivo,
        media_type="application/pdf"
    )

@app.get("/prescricao/gerar-cartao")
async def gerar_cartao_cabine(
    request: Request,
    cliente: str = Query(...),
    talhao: str = Query(...),
    db: Session = Depends(get_db)
):
    """Gera e retorna o cartao de cabine A5 com nomenclatura dinamica."""
    from services.laudo_export_service import LaudoExportService

    nome_arquivo = f"{cliente}_{talhao}_{datetime.now().strftime('%d-%m-%Y')}_cartao.pdf"
    nome_arquivo = nome_arquivo.replace(' ', '_').replace('/', '-')

    service = LaudoExportService()

    # Ler dados do resultado temporario
    import pathlib
    resultado_path = pathlib.Path("data/output/resultado_temp.json")
    dados = {}
    if resultado_path.exists():
        with open(resultado_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

    caminho_pdf = service.gerar_cartao_cabine(dados, nome_arquivo)

    return FileResponse(
        path=caminho_pdf,
        filename=nome_arquivo,
        media_type="application/pdf"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)



