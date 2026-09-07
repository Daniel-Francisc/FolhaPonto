# Ponto Digital DIGEP

MVP funcional do sistema institucional da DIGEP/UnDF para recebimento,
conferência e arquivamento de folhas de ponto. A interface visual foi preservada
e agora conversa com uma API Python local.

## Informações acadêmicas

- Disciplina: Estágio Empresarial I
- Período letivo: 2026.2
- Curso: Engenharia de Software
- Instituição: Universidade do Distrito Federal Professor Jorge Amaury Maia Nunes – UnDF
- Sistema: Ponto Digital DIGEP
- Desenvolvimento do sistema: Jasmine de Sá Araujo
- Identidade visual: Francisco Daniel Bento dos Santos e Estevão Souza Araújo

## Executar no Replit

O workflow do Replit inicia uma API FastAPI na porta 5000:

```bash
python3 -m uvicorn server:app --host 0.0.0.0 --port 5000
```

Abra o Preview para navegar pelo Dashboard e pela tela de Conferência de OCR.
Também é possível iniciar diretamente com:

```bash
python3 main.py
```

A tela de login demonstrativa pode ser aberta em `/?view=login`. O modal
“Sobre o projeto”, no menu lateral, apresenta os créditos acadêmicos completos.

## O que está nesta primeira versão

- Dashboard institucional com competência selecionável, indicadores e atividade recente.
- Fila de Conferência OCR em tela dividida, com visualização protegida da folha e
  formulário de dados reconhecidos.
- Estados de confiança, servidor não identificado e ações de confirmar, pendenciar
  ou rejeitar em modo simulado.
- Navegação preparada para Arquivo, Servidores, Fila de envios, Auditoria e Configurações.
- Upload real de PDF/PNG/JPG com validação de extensão, limite de 20 MB, hash
  SHA-256, proteção contra duplicidade e armazenamento fora da pasta pública.
- Processamento de PDF com PyMuPDF quando disponível; scans sem camada de texto
  seguem em modo demonstrativo explícito, sem fingir que o OCR foi executado.
- Dados claramente fictícios; nenhum arquivo da pasta privada é exposto na web.

## Próximas etapas do MVP

## API disponível

- `GET /api/health` — estado do serviço.
- `GET /api/dashboard?competency=07/2026` — indicadores da competência.
- `GET /api/timesheets` — fila de folhas para conferência.
- `GET /api/employees` — servidores cadastrados.
- `POST /api/batches` — upload e processamento de um lote.
- `POST /api/timesheets/{id}/review` — confirma dados e arquiva.
- `POST /api/timesheets/{id}/pending` — encaminha para pendência.
- `POST /api/timesheets/{id}/reject` — rejeita o processamento.

## Organização do código

- `server.py`: API, banco SQLite, uploads privados e auditoria básica.
- `FolhaPontoBack/processing.py`: camada testável de extração e processamento.
- `FolhaPontoBack/ocr.class.py`: código original do Francisco, preservado.
- `FolhaPontoBack/melhoriaImg.class.py`: código original do Francisco, preservado.
- `index.html`, `styles.css`, `app.js`: interface e integração com a API.
- `tests/test_processing.py`: testes das regras de extração.

Os scripts originais continuam disponíveis para estudo e uso manual. A API não
os importa diretamente porque eles foram escritos como scripts interativos
(`input()` no fluxo principal); a nova camada evita esse bloqueio no ambiente web
sem apagar o trabalho existente.

## Próximas etapas

Adicionar autenticação JWT, importação de XLSX/CSV com prévia, armazenamento do
arquivo original por folha, OCR PaddleOCR em ambiente preparado, consulta com
filtros, fila de e-mail simulado e testes de integração. O MVP já demonstra o
fluxo principal upload → processamento → conferência → arquivamento.