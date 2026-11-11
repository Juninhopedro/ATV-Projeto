# Sertão Digital — API de Transferências

API de carteira digital desenvolvida em Python 3.12, FastAPI, SQLAlchemy e PostgreSQL 16, conforme o desafio **Projeto: Transferências**.

## Regras do desafio implementadas

- Cada usuário começa com 1.000 moedas.
- O saldo não pode ficar negativo: validação na aplicação e `CHECK` no PostgreSQL.
- A soma dos saldos é conservada em toda transferência confirmada.
- Valores de transferência são inteiros estritos: `150` é válido; `"150"`, `150.0`, `true`, zero, negativos e campo ausente são inválidos.
- A origem é obtida exclusivamente do JWT; o cliente informa somente destino e valor.
- A mesma origem/destino/valor não pode ser efetivada novamente em menos de 60 segundos.
- A duplicidade é verificada antes do saldo.
- Um advisory transaction lock serializa requisições idênticas concorrentes.
- As linhas das duas contas são bloqueadas em ordem crescente e atualizadas com refresh do estado bloqueado.
- Débito, crédito e registro são confirmados na mesma transação PostgreSQL.
- `GET /auditoria` retorna contagem de usuários, soma de saldos e transferências efetivadas.
- O volume Docker mantém os dados quando os serviços são parados sem `-v` e iniciados novamente.

## Arquitetura

`Cliente HTTP -> FastAPI -> SQLAlchemy -> PostgreSQL`

Cadastro e login usam hash Argon2 e token JWT. O usuário autenticado é resolvido a partir do token. Na transferência, o PostgreSQL serializa a mesma chave lógica (origem, destino e valor) com `pg_advisory_xact_lock`. Após a verificação de duplicidade, a aplicação bloqueia as contas com `SELECT ... FOR UPDATE`, sempre em ordem crescente, e atualiza os dois saldos e o registro dentro da mesma transação.

A consulta de auditoria usa uma única instrução SQL para ler os totais no mesmo snapshot.

## Pré-requisitos

- Docker Desktop com Docker Compose v2.
- Git (para publicar o repositório).
- VS Code (recomendado para editar e acompanhar os arquivos).

## Configuração e inicialização exigida

Na pasta raiz do projeto, copie `.env.example` para `.env` e defina uma chave JWT longa. No PowerShell:

```powershell
Copy-Item .env.example .env
```

No macOS/Linux:

```bash
cp .env.example .env
```

Para iniciar exatamente conforme o enunciado:

```bash
docker compose down -v
docker compose up --build -d
```

O serviço da aplicação chama-se `api` e publica `localhost:8080`. O PostgreSQL é iniciado como serviço `db`; seu volume é `postgres_data`.

> **Atenção ao `-v`:** `docker compose down -v` remove o volume e apaga os dados existentes. Esse comando é adequado para a inicialização limpa solicitada pelo desafio. Para parar e reiniciar preservando dados, use `docker compose down` (sem `-v`) e depois `docker compose up -d`.

Verifique:

```bash
docker compose ps
docker compose logs --tail=100 api
curl http://localhost:8080/health
```

Documentação interativa: <http://localhost:8080/docs>.

## Endpoints

| Método | Rota | Autenticação | Sucesso |
|---|---|---|---|
| POST | `/auth/registrar` | Não | 201 Created |
| POST | `/auth/login` | Não | 200 OK `{ "token": "..." }` |
| GET | `/conta` | Bearer | 200 OK `{ "username": "joao", "saldo": 1000 }` |
| POST | `/transferencias` | Bearer | 201 Created |
| GET | `/auditoria` | Não | 200 OK |

### Exemplos com curl

Cadastrar dois usuários:

```bash
curl -X POST http://localhost:8080/auth/registrar \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123"}'

curl -X POST http://localhost:8080/auth/registrar \
  -H "Content-Type: application/json" \
  -d '{"username":"maria","password":"senha123"}'
```

Login:

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123"}'
```

Copie o token e use-o no cabeçalho:

```bash
curl http://localhost:8080/conta \
  -H "Authorization: Bearer SEU_TOKEN"
```

Transferir 150 moedas:

```bash
curl -X POST http://localhost:8080/transferencias \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"destino":"maria","valor":150}'
```

Auditoria pública:

```bash
curl http://localhost:8080/auditoria
```

## Códigos de rejeição do contrato

Todas as rejeições de negócio abaixo têm exatamente o corpo `{"error":"CODIGO"}`.

| Situação | HTTP | Corpo exato |
|---|---:|---|
| Valor ausente, texto, decimal, booleano, zero ou negativo | 422 | `{"error":"VALOR_INVALIDO"}` |
| Destino igual à origem | 422 | `{"error":"MESMA_CONTA"}` |
| Destino não cadastrado | 404 | `{"error":"DESTINO_INEXISTENTE"}` |
| Mesma transferência efetivada há menos de 60 s | 409 | `{"error":"TRANSFERENCIA_DUPLICADA"}` |
| Saldo insuficiente | 409 | `{"error":"SALDO_INSUFICIENTE"}` |
| Usuário já existente | 409 | `{"error":"USUARIO_EXISTENTE"}` |
| Login inválido | 401 | `{"error":"CREDENCIAIS_INVALIDAS"}` |
| Token ausente ou inválido | 401 | `{"error":"NAO_AUTENTICADO"}` |

Falhas operacionais inesperadas são registradas no log e retornam HTTP 503 com `{"error":"ERRO_INTERNO"}`; não são tratadas como rejeições de negócio previstas no PDF.

## Testes automatizados

Os testes usam um banco separado chamado `sertao_digital_test`, criado pelo script `db/init/01-create-test-db.sql`. O banco principal `sertao_digital` não é apagado pelo pytest.

Depois de subir o Compose, execute dentro do contêiner da API:

```bash
docker compose exec api pytest -q
```

A suíte cobre cadastro, hash de senha, login inválido, JWT, propriedade da conta, saldo inicial, valores inválidos, códigos e corpos exatos, destino inexistente, mesma conta, saldo insuficiente, duplicidade antes do saldo, requisições idênticas simultâneas, transferências concorrentes diferentes, conservação, rollback após falha simulada e auditoria.

Para rodar pytest no computador host, instale `requirements.txt` e defina `TEST_DATABASE_URL` apontando para `localhost:5432/sertao_digital_test`. A porta PostgreSQL está publicada somente em `127.0.0.1`.

## Variáveis de ambiente

- `DATABASE_URL`: conexão do banco principal.
- `TEST_DATABASE_URL`: conexão do banco isolado de testes.
- `JWT_SECRET`: segredo de assinatura JWT; use chave aleatória longa fora de demonstrações locais.
- `TOKEN_MINUTES`: validade do token (padrão 120 minutos).

As credenciais e a chave padrão do Compose são apenas para desenvolvimento/aula. Não use em produção.

## Relatório da revisão

O arquivo `docs/relatorio_revisao.md` registra as correções realizadas, verificações estáticas executadas, limitações do ambiente e pendências para validação final.

## GitHub e apresentação

1. Crie o repositório `sertao-digital` no GitHub.
2. Envie o código-fonte, `Dockerfile`, `docker-compose.yml`, `db/init`, testes, README e `docs`.
3. Não envie `.env`, tokens ou segredos reais.
4. Preencha no slide final os cinco nomes dos integrantes e a turma.
5. Faça uma inicialização limpa em uma máquina com Docker e execute `docker compose exec api pytest -q` antes da apresentação.

O PDF informa entrega em **17/11 às 23h59** e apresentação/testes em **19/11**. A apresentação deve durar cinco minutos e ser feita por dois integrantes sorteados na hora.

## Pontos para explicar na apresentação

- **Advisory lock:** serializa operações com mesma origem, destino e valor.
- **Duplicidade antes do saldo:** uma repetição recebe `TRANSFERENCIA_DUPLICADA`, mesmo se o saldo atual não comportar a operação.
- **SELECT FOR UPDATE + populate_existing:** bloqueia as contas e atualiza os objetos ORM com os saldos efetivamente lidos após a espera do lock.
- **Atomicidade:** débito, crédito e registro são uma única transação; `commit` confirma tudo e `rollback` desfaz tudo.
- **Conservação:** cada transferência reduz e aumenta exatamente o mesmo valor.
- **Persistência:** o volume PostgreSQL sobrevive a `docker compose down` sem `-v`.
