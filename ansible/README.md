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

## Post-ansible

### Modify .bashrc
Add to .bashrc

    source /usr/local/bin/virtualenvwrapper.sh
    export WORKON_HOME=~/Envs

and reload `. ~/.bashrc`

### Create ac virtualenv

`mkvirtualenv ac`

### Update /etc/vim/vimrc.local

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

### Get requirements

    pip install -r requirements/production.txt

### Add .acrc

     set default settings module
     DJANGO_SETTINGS_MODULE=aircanary.settings.dev; export DJANGO_SETTINGS_MODULE

     AIRNOW_USERNAME=jonstjohn; export AIRNOW_USERNAME
     AIRNOW_PASSWORD=XXXXXXXX; export AIRNOW_PASSWORD

     FORECAST_IO_KEY=XXXXXX; export FORECAST_IO_KEY

then in .bashrc add

    source ~/.acrc

### Install wgrib2

http://www.cpc.noaa.gov/products/wesley/wgrib2/

    cd ~
    mkdir install
    cd install
    mkdir wgrib2
    cd wgrib2/
    wget http://www.ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz.v2.0.1
    tar -zxf wgrib2.tgz.v2.0.1
    cd grib2
    export CC=gcc
    make
    wgrib2/wgrib2 -config ; verify if works
    sudo cp wgrib2/wgrib2 /usr/local/bin/wgrib2

### Create database, user

    su - postgres
    psql
    > CREATE DATABASE air_canary template=template0 encoding='UTF-8' lc_ctype='en_US.UTF-8' lc_collate='en_US.UTF-8';
    > CREATE USER ac_web WITH PASSWORD '[password]';
    > GRANT ALL PRIVILEGES ON DATABASE air_canary TO ac_web
    > \q

Update pg_hba.conf

    local   all             ac_web                                  md5

### Setup celery

Add to .bashrc

    alias startceleryd="cd /home/ac/air-canary-web/aircanary; python manage.py celeryd_detach -f /home/ac/logs/celeryd.log --pidfile /home/ac/celeryd.pid --concurrency=2"
    alias startcelerybeat="cd /home/ac/air-canary-web/aircanary; python manage.py celerybeat --detach -f /home/ac/logs/celerybeat.log -s /home/ac/logs/celery-schedule --pidfile=/home/ac/logs/celerybeat.pid --workdir /home/ac/air-canary-web/aircanary"

    alias startcelery="startceleryd && startcelerybeat"
    alias stopcelery="kill \$(cat /home/ac/celeryd.pid); kill \$(cat /home/ac/logs/celerybeat.pid)"

Then run

    startceleryd
    startcelerybeat

or just

    startcelery

### Setup deploy.sh

    cd /home/ac/air-canary-web
    git pull
    pip install -r requirements/production.txt
    cd /home/ac/air-canary-web/aircanary
    python manage.py migrate
    python manage.py collectstatic --noinput
    sudo service uwsgi restart
    sudo service nginx restart

Modify sudoers file:
    ac    ALL=(ALL:ALL) NOPASSWD: /usr/sbin/service uwsgi restart,/usr/sbin/service nginx restart
    www-data    ALL=(ac) NOPASSWD: /home/ac/deploy.sh
