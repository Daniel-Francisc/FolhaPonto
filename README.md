# Ponto Digital DIGEP

Primeira versão visual navegável do sistema institucional da DIGEP/UnDF para
recebimento, conferência e arquivamento de folhas de ponto.

## Executar no Replit

O projeto está em modo de demonstração nesta etapa. O workflow serve os arquivos
estáticos na porta 5000:

```bash
python3 -m http.server 5000 --bind 0.0.0.0
```

Abra o Preview para navegar pelo Dashboard e pela tela de Conferência de OCR.

## O que está nesta primeira versão

- Dashboard institucional com competência selecionável, indicadores e atividade recente.
- Fila de Conferência OCR em tela dividida, com visualização protegida da folha e
  formulário de dados reconhecidos.
- Estados de confiança, servidor não identificado e ações de confirmar, pendenciar
  ou rejeitar em modo simulado.
- Navegação preparada para Arquivo, Servidores, Fila de envios, Auditoria e Configurações.
- Dados claramente fictícios; nenhum documento enviado é exposto na interface.

## Próximas etapas do MVP

Conectar o frontend a uma API FastAPI, banco de dados, armazenamento privado,
importação de planilhas, separação de PDFs, OCR real com fallback demonstrativo,
autenticação JWT, arquivamento e e-mail simulado. A base Python existente em
`FolhaPontoBack/` será reaproveitada na etapa de processamento.