output "queue_url" {
  description = "URL da fila para configuração do produtor."
  value       = aws_sqs_queue.this.url
}

output "queue_arn" {
  description = "ARN da fila principal para políticas IAM."
  value       = aws_sqs_queue.this.arn
}

output "dead_letter_queue_arn" {
  description = "ARN da dead-letter queue para alarmes e operação."
  value       = aws_sqs_queue.dead_letter.arn
}
