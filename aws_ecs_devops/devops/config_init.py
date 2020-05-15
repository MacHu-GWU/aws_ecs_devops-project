# -*- coding: utf-8 -*-

"""
Read config values based on the current environment name.
"""

import os
from os.path import dirname, join

import jinja2
from configirl import read_text, write_text, json_loads, json_dumps
from pathlib_mate import PathCls as Path

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


# --- Terraform scripts ---
def generate_terraform_script(tf_dir):
    """
    This function looking for ``main.tf.tpl``, ``variables.tf.tpl`` files in
    ``tf_dir``. And use jinja2 template engine to generate the real tf files.
    It pass in the config object to dynamically inject values.

    :param tf_dir: terraform workspace directory.
    """

    tf_dir = Path(tf_dir)
    if not tf_dir.is_dir():
        raise TypeError

    tf_files = [
        "main",
        "variables",
        "backend",
        "output"
    ]

    for file in tf_files:
        tpl_file = Path(tf_dir, file + ".tf.tpl")
        tf_file = Path(tf_dir, file + ".tf")
        if tpl_file.exists():
            tpl = jinja2.Template(tpl_file.read_text(encoding="utf-8"))
            content = tpl.render(config=config)
            tf_file.write_text(content, encoding="utf-8")


# dump ecs service config data
ecs_service_tf_vars_json = join(dir_project_root, "tf", "ecs-service", "terraform.tfvars.json")
write_text(
    text=json_dumps(config.to_terraform_ecs_service_config_data()),
    abspath=ecs_service_tf_vars_json,
)


# dump lbd app config data
lbd_app_tf_vars_json = join(dir_project_root, "tf", "lbd-app", "terraform.tfvars.json")
write_text(
    text=json_dumps(config.to_terraform_lbd_app_config_data()),
    abspath=lbd_app_tf_vars_json,
)
generate_terraform_script(Path(dir_project_root, "tf", "lbd-app"))


# dump lbd app config data
lbd_app_blue_green_tf_vars_json = join(dir_project_root, "tf", "lbd-app-blue-green", "terraform.tfvars.json")
write_text(
    text=json_dumps(config.to_terraform_lbd_app_blue_green_config_data()),
    abspath=lbd_app_blue_green_tf_vars_json,
)
generate_terraform_script(Path(dir_project_root, "tf", "lbd-app-blue-green"))
