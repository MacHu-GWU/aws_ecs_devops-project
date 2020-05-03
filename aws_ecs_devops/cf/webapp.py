# -*- coding: utf-8 -*-

"""
Cloudformation Template Generation.
"""

import json

from troposphere_mate import (
    Template, Parameter, Ref, helper_fn_sub, canned,
    ecr, ecs, iam, elasticloadbalancingv2, ec2,
)

from ..devops.config_init import config

template = Template()

param_project_name = Parameter(
    "ProjectName",
    Type="String",
    Default=config.PROJECT_NAME.get_value()
)

param_project_name_slug = Parameter(
    "ProjectNameSlug",
    Type="String",
    Default=config.PROJECT_NAME_SLUG.get_value()
)

param_stage = Parameter(
    "Stage",
    Type="String",
    Default=config.STAGE.get_value()
)

param_env_name = Parameter(
    "EnvironmentName",
    Type="String",
    Default=config.ENVIRONMENT_NAME.get_value()
)

template.add_parameter(param_project_name)
template.add_parameter(param_project_name_slug)
template.add_parameter(param_stage)
template.add_parameter(param_env_name)

ecr_repo_webapp = ecr.Repository(
    "EcrRepoWebApp",
    RepositoryName=config.ECR_REPO_NAME_WEBAPP.get_value(),
    LifecyclePolicy=ecr.LifecyclePolicy(
        LifecyclePolicyText=json.dumps(
            {
                "rules": [
                    {
                        "rulePriority": 1,
                        "description": "keep untagged (historical) image for N days",
                        "selection": {
                            "tagStatus": "untagged",
                            "countType": "sinceImagePushed",
                            "countUnit": "days",
                            "countNumber": 365
                        },
                        "action": {
                            "type": "expire"
                        }
                    }
                ]
            }
        )
    ),
    DeletionPolicy=config.AWS_CFT_DYNAMIC_DELETEION_POLICY.get_value(),
)

if config.STAGE.get_value() == "prod":
    template.add_resource(ecr_repo_webapp)

ecs_cluster = ecs.Cluster(
    "EcsCluster",
    template=template,
    ClusterName=helper_fn_sub("{}-webapp", param_env_name),
    DeletionPolicy=config.AWS_CFT_DYNAMIC_DELETEION_POLICY.get_value(),
)

ecs_task_definition_execution_role = iam.Role(
    "IamRoleEcsTaskDefinitionExecutionRole",
    template=template,
    RoleName=helper_fn_sub("{}-webapp-ecs-role", param_env_name),
    AssumeRolePolicyDocument=canned.iam.create_assume_role_policy_document([
        "ecs-tasks"
    ]),
    ManagedPolicyArns=[
        canned.iam.AWSManagedPolicyArn.administratorAccess,
    ],
)

ecs_task_definition = ecs.TaskDefinition(
    "EcsTaskDefinition",
    template=template,
    ContainerDefinitions=[
        ecs.ContainerDefinition(
            Name="webapp",
            Image="{}/{}:{}-{}".format(
                config.ECR_ENDPOINT.get_value(),
                config.ECR_REPO_NAME_WEBAPP.get_value(),
                config.APP_VERSION.get_value(),
                config.STAGE.get_value(),
            ),
            Cpu=256,
            MemoryReservation=512,
            PortMappings=[
                ecs.PortMapping(
                    ContainerPort=80,
                    HostPort=80,
                    Protocol="tcp",
                )
            ],
            Essential=True,
        )
    ],
    Family=helper_fn_sub("{}-webapp-task-definition", param_env_name),
    NetworkMode="awsvpc",
    RequiresCompatibilities=[
        "FARGATE"
    ],
    Cpu="256",
    Memory="512",
    ExecutionRoleArn=ecs_task_definition_execution_role.iam_role_arn,
    DependsOn=ecs_task_definition_execution_role,
)

# --- service deployment dependencies
sg_for_elb = ec2.SecurityGroup(
    "ElbSecurityGroup",
    template=template,
    VpcId=config.VPC_ID.get_value(),
    GroupDescription="ECS allowed Ports",
    SecurityGroupIngress=[
        dict(
            IpProtocol="tcp",
            FromPort="80",
            ToPort="80",
            CidrIp="0.0.0.0/0",
        ),
    ]
)

sg_for_ecs = ec2.SecurityGroup(
    "EcsSecurityGroup",
    template=template,
    VpcId=config.VPC_ID.get_value(),
    GroupDescription="ECS allowed Ports",
    SecurityGroupIngress=[
        dict(
            IpProtocol="tcp",
            FromPort="80",
            ToPort="80",
            CidrIp="0.0.0.0/0",
        ),
        dict(
            IpProtocol="tcp",
            FromPort="1",
            ToPort="65535",
            SourceSecurityGroupId=Ref(sg_for_elb),
        ),
    ],
    DependsOn=sg_for_elb,
)

elb_default_target_group = elasticloadbalancingv2.TargetGroup(
    "DefaultTargetGroup",
    template=template,
    VpcId=config.VPC_ID.get_value(),
    Port=80,
    Protocol="HTTP",
    TargetType="ip",
)

elb_lb = elasticloadbalancingv2.LoadBalancer(
    "EcsElasticLoadBalancer",
    template=template,
    Type="application",
    SecurityGroups=[
        Ref(sg_for_elb)
    ],
    Subnets=[
        config.PUBLIC_SUBNET_ID_AZ1.get_value(),
        config.PUBLIC_SUBNET_ID_AZ2.get_value(),
    ],
    Scheme="internet-facing",
    DependsOn=sg_for_elb,
)

elb_listener = elasticloadbalancingv2.Listener(
    "ElbListener",
    template=template,
    LoadBalancerArn=Ref(elb_lb),
    Port=80,
    Protocol="HTTP",
    DefaultActions=[
        elasticloadbalancingv2.Action(
            Type="forward",
            TargetGroupArn=Ref(elb_default_target_group)
        )
    ],
    DependsOn=[
        elb_lb,
        elb_default_target_group,
    ],
)

ecs_service = ecs.Service(
    "EcsService",
    template=template,
    Cluster=Ref(ecs_cluster),
    TaskDefinition=Ref(ecs_task_definition),
    DeploymentConfiguration=ecs.DeploymentConfiguration(
        MaximumPercent=200,
        MinimumHealthyPercent=100,
    ),
    DesiredCount=1,
    LaunchType="FARGATE",
    LoadBalancers=[
        ecs.LoadBalancer(
            ContainerName="webapp",
            ContainerPort=80,
            TargetGroupArn=Ref(elb_default_target_group),
        ),
    ],
    NetworkConfiguration=ecs.NetworkConfiguration(
        AwsvpcConfiguration=ecs.AwsvpcConfiguration(
            AssignPublicIp="ENABLED",
            SecurityGroups=[
                Ref(sg_for_ecs),
            ],
            Subnets=[
                config.PUBLIC_SUBNET_ID_AZ1.get_value(),
                config.PUBLIC_SUBNET_ID_AZ2.get_value(),
            ]
        )
    ),
    SchedulingStrategy="REPLICA",
    HealthCheckGracePeriodSeconds=30,
    DependsOn=[
        sg_for_ecs,
        ecs_task_definition,
        elb_lb,
        elb_default_target_group,
    ],
)

template.create_resource_type_label()

# give all aws resource common tags
common_tags = {
    "ProjectName": Ref(param_project_name),
    "ProjectNameSlug": Ref(param_project_name_slug),
    "Stage": Ref(param_stage),
    "EnvironmentName": Ref(param_env_name),
}
template.update_tags(common_tags)
