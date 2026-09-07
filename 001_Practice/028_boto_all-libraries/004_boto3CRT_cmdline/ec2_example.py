import os
import boto3
import json_operations
import json

#demo speciaifying data as variables
# key_path = './ec2_example.py



#demo loading config data from a json file
config_data = json_operations.load_json_file('config.json')
key_path = config_data['key_path']
key_name = config_data['key_name']
ami_id = config_data['ami_id']
instance_type = config_data['instance_type']
region_name = config_data['region_name']
ec2_json_data_path = config_data['ec2_json_data_path']
print(f"key_path: {key_path}, key_name: {key_name}, ami_id: {ami_id}, instance_type: {instance_type}, region_name: {region_name}, ec2_json_data_path: {ec2_json_data_path}")
ec2_data = json_operations.loadJsonData(ec2_json_data_path)

# Create an boto3 client for EC2
ec2_client = boto3.client('ec2', region_name = region_name)

def create_key_pair():
    if not os.path.exists(key_path):
        key_pair = ec2_client.create_key_pair(KeyName = key_name)
        private_key = key_pair['KeyMaterial']
        with open(key_path, 'w') as f:
            f.write(private_key)

#create aws ec2 instance
def create__instance():
    instance = ec2_client.run_instances(
        ImageId = ami_id,
        MinCount = 1,
