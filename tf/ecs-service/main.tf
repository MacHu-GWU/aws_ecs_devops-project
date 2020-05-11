provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_ecs_cluster" "api_cluster" {
  name = "${var.ENVIRONMENT_NAME}-hub-services-cluster"
}

resource "aws_security_group" "elb" {
  name = "allow visiting elb"
  description = "Allow visiting elb"
  vpc_id = "${var.VPC_ID}"

  ingress {
    description = "For visiting the active service"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }
}

resource "aws_lb" "elb" {
  name = "${var.ENVIRONMENT_NAME}"
  internal = false // internet facing
  load_balancer_type = "application" // application load balancer
  security_groups = [
    "${aws_security_group.elb.id}"
  ]
  subnets = var.SUBNETS
}


resource "aws_iam_role" "task_def_exec_role" {
  name = "${var.ENVIRONMENT_NAME}-sample-webapp-task-exec"
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


resource "aws_iam_role_policy_attachment" "sample_webapp_task_def_exec_role_attachment" {
  role = "${aws_iam_role.task_def_exec_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_ecs_task_definition" "sample_webapp" {
  family = "sample_webapp"
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


resource "aws_security_group" "sample_webapp" {
  name        = "allow-visiting-ecs-service-sample-webapp"
  description = "Allow visiting ecs service sample webapp"
  vpc_id      = "${var.VPC_ID}"

  ingress {
    description = "allow public internet visit ecs service"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }

  ingress {
    description = "allow elb visit ecs service"
    from_port   = 1
    to_port     = 65535
    protocol    = "tcp"
    security_groups = [
      "${aws_security_group.elb.id}",
    ]
  }

  tags = var.COMMON_TAGS
}

