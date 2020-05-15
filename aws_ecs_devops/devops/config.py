# -*- coding: utf-8 -*-

import boto3
from configirl import ConfigClass, Constant, Derivable
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from typing import Type

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

    LBD_APP_ENVIRONMENT_NAME = Derivable()

    @LBD_APP_ENVIRONMENT_NAME.getter
    def get_LBD_APP_ENVIRONMENT_NAME(self):
        return "lbd-app-{}".format(self.STAGE.get_value())

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

    SUBNETS = Derivable()

    @SUBNETS.getter
    def get_SUBNETS(self):
        return [
            self.PUBLIC_SUBNET_ID_AZ1.get_value(),
            self.PUBLIC_SUBNET_ID_AZ2.get_value(),
        ]

    AWS_CFT_DYNAMIC_DELETEION_POLICY = Derivable()

    @AWS_CFT_DYNAMIC_DELETEION_POLICY.getter
    def get_AWS_CFT_DYNAMIC_DELETEION_POLICY(self):
        if self.STAGE.get_value() == "prod":
            return "Retain"
        else:
            return "Delete"


    #--- derivable object ---
    _boto_ses = None  # type: boto3.Session

    @property
    def boto_ses(self) -> boto3.Session:
        if self._boto_ses is None:
            self._boto_ses = boto3.session.Session(
                profile_name=self.AWS_PROFILE_FOR_BOTO3.get_value(),
                region_name=self.AWS_REGION.get_value(),
            )
        return self._boto_ses

    _blue_green_model = None # type: Type[Model]

    @property
    def blue_green_model(self) -> Type[Model]:
        if self._blue_green_model is None:
            class BlueGreenModel(Model):
                class Meta:
                    table_name = "tf-blue-green-deploy"
                    region = self.AWS_REGION.get_value()

                env = UnicodeAttribute(hash_key=True)
                logic_id = UnicodeAttribute()

            self._blue_green_model = BlueGreenModel
        return self._blue_green_model

    #--- Blue Green Deployment ---
    LBD_APP_ACTIVE_FLAG = Derivable()

    @LBD_APP_ACTIVE_FLAG.getter
    def get_LBD_APP_ACTIVE_FLAG(self):
        return None

    # LBD_APP_ACTIVE_LOGIC_ID = Derivable()
    # LBD_APP_ACTIVE_PORT = Derivable()
    #
    # LBD_APP_INACTIVE_FLAG = Derivable()
    # LBD_APP_INACTIVE_LOGIC_ID = Derivable()
    # LBD_APP_INACTIVE_PORT = Derivable()
    #
    # LBD_APP_STAGING_FLAG = Derivable()
    # LBD_APP_STAGING_LOGIC_ID = Derivable()
    # LBD_APP_STAGING_PORT = Derivable()

    def to_terraform_ecs_service_config_data(self):
        tf_keys = [
            self.STAGE.name,
            self.ENVIRONMENT_NAME.name,
            self.VPC_ID.name,
            self.SUBNETS.name,
        ]
        data = self.to_dict()
        config_data = {
            key: data[key]
            for key in tf_keys
        }
        return config_data

    def to_terraform_lbd_app_config_data(self):
        tf_keys = [
            self.STAGE.name,
            self.LBD_APP_ENVIRONMENT_NAME.name,
            self.VPC_ID.name,
            self.SUBNETS.name,
        ]
        data = self.to_dict()
        config_data = {
            key: data[key]
            for key in tf_keys
        }
        return config_data

    def to_terraform_lbd_app_blue_green_config_data(self):
        tf_keys = [
            self.STAGE.name,
            self.LBD_APP_ENVIRONMENT_NAME.name,
        ]
        data = self.to_dict()
        config_data = {
            key: data[key]
            for key in tf_keys
        }
        return config_data
