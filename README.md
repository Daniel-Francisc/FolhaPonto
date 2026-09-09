# Ponto Digital DIGEP

Sistema de recebimento, conferência e arquivamento de folhas de ponto da DIGEP/UnDF.

## Descrição

O **Ponto Digital DIGEP** é um MVP funcional de ponta a ponta para receber PDFs
e imagens de folhas de ponto, separar cada página, extrair dados via OCR quando
disponível, associar cada folha a um servidor pela matrícula, permitir conferência
humana, arquivar o documento, consultar o histórico e simular o envio de e-mails
para servidores que acumulam cargo.

## Problema

A DIGEP recebe folhas de ponto em papel escaneado. O processo manual de conferência
é demorado, sujeito a erros de transcrição e não centraliza o histórico dos
documentos. Sem um sistema, é difícil rastrear quem enviou, quem conferiu, quando
foi arquivado e quais folhas ainda aguardam análise.

## Objetivos

- Receber folhas em PDF, PNG, JPG ou JPEG (até 20 MB).
- Separar automaticamente cada página em documento individual.
- Executar OCR quando Tesseract estiver disponível — sem inventar resultados.
- Associar a folha ao servidor pela matrícula.
- Permitir conferência humana com correção e observações.
- Arquivar com unicidade por servidor e competência.
- Filtrar, pesquisar e consultar o arquivo.
- Simular a fila de envio para servidores com acúmulo de cargo.
- Manter trilha de auditoria com identificação do usuário.
- Proteger dados pessoais (LGPD) com mascaramento e criptografia do CPF.

## Informações acadêmicas

- Disciplina: Estágio Empresarial I
- Período letivo: 2026.2
- Curso: Engenharia de Software
- Instituição: Universidade do Distrito Federal Professor Jorge Amaury Maia Nunes – UnDF
- Sistema: Ponto Digital DIGEP
- Desenvolvimento do sistema: Jasmine de Sá Araujo
- Identidade visual: Francisco Daniel Bento dos Santos e Estevão Souza Araújo

## Tecnologias

- Python 3.12
- FastAPI
- Uvicorn
- SQLite
- Jinja-free static frontend (HTML, CSS, JavaScript)
- PyMuPDF (fitz) para processamento de PDF
- Pillow + pytesseract para OCR (opcional)
- openpyxl para importação XLSX
- python-jose + bcrypt para autenticação JWT
- pytest para testes

## Arquitetura

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌───────────────┐
│  Frontend (estático)│────▶│  FastAPI (server.py)     │────▶│  SQLite       │
│  app.js / index.html│ token│  auth · import · batches │ DB  │  digep.sqlite3│
│                     │      │  conferência · dispatch  │     │               │
└─────────────────────┘      └───────────┬──────────────┘     └───────────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │ FolhaPontoBack/      │
                              │ processing.py (OCR)  │
                              │ preprocess · extract │
                              └──────────────────────┘
```

O frontend é servido pelo próprio FastAPI (`/`, `/app.js`, `/styles.css`). Todas as
rotas privadas exigem `Authorization: Bearer <jwt>`.

## Instalação

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -e ".[test]"
```

## Execução

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 5000 --reload
```

Acesse `http://127.0.0.1:5000`.

O usuário administrador inicial é criado no primeiro startup a partir das variáveis
`ADMIN_USERNAME` e `ADMIN_PASSWORD`. Se não forem definidas, o login fica
desabilitado e o endpoint `/api/auth/login` responde com erro.

Para usar uma senha fixa com o `.env.example`:

```bash
# copy .env.example .env  (opcional; o código lê as variáveis do ambiente)
```

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave de assinatura do JWT | exigida pelo `auth.py` |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Validade do token | `480` |
| `ADMIN_USERNAME` | Login do admin inicial | vazio (sem seed) |
| `ADMIN_PASSWORD` | Senha do admin inicial (hash bcrypt) | vazio |
| `TESSERACT_CMD` | Caminho do executável do Tesseract | auto-detect |
| `CPF_ENCRYPTION_KEY` | Chave Fernet para criptografar CPF em repouso | vazio (CPF fica apenas mascarado) |
| `DATABASE_URL` | Reservado para uso futuro (atualmente SQLite local) | — |

Não versione `.env`.

## Testes

```bash
python -m pytest -q
```

Os testes usam `tmp_path` com um banco isolado e não exigem Tesseract
(`_run_ocr` é mockado quando necessário).

## Endpoints

### Autenticação

- `POST /api/auth/login` — `{username, password}` → `{access_token, user}`
- `POST /api/auth/logout` — revoga o token atual (auditado)
- `GET /api/auth/me` — dados do usuário autenticado

### Dashboard e consulta

- `GET /api/dashboard?competency=07/2026` — indicadores calculados do banco
- `GET /api/timesheets?competency=07/2026&status=arquivada&q=Maria` — lista
- `GET /api/timesheets/{id}` — detalhe individual
- `GET /api/timesheets/{id}/download` — download do PDF individual (requer auth)

### Conferência

- `POST /api/timesheets/{id}/review` — associa servidor, arquiva (exige servidor ou justificativa)
- `POST /api/timesheets/{id}/pending?note=...` — marca pendência
- `POST /api/timesheets/{id}/reject` — rejeita

### Upload/processamento

- `POST /api/batches` — upload de PDF/PNG/JPG (admin/operador)

### Servidores e importação

- `GET /api/employees` — servidores (CPF mascarado)
- `POST /api/employees/import/preview` — valida XLSX/CSV
- `POST /api/employees/import/confirm` — confirma importação

### Fila simulada de envio

- `GET /api/dispatches?status=pendente` — fila
- `POST /api/dispatches/{id}/authorize` — autoriza (admin)
- `POST /api/dispatches/{id}/simulate-send` — simula sucesso/erro
- `POST /api/dispatches/{id}/resend` — volta para pendente

## Requisitos funcionais (RF01–RF12)

| ID | Requisito | Status |
|---|---|---|
| RF01 | Recebimento de folhas (PDF/PNG/JPG, ≤ 20 MB, hash SHA-256) | Implementado |
| RF02 | Separação por página em documentos individuais | Implementado |
| RF03 | OCR com Tesseract quando disponível; sem inventar dados | Implementado |
| RF04 | Associação automática pela matrícula | Implementado |
| RF05 | Conferência humana com correção e observações | Implementado |
| RF06 | Arquivamento com unicidade por servidor e competência | Implementado |
| RF07 | Consulta, filtros e download autorizado | Implementado |
| RF08 | Fila simulada de envio para acúmulo de cargo | Implementado |
| RF09 | Auditoria com identificação do usuário | Implementado |
| RF10 | Importação XLSX/CSV com prévia e validações | Implementado |
| RF11 | Autenticação JWT com perfis (admin, operador, consulta) | Implementado |
| RF12 | Proteção de dados pessoais (LGPD) — CPF mascarado e criptografado | Implementado |

## Segurança

- Senhas com hash bcrypt.
- JWT com expiração e revogação (tokens revogados são rejeitados).
- Rotas protegidas por perfil (`admin`, `operador`, `consulta`).
- CPF nunca exposto completo em nenhuma resposta da API (`***.***.***-XX`).
- CPF armazenado pode ser criptografado com chave Fernet (`CPF_ENCRYPTION_KEY`).
- Auditoria nunca grava senhas, tokens, chaves, CPF completo ou o conteúdo integral da folha.
- Download de folhas exige autenticação.
- Arquivos enviados ficam fora da pasta pública (`data/uploads/`).

## Limitações do MVP

- OCR só funciona se Tesseract estiver instalado no sistema; caso contrário, as
  folhas ficam marcadas como *OCR indisponível* (correção manual).
- O envio de e-mails é **simulado**: nenhum e-mail real é enviado. É necessário
  autorização humana para registrar o despacho.
- O banco continua SQLite local; `DATABASE_URL` está reservado para uso futuro.
- A autenticação usa JWT em header; não há refresh token nem bloqueio por IP.

## Pendências / próximos passos

- Importação de XLSX/CSV com prévia já disponível; falta persistir o arquivo original por folha.
- Autenticação com refresh token e gestão de usuários pelo painel.
- Envio real de e-mails (SMTP) em fases posteriores.
- Consulta com filtros avançados e exportação.
- Migração para `DATABASE_URL` (PostgreSQL) quando a equipe decidir sair do SQLite.
- Implementação de OCR PaddleOCR (projeto original do Francisco) em ambiente preparado.

## Créditos no sistema

A identidade visual foi desenhada por Francisco Daniel Bento dos Santos e Estevão
Souza Araújo e preservada no frontend. Os scripts originais (`ocr.class.py`,
`melhoriaImg.class.py`) continuam disponíveis para estudo em `FolhaPontoBack/`.