#!/bin/bash

# before running file make it executable: chmod +x server_set_up.sh
# run file using: ./server_set_up.sh

# Update and upgrade package lists
sudo apt-get update
sudo apt-get upgrade -y

# Install bash-completion
sudo apt-get install -y bash-completion

# Install Git
sudo apt-get install -y git

# Install Python3
sudo apt-get install -y python3

# Install pip3
sudo apt-get install -y python3-pip

# Install Docker
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose V2
mkdir -p ~/.docker/cli-plugins/
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Update .bashrc for the current user
BASHRC_UPDATE='
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
'

# Append the update to .bashrc if it's not already there
if ! grep -q "bash-completion/bash_completion" ~/.bashrc; then
    echo "$BASHRC_UPDATE" >> ~/.bashrc
fi

# Update /etc/bash.bashrc for all users (requires sudo)
if ! grep -q "bash-completion/bash_completion" /etc/bash.bashrc; then
    echo "$BASHRC_UPDATE" | sudo tee -a /etc/bash.bashrc > /dev/null
fi

# Reload bash
source ~/.bashrc
