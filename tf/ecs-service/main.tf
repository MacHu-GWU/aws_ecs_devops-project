provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_ecs_cluster" "api_cluster" {
  name = "${var.ENVIRONMENT_NAME}-tf-webapp"
}


resource "aws_iam_role" "task_def_exec_role" {
  name = "${var.ENVIRONMENT_NAME}-tf-sample-webapp-task-exec"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "webapp_task_def_exec_role_attachment" {
  role = "${aws_iam_role.task_def_exec_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}


resource "aws_ecs_task_definition" "webapp" {
  family = "${var.ENVIRONMENT_NAME}-tf-webapp-task-definition"
  container_definitions = <<TASK_DEFINITION
[
    {
        "dnsSearchDomains": [],
        "logConfiguration": null,
        "entryPoint": [],
        "portMappings": [
            {
                "hostPort": 80,
                "protocol": "tcp",
                "containerPort": 80
            }
        ],
        "command": [],
        "linuxParameters": null,
        "cpu": 256,
        "environment": [],
        "resourceRequirements": null,
        "ulimits": [],
        "dnsServers": [],
        "mountPoints": [],
        "workingDirectory": null,
        "secrets": [],
        "dockerSecurityOptions": [],
        "memory": null,
        "memoryReservation": 512,
        "volumesFrom": [],
        "stopTimeout": null,
        "image": "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/aws-ecs-devops-webapp:0.0.1-dev",
        "startTimeout": null,
        "firelensConfiguration": null,
        "dependsOn": null,
        "disableNetworking": null,
        "interactive": null,
        "healthCheck": null,
        "essential": true,
        "links": [],
        "hostname": null,
        "extraHosts": [],
        "pseudoTerminal": null,
        "user": null,
        "readonlyRootFilesystem": null,
        "dockerLabels": {},
        "systemControls": [],
        "privileged": null,
        "name": "sample-webapp"
    }
]
TASK_DEFINITION
  network_mode = "awsvpc"
  execution_role_arn = "${aws_iam_role.task_def_exec_role.arn}"
  cpu = 256
  memory = 512
  requires_compatibilities = [
    "FARGATE",
  ]
}


resource "aws_security_group" "elb" {
  name = "${var.ENVIRONMENT_NAME}-tf-elb"
  description = "Allow pubic visiting elb"
  vpc_id = "${var.VPC_ID}"

  ingress {
    description = "For visiting the active service"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
}

resource "aws_lb" "elb" {
  name = "${var.ENVIRONMENT_NAME}-tf"
  internal = false
  // internet facing
  load_balancer_type = "application"
  // application load balancer
  security_groups = [
    "${aws_security_group.elb.id}"
  ]
  subnets = var.SUBNETS
}

// ---
resource "aws_security_group" "ecs" {
  name = "${var.ENVIRONMENT_NAME}-tf-ecs"
  description = "Allow visiting ecs service sample webapp"
  vpc_id = "${var.VPC_ID}"

  ingress {
    description = "allow elb visit ecs service"
    from_port = 1
    to_port = 65535
    protocol = "tcp"
    security_groups = [
      "${aws_security_group.elb.id}",
    ]
  }
}


resource "aws_lb_target_group" "sample_webapp" {
  name = "${var.ENVIRONMENT_NAME}-tf-ecs"
  port = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = "${var.VPC_ID}"
}


resource "aws_lb_listener" "sample_webapp" {
  load_balancer_arn = "${aws_lb.elb.arn}"
  port = "80"
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = "${aws_lb_target_group.sample_webapp.arn}"
  }
}


resource "aws_ecs_service" "sample_webapp" {
  name            = "${var.ENVIRONMENT_NAME}-tf-webapp"
  cluster         = "${aws_ecs_cluster.api_cluster.arn}"
//  task_definition = "${aws_ecs_task_definition.webapp.arn}"
  task_definition = "arn:aws:ecs:us-east-1:110330507156:task-definition/aws-ecs-devops-dev-webapp-task-definition:8"
  desired_count   = 1
  launch_type = "FARGATE"
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 100
  health_check_grace_period_seconds = 30
  scheduling_strategy = "REPLICA"

  load_balancer {
    target_group_arn = "${aws_lb_target_group.sample_webapp.arn}"
    container_name   = "webapp"
    container_port   = 80
  }

  network_configuration {
    subnets = var.SUBNETS
    security_groups = [
      "${aws_security_group.ecs.id}"
    ]
    assign_public_ip = true
  }

  depends_on = [
    aws_lb_target_group.sample_webapp,
    aws_lb_listener.sample_webapp,
  ]
}
