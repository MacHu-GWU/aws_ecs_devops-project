variable "STAGE" {
  type = string
  description = "stage name, dev | test | prod"
}

variable "LBD_APP_ENVIRONMENT_NAME" {
  type = string
  description = "as a prefix for most of the naming convention."
}
