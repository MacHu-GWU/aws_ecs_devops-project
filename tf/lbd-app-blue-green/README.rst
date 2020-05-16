1. Pre-Release Preparation
------------------------------------------------------------------------------

.. code-block:: tf

    // content of lbd-app/main.tf

    provider "aws" {
      region = "us-east-1"
    }

    data "aws_caller_identity" "current" {}

    data "aws_region" "current" {}

    resource "aws_security_group" "elb" {
      name = "${var.LBD_APP_ENVIRONMENT_NAME}-elb"
      description = "Allow pubic visiting elb"
      vpc_id = "${var.VPC_ID}"

      ingress {
        description = "For visiting the active service"
        from_port = 10001
        to_port = 10003
        protocol = "tcp"
        cidr_blocks = [
          "0.0.0.0/0"
        ]
      }
    }

    resource "aws_lb" "elb" {
      name = "${var.LBD_APP_ENVIRONMENT_NAME}"
      internal = false
      // internet facing
      load_balancer_type = "application"
      // application load balancer
      security_groups = [
        "${aws_security_group.elb.id}"
      ]
      subnets = var.SUBNETS
    }

    resource "aws_iam_role" "lambda" {
      name = "iam_for_lambda"

      assume_role_policy = <<EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
    EOF
    }

    resource "aws_iam_role_policy_attachment" "lambda" {
      role = "${aws_iam_role.lambda.name}"
      policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    }

.. code-block:: tf

    // content of lbd-app-blue-green/main.tf

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

    resource "aws_lb_listener" "active" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10001"
      protocol = "HTTP"

      default_action {
        type = "fixed-response"

        fixed_response {
          content_type = "text/plain"
          message_body = "NOTHING"
          status_code  = "200"
        }
      }
    }

    resource "aws_lb_listener" "inactive" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10002"
      protocol = "HTTP"

      default_action {
        type = "fixed-response"

        fixed_response {
          content_type = "text/plain"
          message_body = "NOTHING"
          status_code  = "200"
        }
      }
    }

    resource "aws_lb_listener" "staging" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10003"
      protocol = "HTTP"

      default_action {
        type = "fixed-response"

        fixed_response {
          content_type = "text/plain"
          message_body = "NOTHING"
          status_code  = "200"
        }
      }
    }


2. Deploy version 1 to Staging
------------------------------------------------------------------------------

.. code-block:: tf

    // content lbd-app/main.tf

    // append following content
    module "lbd_a" {
      source = "./lbd-module"

      ENVIRONMENT_NAME = "${var.LBD_APP_ENVIRONMENT_NAME}"
      LOGIC_ID = "a"
      IAM_ROLE_ARN = "${aws_iam_role.lambda.arn}"
      DEPLOYMENT_FILE = "deploy-a.zip"
      LOAD_BALANCER_ARN = "${aws_lb.elb.arn}"
    }

.. code-block:: tf

    // content lbd-app-blue-green/main.tf

    resource "aws_lb_listener" "staging" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10003"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_a_arn}"
      }
    }


3. Deploy version 1 from Staging to Active
------------------------------------------------------------------------------

.. code-block:: tf

    // content lbd-app-blue-green/main.tf

    resource "aws_lb_listener" "active" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10001"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_a_arn}"
      }
    }

    // .. no need to change resource "aws_lb_listener" "inactive"

    resource "aws_lb_listener" "staging" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10003"
      protocol = "HTTP"

      default_action {
        type = "fixed-response"

        fixed_response {
          content_type = "text/plain"
          message_body = "NOTHING"
          status_code  = "200"
        }
      }
    }


4. Deploy version 2 to Staging
------------------------------------------------------------------------------

.. code-block:: tf

    // content of lbd-app/main.tf

    // append following content
    module "lbd_b" {
      source = "./lbd-module"

      ENVIRONMENT_NAME = "${var.LBD_APP_ENVIRONMENT_NAME}"
      LOGIC_ID = "b"
      IAM_ROLE_ARN = "${aws_iam_role.lambda.arn}"
      DEPLOYMENT_FILE = "deploy-b.zip"
      LOAD_BALANCER_ARN = "${aws_lb.elb.arn}"
    }


.. code-block:: tf

    // content of lbd-app-blue-green/main.tf

    resource "aws_lb_listener" "staging" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10003"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_b_arn}"
      }
    }


5. Deploy version 2 from Staging to Active
------------------------------------------------------------------------------

.. code-block:: tf

    // content of lbd-app-blue-green/main.tf

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
        type = "fixed-response"

        fixed_response {
          content_type = "text/plain"
          message_body = "NOTHING"
          status_code  = "200"
        }
      }
    }

6. Deploy version 3 to Staging
-----------------------------------------------------------------------------

.. code-block:: tf

    // content of lbd-app/main.tf

    // append following content
    module "lbd_c" {
      source = "./lbd-module"

      ENVIRONMENT_NAME = "${var.LBD_APP_ENVIRONMENT_NAME}"
      LOGIC_ID = "c"
      IAM_ROLE_ARN = "${aws_iam_role.lambda.arn}"
      DEPLOYMENT_FILE = "deploy-c.zip"
      LOAD_BALANCER_ARN = "${aws_lb.elb.arn}"
    }

.. code-block:: tf

    // content of lbd-app-blue-green/main.tf

    resource "aws_lb_listener" "staging" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10003"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_c_arn}"
      }
    }
