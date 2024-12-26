output "kinesis_stream_arn" {
  value = aws_kinesis_stream.migration_stream.arn
}

# Update outputs to include Lambda function details
output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = module.lambda_function.lambda_function_arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = module.lambda_function.lambda_function_name
}

# output "dms_replication_instance_arn" {
#   value = aws_dms_replication_instance.migration_instance.replication_instance_arn
# }
