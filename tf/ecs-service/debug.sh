#!/bin/bash

dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
dir_project_root=$(dirname $(dirname "${dir_here}"))

# **EDIT THIS**
STAGE="dev"

# Prevent from doing bad action on Prod
if [ "${STAGE}" == "prod" ]
then
    echo "ARE YOU AWARE you are on PROD environment? Type 'y' to confirm."
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
    fi
fi

bash "${dir_project_root}/config/switch-and-init.sh" ${STAGE}

config_file="${dir_project_root}/config/config-final-for-shell-script.json"

# IF local runtime
export AWS_PROFILE="$(cat ${config_file} | jq .AWS_PROFILE_FOR_BOTO3 -r)"

ENVIRONMENT_NAME="$(cat ${config_file} | jq .ENVIRONMENT_NAME -r)"

cd ${dir_here}

#terraform init

terraform workspace new ${ENVIRONMENT_NAME}
terraform workspace select ${ENVIRONMENT_NAME}

# Final terraform command, comment out lines on your behave
terraform plan
#terraform apply
#terraform destroy
