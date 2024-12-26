# # dms.tf
variable "dms_subnet_ids" {
  type        = list(string)
  description = "DMS subnet IDs list"
}

variable "replication_instance_class" {
  type    = string
  default = "dms.t3.medium"
}

variable "dms_source_secrets_name" {
  type        = string
  sensitive   = true
  description = "DMS Source secret name"
}

variable "migration_type" {
  type    = string
  default = "full-load-and-cdc"
}

variable "vpc_id" {
  type = string
}

variable "kinesis_stream_arn" {
  type = string
}

variable "allocated_storage" {
  type    = number
  default = 10
}

variable "target_kinesis_stream_name" {
  type = string
}

variable "table_mappings_rules" {
  type = list(any)
  default = [
    {
      "rule-type" = "selection"
      "rule-id"   = "1"
      "rule-name" = "include-all"
      "object-locator" = {
        "schema-name" = "%"
        "table-name"  = "%"
      }
      "rule-action" = "include"
    }
  ]
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

data "aws_secretsmanager_secret" "dms_source_credentials" {
  name = var.dms_source_secrets_name
}

# Get the latest version of the secret
data "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id = data.aws_secretsmanager_secret.dms_source_credentials.id
}

# Fetch all security groups in the VPC
data "aws_security_groups" "vpc_sg" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

# Decode the JSON secret into a map
locals {
  account_id     = data.aws_caller_identity.current.account_id
  region         = data.aws_region.current.name
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.db_secret_version.secret_string)
}

output "na" {
  value = local.db_credentials
}

# resource "aws_dms_replication_subnet_group" "dms_subnet_group" {
#   replication_subnet_group_description = "Subnet group for DMS"
#   replication_subnet_group_id          = "dms-subnet-group"
#   subnet_ids                           = var.dms_subnet_ids
# }

# resource "aws_dms_replication_instance" "migration_instance" {
#   allocated_storage           = var.allocated_storage
#   apply_immediately           = true
#   replication_instance_class  = var.replication_instance_class
#   replication_instance_id     = "data-migration-instance"
#   replication_subnet_group_id = aws_dms_replication_subnet_group.dms_subnet_group.replication_subnet_group_id
#   vpc_security_group_ids      = data.aws_security_groups.vpc_sg.ids
# }

# resource "aws_dms_endpoint" "source_endpoint" {
#   database_name = "source_database"
#   endpoint_id   = "source-rds-endpoint"
#   endpoint_type = "source"
#   engine_name   = "postgres"
#   server_name   = local.db_credentials.host
#   port          = local.db_credentials.port
#   username      = local.db_credentials.username
#   password      = local.db_credentials.password
# }

# resource "aws_dms_endpoint" "kinesis_endpoint" {
#   endpoint_id         = "kinesis-migration-endpoint"
#   endpoint_type       = "target"
#   engine_name         = "kinesis"
#   service_access_role     = aws_iam_role.dms_vpc_role.arn

#   kinesis_settings {
#     stream_arn = var.kinesis_stream_arn
#     # service_access_role_arn =
#   }
# }

# resource "aws_dms_replication_task" "migration_task" {
#   migration_type           = var.migration_type
#   replication_instance_arn = aws_dms_replication_instance.migration_instance.replication_instance_arn
#   replication_task_id      = "data-migration-task"
#   source_endpoint_arn      = aws_dms_endpoint.source_endpoint.endpoint_arn
#   target_endpoint_arn      = aws_dms_endpoint.kinesis_endpoint.endpoint_arn

#   table_mappings = jsonencode({
#     rules = var.table_mappings_rules
#   })
# }


module "database_migration_service" {
  source  = "terraform-aws-modules/dms/aws"
  version = "2.4.0"

  # Subnet group
  repl_subnet_group_name        = "kite-trackermigration"
  repl_subnet_group_description = "DMS Subnet group"
  repl_subnet_group_subnet_ids  = var.dms_subnet_ids

  # Instance
  repl_instance_allocated_storage            = var.allocated_storage
  repl_instance_auto_minor_version_upgrade   = true
  repl_instance_apply_immediately            = true
  repl_instance_engine_version               = "3.5.2"
  repl_instance_multi_az                     = false
  repl_instance_preferred_maintenance_window = "sun:10:30-sun:14:30"
  repl_instance_publicly_accessible          = false
  repl_instance_class                        = "dms.t3.large"
  repl_instance_id                           = "data-migration-instance"
  repl_instance_vpc_security_group_ids       = data.aws_security_groups.vpc_sg.ids

  endpoints = {
    source = {
      database_name               = local.db_credentials.dbname
      endpoint_id                 = "source-rds-endpoint"
      endpoint_type               = "source"
      engine_name                 = "aurora-postgresql"
      extra_connection_attributes = "heartbeatFrequency=1;"
      username                    = local.db_credentials.username
      password                    = local.db_credentials.password
      port                        = local.db_credentials.port
      server_name                 = local.db_credentials.host
      ssl_mode                    = "none"
      tags                        = { EndpointType = "source" }
    }

    destination = {
      endpoint_id   = "kinesis-destination-endpoint"
      endpoint_type = "target"
      engine_name   = "kinesis"
      tags          = { EndpointType = "destination" }
      kinesis_settings = {
        #  service_access_role_arn        = aws_iam_role.dms_write_to_rating_data_sync.arn
        stream_arn                     = var.kinesis_stream_arn
        partition_include_schema_table = true
        include_partition_value        = true
      }
    }
  }

  replication_tasks = {
    cdc_ex = {
      replication_task_id = "example-cdc"
      migration_type      = "cdc"
      table_mappings = jsonencode({
        rules = var.table_mappings_rules
      })
      source_endpoint_key = "source"
      target_endpoint_key = "destination"
      tags                = { Task = "Aurora-to-Kinesis" }
    }
  }

  # event_subscriptions = {
  #   instance = {
  #     name                             = "instance-events"
  #     enabled                          = true
  #     instance_event_subscription_keys = ["example"]
  #     source_type                      = "replication-instance"
  #     sns_topic_arn                    = "arn:aws:sns:us-east-1:012345678910:example-topic"
  #     event_categories                 = [
  #       "failure",
  #       "creation",
  #       "deletion",
  #       "maintenance",
  #       "failover",
  #       "low storage",
  #       "configuration change"
  #     ]
  #   }
  #   task = {
  #     name                         = "task-events"
  #     enabled                      = true
  #     task_event_subscription_keys = ["cdc_ex"]
  #     source_type                  = "replication-task"
  #     sns_topic_arn                = "arn:aws:sns:us-east-1:012345678910:example-topic"
  #     event_categories             = [
  #       "failure",
  #       "state change",
  #       "creation",
  #       "deletion",
  #       "configuration change"
  #     ]
  #   }
  # }

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}