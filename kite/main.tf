# Provider Configuration
provider "aws" {
  region = var.region # Replace with your desired region

  # Make it faster by skipping something
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true

  default_tags {
    tags = {
      Environment = "dev"
      Service     = "KiteTracker"
      cost-center = "kite-cost-center"
    }
  }

}

module "dms_setup" {
  source = "./modules/dms"

  dms_source_secrets_name    = var.aurora_pg_secret_name
  kinesis_stream_arn         = aws_kinesis_stream.migration_stream.arn
  allocated_storage          = var.dms_allocated_storate
  vpc_id                     = var.vpc_id
  dms_subnet_ids             = var.subnet_ids
  target_kinesis_stream_name = var.kinesis_stream_name
}