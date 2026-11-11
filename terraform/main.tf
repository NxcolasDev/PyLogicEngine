# A raiz compõe módulos reutilizáveis; backend remoto/state por ambiente é configurado no init.
module "telemetry_queue" {
  source = "./modules/sqs"

  name                       = "${var.queue_name}-${var.environment}"
  environment                = var.environment
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds
  tags                       = var.tags
}
