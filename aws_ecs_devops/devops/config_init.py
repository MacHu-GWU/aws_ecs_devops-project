# -*- coding: utf-8 -*-

"""
Read config values based on the current environment name.
"""

import os
from os.path import dirname, join

from configirl import read_text, write_text, json_loads, json_dumps

from .config import Config

dir_project_root = dirname(dirname(dirname(__file__)))
shared_config_file = join(dir_project_root, "config", "00-config-shared.json")
shared_secret_config_file = join(dir_project_root, "config", "00-config-shared-secrets.json")
env_config_file = join(dir_project_root, "config", "config-raw.json")

config = Config()

# circleci container runtime
if config.is_aws_code_build_runtime():
    config.update(json_loads(read_text(shared_config_file)))
    config.update(json_loads(read_text(env_config_file)))
    config.AWS_ACCOUNT_ID.set_value(os.environ["AWS_ACCOUNT_ID"])
# local runtime
else:
    config.update(json_loads(read_text(shared_config_file)))
    config.update(json_loads(read_text(shared_secret_config_file)))
    config.update(json_loads(read_text(env_config_file)))

# Read additional config data from external store.
# put your code here ...
config.CONFIG_DIR = join(dir_project_root, "config")
config.dump_shell_script_json_config_file()

# dump ecs
ecs_service_tf_vars_json = join(dir_project_root, "tf", "ecs-service", "terraform.tfvars.json")
write_text(
    text=json_dumps(config.to_terraform_ecs_service_config_data()),
    abspath=ecs_service_tf_vars_json,
)
