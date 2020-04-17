#!/bin/bash

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname $(dirname ${dir_here}))"
dir_webapp_dockerfile="${dir_here}"

source ${dir_project_root}/bin/py/python-env.sh

path_get_config_value_script="${dir_project_root}/config/get-config-value"
local_repo_name="$(${bin_python} ${path_get_config_value_script} "ECR_REPO_NAME_WEBAPP")"
app_version="$(${bin_python} ${path_get_config_value_script} "APP_VERSION")"
stage="$(${bin_python} ${path_get_config_value_script} "STAGE")"
tag_name="${app_version}-${stage}"
container_name="${local_repo_name}-smoke-test"

check_exit_status() {
    exit_status=$1
    if [ $exit_status != 0 ]
    then
        echo "FAILED!"
        docker container stop "${container_name}"
        exit $exit_status
    fi
}

docker run --rm -dt --name "${container_name}" -p 10001:80 "${local_repo_name}:${tag_name}"
sleep 10 # sleep 2 seconds wait web server become ready

echo "check if the web app successfully running locally"
curl "http://127.0.0.1:10001"
check_exit_status $?
echo "yes"

# remove container if all success
docker container stop "${container_name}"
