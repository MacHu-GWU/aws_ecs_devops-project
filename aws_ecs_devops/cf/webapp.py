# -*- coding: utf-8 -*-

"""
Cloudformation Template Generation.
"""

import json

from troposphere_mate import (
    Template, Parameter, Ref, ecr, helper_fn_sub
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

ecr_repo = ecr.Repository(
    "EcrRepoWebApp",
    template=template,
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
    DeletionPolicy="Retain",
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
