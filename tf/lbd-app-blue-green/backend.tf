terraform {
  backend "s3" {
    bucket = "eq-sanhe-tf-state"
    key = "lbd-app-blue-green/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-state"
    encrypt = "1"
  }
}
