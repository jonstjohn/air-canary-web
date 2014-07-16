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

### Generate SSH key

`ssh-keygen -t rsa -C "email@email.com"`

Add to github repository as deploy key

