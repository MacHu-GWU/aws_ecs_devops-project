terraform {
  backend "s3" {
    bucket = "eq-sanhe-tf-state"
    key = "lbd-app/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-state"
    encrypt = "1"
  }
}
