"""Serviços pequenos e testáveis que complementam os scripts originais.

Os arquivos `ocr.class.py` e `melhoriaImg.class.py` foram mantidos como vieram
do projeto importado. Este módulo fornece a camada web uma API segura e sem
interação via terminal. PaddleOCR/OpenCV são opcionais no MVP: quando não
estão instalados, o sistema usa o resultado demonstrativo explicitamente.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Extraction:
    matricula: str | None
    nome: str | None
    competencia: str | None
    confianca: float
    modo: str


def _find(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_fields(text: str) -> Extraction:
    """Extrai os campos mais estáveis do formulário de frequência da UnDF."""
    if not text.strip():
        return Extraction(None, None, None, 0.41, "demo")
    matricula = _find(r"MATR[IÍ]CULA\s*:\s*([0-9]{5,})", text)
    nome = _find(r"NOME\s+DO\s+SERVIDOR\s*:\s*([^\n]+)", text)
    competencia = _find(
        r"(?:REFER[EÊ]NCIA|COMPET[EÊ]NCIA)\s*:\s*([A-ZÇÃÕÊÉ]+[ /-]+20\d{2})",
        text,
    )
    found = sum(value is not None for value in (matricula, nome, competencia))
    confidence = {0: 0.41, 1: 0.62, 2: 0.78, 3: 0.94}[found]
    return Extraction(matricula, nome, competencia, confidence, "ocr-texto")


def process_document(path: Path) -> dict[str, Any]:
    """Processa PDF/imagem sem quebrar quando OCR opcional não existe.

    A contagem de páginas usa PyMuPDF quando disponível. O texto é analisado
    quando o PDF tem camada textual; scans sem texto seguem para demonstração.
    """
    pages = 1
    extracted = Extraction(None, None, None, 0.41, "demo")
    try:
        import fitz  # type: ignore

        document = fitz.open(path)
        pages = max(1, document.page_count)
        texts = [page.get_text("text") for page in document]
        extracted = extract_fields("\n".join(texts))
        if not any(texts):
            extracted.modo = "demo-sem-texto"
        document.close()
    except (ImportError, RuntimeError, ValueError):
        extracted.modo = "demo-sem-pymupdf"

    return {
        "pages": pages,
        "extraction": {
            "matricula": extracted.matricula,
            "nome": extracted.nome,
            "competencia": extracted.competencia,
            "confidence": extracted.confianca,
            "mode": extracted.modo,
        },
    }