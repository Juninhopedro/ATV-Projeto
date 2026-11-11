# Relatório de revisão — Sertão Digital

## Escopo

Revisão feita contra o PDF `Projeto: Transferências.pdf`, examinando código-fonte, modelos, validação, segurança, rotas, Docker Compose, testes, README e apresentação.

## Correções realizadas nesta revisão

1. **Concorrência entre transferências diferentes:** a consulta `SELECT FOR UPDATE` agora usa `populate_existing()`. Sem isso, o SQLAlchemy poderia devolver objetos já carregados no identity map com saldos antigos depois de esperar pelo lock. Isso poderia sobrescrever um saldo atualizado por outra requisição e quebrar a conservação das moedas.
2. **Janela de duplicidade:** a consulta usa `clock_timestamp()` do PostgreSQL e `created_at` é preenchido pelo relógio do banco. O operador `>` aplica a regra estrita de “menos de 60 segundos”; exatamente 60 segundos não é tratado como duplicidade.
3. **Duplicidade simultânea:** mantido `pg_advisory_xact_lock` por origem/destino/valor; o lock é transacional e fica retido até commit/rollback.
4. **Validação estrita:** `StrictInt` rejeita texto numérico, decimal, booleano, zero, negativo e valor ausente. As credenciais deixaram de impor uma senha mínima não exigida pelo PDF, para que login inválido retorne o código 401 previsto.
5. **Atomicidade:** débito, crédito e inserção da transferência continuam na mesma transação. Falha após flush provoca rollback. Falhas inesperadas passam a retornar HTTP 503 `ERRO_INTERNO`, com detalhes somente no log.
6. **Auditoria:** os três totais são consultados em uma única instrução SQL, evitando leitura em snapshots diferentes.
7. **Persistência e testes:** criado banco separado `sertao_digital_test` via script de inicialização; pytest não apaga o banco principal. O Compose publica PostgreSQL somente em `127.0.0.1` para testes locais.
8. **Prontidão:** `/health` verifica também a conexão com o PostgreSQL; Compose espera o banco saudável antes de iniciar a API.
9. **Cobertura de testes:** adicionados cenários de autenticação, hash Argon2, propriedade da conta, erros exatos, valores inválidos, duplicidade antes do saldo, concorrência idêntica, concorrência com destinos diferentes, limite de 60 segundos, rollback simulado e auditoria.
10. **Documentação:** README e roteiro foram atualizados; slide de concorrência explica `populate_existing()` e o slide final lembra de preencher os cinco nomes e a turma.

## Verificações efetivamente executadas

- `python -m compileall -q app tests`: **PASSOU** (verificação de sintaxe/compilação dos módulos Python).
- Smoke check Pydantic: **PASSOU** para aceitar inteiro positivo e rejeitar texto `"150"`, decimal, booleano, zero, negativo, `null` e campo ausente.
- Leitura estrutural de `docker-compose.yml` com parser YAML: **PASSOU**; serviços `api` e `db`, porta 8080 e volume persistente identificados.
- Apresentação PowerPoint: arquivo aberto e inspecionado; 7 slides identificados e conteúdo de concorrência atualizado.

## Testes de integração não executados

Não foi possível executar `pytest`, construir a imagem ou subir os serviços neste ambiente porque não há Docker/Docker Compose, PostgreSQL/`psql`, nem os módulos `psycopg` e `pwdlib` instalados. Portanto, **nenhum teste de integração ou concorrência real foi declarado aprovado**. Os testes adicionados precisam ser executados em um ambiente com Docker.

## Como validar no computador do grupo

Na raiz do projeto:

```bash
docker compose down -v
docker compose up --build -d
docker compose ps
docker compose exec api pytest -q
```

Depois, abrir `http://localhost:8080/docs` e demonstrar cadastro, login, consulta, transferência, auditoria e repetição da mesma transferência. Para verificar persistência, usar `docker compose down` **sem** `-v`, iniciar com `docker compose up -d` e consultar novamente os saldos.

> O comando `docker compose down -v` apaga os dados do volume. Ele serve para a inicialização limpa do desafio; não deve ser usado no teste de persistência.

## Pendências antes da entrega

- Executar a suíte completa em PostgreSQL real com `docker compose exec api pytest -q` e guardar a saída.
- Se houver falha, corrigir e repetir a suíte.
- Fazer a inicialização limpa em uma máquina do grupo.
- Preencher no slide final os cinco integrantes e a turma.
- Criar o repositório GitHub, enviar todos os arquivos e conferir que `.env` não foi publicado.
- Fazer ensaio de cinco minutos, priorizando advisory lock, `SELECT FOR UPDATE`, `populate_existing()`, commit/rollback e conservação dos saldos.
