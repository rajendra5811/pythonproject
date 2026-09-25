import boto3

ec2 = boto3.client('ec2')

resp = ec2.create_key_pair(KeyName ='my-key-pair')
print("resp['KeyMaterial']")
file = open("my-key-pair.pem",'w')
file.write(resp['KeyMaterial'])
file.close()
print("Key pair created and saved to my-key-pair.pem")
print("Security groups:")
print(ec2.describe_security_groups())
resp = ec2.create_security_group(GroupName='my-security-group', Description='My security group', VpcId='vpc-12345678')
print("Security group created with ID:", resp['GroupId'])


ec2.authorize_security_group_ingress( 
                                        
    GroupId=resp['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

ec2_resource = boto3.resource('ec2')
instances = ec2_resource.create_instances(
    ImageId = " ",
    