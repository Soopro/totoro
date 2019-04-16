#!/bin/bash

mkdir -p /data/deployment_data/totoro/log
mkdir -p /data/deployment_data/totoro/tmp

cd /var/www/totoro/ && git stash save --keep-index && git stash drop
cd /var/www/totoro/ && find . -name \*.pyc -delete
cd /var/www/totoro/ && git pull origin master


for arg in $@
do
  if [ $arg = "-r" -o $arg = "--refresh" ]
    then
      echo 'Refresh ...'
      cd /var/www/totoro/server/ &&
      python toolkits.py migration -p &&
      python toolkits.py index -p
  fi
done

sudo supervisorctl restart totoro
sudo supervisorctl restart totoro_master
