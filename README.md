# desafio_chat_cm_redis

para rodar:
`uvicorn app.main:app --reload`

# Redis

## O que é?
O Redis (Remote Dictionary Server) é um banco de dados em memória, de código aberto, usado principalmente como cache, armazenamento de dados em tempo real e sistema de mensagens. Ele é extremamente rápido porque mantém os dados na memória RAM (em vez de gravar no disco como bancos tradicionais).

Ele é extremamente rápido. Armazena dados no formato de chave e valor. Possui estruturas próprias como strings, listas, sets, hashes e pub/sub. O desempenho do Redis é alto porque os dados ficam na memória.

O Pub/Sub permite que vários clientes recebam mensagens ao mesmo tempo, mas não guarda histórico. Se um cliente estiver desconectado, ele perde a mensagem. Por isso, normalmente ele é combinado com listas, garantindo que mensagens antigas possam ser recuperadas.


## Para que é usado?
É usado principalmente para:

Uso Descrição
* ``Cache``: Guardar dados temporários para acesso ultra rápido, reduzindo carga em banco de dados
* ``Session Store``: Salvar sessões de usuário em aplicações web e microserviços
* ``Fila e Mensageria``: Usado como broker de mensagens, filas, pub/sub e streams
* ``Contadores e Rankings``: Para likes, views, rankings de jogos, contagens em tempo real
* ``Rate Limiting``: Bloquear excesso de requisições (ex: limitar 100 requisições/minuto)
* ``Real-time analytics``: Métricas e dashboards com atualização instantânea

## Vantagens

* Extremamente rápido (milhões de execuções por segundo)
* Baixa latência
* Suporte a persistência opcional
* Escalável e distribuído

# Comandos
```bash
# Entra no terminal do redis 
# PARAMETROS: 
# * --raw habilita a exebição do padrão utf-8
redis-cli

# adiciona uma nova chave com um valor respectivo
# PARAMETROS:
# * NX no final da sentença não adiciona o campo caso ele já exista
# * XX no final da sentença altera um campo caso ele já exista, senão existe ele não cria um novo campo
SET key "value"
-----
SET dia_31_otc "Dia do Hallowenn"

# busca o valor pertecente a uma chave
GET key
-----
GET dia_31_otc

# rotorna todas as chaves cadastradas
KEYS *

# Cria uma lista ordenada baseado no parametro order
ZADD key order "value"
-----
ZADD dia_31 5 "Acordar"
ZADD dia_31 10 "Almocar"
ZADD dia_31 11 "Ir trabalhar"
ZADD dia_31 13 "Chegar no trabalho"

# lista elementos da lista do valor inicial ao final
ZRANGE key init end
ZRANGE dia_31 0 -1

# cria uma pilha
LPUSH key value
-----
LPUSH dia_01 "sabado"
LPUSH dia_01 "comprar potes de vidro"
LPUSH dia_01 "Sair no date"

# lista os elementos da pilha do valor inicial ao final
LRANGE key init end
LRANGE dia_31 0 -1

# cria uma chave com o campo de dicionário
HSET key field value {field value}...
HSET pessoa_01 nome "jose carlos" idade 22 raca "negro/pardo" genero "masculino"

# lista as keys cadastrada nesse campo
HKEYS key
HKEYS pessoa_01

# lista os valores cadastrados em cada um dos campos
HVALS key
HVALS pessoa_01

# limpa todos os dados salvos no banco
FLUSHDB

# Mostra o valor antida da key e substitui pelo novo valor informado
# a inserção funciona igual a uma inserção normal
GETSET key value
GETSET tarefa:001 "Sobreescreve mensagem da key"

# Permite visualização de n keys
MGET key key1 key2...
MGET tarefa:001 tarefa:002 tarefa:003

# Permite a inserção de n chaves-valor
MSET key1 value1 key2 value2
MSET tarefa:004 "Verificacao de emails as 15:15 Hrs" tarefa:005 "Analise do novo contrato as 16:45 Hrs"

# junta o valor informado com o texto já presente na key
APPEND key value
# tarefa:001 > "Reuniao com a equipe as 10:05 Hrs"
APPEND tarefa:001 "- CONClUIDO"
# tarefa:001 > "Reuniao com a equipe as 10:05 Hrs - CONClUIDO"

# apaga uma key
DEL key

# coloca uma validade na key
EXPIREAT key timestamp
EXPIREAT tarefa:001 1762172760

# Fala a quantidade de tempo para uma tarefa estar expirada
TTL tarefa:001

```

### Boas práticas de nomeclatura
Namesapce:Subspace:Identificador