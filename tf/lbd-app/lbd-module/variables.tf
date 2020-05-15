variable "ENVIRONMENT_NAME" {
  type = string
  description = "as a prefix for most of the naming convention."
}

variable "LOGIC_ID" {
  type = string
  description = "resource logic id surfix"
}

variable "IAM_ROLE_ARN" {
  type = string
  description = "lambda execution role arn"
}

variable "DEPLOYMENT_FILE" {
  type = string
}

variable "LOAD_BALANCER_ARN" {
  type = string
}
