output "database" {
  description = "The name of the deployed DynamoDB table."
  value       = aws_dynamodb_table.database.name
}

output "endpoint" {
  description = "The URL of the deployed Lambda server."
  value       = aws_lambda_function_url.endpoint.function_url
}
