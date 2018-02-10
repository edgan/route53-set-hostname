#!/usr/bin/python3

import argparse
import boto3
import os
import random
import re
import sys
import time
import urllib

from datetime import datetime
from IPy import IP

def get_public_ip():
    urls = [
            'https://v4.ident.me/',
            'https://ipinfo.io/ip/',
            'https://ipv4.icanhazip.com/',
            'https://bot.whatismyipaddress.com/',
            'https://ifconfig.io/',
            'https://ipv4bot.whatismyipaddress.com/',
            'https://4.ifcfg.me/',
            'https://myexternalip.com/raw',
            'https://in.je/ip'
           ]

    randomized_urls = random.sample(urls, len(urls))

    timeout = 5 # seconds

    for url in randomized_urls:
        response = ''
        try:
            req = urllib.request.Request(url, data=None, headers={'User-Agent': 'curl/7.55.1'})
            response = urllib.request.urlopen(req, timeout=timeout).read()
        except:
            continue
        finally:
            public_ip = "".join(map(chr, response))

        if public_ip != '':
          if public_ip[-1] == '\n':
              public_ip = public_ip.strip()
        else:
            continue

        try:
            IP(public_ip)
        finally:
            return public_ip

    print('ERROR: Failed to find public ip address.')
    sys.exit(1)

def set_hostname_record(access_key, secret_key, boto3_route53, hostname, public_ip, zone_id):
    response = boto3_route53.change_resource_record_sets(
      HostedZoneId=zone_id,
      ChangeBatch={
        "Changes": [
          {
            "Action": "UPSERT",
            "ResourceRecordSet": {
              "Name": hostname,
              "Type": "A",
              "TTL": 300,
              "ResourceRecords": [
                {
                  "Value": public_ip
                },
              ]
            }
          },
        ]
      }
    )
    idstring = response.get('ChangeInfo').get('Id')
    response = boto3_route53.get_change(Id=idstring)
    while response.get('ChangeInfo').get('Status') == 'PENDING':
       time.sleep(5)
       response = boto3_route53.get_change(Id=idstring)
    else:
       return

def main():
    parser = argparse.ArgumentParser(description='AWS Route53 hostname managment')
    parser.add_argument('--hostname', required=True, help="The hostname string, ie foo.bar.com")

    arg = parser.parse_args()

    hostname = arg.hostname
    if hostname.count('.') == 1:
        domain_dot = hostname + '.'
    else:
        domain_dot =  ".".join(hostname.split('.')[1:]) + '.'

    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']

    public_ip = get_public_ip()

    boto3_route53 = boto3.client('route53')
    zones = boto3_route53.list_hosted_zones()
    for zone in zones['HostedZones']:
        if zone['Name'] == domain_dot and not zone['Config']['PrivateZone']:
            zone_id = zone['Id'].split('/')[2]
            records = boto3_route53.list_resource_record_sets(HostedZoneId=zone_id)

    for record in records['ResourceRecordSets']:
        if record['Type'] == 'A' and record['Name'][:-1] == hostname and record['ResourceRecords'][0]['Value'] != public_ip:
            set_hostname_record(access_key, secret_key, boto3_route53, hostname, public_ip, zone_id)

if __name__ == '__main__':
    sys.exit(main())
