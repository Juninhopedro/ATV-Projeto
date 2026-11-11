# Sertão Digital — roteiro de apresentação (5 minutos)

## Integrante 1 — problema, arquitetura e segurança (aprox. 2min30)

“Nosso projeto é uma API de carteira digital. Cada usuário começa com 1.000 moedas e pode transferir valores inteiros para outro usuário. O desafio é garantir que moedas não sejam criadas nem destruídas, que o saldo nunca fique negativo e que requisições repetidas ou simultâneas não dupliquem uma transferência.

Usamos Python com FastAPI para as rotas, PostgreSQL para persistência e SQLAlchemy para as operações no banco. O login gera um JWT e as senhas são guardadas com hash Argon2.

A origem de uma transferência vem exclusivamente do token. O cliente só informa o destino e o valor; por isso, não consegue escolher a conta de outra pessoa.”

## Integrante 2 — concorrência, atomicidade e demonstração (aprox. 2min30)

“A parte central é a transferência. Primeiro, usamos um advisory lock transacional com a chave origem, destino e valor. Isso faz com que requisições idênticas sejam processadas uma por vez. Depois consultamos se já houve uma transferência igual nos últimos 60 segundos. Essa verificação vem antes do saldo, como exige o desafio.

Em seguida, bloqueamos as duas contas com SELECT FOR UPDATE, sempre em ordem crescente de ID. Também atualizamos os objetos do SQLAlchemy com os valores lidos depois do bloqueio, para não usar saldo antigo em requisições concorrentes diferentes.

O débito, o crédito e o registro são gravados na mesma transação. O commit confirma tudo; se houver falha antes dele, o rollback desfaz tudo. Assim, a transferência acontece inteira ou não acontece.”

## Demonstração sugerida

1. Abrir `http://localhost:8080/docs`.
2. Cadastrar `joao` e `maria`.
3. Fazer login como `joao` e copiar o token.
4. Consultar `/conta`: saldo 1.000.
5. Transferir 150 para `maria`.
6. Consultar os saldos: João 850, Maria 1.150.
7. Consultar `/auditoria`: 2 usuários, soma 2.000 moedas e 1 transferência.
8. Repetir a mesma operação dentro de 60 segundos: `TRANSFERENCIA_DUPLICADA`.
9. Se houver tempo, demonstrar a suíte: `docker compose exec api pytest -q`.

## Perguntas que podem surgir

- **Como evitam duas transferências iguais ao mesmo tempo?** Advisory lock transacional por origem/destino/valor.
- **E se duas transferências diferentes tentarem gastar o mesmo saldo?** SELECT FOR UPDATE bloqueia a conta e `populate_existing()` garante que o saldo seja atualizado após a espera.
- **E se a API cair no meio?** Commit ou rollback do PostgreSQL: débito, crédito e registro não ficam parciais.
- **Como impedem saldo negativo?** Lock da conta, validação do saldo e restrição CHECK no banco.
- **Como garantem que ninguém movimenta outra conta?** A origem é obtida pelo usuário autenticado no JWT.
- **Como os dados sobrevivem ao reinício?** Volume persistente do PostgreSQL; não se usa `down -v` quando a intenção é preservar dados.

## Antes de apresentar

- Preencher os nomes dos cinco integrantes e a turma no slide final.
- Fazer a inicialização limpa com os comandos do PDF.
- Executar todos os testes no PostgreSQL do Compose.
- Guardar a saída do pytest e a demonstração dos saldos/auditoria para comprovar o funcionamento.
