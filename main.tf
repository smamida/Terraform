provider "aws" {
  region = "ap-south-1"
  
}

resource "aws_iam_role" "lambda_execu_role" {
  name = var.iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
      },
    ],
  })
}


resource "aws_iam_policy" "lambda_policy" {
  name = var.iam_role_policy_name


  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:ap-south-1:471112791735:log-group:*"
      },
      {
        Sid    = "Statement1",
        Effect = "Allow",
        Action = [
          "lambda:*"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:ListSecrets",
          "secretsmanager:DescribeSecret",
          "secretsmanager:PutResourcePolicy",
          "secretsmanager:*",
          "secretsmanager:UpdateSecret"
        ],
        Resource = ["arn:aws:secretsmanager:ap-south-1:471112791735:secret:hanu_sn-iBJsoo"]
      },
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:ListSecrets",
          "secretsmanager:DescribeSecret"
        ],
        Resource = ["*"]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject"
        ],

        Resource = "arn:aws:s3:::${var.s3_bucket_name}/*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execu_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}


resource "aws_lambda_function" "my_lambda" {
  function_name = var.function_name
  s3_bucket     = var.s3_bucket_name
  s3_key        = var.s3_key
  role          = aws_iam_role.lambda_execu_role.arn
  handler       = var.handler
  runtime       = var.runtime




}
