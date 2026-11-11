#!/usr/bin/env bash
# Executa verificações locais necessárias antes de aprovar um deploy.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

for command in python docker; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'Comando obrigatório não encontrado: %s\n' "$command" >&2
    exit 1
  fi
done

if [[ ! -f .env ]]; then
  printf 'Arquivo .env ausente. Crie-o localmente a partir de .env.example.\n' >&2
  exit 1
fi

if grep -Eq '^(POSTGRES_PASSWORD|JWT_SECRET_KEY)=(|MOCK_ONLY_|replace-|change-me|your-)' .env; then
  printf 'Defina POSTGRES_PASSWORD e JWT_SECRET_KEY locais antes do deploy.\n' >&2
  exit 1
fi

python -m pytest -q
python -m black --check backend/app src tests
python -m flake8 backend/app src tests
docker compose config --quiet

if command -v terraform >/dev/null 2>&1; then
  terraform -chdir=terraform fmt -check -recursive
  terraform -chdir=terraform validate
else
  printf 'Aviso: Terraform não está instalado; validação IaC foi ignorada.\n' >&2
fi

printf 'Checagens concluídas. Revise o plan e obtenha aprovação antes de aplicar produção.\n'
