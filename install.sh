#!/bin/bash

pip3 install -r requirements.txt
cp .aws_keys /root
cp cron.d/route53-set-hostname /etc/cron.d
chown root:root /root/.aws_keys
cp route53-set-hostname /usr/local/sbin
chown root:root /usr/local/sbin/route53-set-hostname
cp route53-set-hostname.py /usr/local/bin
chown root:root /usr/local/bin/route53-set-hostname.py
