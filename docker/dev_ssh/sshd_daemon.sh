#!/bin/sh

cd /etc/ssh
ssh-keygen -A


echo $PATH
/usr/sbin/sshd -D
