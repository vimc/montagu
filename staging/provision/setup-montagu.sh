#!/usr/bin/env bash
set -x

DOCKER_VERSION=17.03.0~ce-0~ubuntu-xenial
COMPOSE_VERSION=1.13.0

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
    sudo apt-get install -y docker-ce=$DOCKER_VERSION
    sudo usermod -aG docker vagrant
fi

if which -a docker-compose > /dev/null; then
    echo "docker-compose is already installed"
else
    echo "installing docker-compose"
    sudo curl -L \
         "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" \
         -o /usr/bin/docker-compose
    sudo chmod +x /usr/bin/docker-compose
fi

if which -a pip3 > /dev/null; then
    echo "pip is already installed (for Python 3)"
else
    echo "installing pip (for Python 3)"
    sudo apt-get update
    sudo apt-get install -y python3-pip
    sudo pip3 install --upgrade pip
fi
