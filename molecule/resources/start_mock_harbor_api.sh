#!/bin/sh
set -eu

pid_file=$1
log_file=$2
port=$3
script_dir=$(CDPATH= cd -- "$(/usr/bin/dirname -- "$0")" && /bin/pwd)

/usr/bin/nohup /usr/bin/python3 "${script_dir}/mock_harbor_api.py" --port "${port}" --log "${log_file}" >/dev/null 2>&1 &
echo "$!" > "${pid_file}"
