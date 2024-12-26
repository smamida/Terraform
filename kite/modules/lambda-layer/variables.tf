variable "layer_name" {
  description = "Name of the Lambda layer"
  type        = string
}

variable "requirements_file" {
  description = "Path to the requirements.txt file"
  type        = string
}

variable "python_runtime" {
  description = "Python runtime version"
  type        = string
  default     = "python3.11"
}
