"""Endpoints da Biblioteca Técnica (artigos de conhecimento)."""
from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from db.database import get_db
from models.conhecimento import CategoriaArtigo
from app.services.conhecimento_service import ConhecimentoError, ConhecimentoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conhecimento", tags=["conhecimento"])


class ArtigoIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: UUID
    categoria: CategoriaArtigo
    titulo: str = Field(min_length=1, max_length=255)
    conteudo: str = Field(min_length=1)
    referencias: Optional[str] = None
    chave_vinculo: Optional[str] = Field(default=None, max_length=64)


class ArtigoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: Optional[CategoriaArtigo] = None
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=255)
    conteudo: Optional[str] = None
    referencias: Optional[str] = None
    chave_vinculo: Optional[str] = Field(default=None, max_length=64)


class ArtigoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    categoria: CategoriaArtigo
    titulo: str
    conteudo: str
    referencias: Optional[str]
    chave_vinculo: Optional[str]


@router.post(
    "/artigos",
    response_model=ArtigoOut,
    status_code=status.HTTP_201_CREATED,
)
def criar_artigo(payload: ArtigoIn, db: Session = Depends(get_db)) -> ArtigoOut:
    svc = ConhecimentoService(db)
    artigo = svc.criar(
        tenant_id=payload.tenant_id,
        categoria=payload.categoria,
        titulo=payload.titulo,
        conteudo=payload.conteudo,
        referencias=payload.referencias,
        chave_vinculo=payload.chave_vinculo,
    )
    return ArtigoOut.model_validate(artigo)


@router.get("/artigos", response_model=list[ArtigoOut])
def listar_artigos(
    tenant_id: UUID,
    categoria: Optional[CategoriaArtigo] = None,
    busca: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ArtigoOut]:
    svc = ConhecimentoService(db)
    artigos = svc.listar(tenant_id, categoria, busca, limit, offset)
    return [ArtigoOut.model_validate(a) for a in artigos]


@router.get("/artigos/{artigo_id}", response_model=ArtigoOut)
def obter_artigo(
    artigo_id: UUID,
    tenant_id: UUID,
    db: Session = Depends(get_db),
) -> ArtigoOut:
    svc = ConhecimentoService(db)
    try:
        artigo = svc.obter(tenant_id, artigo_id)
    except ConhecimentoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return ArtigoOut.model_validate(artigo)


@router.patch("/artigos/{artigo_id}", response_model=ArtigoOut)
def atualizar_artigo(
    artigo_id: UUID,
    tenant_id: UUID,
    payload: ArtigoUpdate,
    db: Session = Depends(get_db),
) -> ArtigoOut:
    svc = ConhecimentoService(db)
    try:
        artigo = svc.atualizar(
            tenant_id, artigo_id, **payload.model_dump(exclude_unset=True)
        )
    except ConhecimentoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return ArtigoOut.model_validate(artigo)


@router.delete("/artigos/{artigo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_artigo(
    artigo_id: UUID,
    tenant_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    svc = ConhecimentoService(db)
    try:
        svc.remover(tenant_id, artigo_id)
    except ConhecimentoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("/vincular", response_model=list[ArtigoOut])
def vincular_documentacao(
    tenant_id: UUID,
    metodologia: str = Query(..., min_length=1),
    culturas: Optional[list[str]] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[ArtigoOut]:
    svc = ConhecimentoService(db)
    artigos = svc.vincular_documentacao(tenant_id, metodologia, culturas, limit)
    return [ArtigoOut.model_validate(a) for a in artigos]