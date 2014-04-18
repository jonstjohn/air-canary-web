#!/bin/bash
#
# Windows shell provisioner for Ansible playbooks, based on KSid's
# windows-vagrant-ansible: https://github.com/KSid/windows-vagrant-ansible
#
# @todo - Allow proxy configuration to be passed in via Vagrantfile config.
#
# @see README.md
# @author Jeff Geerling, 2014
# @version 1.0
#

# Uncomment if behind a proxy server.
# export {http,https,ftp}_proxy='http://username:password@proxy-host:80'

ANSIBLE_PLAYBOOK=$1
ANSIBLE_HOSTS=$2
EXTRA_VARS=$3
TEMP_HOSTS="/tmp/ansible_hosts"

echo $ANSIBLE_PLAYBOOK

if [ ! -f /vagrant/$ANSIBLE_PLAYBOOK ]; then
  echo "Cannot find Ansible playbook."
  exit 1
fi

if [ ! -f /vagrant/$ANSIBLE_HOSTS ]; then
  echo "Cannot find Ansible hosts."
  exit 2
fi

# Install Ansible and its dependencies if it's not installed already.
if [ ! -f /usr/bin/ansible ]; then
  echo "Installing Ansible dependencies and Git."
  apt-get update -q -y
  apt-get install -q -y git python python-dev python-pip
  echo "Installing required python modules."
  pip install paramiko pyyaml jinja2 markupsafe
  echo "Installing Ansible."
  pip install ansible
fi

cp /vagrant/${ANSIBLE_HOSTS} ${TEMP_HOSTS} && chmod -x ${TEMP_HOSTS}
echo "Running Ansible provisioner defined in Vagrantfile."

ansible-playbook /vagrant/${ANSIBLE_PLAYBOOK} --inventory-file=${TEMP_HOSTS} --extra-vars "is_windows=true $EXTRA_VARS" --connection=local
rm ${TEMP_HOSTS}