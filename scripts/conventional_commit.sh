#!/usr/bin/env bash
# Interativamente monta e valida uma mensagem Conventional Commit antes de criar o commit.
set -euo pipefail

types=(feat fix docs style refactor perf test build ci chore revert)
printf 'Tipo de commit:\n'
select type in "${types[@]}"; do
  if [[ -n "${type:-}" ]]; then
    break
  fi
  printf 'Selecione um tipo listado.\n' >&2
done

read -r -p "Escopo opcional (ex.: api, docs; vazio para nenhum): " scope
read -r -p "Resumo curto no imperativo, sem ponto final: " subject

if [[ -z "$subject" || "$subject" == *$'\n'* ]]; then
  printf 'Resumo obrigatório em uma única linha.\n' >&2
  exit 1
fi

if ((${#subject} > 72)); then
  printf 'Mantenha o resumo em até 72 caracteres.\n' >&2
  exit 1
fi

if [[ -n "$scope" ]]; then
  if ! [[ "$scope" =~ ^[a-z0-9._/-]+$ ]]; then
    printf 'Escopo deve usar letras minúsculas, números, ponto, _, / ou -.\n' >&2
    exit 1
  fi
  message="${type}(${scope}): ${subject}"
else
  message="${type}: ${subject}"
fi

printf 'Mensagem: %s\n' "$message"
read -r -p "Criar commit com as alterações staged? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  printf 'Commit cancelado; nenhuma alteração foi criada.\n'
  exit 0
fi

git diff --cached --quiet && {
  printf 'Não há alterações staged. Use git add antes deste script.\n' >&2
  exit 1
}
git commit -m "$message"
