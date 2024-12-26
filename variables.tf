
variable "iam_role_name" {
  type        = string
 
}

variable "iam_role_policy_name" { 
  type        = string
}

variable "aws_iam_role_policy_attachment" { 
  type        = string
}
variable "function_name" {
  type        = string
}
variable "region" {
    type = string
}
variable "account_id" {
  type        = string 
}

variable "s3_bucket_name" {
  type = string
}
variable "handler" {
  type = string
}
variable "s3_key" {
  type = string
}
variable "runtime" {
  type = string
}
variable "secret_name" {
  type = string
}



variable "tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
  default     = {
    Environment = "Dev"
    Project     = "CloudTrailSetup"
  }
}