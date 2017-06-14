#!/usr/bin/env bash
set -x

if which -a docker > /dev/null; then
    echo "docker is already installed"
else
    echo "installing docker"
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository \
         "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
fi

if which -a docker-compose > /dev/null; then
    echo "docker-compose is already installed"
else
    echo "installing docker-compose"
    sudo curl -L \
         "https://github.com/docker/compose/releases/download/1.13.0/docker-compose-$(uname -s)-$(uname -m)" \
         -o /usr/bin/docker-compose
    sudo chmod +x /usr/bin/docker-compose
fi
