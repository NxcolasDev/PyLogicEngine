# Cloud e Terraform: AWS, GCP e módulos reutilizáveis

## AWS e GCP

| Conceito | AWS | Google Cloud |
|---|---|---|
| Identidade e permissões | IAM roles/policies | IAM roles/policies |
| Função serverless | AWS Lambda | Cloud Functions / Cloud Run functions |
| Fila gerenciada | Amazon SQS | Cloud Tasks ou Pub/Sub, conforme o padrão |
| SQL gerenciado | Amazon RDS/Aurora | Cloud SQL |
| Objetos | Amazon S3 | Cloud Storage |
| Infraestrutura como código | Terraform e CloudFormation | Terraform e ferramentas Google |

Os serviços não são substitutos um-para-um em todos os detalhes. Escolha
conforme semântica de entrega, integração, requisitos de rede, disponibilidade,
custos, skills e portabilidade. Abstrair tudo em um denominador mínimo pode
esconder capacidades importantes; abstraia contratos de aplicação, não as
diferenças operacionais que precisam ser geridas.

## Serverless e event-driven

Serverless reduz a gestão direta de servidores, não elimina responsabilidade
por capacidade, identidade, custos, observabilidade ou segurança. Em
arquiteturas orientadas a eventos, produtores publicam contratos versionados;
consumidores processam de forma assíncrona. Projete para duplicatas,
reprocessamento, atrasos, mensagens inválidas, DLQ, backpressure e tracing.
Configure timeout, retries e limites de concorrência em conjunto para evitar
amplificar incidentes.

## Por que módulos Terraform?

Um módulo é um conjunto reutilizável de recursos Terraform com inputs
(`variables`), recursos e outputs. A raiz configura provider/ambiente e invoca
o módulo com dados específicos. Assim, a mesma implementação pode criar N
filas com nomes, retenção e parâmetros distintos sem copiar blocos inteiros.

```hcl
module "telemetry_dev" {
  source      = "./modules/sqs"
  name        = "pylogic-telemetry-dev"
  environment = "dev"
}

module "telemetry_prod" {
  source      = "./modules/sqs"
  name        = "pylogic-telemetry-prod"
  environment = "prod"
}
```

Em operação real, reavalie a separação de state por ambiente: ambientes de
produção normalmente têm state, permissões e ciclos de mudança independentes.
O exemplo root chama um módulo de SQS para padronizar recursos e outputs; o
provider e o backend permanecem na raiz, e não dentro do módulo reutilizável.

### Fluxo de uso

1. `terraform fmt -recursive` formata HCL.
2. `terraform init` inicializa providers e backend.
3. `terraform validate` valida configuração.
4. `terraform plan` revisa a mudança antes de aplicar.
5. `terraform apply` exige aprovação e identidade AWS/GCP de menor privilégio.

Use backend remoto com criptografia, controle de acesso e locking quando
disponível; restrinja state porque ele pode conter dados sensíveis de recursos.
Não comite state, plan files, credenciais ou `.tfvars` contendo segredos.
Credenciais devem vir de IAM Role, workload identity, SSO ou secret manager.

## Prática segura de custo

- Defina tags de ambiente, dono, produto e centro de custo.
- Use budgets/alerts e revise custos de invocações, logs e tráfego de rede.
- Configure retenção e DLQ adequadamente; não deixe filas sem monitoramento.
- Use regiões, redundância e backups em conformidade com requisitos do produto.
- Faça `plan` e revisão de mudanças em PR; produção deve ter aprovação explícita.
