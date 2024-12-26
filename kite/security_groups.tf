resource "aws_security_group" "dms_sg" {
  name        = "dms-migration-sg"
  description = "Security group for DMS migration"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    #cidr_blocks = ["0.0.0.0/0"]
    cidr_blocks = var.dms_sg_cidr_Block
  }

  tags = {
    Name = "dms-migration-sg"
  }
}

resource "aws_security_group" "lambda_sg" {
  name        = "lambda-migration-sec-group"
  description = "Security group for Lambda function"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    #cidr_blocks = ["0.0.0.0/0"]
    cidr_blocks = var.lambda_sg_cidr_Block
  }

  tags = {
    Name = "lambda-migration-sg"
  }
}
