#!/bin/bash

# write docker variables to .env file
WORKDIR=/root/
CONTAINER_NAME=skai_msg_interface
echo CONTAINER_NAME=$CONTAINER_NAME > .env
echo WORKDIR=$WORKDIR >> .env

# remove
docker-compose down -t 0

# build
docker-compose build

# launch
docker-compose up --detach

