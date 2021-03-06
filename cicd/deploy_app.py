# -*- coding: utf-8 -*-

from troposphere_mate import StackManager

from aws_ecs_devops.cf import webapp
from aws_ecs_devops.devops.boto_ses import boto_ses
from aws_ecs_devops.devops.config_init import config

template = webapp.template

#--- Add
template.add_resource(webapp.ecs_task_definition_execution_role)
template.add_resource(webapp.ecs_task_definition)

template.add_resource(webapp.sg_for_elb)
template.add_resource(webapp.elb_lb)

template.add_resource(webapp.sg_for_ecs)
template.add_resource(webapp.elb_default_target_group)
template.add_resource(webapp.elb_listener)

template.add_resource(webapp.ecs_service)

# --- Remove

sm = StackManager(
    boto_ses=boto_ses,
    cft_bucket=config.S3_BUCKET_FOR_DEPLOY.get_value(),
)
sm.deploy(
    template=template,
    stack_name=config.ENVIRONMENT_NAME.get_value(),
    stack_tags={
        "ProjectName": config.PROJECT_NAME.get_value(),
    },
    include_iam=True,
)
