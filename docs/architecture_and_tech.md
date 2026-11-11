# Arquitetura e escolhas tecnológicas

## Objetivo do produto

O PyLogic Engine é um ecossistema de aprendizagem prática, não apenas uma API de
analytics. Sua trilha pode evoluir de fundamentos de Python para engenharia de
software, bancos relacionais e NoSQL, cloud AWS/GCP, Terraform e DevOps. O
assistente de IA é uma integração opcional: o domínio e as rotas não dependem de
um fornecedor específico.

## Decisões de tecnologia

### Python

Python combina uma curva de entrada amigável com uso profissional em automação,
plataformas de dados, backend, infraestrutura e ferramentas DevOps. Tipagem
estática opcional, ecossistema amplo e bibliotecas maduras permitem ensinar
fundamentos e, gradualmente, conceitos de produção. A linguagem não substitui
fundamentos de sistemas, segurança ou redes; ela torna-os acessíveis por meio
de exemplos executáveis.

### FastAPI

FastAPI usa type hints para validar contratos, gerar documentação OpenAPI e
integrar dependências. `async`/`await` é útil em I/O concorrente, mas chamadas
bloqueantes devem usar bibliotecas assíncronas ou ser isoladas em threadpool.
O domínio permanece em funções e tipos independentes do framework para poder
ser testado sem servidor HTTP.

### PostgreSQL

PostgreSQL é o armazenamento transacional de referência para identidades,
eventos e estado de aprendizagem que exija consistência. Constraints,
transações, índices e agregações SQL oferecem uma base clara para estudar
modelagem relacional e analytics. Migrações Alembic são revisadas e aplicadas
explicitamente, sem alterações de esquema implícitas no startup.

### AWS SQS

SQS absorve picos e separa o produtor de telemetria de seus consumidores.
O produtor persiste o evento primeiro e publica uma mensagem de forma opcional;
workers podem ser escalados independentemente e mensagens problemáticas podem
ser encaminhadas para dead-letter queue. SQS oferece entrega *at-least-once*:
consumidores devem ser idempotentes e tolerar duplicatas. A fila não substitui
o registro transacional no banco.

## Limites e fluxo de dados

```text
Usuário
  │ HTTP + JWT
  ▼
FastAPI ───────────────► PostgreSQL (fonte de verdade transacional)
  │                          │
  ├──► adapter de IA          └──► consultas agregadas protegidas por usuário
  │     (opcional, timeout)
  │
  └──► SQS (opcional) ──► consumidor/workers independentes
                            └──► analytics, notificações ou materializações
```

- **API:** autentica, valida e coordena as operações.
- **Domínio (`src/domain`):** lógica pura e regras de aprendizagem sem
  dependências de rede, banco ou provedor de IA.
- **Serviços:** fronteiras de integração com SQS, banco e o adapter de IA.
- **PostgreSQL:** persistência relacional e consultas consistentes.
- **SQS:** comunicação assíncrona; configurada por `SQS_QUEUE_URL`.
- **IA:** configurada por variáveis de ambiente. Sem configuração, o endpoint
  responde explicitamente que o serviço está indisponível, sem fallback que
  finja ter produzido uma resposta.

## Segurança e confiabilidade

- Secrets são fornecidos por ambiente/secret manager e nunca versionados.
- Produção deve usar IAM Role/workload identity, credenciais temporárias,
  TLS, rotação e permissões mínimas.
- JWT tem expiração; senhas são armazenadas com Argon2.
- Endpoints de aprendizagem que chamam serviços pagos exigem autenticação e
  limites de uso devem ser aplicados no gateway/serviço de produção.
- Integrações externas têm timeout e erros explícitos; não registrar tokens,
  prompts privados ou respostas de erro contendo dados sensíveis.
- Para tornar publicação no SQS atômica em relação ao commit do banco, adote o
  padrão **Transactional Outbox**: grava evento e mensagem outbox na mesma
  transação; um publisher separado envia e marca a mensagem. A implementação
  inicial é deliberadamente menor e documenta essa evolução necessária.

## Caminho de evolução

1. Separar workers consumidores de SQS e incluir idempotency key.
2. Adicionar outbox, DLQ alarmes e dashboards.
3. Persistir cursos, trilhas e progresso com migrações e políticas de retenção.
4. Aplicar rate limiting, auditoria, quotas e controle de custo do assistente.
5. Implantar em AWS ou GCP mantendo adapters e contratos independentes do
   provedor.
