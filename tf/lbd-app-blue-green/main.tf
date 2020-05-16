provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "terraform_remote_state" "lbd_app" {
  backend = "s3"
  workspace = "aws-ecs-devops-dev"
  config = {
    bucket = "eq-sanhe-tf-state"
    key = "lbd-app/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-state"
    encrypt = "1"
  }
}

resource "aws_lb_listener" "lbd_a" {
  load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
  port = "10001"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_a_arn}"
  }
}
