#!/usr/bin/python

import json
import os
import requests

def get_aws_metadata():
    """
    Grab EC2 metadata from the host environment if it exists and set Tutor plugin configuration
    when possible. This will be used in the `send-logs-to-s3` bash script for naming the S3 
    bucket directory names for this particular host EC2 machine.

    Ref: https://www.learnaws.org/2023/02/27/aws-instance-metadata-python/
    """
    metadata = {}

    instance_metadata = {
        'ami-id': "",
        'ami-launch-index': "",
        'ami-manifest-path': "",
        'block-device-mapping/': "",
        'events/': "",
        'hostname': "",
        'identity-credentials/': "",
        'instance-action': "",
        'instance-id': "",
        'instance-life-cycle': "",
        'instance-type': "",
        'local-hostname': "",
        'local-ipv4': "",
        'mac': "",
        'metrics/': "",
        'network/': "",
        'placement/': "",
        'profile': "",
        'public-hostname': "",
        'public-ipv4': "",
        'public-keys/': "",
        'reservation-id': "",
        'security-groups': "",
        'services/': "",
        'system': ""
    }

    dynamic_instance_metadata = {
        'accountId': "",
        'architecture': "",
        'availabilityZone': "",
        'billingProducts': "",
        'devpayProductCodes': "",
        'marketplaceProductCodes': "",
        'imageId': "",
        'instanceId': "",
        'instanceType': "",
        'kernelId': "",
        'pendingTime': "",
        'privateIp': "",
        'ramdiskId': "",
        'region': "",
        'version': ""
    }
   
    # Instance metadata
    for key in instance_metadata.keys():
        try:
            resp = requests.get(
                f'http://169.254.169.254/latest/meta-data/{key}',
                timeout=1
            )
            if resp.status_code != 200:
                print(f"tutor-contrib-utils plugin: get_aws_metadata() - Could not locate EC2 instance_metadata. Using defaults from the container.")

            metadata[key] = resp.text
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
           # Not on EC2 instance so just return empty dictionary.
           return metadata

    # Dynamic instance metadata
    for key in dynamic_instance_metadata.keys():
        try:
            resp = requests.get(
                f'http://169.254.169.254/latest/dynamic/instance-identity/document',
                timeout=1
            )
            if resp.status_code != 200:
                print("tutor-contrib-utils plugin: get_aws_metadata() - Could not locate EC2 dynamic_instance_metadata. Using defaults from the container.")

            metadata[key] = json.loads(resp.text).get(key)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
           # Not on EC2 instance so just return empty dictionary.
           return metadata
   
    return metadata


def export_aws_metadata():
    """
    Grabs AWS EC2 settings from the host machine and stores them in environment 
    variables which the 'logrotate-s3' service will pickup and use when passing 
    into the docker container environment variables. 

    This makes the values used within the docker container dynamic and avoids 
    having to build out a new image for each unique AWS EC2 host.
    """
    ec2_metadata = get_aws_metadata()

    # Persist the environment variable across sessions by writing to the host
    # machine user environment.
    # https://blog.tintoy.io/2017/06/exporting-environment-variables-from-python-to-bash/
    print(f"export AWS_INSTANCE_ID='{ec2_metadata.get('instance-id')}'")
    print(f"export AWS_LOCAL_IPV4='{ec2_metadata.get('local-ipv4')}'")
    print(f"export AWS_REGION='{ec2_metadata.get('region')}'")


if __name__ == "__main__":
    export_aws_metadata()
