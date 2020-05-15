variable "STAGE" {
  type = string
  description = "stage name, dev | test | prod"
}

variable "LBD_APP_ENVIRONMENT_NAME" {
  type = string
  description = "as a prefix for most of the naming convention."
}

variable "VPC_ID" {
  type = string
  description = ""
}

variable "SUBNETS" {
  type = list
  description = ""
}
//
//variable "HUB_SERVICE_SAMPLE_WEBAPP_IMAGE_DIGEST" {
//  type = string
//  description = ""
//}
//
//variable "COMMON_TAGS" {
//  type = map
//  description = "common tags for most of AWS Resource"
//}
