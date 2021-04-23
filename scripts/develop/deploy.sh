#!/bin/bash

echo -e "\e[1;123m*** DEPLOYING NEW SOURCE CODE ***"
rsync -avz --delete --exclude env ./ $1:rc-mission-operator
