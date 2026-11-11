<div align="center">
<img src="assets/logo.png" alt="PyLogic Engine" width="160"/>
<h1>PyLogic Engine</h1>
<p>Ecossistema de aprendizagem interativa para Python, Cloud, dados, Terraform e DevOps.</p>

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
</div>

## Visão geral

O PyLogic Engine combina CLI, API de aprendizagem, analytics e um assistente de
IA opcional. A trilha abrange fundamentos e engenharia Python, cloud AWS/GCP,
bancos SQL/NoSQL, Terraform e DevOps. Eventos são persistidos no PostgreSQL e
podem ser publicados em SQS. O assistente usa um adapter configurável por
ambiente e funciona sem acoplar domínio ou rotas a um fornecedor.

## Arquitetura

```text
[Cliente / Swagger UI] --REST--> [FastAPI: JWT + Analytics]
[CLI Python src/] -------------> [Motor de lógica]
[FastAPI] ----------------------> [PostgreSQL: usuários/eventos]
[FastAPI] ----------------------> [AWS SQS opcional: Terraform]
[FastAPI /learning/assistant] --> [Adapter de IA opcional]
```

## Requisitos

- Docker com Docker Compose v2 para execução completa.
- Python 3.12+ e PostgreSQL acessível para execução local sem Docker.
- Terraform 1.5+ e credenciais AWS fornecidas pelo ambiente (apenas para
  provisionar a fila).

## Executar com Docker Compose

1. Copie `.env.example` para `.env` e substitua todos os valores `MOCK_ONLY`
por valores locais fortes para
`POSTGRES_PASSWORD` e `JWT_SECRET_KEY` (pelo menos 32 caracteres). Uma chave
pode ser gerada com `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. Inicialize a API e o banco:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose lê `.env` para interpolar configurações; não versione esse arquivo.
A API aguarda o healthcheck do PostgreSQL e executa `alembic upgrade head`
antes de iniciar.
3. Acesse a documentação interativa em <http://localhost:8000/docs> e a
verificação de saúde em <http://localhost:8000/health>.
4. Finalize com `docker compose down`. Os dados permanecem no volume nomeado;
use `docker compose down -v` somente se quiser removê-los.

O `.env.example` contém exclusivamente placeholders fictícios e não são
credenciais. O `.env` local é ignorado pelo Git; nunca o versione nem reutilize
esses mocks em ambientes reais.

Para publicar telemetria na SQS, configure `AWS_REGION` e `SQS_QUEUE_URL` no
`.env`. Em desenvolvimento local, o SDK pode receber `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY` e `AWS_SESSION_TOKEN` do ambiente. Em produção, prefira
IAM Roles/credenciais temporárias. Sem `SQS_QUEUE_URL`, a API ainda armazena os
eventos no PostgreSQL.

O assistente opcional aceita um endpoint compatível com Chat Completions por
`AI_API_URL`, `AI_MODEL`, `AI_TIMEOUT_SECONDS` e `AI_API_KEY`. Use um secret
manager em produção; quando não configurado, `/api/v1/learning/assistant`
responde `503` explicitamente. O endpoint requer usuário autenticado. Não envie
segredos, dados pessoais ou informações confidenciais em prompts.

## Execução local

Crie um ambiente virtual, instale as dependências e exporte `DATABASE_URL` e
`JWT_SECRET_KEY`. O endereço de banco deve usar o driver `psycopg`, por exemplo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg://usuario:senha@localhost:5432/pylogic"
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
alembic -c backend/alembic.ini upgrade head
uvicorn app.main:app --app-dir backend --reload
```

As migrações devem ser aplicadas antes de iniciar a API. Os dados de conexão e
segredos são configuração do ambiente, não valores padrão no código.

## API

- `POST /api/v1/auth/register`: cria usuário; corpo `{"email":"...","password":"..."}`.
- `POST /api/v1/auth/login`: recebe formulário OAuth2 (`username` e `password`)
  e retorna um token Bearer.
- `POST /api/v1/analytics/events`: registra evento autenticado.
- `GET /api/v1/analytics/events`: lista eventos do usuário; aceita `severity`,
  `created_after`, `created_before`, `limit` e `offset`.
- `GET /api/v1/analytics/summary`: agrega contagens por severidade para o usuário.
- `POST /api/v1/learning/assistant`: pergunta educacional para adapter de IA
  opcional, com limite de tamanho e autenticação.

## Banco e índices

Alembic versiona o esquema, evitando alterações implícitas no startup.
Analytics combina `JOIN` entre eventos e usuários para limitar os resultados
ao usuário autenticado, e usa `COUNT`/`GROUP BY` para agregar por severidade.
Índices em `severity` e `created_at` aceleram filtros frequentes; o índice
composto por usuário/data ajuda a paginação e os filtros de intervalo.

## Testes

```powershell
pytest
```

Os testes de API usam SQLite temporário e substituem a dependência de banco,
sem exigir um PostgreSQL em execução. A suíte também protege o comportamento
existente da CLI/motor de lógica.

## Terraform (AWS SQS modular)

```powershell
cd terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var="aws_region=us-east-1"
terraform apply -var="aws_region=us-east-1"
terraform output queue_url
```

O módulo reutilizável está em `terraform/modules/sqs`; a raiz compõe a fila de
telemetria e DLQ. Inputs/outputs facilitam criar recursos com configuração
consistente sem duplicar recursos. O provider AWS segue a cadeia padrão de
credenciais; nunca coloque chaves no código Terraform. O backend local é o
padrão do Terraform, portanto configure um backend remoto e um `key` distinto
por ambiente antes de compartilhar/operar infraestrutura.

## Fluxo Git e Conventional Commits

- `main` contém código integrado e revisado; não faça push direto.
- `feature/<nome-curto>` implementa evolução, por exemplo
  `feature/learning-assistant`.
- `hotfix/<nome-curto>` corrige produção com escopo mínimo e revisão urgente.
- Abra Pull Request para `main`; CI executa testes, Black, Flake8 e valida os
  títulos de todos os commits da PR.
- Use commits como `feat(api): add learning assistant`, `fix(auth): reject
  expired token`, `docs: explain database indexes`, `chore(ci): pin toolchain`
  e `test: cover learner isolation`.
- Execute `bash scripts/conventional_commit.sh` para montar uma mensagem ou
  `bash scripts/deploy_check.sh` antes de uma promoção de ambiente.

## Referências oficiais

- [Python](https://docs.python.org/3/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Terraform](https://developer.hashicorp.com/terraform/docs)
- [AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [Google Cloud](https://cloud.google.com/docs)

## Guias de estudo

- [Arquitetura e tecnologias](docs/architecture_and_tech.md)
- [SQL e NoSQL](docs/databases_guide.md)
- [Cloud e Terraform](docs/cloud_and_terraform.md)
- [Python do básico ao avançado](docs/python_mastery.md)

## Estrutura principal

```text
backend/app/       API, configuração, domínio, serviços e rotas
backend/migrations/ Migrações Alembic
terraform/         Fila SQS e variáveis AWS
terraform/modules/ Módulos IaC reutilizáveis
docs/              Guias técnicos e trilhas de estudo
scripts/           Checagens locais de commit e deploy
.github/workflows/ CI para pull requests
tests/             Testes da CLI e da API
src/               Motor/CLI Python existente
```
