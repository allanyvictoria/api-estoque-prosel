# API de Estoque: Prosel Ecomp Jr. 2026.2

API REST para gerenciar produtos, fornecedores, categorias e movimentações de
estoque da loja "愚公移山 Variedades", substituindo o controle feito em papel.

## Tecnologias
Python, FastAPI, PostgreSQL, SQLAlchemy 2 e Alembic.

## Como rodar

```bash
git clone https://github.com/allanyvictoria/api-estoque-prosel.git
cd api-estoque-prosel
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

1. Crie um banco PostgreSQL vazio (ex.: `estoque_db`).
2. Copie `.env.example` para `.env` e preencha a `DATABASE_URL`.
3. Crie as tabelas: `alembic upgrade head`
4. Suba a API: `uvicorn app.main:app --reload`
5. Documentação interativa (Swagger): http://127.0.0.1:8000/docs

## Estrutura
```
app/
├── core/       configuração, banco e exceções
├── models/     tabelas (SQLAlchemy)
├── schemas/    validação de entrada e saída (Pydantic)
├── services/   regras de negócio e transações
└── routers/    endpoints
alembic/        migrations
```

## Formato padrão de erro
Todo erro devolve o status HTTP adequado e este corpo (nunca stack trace):
```json
{"erro": "NAO_ENCONTRADO", "mensagem": "Categoria 7 não encontrada."}
```

| Status | Quando |
|---|---|
| 400 | Dados inválidos (campo ausente, CNPJ inválido, `skip` negativo) e regras de negócio (estoque insuficiente) |
| 404 | Recurso inexistente |
| 405 | Método não permitido (ex.: editar uma movimentação) |
| 409 | Duplicidade (nome, SKU, CNPJ, e-mail) ou exclusão bloqueada por vínculo |
| 500 | Erro interno (mensagem genérica; o detalhe fica só no log do servidor) |

## Endpoints

### Categorias
| Método | Rota | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/categorias` | Cria | 201 | 400, 409 |
| GET | `/categorias?skip=0&limit=100` | Lista (paginada) | 200 | 400 |
| GET | `/categorias/{id}` | Busca por ID | 200 | 404 |
| PUT | `/categorias/{id}` | Atualiza | 200 | 400, 404, 409 |
| DELETE | `/categorias/{id}` | Exclui (bloqueado se houver produtos) | 204 | 404, 409 |

Body (POST/PUT): `{"nome": "Eletrônicos"}`

### Fornecedores
| Método | Rota | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/fornecedores` | Cria | 201 | 400, 409 |
| GET | `/fornecedores?skip=0&limit=100` | Lista | 200 | 400 |
| GET | `/fornecedores/{id}` | Busca por ID | 200 | 404 |
| PUT | `/fornecedores/{id}` | Atualiza | 200 | 400, 404, 409 |
| DELETE | `/fornecedores/{id}` | Exclui (bloqueado se houver produtos) | 204 | 404, 409 |

Body (POST/PUT):
```json
{"nome": "Importadora Sol", "cnpj": "11.222.333/0001-81",
 "telefone": "75999990000", "email": "contato@sol.com"}
```
O CNPJ é validado (dígitos verificadores) e guardado só com os 14 dígitos.

### Produtos
| Método | Rota | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/produtos` | Cria (nasce com estoque 0) | 201 | 400, 404, 409 |
| GET | `/produtos` | Lista. Filtros: `nome`, `categoria_id`, `fornecedor_id`, `skip`, `limit` | 200 | 400 |
| GET | `/produtos/estoque-minimo` | Produtos com `quantidade_em_estoque <= estoque_minimo` | 200 | 400 |
| GET | `/produtos/{id}` | Busca por ID | 200 | 404 |
| PUT | `/produtos/{id}` | Atualiza (não altera o saldo) | 200 | 400, 404, 409 |
| DELETE | `/produtos/{id}` | Exclui (bloqueado se houver movimentações) | 204 | 404, 409 |

Body (POST/PUT):
```json
{"nome": "Fone Bluetooth", "sku": "FONE-001", "preco_custo": "35.00",
 "preco_venda": "69.90", "estoque_minimo": 5, "categoria_id": 1, "fornecedor_id": 1}
```

### Movimentações (imutáveis: só criação e consulta)
| Método | Rota | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/movimentacoes` | Registra entrada/saída e atualiza o estoque | 201 | 400, 404 |
| GET | `/movimentacoes` | Histórico. Filtros: `data_inicio`, `data_fim` (AAAA-MM-DD), `fornecedor_id`, `produto_id`, `tipo`, `skip`, `limit` | 200 | 400 |
| GET | `/movimentacoes/{id}` | Busca por ID | 200 | 404 |

Body (POST): `{"tipo": "saida", "produto_id": 1, "quantidade": 3}` (`tipo`: `entrada` ou `saida`)

Exemplo de erro (saída maior que o saldo), status 400:
```json
{"erro": "ESTOQUE_INSUFICIENTE", "mensagem": "Estoque insuficiente: disponível 10, solicitado 50."}
```

## Decisões de arquitetura
- **Camadas:** router (HTTP) → service (regras e transação) → model (banco). O router não tem regra de negócio e o service não conhece HTTP.
- **Integridade:** FKs com `ON DELETE RESTRICT`; unicidade de nome (categoria), SKU, CNPJ e e-mail garantida no banco; `CHECK` impede estoque negativo e quantidade de movimentação ≤ 0. O service checa antes para devolver mensagem clara.
- **Auditoria:** o saldo só muda por movimentação, e o `PUT` de produto não aceita `quantidade_em_estoque`. Movimentações não têm rota de edição nem exclusão.
- **Transação:** a movimentação e a atualização do saldo ocorrem no mesmo `commit`; qualquer falha faz `rollback`.
- **Concorrência (diferencial):** lock pessimista (`SELECT ... FOR UPDATE`) no produto durante a movimentação, para duas saídas simultâneas não gerarem estoque negativo.
- **Dinheiro:** `Numeric(10,2)`, não float.
- **Estoque mínimo:** campo `estoque_minimo` no produto (além dos campos exigidos) para viabilizar a consulta de reposição.
- **Migrations:** Alembic versiona o schema.

## Diferenciais
- Concorrência: implementada. [Testes automatizados: preencher se fizer. Autenticação JWT: preencher se fizer.]

## Uso de IA
[Escreva com suas palavras: o que aceitou como veio, o que reescreveu e por quê. Exemplos de coisas que você de fato fez: corrigiu o nome da coluna `quantidade_em_estoque`, corrigiu o `.limit(1)` do `buscar_por_id`, corrigiu a validação de `skip`/`limit`, ajustou o Enum, decidiu a regra de exclusão.]