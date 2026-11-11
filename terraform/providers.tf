# Provider sem chaves embutidas: AWS SDK/CLI/role fornece credenciais pela cadeia padrão.
# Para state compartilhado, configure backend remoto e um key distinto por ambiente
# em arquivo externo durante `terraform init -backend-config=...`.
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
