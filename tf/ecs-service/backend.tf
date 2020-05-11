terraform {
  backend "s3" {
    bucket = "eq-sanhe-tf-state"
    key = "ecs-service/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-state"
    encrypt = "1"
  }
}
