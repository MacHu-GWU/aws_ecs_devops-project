#!/bin/bash

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname $(dirname ${dir_here}))"

source ${dir_project_root}/bin/aws/aws-env.sh
source ${dir_project_root}/bin/py/python-env.sh

path_get_config_value_script="${dir_project_root}/config/get-config-value"

aws_region="$(${bin_python} ${path_get_config_value_script} "AWS_REGION")"
aws_account_id="$(${bin_python} ${path_get_config_value_script} "AWS_ACCOUNT_ID")"
local_repo_name="$(${bin_python} ${path_get_config_value_script} "ECR_REPO_NAME_WEBAPP")"
app_version="$(${bin_python} ${path_get_config_value_script} "APP_VERSION")"
ecr_repo_name="${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com/${local_repo_name}"
ecr_uri="https://${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com"

docker tag "${local_repo_name}:${app_version}" "${ecr_repo_name}:${app_version}"
aws ecr get-login --no-include-email --region ${aws_region} ${aws_cli_profile_arg} | awk '{printf $6}' | docker login -u AWS ${ecr_uri} --password-stdin
docker push "${ecr_repo_name}:${app_version}"
