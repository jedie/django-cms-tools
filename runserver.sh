#!/usr/bin/env bash

# run a **public** dev. server in a loop

clear

IP=$(hostname -I | cut -f1 -d' ')

echo IP: ${IP}

cd django_cms_tools_test_project

#echo -n "Use 'runserver_plus' [y/n]: "
#read -n 1 usage
#if [ "${usage}" == "y" ]; then
#    CMD=runserver_plus
#else
#    CMD=runserver
#fi
CMD=runserver

source scripts/bootstrap.sh

while true
do
(
    clear
    echo "====================================================================="
    echo "====================================================================="
    echo "====================================================================="
    set -x
    ./manage.py ${CMD} ${IP}:8080
    sleep 2
)
done
