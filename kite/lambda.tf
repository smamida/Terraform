module "lambda_layer" {
  source = "./modules/lambda-layer"

  layer_name        = "etl_dependencies"
  requirements_file = "${path.module}/requirements1.txt"
  python_runtime    = var.python_runtime
}

# resource "aws_secretsmanager_secret" "aurora_credentials" {
#   name = var.aurora_pg_secret_name
# }

data "aws_secretsmanager_secret" "aurora_credentials" {
  name = var.aurora_pg_secret_name
}

# Add module for Lambda
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.16.0"

  function_name = "kinesis-to-aurora-processor"
  description   = "Process Kinesis stream and write to Aurora Postgres"

  # Use the local file as the source code
  source_path = "${path.module}/src/etl_handler/app.py"

  # Runtime and handler
  runtime = var.python_runtime
  handler = "app.handler"
  timeout = var.lambda_timeout

  # VPC Configuration
  vpc_subnet_ids         = var.subnet_ids
  vpc_security_group_ids = [aws_security_group.lambda_sg.id]

  # IAM Role and Policies
  attach_network_policy    = true
  attach_policy_statements = true
  policy_statements = {
    kinesis_access = {
      effect = "Allow"
      actions = [
        "kinesis:GetRecords",
        "kinesis:GetShardIterator",
        "kinesis:DescribeStream",
        "kinesis:ListShards"
      ]
      resources = [aws_kinesis_stream.migration_stream.arn]
    }
    secrets_access = {
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue"
      ]
      resources = [data.aws_secretsmanager_secret.aurora_credentials.arn]
    }
  }

  # Environment Variables
  environment_variables = {
    AURORA_SECRET_NAME = data.aws_secretsmanager_secret.aurora_credentials.name
  }

  # Layers (optional, if you need additional Python dependencies)
  layers = [
    module.lambda_layer.layer_arn
  ]

  # Publish the function
  publish                           = true
  cloudwatch_logs_retention_in_days = 90

  # Allowed triggers (optional)
  allowed_triggers = {
    KinesisStreamTrigger = {
      service    = "kinesis"
      source_arn = aws_kinesis_stream.migration_stream.arn
    }
  }

  # Depends on
  depends_on = [aws_security_group.lambda_sg]
}

resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn                   = aws_kinesis_stream.migration_stream.arn
  function_name                      = module.lambda_function.lambda_function_name
  starting_position                  = "LATEST"
  batch_size                         = 100
  maximum_batching_window_in_seconds = 60
}

data "aws_vpc" "selected" {
  id = var.vpc_id
}

module "vpc_endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = "5.0.0"

  vpc_id             = var.vpc_id
  security_group_ids = var.vpce_sec_group_ids

  endpoints = {
    lambda = {
      service             = "lambda"
      private_dns_enabled = true
      subnet_ids          = var.subnet_ids
    },
    secrets_manager = {
      service      = "secretsmanager"
      service_type = "Interface"
      subnet_ids   = var.subnet_ids
    }
  }
}


# resource "aws_lambda_function" "kinesis_processor" {
#   function_name = "kinesis-to-aurora-processor"
#   role          = aws_iam_role.lambda_execution_role.arn
#   handler       = "index.handler"
#   runtime       = "python3.9"

#   vpc_config {
#     subnet_ids         = var.subnet_ids
#     security_group_ids = [aws_security_group.lambda_sg.id]
#   }

#   environment {
#     variables = {
#       SECRET_ARN         = aws_secretsmanager_secret.aurora_credentials.arn
#       AURORA_ENDPOINT    = aws_rds_cluster.aurora_postgres.endpoint
#       KINESIS_STREAM_ARN = aws_kinesis_stream.migration_stream.arn
#     }
#   }

#   source_code_hash = data.archive_file.lambda_code.output_base64sha256
#   filename         = data.archive_file.lambda_code.output_path
# }

# data "archive_file" "lambda_code" {
#   type        = "zip"
#   source_file = "${path.module}/lambda_function.py"
#   output_path = "${path.module}/lambda_function.zip"
# }
