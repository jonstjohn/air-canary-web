# Ansible

## Pre-Ansible Setup

### Create server
Ubuntu 14.04

### Create user ac
`adduser ac`

### Configure SSH
Disable root ssh access and limit to ac user
`vim /etc/ssh/sshd_config`

`PermitRootLogin No`

`AllowUsers ac`

`service ssh restart`

### Add ac to sudoers
Change default editor to vim
`update-alternatives --config editor`

Modify sudoers

`visudo`

`ac    ALL=(ALL:ALL) ALL`

### Change to ac user

`su - ac`

### Generate SSH key

`ssh-keygen -t rsa -C "email@email.com"`

Add to github repository as deploy key

### Create logs directory

    mkdir ~/logs
    
### Install git

`sudo apt-get install git`
    
### Checkout code

    cd ~
    git clone git@github.com:jonstjohn/air-canary-web.git
    
### Setup ansible

    sudo apt-get update -q -y
    sudo apt-get install -q -y git python python-dev python-pip
    sudo pip install paramiko pyyaml jinja2 markupsafe
    sudo pip install ansible
    
## Run ansible





