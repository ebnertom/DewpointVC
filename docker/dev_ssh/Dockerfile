FROM python:3.10-alpine

# required for installing rpi-gpio python package
RUN apk add --no-cache gcc libc-dev
RUN apk add --no-cache openssh-server sudo bash shadow
RUN chsh root --shell /bin/bash
EXPOSE 22

COPY tmp/dev_ssh_hostkeys/etc/ssh /etc/ssh

RUN mkdir -p /run/sshd

ARG home=/root
RUN mkdir $home/.ssh
COPY docker/dev_ssh/authorized_keys.pub $home/.ssh/authorized_keys
RUN chown root:root $home/.ssh/authorized_keys && \
    chmod 600 $home/.ssh/authorized_keys
RUN sed -i 's/[# ]*AllowTcpForwarding .*/AllowTcpForwarding yes/g' /etc/ssh/sshd_config && \
    sed -i 's/[# ]*PasswordAuthentication .*/PasswordAuthentication no/g' /etc/ssh/sshd_config

COPY docker/dev_ssh/sshd_daemon.sh /sshd_daemon.sh
COPY tmp/dev_ssh_hostkeys/ /etc/ssh
RUN chmod 755 /sshd_daemon.sh
CMD ["/sshd_daemon.sh"]

COPY src/requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt


ENTRYPOINT ["sh", "-c", "/sshd_daemon.sh"]
