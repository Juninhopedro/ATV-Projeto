# Contrato de respostas do desafio

| Caso | HTTP | Corpo |
|---|---:|---|
| Cadastro | 201 | `{"username":"joao"}` |
| Login | 200 | `{"token":"..."}` |
| Conta | 200 | `{"username":"joao","saldo":1000}` |
| Transferência | 201 | `{"id":1,"origem":"joao","destino":"maria","valor":150,"saldo":850}` |
| Auditoria | 200 | `{"usuarios":2,"somaSaldos":2000,"transferencias":1}` |
| Valor inválido | 422 | `{"error":"VALOR_INVALIDO"}` |
| Mesma conta | 422 | `{"error":"MESMA_CONTA"}` |
| Destino inexistente | 404 | `{"error":"DESTINO_INEXISTENTE"}` |
| Duplicada em menos de 60 s | 409 | `{"error":"TRANSFERENCIA_DUPLICADA"}` |
| Saldo insuficiente | 409 | `{"error":"SALDO_INSUFICIENTE"}` |
| Não autenticado | 401 | `{"error":"NAO_AUTENTICADO"}` |
| Usuário existente | 409 | `{"error":"USUARIO_EXISTENTE"}` |
| Credenciais inválidas | 401 | `{"error":"CREDENCIAIS_INVALIDAS"}` |

Falha operacional inesperada: HTTP 503 `{"error":"ERRO_INTERNO"}`. Essa resposta não substitui nenhum dos códigos de negócio definidos no PDF.
