"""API do MVP do Ponto Digital DIGEP.

A aplicação é deliberadamente simples: FastAPI + SQLite local + arquivos fora
da pasta pública. Isso deixa o fluxo demonstrável no Replit e fácil de explicar
em sala, sem esconder dependências em serviços externos.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from FolhaPontoBack.processing import process_document


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "digep.sqlite3"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Ponto Digital DIGEP", version="0.2.0")

DEMO_EMPLOYEES = [
    ("Alexandre Nata Vicente", "17289106", "alexandre.demo@example.invalid", 40, 0),
    ("Ana Ribeiro", "16234018", "ana.demo@example.invalid", 40, 0),
    ("Caio Ferreira", "17450291", "caio.demo@example.invalid", 40, 1),
    ("João Martins", "16871904", "joao.demo@example.invalid", 40, 1),
]
DEMO_SHEETS = [
    ("Alexandre Nata Vicente", "17289106", 78, "revisao", "JULHO/2026", "CEINTER"),
    ("Ana Ribeiro", "16234018", 62, "baixa_confianca", "JULHO/2026", "CEINTER"),
    ("Caio Ferreira", "17450291", 78, "revisao", "JULHO/2026", "CEINTER"),
    ("Servidor não identificado", None, 41, "nao_identificado", "JULHO/2026", None),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_competency(value: str) -> str:
    month_names = {
        "01": "JANEIRO", "02": "FEVEREIRO", "03": "MARÇO", "04": "ABRIL",
        "05": "MAIO", "06": "JUNHO", "07": "JULHO", "08": "AGOSTO",
        "09": "SETEMBRO", "10": "OUTUBRO", "11": "NOVEMBRO", "12": "DEZEMBRO",
    }
    month, _, year = value.upper().partition("/")
    return f"{month_names.get(month, month)}/{year}" if year else value.upper()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              matricula TEXT NOT NULL UNIQUE,
              email TEXT NOT NULL,
              carga_horaria INTEGER NOT NULL DEFAULT 40,
              acumula_cargo INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS batches (
              id TEXT PRIMARY KEY,
              original_name TEXT NOT NULL,
              stored_path TEXT NOT NULL,
              sha256 TEXT NOT NULL UNIQUE,
              page_count INTEGER NOT NULL DEFAULT 1,
              mode TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS timesheets (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              batch_id TEXT,
              employee_id INTEGER,
              name TEXT NOT NULL,
              matricula TEXT,
              competencia TEXT NOT NULL,
              unidade TEXT,
              confidence INTEGER NOT NULL,
              status TEXT NOT NULL,
              note TEXT NOT NULL DEFAULT '',
              reviewed_at TEXT,
              archived_at TEXT,
              source_page INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(batch_id) REFERENCES batches(id),
              FOREIGN KEY(employee_id) REFERENCES employees(id)
            );
            CREATE TABLE IF NOT EXISTS audit_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              action TEXT NOT NULL,
              entity TEXT NOT NULL,
              entity_id TEXT,
              details TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_timesheets_competencia ON timesheets(competencia);
            CREATE INDEX IF NOT EXISTS idx_timesheets_matricula ON timesheets(matricula);
            CREATE INDEX IF NOT EXISTS idx_timesheets_status ON timesheets(status);
            """
        )
        employee_count = db.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if employee_count == 0:
            db.executemany(
                """
                INSERT INTO employees (name, matricula, email, carga_horaria, acumula_cargo, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [(*employee, now()) for employee in DEMO_EMPLOYEES],
            )
        sheet_count = db.execute("SELECT COUNT(*) FROM timesheets").fetchone()[0]
        if sheet_count == 0:
            for index, (name, matricula, confidence, status, competency, unit) in enumerate(DEMO_SHEETS):
                employee_id = None
                if matricula:
                    row = db.execute("SELECT id FROM employees WHERE matricula = ?", (matricula,)).fetchone()
                    employee_id = row["id"] if row else None
                db.execute(
                    """
                    INSERT INTO timesheets
                    (name, matricula, competencia, unidade, confidence, status, source_page, created_at, updated_at, employee_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name, matricula, competency, unit, confidence, status, index + 1, now(), now(), employee_id),
                )
        db.execute(
            "INSERT INTO audit_logs (action, entity, entity_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
            ("startup", "system", None, json.dumps({"mode": "demo"}), now()),
        )


@app.on_event("startup")
def startup() -> None:
    init_db()


class ReviewPayload(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    matricula: str | None = Field(default=None, max_length=30)
    competencia: str = Field(min_length=3, max_length=30)
    employee_id: int | None = None
    note: str = Field(default="", max_length=500)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["confidence"] = int(item["confidence"])
    item["employee_id"] = item.get("employee_id")
    item["status_label"] = {
        "reconhecida": "Reconhecida",
        "revisao": "Revisão necessária",
        "baixa_confianca": "Baixa confiança",
        "nao_identificado": "Não identificado",
        "pendente": "Pendente",
        "arquivada": "Arquivada",
        "rejeitada": "Rejeitada",
    }.get(item["status"], item["status"])
    return item


def audit(db: sqlite3.Connection, action: str, entity: str, entity_id: str | int | None, details: dict[str, Any]) -> None:
    db.execute(
        "INSERT INTO audit_logs (action, entity, entity_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
        (action, entity, str(entity_id) if entity_id is not None else None, json.dumps(details), now()),
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "demo", "database": "sqlite"}


@app.get("/api/dashboard")
def dashboard(competency: str = Query("07/2026")) -> dict[str, Any]:
    competency = normalize_competency(competency)
    with connect() as db:
        rows = db.execute("SELECT * FROM timesheets WHERE competencia LIKE ?", (f"%{competency[-7:]}%",)).fetchall()
        all_rows = db.execute("SELECT * FROM timesheets").fetchall()
        statuses = {status: sum(1 for row in rows if row["status"] == status) for status in ("reconhecida", "revisao", "baixa_confianca", "nao_identificado", "arquivada")}
        total = len(rows)
        archived = statuses["arquivada"]
        recognized = statuses["reconhecida"]
        pending = statuses["revisao"] + statuses["baixa_confianca"] + statuses["nao_identificado"]
        pending += sum(1 for row in rows if row["status"] == "pendente")
        return {
            "competency": competency,
            "total": total,
            "recognized": recognized,
            "review": pending,
            "low_confidence": statuses["baixa_confianca"],
            "unidentified": statuses["nao_identificado"],
            "archived": archived,
            "recognition_rate": round((recognized / total) * 100) if total else 0,
            "average_processing_seconds": 102,
            "dispatch_pending": 7,
            "dispatch_sent": 7,
            "demo": True,
            "sample_size": len(all_rows),
        }


@app.get("/api/timesheets")
def list_timesheets(
    status: str | None = None,
    q: str | None = None,
    competency: str = "07/2026",
) -> list[dict[str, Any]]:
    conditions = ["competencia LIKE ?"]
    params: list[Any] = [f"%{normalize_competency(competency)}%"]
    if status and status != "todos":
        conditions.append("status = ?")
        params.append(status)
    if q:
        conditions.append("(name LIKE ? OR matricula LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    with connect() as db:
        rows = db.execute(f"SELECT * FROM timesheets WHERE {' AND '.join(conditions)} ORDER BY id", params).fetchall()
        return [row_to_dict(row) for row in rows]


@app.get("/api/employees")
def list_employees() -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM employees ORDER BY name").fetchall()]


@app.get("/api/timesheets/{timesheet_id}")
def get_timesheet(timesheet_id: int) -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Folha não encontrada.")
        return row_to_dict(row)


@app.post("/api/timesheets/{timesheet_id}/review")
def review_timesheet(timesheet_id: int, payload: ReviewPayload) -> dict[str, Any]:
    with connect() as db:
        current = db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone()
        if not current:
            raise HTTPException(404, "Folha não encontrada.")
        employee_id = payload.employee_id
        if employee_id is None and payload.matricula:
            employee = db.execute("SELECT id FROM employees WHERE matricula = ?", (payload.matricula,)).fetchone()
            employee_id = employee["id"] if employee else None
        db.execute(
            """
            UPDATE timesheets
            SET name = ?, matricula = ?, competencia = ?, employee_id = ?, note = ?,
                status = 'arquivada', reviewed_at = ?, archived_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (payload.name, payload.matricula, payload.competencia, employee_id, payload.note, now(), now(), now(), timesheet_id),
        )
        audit(db, "archive", "timesheet", timesheet_id, {"name": payload.name, "mode": "manual-review"})
        row = db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone()
        return row_to_dict(row)


@app.post("/api/timesheets/{timesheet_id}/pending")
def mark_pending(timesheet_id: int, note: str = "") -> dict[str, Any]:
    with connect() as db:
        current = db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone()
        if not current:
            raise HTTPException(404, "Folha não encontrada.")
        db.execute("UPDATE timesheets SET status = 'pendente', note = ?, updated_at = ? WHERE id = ?", (note[:500], now(), timesheet_id))
        audit(db, "pending", "timesheet", timesheet_id, {"note": note[:120]})
        return row_to_dict(db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone())


@app.post("/api/timesheets/{timesheet_id}/reject")
def reject_timesheet(timesheet_id: int) -> dict[str, Any]:
    with connect() as db:
        if not db.execute("SELECT id FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone():
            raise HTTPException(404, "Folha não encontrada.")
        db.execute("UPDATE timesheets SET status = 'rejeitada', updated_at = ? WHERE id = ?", (now(), timesheet_id))
        audit(db, "reject", "timesheet", timesheet_id, {})
        return row_to_dict(db.execute("SELECT * FROM timesheets WHERE id = ?", (timesheet_id,)).fetchone())


@app.post("/api/batches")
async def create_batch(file: UploadFile = File(...)) -> dict[str, Any]:
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(400, "Formato inválido. Envie PDF, PNG, JPG ou JPEG.")
    content = await file.read()
    if not content:
        raise HTTPException(400, "O arquivo enviado está vazio.")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(413, "O arquivo excede o limite de 20 MB.")
    digest = hashlib.sha256(content).hexdigest()
    with connect() as db:
        existing = db.execute("SELECT id FROM batches WHERE sha256 = ?", (digest,)).fetchone()
        if existing:
            raise HTTPException(409, "Este arquivo já foi processado.")
        batch_id = f"LOTE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:5].upper()}"
        target = UPLOAD_DIR / f"{batch_id}{suffix}"
        target.write_bytes(content)
        processed = process_document(target)
        batch_mode = processed["extraction"]["mode"]
        db.execute(
            "INSERT INTO batches (id, original_name, stored_path, sha256, page_count, mode, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (batch_id, original_name, str(target.relative_to(ROOT)), digest, processed["pages"], batch_mode, now()),
        )
        seed = DEMO_SHEETS
        for page in range(processed["pages"]):
            base = seed[page % len(seed)]
            name, matricula, confidence, status, competency, unit = base
            db.execute(
                """
                INSERT INTO timesheets
                (batch_id, name, matricula, competencia, unidade, confidence, status, source_page, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (batch_id, name, matricula, competency, unit, confidence, status, page + 1, now(), now()),
            )
        audit(db, "upload", "batch", batch_id, {"pages": processed["pages"], "mode": batch_mode})
    return {"batch_id": batch_id, "pages": processed["pages"], "mode": batch_mode, "status": "processed"}


@app.get("/api/timesheets/{timesheet_id}/download")
def download_timesheet(timesheet_id: int) -> FileResponse:
    raise HTTPException(501, "Download será liberado após o arquivamento do arquivo original.")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/styles.css")
def styles() -> FileResponse:
    return FileResponse(ROOT / "styles.css", media_type="text/css")


@app.get("/app.js")
def javascript() -> FileResponse:
    return FileResponse(ROOT / "app.js", media_type="application/javascript")