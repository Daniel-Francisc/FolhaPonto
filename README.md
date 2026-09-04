Ponto Digital DIGEP

Sistema acadêmico para gestão, processamento, conferência e arquivamento de folhas de ponto da Diretoria de Gestão de Pessoas (DIGEP) da Universidade do Distrito Federal Professor Jorge Amaury Maia Nunes (UnDF).

Projeto em desenvolvimento. A versão atual apresenta um MVP funcional com interface integrada a uma API local. Parte do processamento ainda opera em modo de demonstração e não deve ser considerada pronta para uso institucional ou com dados pessoais reais.

Informações acadêmicas

Item

Informação

Instituição

Universidade do Distrito Federal Professor Jorge Amaury Maia Nunes – UnDF

Curso

Engenharia de Software

Disciplina

Estágio Empresarial I

Período letivo

2026.2

Sistema

Ponto Digital DIGEP

Desenvolvimento do sistema

Jasmine de Sá Araujo

Identidade visual

Francisco Daniel Bento dos Santos e Estevão Souza Araújo

Sobre o projeto

A DIGEP recebe e organiza mensalmente folhas de ponto de servidores e docentes. O processo envolve digitalização, identificação, conferência, arquivamento, localização posterior e, em casos de acumulação de cargo, encaminhamento da folha ao e-mail pessoal do servidor.

O Ponto Digital DIGEP foi proposto para apoiar esse fluxo por meio de upload em lote, extração de informações, conferência humana e organização dos documentos por servidor e competência.

Problema

O procedimento manual exige a análise e organização de um grande volume de documentos. Isso pode aumentar o tempo necessário para:

identificar o servidor de cada folha;

relacionar a folha à competência correta;

localizar documentos arquivados;

controlar documentos pendentes;

encaminhar folhas de servidores que acumulam cargo;

registrar erros e operações realizadas.

Objetivo geral

Desenvolver um sistema web que reduza o trabalho manual envolvido no recebimento, na identificação, na conferência, no arquivamento, na consulta e na distribuição de folhas de ponto da DIGEP.

Objetivos específicos

importar e manter os dados dos servidores;

receber PDFs e imagens de folhas de ponto;

separar documentos enviados em lote;

extrair matrícula, nome e competência;

relacionar cada folha ao servidor correspondente;

encaminhar resultados incertos para conferência humana;

arquivar folhas por servidor e competência;

permitir pesquisa, visualização e download;

identificar servidores que acumulam cargo;

controlar o envio das respectivas folhas;

registrar as operações em histórico de auditoria.

Escopo do MVP

O MVP foi planejado para demonstrar o fluxo:

Upload → Processamento → Extração → Conferência → Arquivamento → Consulta

A automação não elimina a validação humana. Resultados de baixa confiança, matrículas não encontradas e divergências devem permanecer pendentes até a conferência por um operador autorizado.

Funcionalidades da versão atual

interface web responsiva com identidade visual azul e verde;

tela de login demonstrativa;

dashboard com indicadores por competência;

navegação entre as áreas principais;

upload de PDF, PNG, JPG e JPEG;

limite de 20 MB por upload;

geração de hash SHA-256 para detectar arquivos duplicados;

armazenamento de uploads fora da pasta pública;

contagem das páginas de documentos PDF;

extração por expressões regulares quando o PDF possui camada de texto;

fila de conferência;

correção manual dos campos extraídos;

ações de arquivar, deixar pendente ou rejeitar;

persistência local com SQLite;

auditoria básica das operações;

dados fictícios identificados como demonstração;

testes unitários da extração de campos.

O que ainda é demonstrativo

Na versão atual, documentos escaneados sem camada de texto ainda não são processados por um mecanismo completo de OCR. Nessa situação, o sistema utiliza um modo demonstrativo explicitamente identificado.

Os seguintes recursos ainda precisam ser implementados ou concluídos:

autenticação real e autorização por perfil;

importação de servidores por XLSX e CSV;

OCR real em cada página escaneada;

tratamento automático das imagens com OpenCV;

associação individual de todas as páginas por matrícula;

armazenamento de cada página como documento independente;

visualização e download do documento arquivado;

pesquisa completa com filtros e paginação;

fila de e-mail para servidores que acumulam cargo;

cadastro e gerenciamento de usuários;

auditoria detalhada com identificação do usuário;

testes de integração da API e testes da interface.

A aplicação não deve atribuir dados fictícios a documentos reais nem apresentar uma simulação como resultado verdadeiro de OCR.

Tecnologias utilizadas

Camada

Tecnologia

Interface

HTML, CSS e JavaScript

API

Python e FastAPI

Servidor local

Uvicorn

Banco de dados

SQLite

Manipulação de PDF

PyMuPDF

Validação da API

Pydantic

Testes atuais

Unittest

OCR experimental

PaddleOCR

Tratamento experimental de imagem

OpenCV

Arquitetura atual

FolhaPonto/
├── FolhaPontoBack/
│   ├── __init__.py
│   ├── processing.py
│   ├── ocr.class.py
│   └── melhoriaImg.class.py
├── data/
│   ├── digep.sqlite3
│   └── uploads/
├── tests/
│   └── test_processing.py
├── index.html
├── styles.css
├── app.js
├── server.py
├── main.py
├── pyproject.toml
└── README.md

Principais arquivos

server.py: API FastAPI, persistência SQLite, uploads e auditoria básica.

FolhaPontoBack/processing.py: contagem de páginas e extração testável dos campos.

FolhaPontoBack/ocr.class.py: experimento inicial com PaddleOCR.

FolhaPontoBack/melhoriaImg.class.py: experimento inicial de tratamento de imagem.

index.html: estrutura da interface.

styles.css: identidade visual e responsividade.

app.js: navegação e integração da interface com a API.

tests/test_processing.py: testes unitários da extração.

Os scripts experimentais foram preservados para fins acadêmicos, mas não são importados diretamente pela aplicação web porque possuem interação via terminal.

Como executar no Replit

Importe o repositório no Replit.

Confirme que o projeto está utilizando Python 3.12 ou versão compatível.

Instale as dependências do pyproject.toml.

Execute:

python3 -m uvicorn server:app --host 0.0.0.0 --port 5000

Também é possível iniciar por:

python3 main.py

Abra o Preview do Replit.

A tela demonstrativa de login pode ser acessada por:

/?view=login

Como executar localmente

Pré-requisitos

Python 3.12 ou versão compatível;

ambiente virtual Python;

Git, caso o projeto seja clonado de um repositório.

Instalação

python3 -m venv .venv

No Linux ou macOS:

source .venv/bin/activate

No Windows PowerShell:

.venv\Scripts\Activate.ps1

Instale as dependências conforme o gerenciador configurado no projeto e inicie a aplicação:

python3 -m uvicorn server:app --reload --port 5000

Acesse http://localhost:5000 no navegador.

Endpoints disponíveis

Método

Endpoint

Finalidade

GET

/api/health

Consultar o estado da API

GET

/api/dashboard

Obter indicadores da competência

GET

/api/timesheets

Listar folhas para conferência

GET

/api/timesheets/{id}

Consultar uma folha

GET

/api/employees

Listar servidores cadastrados

POST

/api/batches

Enviar e processar um lote

POST

/api/timesheets/{id}/review

Confirmar dados e arquivar

POST

/api/timesheets/{id}/pending

Encaminhar para pendência

POST

/api/timesheets/{id}/reject

Rejeitar o processamento

GET

/api/timesheets/{id}/download

Download planejado; ainda não concluído

Testes

Execute os testes atuais com:

python3 -m unittest discover -s tests -v

Os testes atuais verificam:

extração de matrícula, nome e competência de um texto compatível com o formulário da UnDF;

classificação explícita de baixa confiança quando nenhum texto é encontrado.

Esse conjunto ainda é pequeno e deve ser ampliado antes da conclusão do MVP.

Requisitos funcionais

Código

Requisito

Situação atual

RF01

Cadastro/importação de servidores

Parcial

RF02

Upload em lote

Parcial

RF03

Processamento com OCR

Demonstrativo

RF04

Extração de dados

Parcial

RF05

Identificação automática

Parcial

RF06

Arquivamento

Parcial

RF07

Consulta

Parcial

RF08

Visualização e download

Pendente

RF09

Identificação de acumuladores

Parcial

RF10

Envio das folhas

Pendente

RF11

Controle do envio

Pendente

RF12

Rastreamento e auditoria

Parcial

Legenda

Concluído: implementado e testado no fluxo previsto.

Parcial: existe implementação inicial, mas ainda faltam regras ou testes.

Demonstrativo: apresentado visualmente ou por simulação controlada.

Pendente: ainda não implementado.

Regras planejadas para o OCR

Condição

Classificação

Confiança igual ou superior a 90% e matrícula encontrada

Reconhecido

Confiança entre 70% e 89%

Revisão necessária

Confiança inferior a 70%

Baixa confiança

Matrícula não localizada

Servidor não identificado

Nome incompatível com a matrícula

Possível divergência

Independentemente da confiança, nenhuma folha deve ser descartada automaticamente.

Segurança e LGPD

O sistema trata documentos funcionais e pode lidar com dados pessoais. Uma eventual implantação institucional deverá incluir:

autenticação e autorização por perfil;

princípio do menor privilégio;

arquivos privados;

proteção e mascaramento do CPF;

validação de acesso para visualização e download;

trilha de auditoria;

política de retenção e descarte;

proteção de credenciais por variáveis de ambiente;

backups e procedimento de recuperação;

uso somente de dados fictícios ou anonimizados durante o desenvolvimento.

Esta versão acadêmica não está autorizada para armazenar dados pessoais reais em ambiente público.

Boas práticas do repositório

Não devem ser enviados ao GitHub:

bancos SQLite preenchidos;

folhas de ponto reais;

documentos pessoais;

arquivos processados em data/uploads/;

senhas, tokens ou credenciais;

arquivos .env;

materiais de outros projetos acadêmicos;

cópias desnecessárias dos prompts utilizados no desenvolvimento.

Exemplo mínimo para o .gitignore:

.env
.venv/
__pycache__/
*.pyc
data/
output/
*.sqlite3

Limitações conhecidas

documentos escaneados sem camada de texto ainda não passam por OCR completo na aplicação web;

parte dos registros utilizados na interface é fictícia;

o login atual é demonstrativo;

o envio de e-mail ainda não foi implementado;

o download do documento arquivado ainda retorna estado não implementado;

o banco local é adequado ao protótipo, mas não à implantação institucional;

ainda não existem testes suficientes para todos os endpoints e regras de negócio.

Próximas etapas

Implementar a importação de XLSX e CSV com prévia e validação.

Separar fisicamente cada página do PDF.

Integrar OCR real ao fluxo web.

Associar cada página ao servidor pela matrícula.

Armazenar e disponibilizar cada folha com acesso autorizado.

Implementar busca e filtros.

Criar autenticação e perfis de acesso.

Implementar fila simulada de envio de e-mails.

Expandir a auditoria.

Criar testes unitários, de integração e de interface.

Critérios de conclusão do MVP

O MVP poderá ser considerado concluído quando for possível:

importar uma planilha de servidores;

enviar um PDF com várias páginas;

separar cada página como uma folha individual;

executar OCR em cada folha;

extrair matrícula, nome e competência;

associar a folha ao servidor correspondente;

corrigir dados na conferência humana;

arquivar e pesquisar a folha;

visualizar e baixar o documento autorizado;

identificar acumuladores e simular o envio;

registrar as operações na auditoria;

executar os testes principais sem falhas.

Créditos

Desenvolvimento do sistema

Jasmine de Sá Araujo

Identidade visual

Francisco Daniel Bento dos Santos
Estevão Souza Araújo

Aviso acadêmico

Projeto acadêmico desenvolvido na disciplina Estágio Empresarial I, do curso de Engenharia de Software da UnDF, durante o período letivo 2026.2.

