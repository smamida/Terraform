variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "vpc_id" {
  description = "VPC ID for the infrastructure"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the infrastructure"
  type        = list(string)
}

variable "aurora_pg_secret_name" {
  type        = string
  description = "Secrets manager secret ID of destination instance"
}

variable "lambda_timeout" {
  type        = number
  description = "The no of seconds until lambda timesout"
}

variable "vpc_endpoint_service_name" {
  type        = string
  description = "Name of the service for VPC endpoint communication"
}

variable "vpce_sec_group_ids" {
  type = list(string)
}

variable "python_runtime" {
  type = string
}

variable "dms_source_secrets_name" {
  type        = string
  description = "Secrets manager secret ID of data source for DMS"
}

variable "kinesis_stream_name" {
  type    = string
  default = "data-migration-stream"
}

variable "dms_allocated_storate" {
  type = number
  default = 20
  description = "Storage allocated for DMS service"
}

variable "dms_sg_cidr_Block" {
   type        = list(string)
  description = "List of CIDR blocks for the DMS resources."
}

variable "lambda_sg_cidr_Block" {
   type        = list(string)
  description = "List of CIDR blocks for the DMS resources."
}