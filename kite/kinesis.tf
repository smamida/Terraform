resource "aws_kinesis_stream" "migration_stream" {
  name             = var.kinesis_stream_name
  shard_count      = 1
  retention_period = 24

  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes"
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
  # encryption_type = "KMS"
  #kms_key_id      = aws_kms_key.kinesis_key.arn
}


# resource "aws_kms_key" "kinesis_key" {
#   description = "KMS key for encrypting Kinesis Data Stream"
#   enable_key_rotation = true

#   policy = <<EOT
# {
#   "Version": "2012-10-17",
#   "Id": "key-policy-1",
#   "Statement": [
#     {
#       "Sid": "AllowRootUser",
#       "Effect": "Allow",
#       "Principal": {
#         "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
#       },
#       "Action": "kms:*",
#       "Resource": "*"
#     },
#     {
#       "Sid": "AllowKinesisToUseKey",
#       "Effect": "Allow",
#       "Principal": {
#         "Service": "kinesis.amazonaws.com"
#       },
#       "Action": [
#         "kms:Encrypt",
#         "kms:Decrypt",
#         "kms:GenerateDataKey",
#         "kms:DescribeKey"
#       ],
#       "Resource": "*",
#       "Condition": {
#         "StringEquals": {
#           "kms:ViaService": "kinesis.${data.aws_region.current.name}.amazonaws.com"
#         }
#       }
#     }
#   ]
# }
# EOT
# }

