# Inputs tipados tornam o módulo reutilizável e validam configuração antes do apply.
variable "name" {
  description = "Nome único da fila principal."
  type        = string
}

variable "environment" {
  description = "Ambiente usado para identificar/taguear os recursos."
  type        = string
}

variable "visibility_timeout_seconds" {
  description = "Período em que uma mensagem recebida fica invisível."
  type        = number
  default     = 30

  validation {
    condition     = var.visibility_timeout_seconds >= 0 && var.visibility_timeout_seconds <= 43200
    error_message = "O visibility timeout deve estar entre 0 e 43200 segundos."
  }
}

variable "message_retention_seconds" {
  description = "Retenção da fila principal, de 60 segundos a 14 dias."
  type        = number
  default     = 345600

  validation {
    condition     = var.message_retention_seconds >= 60 && var.message_retention_seconds <= 1209600
    error_message = "A retenção deve estar entre 60 segundos e 14 dias."
  }
}

variable "max_receive_count" {
  description = "Recebimentos antes de redirecionar a mensagem para a DLQ."
  type        = number
  default     = 5

  validation {
    condition     = var.max_receive_count >= 1
    error_message = "max_receive_count deve ser pelo menos 1."
  }
}

variable "tags" {
  description = "Tags adicionais aplicadas às filas."
  type        = map(string)
  default     = {}
}
