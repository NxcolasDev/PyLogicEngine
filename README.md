<div align="center">
<img src="assets/logo.png" alt="PyLogic Engine" width="160"/>
<h1>PyLogic Engine</h1>
<p>API de analytics e motor de lógica com FastAPI, PostgreSQL, Alembic e AWS SQS.</p>

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
</div>

## Visão geral

O PyLogic Engine mantém a CLI didática existente e acrescenta uma API REST para
cadastro/autenticação e analytics de eventos. Eventos são persistidos no
PostgreSQL; quando uma URL SQS é configurada, também são publicados na fila.
O acesso AWS usa a cadeia padrão de credenciais do SDK (por exemplo, IAM Role
ou variáveis de ambiente), sem credenciais embutidas no código.

## Arquitetura

```text
[Cliente / Swagger UI] --REST--> [FastAPI: JWT + Analytics]
[CLI Python src/] -------------> [Motor de lógica]
[FastAPI] ----------------------> [PostgreSQL: usuários/eventos]
[FastAPI] ----------------------> [AWS SQS opcional: Terraform]
```

## Requisitos

- Docker com Docker Compose v2 para execução completa.
- Python 3.12+ e PostgreSQL acessível para execução local sem Docker.
- Terraform 1.5+ e credenciais AWS fornecidas pelo ambiente (apenas para
  provisionar a fila).

## Executar com Docker Compose

1. Copie `.env.example` para `.env` e defina valores locais fortes para
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

Para publicar telemetria na SQS, configure `AWS_REGION` e `SQS_QUEUE_URL` no
`.env`. Em desenvolvimento local, o SDK pode receber `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY` e `AWS_SESSION_TOKEN` do ambiente. Em produção, prefira
IAM Roles/credenciais temporárias. Sem `SQS_QUEUE_URL`, a API ainda armazena os
eventos no PostgreSQL.

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

## Terraform (AWS SQS)

```powershell
cd terraform
terraform init
terraform plan -var="aws_region=us-east-1"
terraform apply -var="aws_region=us-east-1"
terraform output queue_url
```

O provider usa a cadeia padrão de credenciais AWS; nunca coloque chaves no
código Terraform. O backend local é o padrão do Terraform, portanto configure
um backend remoto e um `key` distinto por ambiente (por exemplo,
`dev/pylogic/terraform.tfstate` e `prod/pylogic/terraform.tfstate`) antes de
compartilhar ou executar infraestrutura em equipe. Configure o backend durante
`terraform init` por arquivo de configuração seguro fora do repositório, para
isolar o state por ambiente e habilitar controle de acesso/locking conforme o
backend escolhido.

## Estrutura principal

```text
backend/app/       API, configuração, domínio, serviços e rotas
backend/migrations/ Migrações Alembic
terraform/         Fila SQS e variáveis AWS
tests/             Testes da CLI e da API
src/               Motor/CLI Python existente
```
