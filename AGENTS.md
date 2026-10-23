# AGENTS.md

## Contexto
API de estoque para a loja "愚公移山 Variedades" (Prosel Ecomp Jr. 2026.2, trilha Back-End).
Stack: FastAPI, PostgreSQL, SQLAlchemy, Alembic.

## Como a IA deve me ajudar
- Meu objetivo é APRENDER. Eu escrevo o código; a IA revisa e explica.
- Explique o "porquê" antes do "como".
- Não gere endpoints ou arquivos inteiros prontos. Dê passos pequenos, um arquivo por vez.
- Se eu pedir algo que fuja destes padrões, avise.
- Em erros, me ensine a ler a mensagem antes de dar a solução.

## Arquitetura (não quebrar)
- `models/`: tabelas SQLAlchemy
- `schemas/`: validação de entrada/saída (Pydantic)
- `services/`: regras de negócio (nunca conhecem HTTP)
- `routers/`: endpoints (nunca têm regra de negócio)
- `core/`: configuração, banco e exceções

## Regras de negócio críticas
- Movimentação de estoque é IMUTÁVEL: só existem POST e GET, nunca PUT/PATCH/DELETE.
- `quantidade_em_estoque` só muda por meio de movimentação, nunca por edição direta do produto.
- Criar movimentação e atualizar o estoque acontecem na MESMA transação.
- Saída maior que o estoque disponível deve ser recusada.
- Não excluir categoria ou fornecedor que ainda tenham produtos (FK com RESTRICT + checagem no service).
- cnpj, email (fornecedor), sku (produto) e nome (categoria) são únicos.

## Erros
- Respostas de erro sempre no mesmo formato JSON, com o status HTTP correto.
- Nunca expor stack trace. Nunca devolver 200 em falha.

## Commits
- Conventional Commits (feat:, fix:, docs:, refactor:, chore:, test:).
- Um commit por mudança lógica, com mensagem descritiva.

## Comentários
- O código explica o "o quê"; comentários explicam o "porquê" (decisões, transações, regras complexas).