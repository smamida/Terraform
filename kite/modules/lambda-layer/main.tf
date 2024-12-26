locals {
  zip_file_basename = "${var.layer_name}-layer"
  filename          = "${path.module}/${local.zip_file_basename}.zip"
  pip_dest          = "${path.module}/${local.zip_file_basename}"
}

resource "null_resource" "layer_dependencies" {
  provisioner "local-exec" {
    command = <<-EOT
      rm -rf "${local.pip_dest}/python" && mkdir -p "${local.pip_dest}/python"
      rm ../${local.zip_file_basename}.zip
      pip install --quiet -r ${var.requirements_file} -t "${local.pip_dest}/python"
      cd ${local.pip_dest} && zip -r "../${local.zip_file_basename}.zip" .
    EOT
  }

  triggers = {
    requirements_hash = filemd5(var.requirements_file)
    filename          = local.filename
    pip_dest          = local.pip_dest
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
        rm -f ${self.triggers.filename}
        rm -rf ${self.triggers.pip_dest}
        EOT
  }
}

resource "aws_lambda_layer_version" "layer" {
  filename   = local.filename
  layer_name = var.layer_name

  compatible_runtimes = [var.python_runtime]

  depends_on = [null_resource.layer_dependencies]
}

output "layer_arn" {
  description = "ARN of the created Lambda layer"
  value       = aws_lambda_layer_version.layer.arn
}
