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

run it

### Post-ansible

## Modify .bashrc
Add to .bashrc

    source /usr/local/bin/virtualenvwrapper.sh
    export WORKON_HOME=~/Envs

and reload `. ~/.bashrc`

## Create ac virtualenv

`mkvirtualenv ac`

## Update /etc/vim/vimrc.local

    colo evening
    "set noswapfile
    "set nobackup
    "set nowritebackup
    set ai
    set tabstop=4
    set softtabstop=4
    set shiftwidth=4
    set expandtab

    set viminfo='10,\"100,:20,%,n~/.viminfo

    " Uncomment the following to have Vim jump to the last position when
    " reopening a file
    if has("autocmd")
      au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
      endif

## Get requirements

    pip install -r requirements/production.txt

## Add .acrc

     set default settings module
     DJANGO_SETTINGS_MODULE=aircanary.settings.dev; export DJANGO_SETTINGS_MODULE

     AIRNOW_USERNAME=jonstjohn; export AIRNOW_USERNAME
     AIRNOW_PASSWORD=XXXXXXXX; export AIRNOW_PASSWORD

     FORECAST_IO_KEY=XXXXXX; export FORECAST_IO_KEY

then in .bashrc add

    source ~/.acrc
