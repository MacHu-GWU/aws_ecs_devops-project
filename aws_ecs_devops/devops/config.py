# -*- coding: utf-8 -*-

from configirl import ConfigClass, Constant, Derivable

from .._version import __version__


class Config(ConfigClass):
    METADATA = Constant(default=dict(), dont_dump=True)

    PROJECT_NAME = Constant()
    PROJECT_NAME_SLUG = Derivable()

    @PROJECT_NAME_SLUG.getter
    def get_project_name_slug(self):
        return self.PROJECT_NAME.get_value().replace("_", "-")

    STAGE = Constant()  # example dev / test / prod

    ENVIRONMENT_NAME = Derivable()

    @ENVIRONMENT_NAME.getter
    def get_ENVIRONMENT_NAME(self):
        return "{}-{}".format(self.PROJECT_NAME_SLUG.get_value(self), self.STAGE.get_value())

    AWS_PROFILE = Constant()

    AWS_PROFILE_FOR_BOTO3 = Derivable()

    @AWS_PROFILE_FOR_BOTO3.getter
    def get_AWS_PROFILE_FOR_BOTO3(self):
        if self.is_aws_code_build_runtime():
            return None
        else:  # local computer runtime
            return self.AWS_PROFILE.get_value()

    AWS_REGION = Constant()
    AWS_ACCOUNT_ID = Constant(printable=False)
    S3_BUCKET_FOR_DEPLOY = Constant()

    ECR_ENDPOINT = Derivable()

    @ECR_ENDPOINT.getter
    def get_ECR_ENDPOINT(self):
        return "{}.dkr.ecr.{}.amazonaws.com".format(
            self.AWS_ACCOUNT_ID.get_value(),
            self.AWS_REGION.get_value()
        )

    ECR_REPO_NAME_WEBAPP = Derivable()

    @ECR_REPO_NAME_WEBAPP.getter
    def get_ECR_REPO_NAME_WEBAPP(self):
        return "{}-webapp".format(self.PROJECT_NAME_SLUG.get_value())

    APP_VERSION = Derivable()

    @APP_VERSION.getter
    def get_APP_VERSION(self):
        return __version__

    VPC_ID = Constant()
    PUBLIC_SUBNET_ID_AZ1 = Constant()
    PUBLIC_SUBNET_ID_AZ2 = Constant()

    AWS_CFT_DYNAMIC_DELETEION_POLICY = Derivable()

    @AWS_CFT_DYNAMIC_DELETEION_POLICY.getter
    def get_AWS_CFT_DYNAMIC_DELETEION_POLICY(self):
        if self.STAGE.get_value() == "prod":
            return "Retain"
        else:
            return "Delete"
