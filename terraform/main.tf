# A fila de dead-letter preserva mensagens que excedem o limite de tentativas.
# O state deve ser isolado por ambiente via backend/key definidos no `terraform init`.
resource "aws_sqs_queue" "dead_letter" {
  name                      = "${var.queue_name}-${var.environment}-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled   = true
  tags                      = merge(var.tags, { Environment = var.environment })
}

resource "aws_sqs_queue" "telemetry" {
  name                       = "${var.queue_name}-${var.environment}"
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds
  sqs_managed_sse_enabled    = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter.arn
    maxReceiveCount     = 5
  })
  tags = merge(var.tags, { Environment = var.environment })
}
