import boto3

# Create an boto3 client for IAM
iam = boto3.client('s3',
                 aws_access_key_id='YOUR_ACCESS_KEY',
                 aws_secret_access_key='YOUR_SECRET_KEY',
                 aws_session_token='YOUR_SESSION_TOKEN', 
                 region_name='YOUR_REGION')

#Create a boto3 session for IAM
session = boto3.Session( aws_access_key_id='YOUR_ACCESS_KEY',
                         aws_secret_access_key='YOUR_SECRET_KEY',   
                         aws_session_token='YOUR_SESSION_TOKEN',
                         region_name='YOUR_REGION')

#Create an boto3 resource for IAM
resource = boto3.resource('s3',
                    aws_access_key_id='YOUR_ACCESS_KEY',
                    aws_secret_access_key='YOUR_SECRET_KEY',
                    aws_session_token='YOUR_SESSION_TOKEN',
                    region_name='YOUR_REGION')