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

//=== Active, Inactive, Staing listener
//--- For empty listener, use this default action
//  default_action {
//    type = "fixed-response"
//
//    fixed_response {
//      content_type = "text/plain"
//      message_body = "NOTHING"
//      status_code  = "200"
//    }
//  }
resource "aws_lb_listener" "active" {
  load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
  port = "10001"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_b_arn}"
  }
}

resource "aws_lb_listener" "inactive" {
  load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
  port = "10002"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_a_arn}"
  }
}

resource "aws_lb_listener" "staging" {
  load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
  port = "10003"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_c_arn}"
  }
}
