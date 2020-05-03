# -*- coding: utf-8 -*-

from troposphere_mate import StackManager

from aws_ecs_devops.cf import webapp
from aws_ecs_devops.devops.boto_ses import boto_ses
from aws_ecs_devops.devops.config_init import config


webapp.template.remove_resource(webapp.elb_lb)


sm = StackManager(
    boto_ses=boto_ses,
    cft_bucket=config.S3_BUCKET_FOR_DEPLOY.get_value(),
)
sm.deploy(
    template=webapp.template,
    stack_name=config.ENVIRONMENT_NAME.get_value(),
    stack_tags={
        "ProjectName": config.PROJECT_NAME.get_value(),
    },
    include_iam=True,
)
