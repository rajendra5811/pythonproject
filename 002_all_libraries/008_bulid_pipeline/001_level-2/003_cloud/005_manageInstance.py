import boto3
import os
import sys
from botocore.exceptions import ClientError

def get_latest_ubuntu_ami(region_name='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region_name)
    try:
        response = ec2.describe_images(
            Owners=['099720109477'],  # Canonical
            Filters=[
                {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        images = response['Images']
        if not images:
            print("No Ubuntu AMIs found.")
            sys.exit(1)
        latest_image = max(images, key=lambda x: x['CreationDate'])
        return latest_image['ImageId']
    except ClientError as e:
        print(f"Error fetching AMI: {e}")
        sys.exit(1)
    create_key_pair(ec2, key_name)
    image_id = get_latest_ubuntu_ami(region)
    response = ec2.run_instances(
        ImageId = image_id,
        MinCount = 1,
        MaxCount = 1,
        KeyName = key_name
    )
    print(f"Instance created with ID: {response['Instances'][0]['InstanceId']},waitng for getting public IP... ")
    instance_id = response['Instances'][0]['InstanceId']
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print("Instance is now up and running.")
elif action in ['start','stop','reboot','terminate']:
    if not instance_id:
        print("The action '<action>' requires an instance ID.")
        sys.exit(1)
    def main():
        if len(sys.argv) < 2:
            print("Usage: python 005_manageInstance.py <action> |<key_name>| |<instance_id>| <region>")
            sys.exit(1)

        action = sys.argv[1]
        key_name = sys.argv[2] if len(sys.argv) > 2 else None
        instance_id = sys.argv[3] if len(sys.argv) > 3 else None
        region = sys.argv[4] if len(sys.argv) > 4 else 'us-east-1'
        manage_instance(action, key_name, instance_id, region)

    if __name__ == "__main__":
        main()