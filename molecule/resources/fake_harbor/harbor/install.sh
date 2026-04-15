#!/bin/sh
set -eu

mkdir -p common/config common/templates
cp harbor.yml common/config/harbor.yml.installed
printf 'mock install complete\n' > harbor_install_log.txt
