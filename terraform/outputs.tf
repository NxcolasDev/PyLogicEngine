// Outputs expõem identificadores não secretos para configuração da aplicação.
output "queue_url" {
  description = "URL da fila principal para configurar SQS_QUEUE_URL na aplicação."
  value       = aws_sqs_queue.telemetry.url
}

output "queue_arn" {
  description = "ARN da fila principal para políticas IAM do produtor/consumidor."
  value       = aws_sqs_queue.telemetry.arn
}

output "dead_letter_queue_arn" {
  description = "ARN da fila de dead-letter para monitoramento."
  value       = aws_sqs_queue.dead_letter.arn
}
