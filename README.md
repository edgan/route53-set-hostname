# route53-set-hostname

Sets up a dynamic dns cron job to update an A record in a AWS Route53 hosted
domain with your public ip address. This is good when you have service behind
a NAT firewall, like a wireless router.

It picks randomly from list of nine services that will return your ip address.
If one fails it moves on to the next. All nine would have to fail for it not to
work. It also only updates if the ip address as changed.

## Requirements
python3
python3-boto3

## Install
sudo ./install.sh

Edit /etc/cron.d/route53-set-hostname to change the hostname.

Edit /root/.aws_keys with AWS keys that have access to make record checks for your AWS Route53 hosted domain

## Usage
route53-set-hostname.py --hostname acme.com
