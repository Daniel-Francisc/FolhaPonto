"""Processamento real e testável das folhas de ponto.

Os scripts originais do projeto continuam preservados. Esta camada não depende
de ``input()`` e coordena a separação das páginas, OCR opcional e extração dos
campos usados pela API web.
"""

from __future__ import annotations

import shutil
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
    texto: str = ""


def _find(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_fields(text: str) -> Extraction:
    """Extrai matrícula, nome e competência do texto reconhecido."""
    clean_text = text.strip()
    if not clean_text:
        return Extraction(None, None, None, 0.0, "ocr-indisponivel", "")

    matricula = _find(r"MATR[IÍ]CULA\s*:\s*([0-9]{5,})", clean_text)
    nome = _find(r"NOME\s+DO\s+SERVIDOR\s*:\s*([^\n]+)", clean_text)
    competencia = _find(
        r"(?:REFER[EÊ]NCIA|COMPET[EÊ]NCIA)\s*:\s*([A-ZÇÃÕÊÉ]+[ /-]+20\d{2})",
        clean_text,
    )
    found = sum(value is not None for value in (matricula, nome, competencia))
    confidence = {0: 0.41, 1: 0.62, 2: 0.78, 3: 0.94}[found]
    return Extraction(matricula, nome, competencia, confidence, "ocr-texto", clean_text)


def _run_ocr(image_bytes: bytes) -> tuple[str, str]:
    """Executa Tesseract quando disponível, sem inventar um resultado."""
    try:
        import io

        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        text = pytesseract.image_to_string(Image.open(io.BytesIO(image_bytes)), lang="por+eng")
        return text.strip(), "ocr-tesseract"
    except (ImportError, OSError, RuntimeError):
        return "", "ocr-indisponivel"


def _page_extraction(text: str, image_bytes: bytes | None = None) -> Extraction:
    if text.strip():
        return extract_fields(text)
    if image_bytes is None:
        return Extraction(None, None, None, 0.0, "ocr-indisponivel", "")
    ocr_text, mode = _run_ocr(image_bytes)
    if ocr_text:
        extracted = extract_fields(ocr_text)
        extracted.modo = mode
        return extracted
    return Extraction(None, None, None, 0.0, mode, "")


def _extraction_dict(extracted: Extraction) -> dict[str, Any]:
    return {
        "matricula": extracted.matricula,
        "nome": extracted.nome,
        "competencia": extracted.competencia,
        "confidence": extracted.confianca,
        "mode": extracted.modo,
        "text": extracted.texto,
    }


def process_document(path: Path, pages_dir: Path | None = None) -> dict[str, Any]:
    """Separa cada página e retorna uma extração independente por página."""
    pages_dir = pages_dir or path.parent / f"{path.stem}_pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_results: list[dict[str, Any]] = []

    if path.suffix.lower() == ".pdf":
        try:
            import fitz  # type: ignore
        except ImportError:
            return {
                "pages": 0,
                "page_results": [],
                "extraction": _extraction_dict(Extraction(None, None, None, 0.0, "ocr-indisponivel")),
            }

        document = fitz.open(path)
        try:
            for page_number in range(document.page_count):
                page = document[page_number]
                text = page.get_text("text") or ""
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image_bytes = pixmap.tobytes("png")
                extracted = _page_extraction(text, image_bytes)
                individual_path = pages_dir / f"pagina-{page_number + 1:03d}.pdf"
                individual = fitz.open()
                individual.insert_pdf(document, from_page=page_number, to_page=page_number)
                individual.save(individual_path)
                individual.close()
                page_results.append(
                    {
                        "source_page": page_number + 1,
                        "stored_path": individual_path,
                        "extraction": _extraction_dict(extracted),
                    }
                )
        finally:
            document.close()
    else:
        image_bytes = path.read_bytes()
        extracted = _page_extraction("", image_bytes)
        individual_path = pages_dir / f"pagina-001{path.suffix.lower()}"
        shutil.copyfile(path, individual_path)
        page_results.append(
            {
                "source_page": 1,
                "stored_path": individual_path,
                "extraction": _extraction_dict(extracted),
            }
        )

    first_extraction = page_results[0]["extraction"] if page_results else _extraction_dict(
        Extraction(None, None, None, 0.0, "ocr-indisponivel")
    )
    return {
        "pages": len(page_results),
        "page_results": page_results,
        "extraction": first_extraction,
    }