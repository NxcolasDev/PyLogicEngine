# Variáveis mantêm configuração por ambiente separada do código e facilitam revisão.
variable "aws_region" {
  description = "Região AWS onde as filas serão provisionadas."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Nome do ambiente, usado para identificar recursos."
  type        = string
  default     = "dev"
}

variable "queue_name" {
  description = "Prefixo lógico para a fila de telemetria."
  type        = string
  default     = "pylogic-telemetry"
}

variable "visibility_timeout_seconds" {
  description = "Tempo de invisibilidade da mensagem após recebimento."
  type        = number
  default     = 30

  validation {
    condition     = var.visibility_timeout_seconds >= 0 && var.visibility_timeout_seconds <= 43200
    error_message = "O visibility timeout deve estar entre 0 e 43200 segundos."
  }
}

variable "message_retention_seconds" {
  description = "Retenção da fila principal em segundos."
  type        = number
  default     = 345600

  validation {
    condition     = var.message_retention_seconds >= 60 && var.message_retention_seconds <= 1209600
    error_message = "A retenção deve estar entre 60 segundos e 14 dias."
  }
}

variable "tags" {
  description = "Tags adicionais aplicadas aos recursos."
  type        = map(string)
  default     = {}
}
