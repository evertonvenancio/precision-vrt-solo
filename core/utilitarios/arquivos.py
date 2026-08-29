"""
Funções de utilidade para operações de arquivo.
"""
import uuid
from pathlib import Path
from fastapi import UploadFile

def _salvar_upload(upload: UploadFile, destino: Path) -> Path:
    """Salva um UploadFile no destino e retorna o caminho."""
    destino = destino / f"{uuid.uuid4().hex}_{upload.filename}"
    with open(destino, "wb") as f:
        import shutil
        shutil.copyfileobj(upload.file, f)
    return destino