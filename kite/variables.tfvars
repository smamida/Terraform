# vpc_id              = "vpc-xxxxxxxx"
subnet_ids                = []
vpc_id                    = "vpc-xxx"
aurora_pg_secret_name     = "aurora-postgres-credentials2"
dms_source_secrets_name   = "dms-source-credentials2"
lambda_timeout            = 600
vpc_endpoint_service_name = "com.amazonaws.ap-south-1.secretsmanager"
vpce_sec_group_ids        = [""]
python_runtime            = "python3.8"
dms_allocated_storate     = 20
dms_sg_cidr_Block         = []
lambda_sg_cidr_Block      = []

