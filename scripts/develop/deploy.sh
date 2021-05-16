#!/bin/bash

echo -e "\e[1;123m*** DEPLOYING NEW SOURCE CODE ***"
rsync -avz --delete --exclude venv ./ $1:rc-mission-operator
