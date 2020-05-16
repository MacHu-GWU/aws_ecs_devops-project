Blue Green IAC Implementation Guide
==============================================================================

我们这里采用的是 Active, Inactive, Staging 的三环境的部署策略. 之所以使用三环境而不是两环境是因为 Blue Green 两环境对调之后, 当你部署新环境的时候, 必然覆盖该上一个版本的环境, 也就是你无法向 Blue Green 声称的那样, 可以返回上一个版本的环境了. 这样的风险比较大.

三环境的部署策略:

- 所有的新的资源, 都部署到 Staging. 在 Staging 测试好了之后, 再部署到 Active.
- 每次部署到 Active 的时候, 实际上时将 Load Balancer 的 Route 对调, 将 Active 变成 Inactive, 将 Staging 变成 Active, 原来的 Inactive 虽然还在, 但没有流量会被路由到这上面.
- 路由是在 AWS Load Balancer 和 Listener 中进行定义.

三环境的 IAC 实现:

首先我们要注意一个问题, 使用过 IAC 实现的 Resource, 都有一个 Logic ID, 而这个 Logic ID 的对应的 Active, Inactive, Staging 是变化的.

具体实现:

你需要两个 IAC Stack, 一个 Stack 叫做 ``Resource Stack``, 定义了各个环境中实际的计算资源. 另一个 Stack 叫做 ``Routing Stack``, 定义了流量是如何被路由到各个资源上的.

- 在 ``Resource Stack`` 中, 有 3 个 Logic Id 分别叫做, A, B, C. 每个都对应了一套计算资源 和一个 Load Balancer Target Group. 这些计算资源都被注册到这个 Target Group 上.
- 在 ``Routing Stack`` 中, 有 3 个 Logic Id 分别叫做, Active, Inactive, Staging. 而我们默认 10001 端口用于 Active, 10002 用于 Inactive, 10003 用于 Staging.

在 ``Resource Stack`` 中定义 3 套环境::

    resource ec2 a {
        artifacts = v1
    }

    resource aws_lb_target_group a {
        attachment = [
            ec2.a
        ]
    }

    resource ec2 b {
        artifacts = v2
    }

    resource aws_lb_target_group b {
        attachment = [
            ec2.b
        ]
    }

    resource ec2 c {
        artifacts = v3
    }

    resource aws_lb_target_group c {
        attachment = [
            ec2.c
        ]
    }

在最开始的时候, 在 ``Routing Stack`` 中定义 3 个资源 (伪代码)::

    resource aws_lb_listener active {
        port = 10001
        default_action = "forward-to-target-group-b"
    }

    resource aws_lb_listener inactive {
        port = 10002
        default_action = "forward-to-target-group-a"
    }

    resource aws_lb_listener staging {
        port = 10003
        default_action = "fix-response"
    }

每次部署新版本时都有两个步骤:

1. 部署到 Staging.
2. 将 Staging 变成 Active, Active 变成 Inactive.


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


7. Deploy version 3 from Staging to Active
------------------------------------------------------------------------------


.. code-block:: tf

    // content of lbd-app-blue-green/main.tf
    resource "aws_lb_listener" "active" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10001"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_c_arn}"
      }
    }

    resource "aws_lb_listener" "inactive" {
      load_balancer_arn = "${data.terraform_remote_state.lbd_app.outputs.lb_arn}"
      port = "10002"
      protocol = "HTTP"

      default_action {
        type = "forward"
        target_group_arn = "${data.terraform_remote_state.lbd_app.outputs.target_group_b_arn}"
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
